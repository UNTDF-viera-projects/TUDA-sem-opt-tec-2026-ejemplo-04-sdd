"""T08 (etapa 6): doble cancelacion simultanea, reloj tras el bloqueo y `busy`.

Patron de `ConcurrencyTests` (test_base): TransactionTestCase, archivo real
`data/test.sqlite3`, dos hilos + Barrier, conexiones cerradas al final.
Reloj fijo NOW importado de test_base.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import OperationalError, close_old_connections, connections
from django.test import TransactionTestCase

from activities.models import Registration
from activities.services import cancel, with_availability
from activities.tests.test_base import NOW, activity


def make_user(username):
    return get_user_model().objects.create_user(username)


class CancelConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.ana = make_user("ana")
        self.activity = activity(starts_at=NOW + timedelta(hours=48), capacity=1)
        Registration.objects.create(student=self.ana, activity=self.activity)

    def race_cancel(self):
        barrier = Barrier(2)

        def worker(_):
            close_old_connections()
            try:
                database = str(connections["default"].settings_dict["NAME"])
                assert database.endswith("test.sqlite3"), database
                assert "memory" not in database, database
                barrier.wait(timeout=10)
                return cancel(student=self.ana, activity_id=self.activity.pk, now=NOW)
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            return list(executor.map(worker, range(2)))

    def test_E13_concurrent_pair_single_transition(self):
        results = self.race_cancel()
        self.assertLessEqual(set(results), {"cancelled", "already_cancelled", "busy"})
        self.assertLessEqual(results.count("cancelled"), 1)
        self.assertEqual(Registration.objects.count(), 1)
        if "cancelled" in results:
            reg = Registration.objects.get()
            self.assertIsNotNone(reg.cancelled_at)
            self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)
        else:  # todo `busy`: sin efecto parcial
            self.assertIsNone(Registration.objects.get().cancelled_at)
            self.assertEqual(with_availability().get(pk=self.activity.pk).available, 0)

    def test_conditional_write_alone_returns_already(self):
        reg = Registration.objects.get()
        stolen_at = NOW + timedelta(minutes=5)

        def race_lost():
            # Otra transicion escribe primero por otro camino; la escritura
            # condicional de cancel() ya no encuentra fila confirmada.
            Registration.objects.filter(pk=reg.pk).update(cancelled_at=stolen_at)
            return NOW

        with patch("activities.services.timezone.now", side_effect=race_lost):
            self.assertEqual(
                cancel(student=self.ana, activity_id=self.activity.pk),
                "already_cancelled",
            )
        self.assertEqual(Registration.objects.get().cancelled_at, stolen_at)
        # La transicion ajena ya libero el unico cupo; la defensa no libera otro.
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)

    def test_clock_after_lock_outside_window_rejects(self):
        self.assertFalse(connections["default"].in_atomic_block)

        def after_lock():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW + timedelta(hours=25)  # pasado el limite NOW+24h

        with patch("activities.services.timezone.now", side_effect=after_lock) as clock:
            self.assertEqual(
                cancel(student=self.ana, activity_id=self.activity.pk),
                "window_closed",
            )
            clock.assert_called_once()
        self.assertIsNone(Registration.objects.get().cancelled_at)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 0)

    def test_clock_after_lock_inside_window_allows(self):
        def inside():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW

        with patch("activities.services.timezone.now", side_effect=inside):
            self.assertEqual(
                cancel(student=self.ana, activity_id=self.activity.pk),
                "cancelled",
            )
        self.assertIsNotNone(Registration.objects.get().cancelled_at)

    def test_L28_locked_returns_busy_without_effect(self):
        with patch(
            "activities.services.Registration.objects.filter",
            side_effect=OperationalError("database is locked"),
        ):
            self.assertEqual(
                cancel(student=self.ana, activity_id=self.activity.pk, now=NOW),
                "busy",
            )
        self.assertIsNone(Registration.objects.get().cancelled_at)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 0)

    def test_L29_other_operational_error_propagates(self):
        with patch(
            "activities.services.Registration.objects.filter",
            side_effect=OperationalError("broken schema"),
        ):
            with self.assertRaises(OperationalError):
                cancel(student=self.ana, activity_id=self.activity.pk, now=NOW)
