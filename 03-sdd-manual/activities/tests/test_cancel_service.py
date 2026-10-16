"""T02+T03 (X-01, R-1): modelo cancelled_at + regla de dominio en services.

Convencion de trazabilidad: cada test se nombra con el ID de spec/plan que verifica.
Reloj fijo NOW importado de test_base (mismo patron que la suite base).
"""
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import OperationalError
from django.test import TestCase

from activities.models import Registration
from activities.services import (
    MESSAGES,
    WINDOW,
    can_cancel,
    cancel,
    cancellation_deadline,
    register,
    with_availability,
)
from activities.tests.test_base import NOW, activity


def users():
    User = get_user_model()
    ana = User.objects.create_user("ana")
    bruno = User.objects.create_user("bruno")
    return ana, bruno


class RegistrationModelTests(TestCase):
    """T02: F1-R08, F1-R12, F1-R29."""

    def test_T02_is_cancelled_false_when_no_date(self):
        ana, _ = users()
        act = activity()
        reg = Registration.objects.create(student=ana, activity=act)
        self.assertIsNone(reg.cancelled_at)
        self.assertIs(reg.is_cancelled, False)

    def test_T02_is_cancelled_true_when_dated(self):
        ana, _ = users()
        act = activity()
        reg = Registration.objects.create(student=ana, activity=act, cancelled_at=NOW)
        self.assertIs(reg.is_cancelled, True)

    def test_T02_clean_accepts_capacity_equal_confirmed_with_cancelled(self):
        ana, bruno = users()
        carla = get_user_model().objects.create_user("carla")
        act = activity(capacity=3)
        Registration.objects.create(student=ana, activity=act)
        Registration.objects.create(student=bruno, activity=act)
        Registration.objects.create(student=carla, activity=act, cancelled_at=NOW)
        act.capacity = 2  # == confirmadas (2), con 1 cancelada presente
        act.full_clean()  # no debe lanzar

    def test_T02_clean_rejects_below_confirmed(self):
        ana, bruno = users()
        carla = get_user_model().objects.create_user("carla")
        act = activity(capacity=3)
        Registration.objects.create(student=ana, activity=act)
        Registration.objects.create(student=bruno, activity=act)
        Registration.objects.create(student=carla, activity=act, cancelled_at=NOW)
        act.capacity = 1  # por debajo de confirmadas (2)
        with self.assertRaises(ValidationError) as ctx:
            act.full_clean()
        self.assertIn("No puede reducir", str(ctx.exception))


class CancelMessagesTests(TestCase):
    def test_F01_five_keys_present(self):
        for key in ("cancelled", "already_cancelled", "window_closed", "not_cancellable", "not_reenrollable"):
            self.assertIn(key, MESSAGES)
        self.assertEqual(MESSAGES["cancelled"], "Inscripción cancelada. Se liberó un cupo.")
        self.assertEqual(MESSAGES["already_cancelled"], "Esta inscripción ya estaba cancelada.")
        self.assertEqual(
            MESSAGES["window_closed"], "No podés cancelar: el plazo venció 24 h antes del inicio."
        )
        self.assertEqual(MESSAGES["not_cancellable"], "No se pudo cancelar esta inscripción.")
        self.assertEqual(
            MESSAGES["not_reenrollable"],
            "Tu inscripción fue cancelada; la reinscripción no está habilitada.",
        )


class CancelDeadlineTests(TestCase):
    """L-01...L-08 con S = NOW+48h, L = S-24h = NOW+24h."""

    def setUp(self):
        self.ana, self.bruno = users()
        self.starts_at = NOW + timedelta(hours=48)
        self.activity = activity(starts_at=self.starts_at, capacity=2)
        Registration.objects.create(student=self.ana, activity=self.activity)
        self.limit = self.starts_at - timedelta(hours=24)
        self.assertEqual(WINDOW, timedelta(hours=24))
        self.assertEqual(cancellation_deadline(self.activity), self.limit)

    def cancel_ana(self, now):
        return cancel(student=self.ana, activity_id=self.activity.pk, now=now)

    def test_L01_minus_one_hour_allows(self):
        self.assertEqual(self.cancel_ana(self.limit - timedelta(hours=1)), "cancelled")

    def test_L02_minus_one_second_allows(self):
        self.assertEqual(self.cancel_ana(self.limit - timedelta(seconds=1)), "cancelled")

    def test_L03_deadline_inclusive_allows(self):
        self.assertEqual(self.cancel_ana(self.limit), "cancelled")

    def test_L04_one_microsecond_past_rejected(self):
        self.assertEqual(
            self.cancel_ana(self.limit + timedelta(microseconds=1)), "window_closed"
        )
        self.assertIsNone(Registration.objects.get().cancelled_at)

    def test_L05_plus_one_second_rejected(self):
        self.assertEqual(self.cancel_ana(self.limit + timedelta(seconds=1)), "window_closed")

    def test_L06_plus_59min_rejected(self):
        self.assertEqual(self.cancel_ana(self.limit + timedelta(minutes=59)), "window_closed")

    def test_L07_at_start_rejected(self):
        self.assertEqual(self.cancel_ana(self.starts_at), "window_closed")

    def test_L08_started_two_hours_ago_rejected(self):
        self.activity.starts_at = NOW - timedelta(hours=2)
        self.activity.save()
        self.assertEqual(self.cancel_ana(NOW), "window_closed")
        self.assertIsNone(Registration.objects.get().cancelled_at)

    def test_E07_E08_window_closed_keeps_row(self):
        before = with_availability().get(pk=self.activity.pk).available
        self.assertEqual(self.cancel_ana(self.limit + timedelta(seconds=1)), "window_closed")
        self.assertIsNone(Registration.objects.get().cancelled_at)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, before)

    def test_asymmetry_register_exclusive_vs_cancel_inclusive(self):
        # register rechaza en starts_at == now (borde exclusivo del alta)...
        self.assertEqual(
            register(student=self.bruno, activity_id=self.activity.pk, now=self.starts_at),
            "started",
        )
        # ...mientras cancel concede en now == starts_at - WINDOW (borde inclusivo de la baja).
        self.assertEqual(self.cancel_ana(self.limit), "cancelled")


class CancelStateTests(TestCase):
    """L-09...L-16, E-03/E-04, E-06, E-09/E-10."""

    def setUp(self):
        self.ana, self.bruno = users()
        self.activity = activity(starts_at=NOW + timedelta(hours=48), capacity=2)

    def test_E01_effective_cancel_keeps_row_and_frees_one(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        reg_before = Registration.objects.get()
        created = reg_before.created_at
        before = with_availability().get(pk=self.activity.pk).available
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "cancelled")
        reg = Registration.objects.get()
        self.assertEqual(reg.pk, reg_before.pk)
        self.assertIsNotNone(reg.cancelled_at)
        self.assertEqual(reg.created_at, created)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, before + 1)

    def test_E02_exactly_one_seat(self):
        self.activity.capacity = 2
        self.activity.save()
        Registration.objects.create(student=self.ana, activity=self.activity)
        Registration.objects.create(student=self.bruno, activity=self.activity)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 0)
        n_rows = Registration.objects.count()
        n_conf = Registration.objects.filter(cancelled_at__isnull=True).count()
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "cancelled")
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)
        self.assertEqual(Registration.objects.count(), n_rows)
        self.assertEqual(Registration.objects.filter(cancelled_at__isnull=True).count(), n_conf - 1)

    def test_E03_foreign_is_generic(self):
        Registration.objects.create(student=self.bruno, activity=self.activity)
        before = with_availability().get(pk=self.activity.pk).available
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "not_cancellable")
        self.assertIsNone(Registration.objects.get().cancelled_at)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, before)

    def test_E04_missing_is_same_as_foreign(self):
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "not_cancellable")

    def test_L15_missing_activity_is_generic(self):
        self.assertEqual(cancel(student=self.ana, activity_id=999999, now=NOW), "not_cancellable")

    def test_E06_disabled_still_cancellable(self):
        self.activity.is_active = False
        self.activity.save()
        Registration.objects.create(student=self.ana, activity=self.activity)
        before = with_availability().get(pk=self.activity.pk).available
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "cancelled")
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, before + 1)

    def test_E09_repetition_keeps_original_date(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "cancelled")
        first = Registration.objects.get().cancelled_at
        before = with_availability().get(pk=self.activity.pk).available
        self.assertEqual(
            cancel(student=self.ana, activity_id=self.activity.pk, now=NOW + timedelta(hours=1)),
            "already_cancelled",
        )
        self.assertEqual(Registration.objects.get().cancelled_at, first)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, before)

    def test_E10_repetition_outside_window_still_already(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "cancelled")
        first = Registration.objects.get().cancelled_at
        # El reloj avanza mas alla del limite (o se reprograma antes): sigue already_cancelled.
        late = self.activity.starts_at - WINDOW + timedelta(seconds=1)
        self.assertEqual(
            cancel(student=self.ana, activity_id=self.activity.pk, now=late), "already_cancelled"
        )
        self.assertEqual(Registration.objects.get().cancelled_at, first)

    def test_L09_L16_matrix(self):
        # L-09: cancelada dentro de plazo
        Registration.objects.create(student=self.ana, activity=self.activity, cancelled_at=NOW)
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "already_cancelled")
        # L-10: cancelada fuera de plazo
        late = self.activity.starts_at - WINDOW + timedelta(hours=1)
        self.assertEqual(
            cancel(student=self.ana, activity_id=self.activity.pk, now=late), "already_cancelled"
        )
        # L-11: cancelada + deshabilitada
        self.activity.is_active = False
        self.activity.save()
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "already_cancelled")
        # L-12: cancelada + iniciada
        self.activity.starts_at = NOW - timedelta(hours=1)
        self.activity.save()
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "already_cancelled")
        # L-13/L-14: ajena con deshabilitada/iniciada -> generico sin fuga
        other = activity(title="Otra", starts_at=NOW - timedelta(hours=1), is_active=False)
        Registration.objects.create(student=self.bruno, activity=other)
        self.assertEqual(cancel(student=self.ana, activity_id=other.pk, now=NOW), "not_cancellable")
        # L-16: titular con A cancelada y B confirmada; repetir en A no toca B
        Registration.objects.create(student=self.ana, activity=other)
        self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "already_cancelled")
        self.assertIsNone(Registration.objects.get(student=self.ana, activity=other).cancelled_at)

    def test_R15_repetition_does_not_read_clock(self):
        Registration.objects.create(student=self.ana, activity=self.activity, cancelled_at=NOW)

        def fail_now():
            raise AssertionError("clock must not be read on already_cancelled")

        with patch("activities.services.timezone.now", side_effect=fail_now):
            self.assertEqual(
                cancel(student=self.ana, activity_id=self.activity.pk), "already_cancelled"
            )


class CancelCapacityTests(TestCase):
    """L-17...L-23, E-15 (guardian X-01), E-16, F1-R07."""

    def setUp(self):
        self.ana, self.bruno = users()
        self.carla = get_user_model().objects.create_user("carla")

    def test_L17_single_seat_cancel_frees_one(self):
        act = activity(capacity=1)
        Registration.objects.create(student=self.ana, activity=act)
        self.assertEqual(with_availability().get(pk=act.pk).available, 0)
        self.assertEqual(cancel(student=self.ana, activity_id=act.pk, now=NOW), "cancelled")
        self.assertEqual(with_availability().get(pk=act.pk).available, 1)

    def test_E15_L18_freed_seat_is_registerable_guardian(self):
        act = activity(capacity=1)
        Registration.objects.create(student=self.ana, activity=act)
        self.assertEqual(cancel(student=self.ana, activity_id=act.pk, now=NOW), "cancelled")
        self.assertEqual(register(student=self.bruno, activity_id=act.pk, now=NOW), "registered")
        self.assertEqual(with_availability().get(pk=act.pk).available, 0)

    def test_L19_repeat_does_not_free_second(self):
        act = activity(capacity=1)
        Registration.objects.create(student=self.ana, activity=act)
        self.assertEqual(cancel(student=self.ana, activity_id=act.pk, now=NOW), "cancelled")
        self.assertEqual(with_availability().get(pk=act.pk).available, 1)
        self.assertEqual(cancel(student=self.ana, activity_id=act.pk, now=NOW), "already_cancelled")
        self.assertEqual(with_availability().get(pk=act.pk).available, 1)

    def test_L20_load_counts_only_confirmed(self):
        act = activity(capacity=10)
        for u in (self.ana, self.bruno, self.carla):
            Registration.objects.create(student=u, activity=act)
        for u in (self.ana, self.bruno):
            Registration.objects.filter(student=u, activity=act).update(cancelled_at=NOW)
        # 8 confirmadas de 10 -> available 10 si hubiera 8... aca 1 confirmada:
        self.assertEqual(with_availability().get(pk=act.pk).available, 9)

    def test_L21_L22_E16_capacity_floor_over_confirmed(self):
        act = activity(capacity=3)
        Registration.objects.create(student=self.ana, activity=act)
        Registration.objects.create(student=self.bruno, activity=act)
        Registration.objects.create(student=self.carla, activity=act, cancelled_at=NOW)
        act.capacity = 2  # == confirmadas -> guarda
        act.full_clean()
        act.capacity = 1  # por debajo -> ValidationError con texto vigente
        with self.assertRaises(ValidationError) as ctx:
            act.full_clean()
        self.assertIn("No puede reducir", str(ctx.exception))

    def test_R07_reschedule_reopens_and_closes_window(self):
        act = activity(starts_at=NOW + timedelta(hours=48), capacity=2)
        Registration.objects.create(student=self.ana, activity=act)
        late = NOW + timedelta(hours=25)  # fuera de plazo para starts_at original
        self.assertEqual(cancel(student=self.ana, activity_id=act.pk, now=late), "window_closed")
        act.starts_at = NOW + timedelta(hours=72)  # mover adelante reabre
        act.save()
        self.assertEqual(cancel(student=self.ana, activity_id=act.pk, now=late), "cancelled")
        # y mover antes lo cierra de golpe
        act2 = activity(title="Otra", starts_at=NOW + timedelta(hours=72), capacity=2)
        Registration.objects.create(student=self.bruno, activity=act2)
        self.assertEqual(cancel(student=self.bruno, activity_id=act2.pk, now=late), "cancelled")


class ReenrollTests(TestCase):
    """E-11/E-12, F1-R20...R23."""

    def setUp(self):
        self.ana, self.bruno = users()
        self.activity = activity(starts_at=NOW + timedelta(hours=48), capacity=2)

    def test_E11_reenroll_rejected_with_own_message(self):
        Registration.objects.create(student=self.ana, activity=self.activity, cancelled_at=NOW)
        n = Registration.objects.count()
        result = register(student=self.ana, activity_id=self.activity.pk, now=NOW)
        self.assertEqual(result, "not_reenrollable")
        self.assertNotEqual(MESSAGES["not_reenrollable"], MESSAGES["already_registered"])
        self.assertEqual(Registration.objects.count(), n)
        self.assertIsNotNone(Registration.objects.get().cancelled_at)

    def test_E12_reenroll_wins_over_disabled_started_full(self):
        Registration.objects.create(student=self.ana, activity=self.activity, cancelled_at=NOW)
        self.activity.is_active = False
        self.activity.starts_at = NOW
        self.activity.capacity = 1
        self.activity.save()
        self.assertEqual(register(student=self.ana, activity_id=self.activity.pk, now=NOW), "not_reenrollable")

    def test_full_counts_only_confirmed(self):
        act = activity(capacity=1)
        Registration.objects.create(student=self.ana, activity=act, cancelled_at=NOW)
        self.assertEqual(register(student=self.bruno, activity_id=act.pk, now=NOW), "registered")


class CancelClockAndBusyTests(TestCase):
    """F1-R06 (reloj dentro del atomic), F1-R17 (busy selectivo)."""

    def setUp(self):
        self.ana, _ = users()
        self.activity = activity(starts_at=NOW + timedelta(hours=48), capacity=2)
        Registration.objects.create(student=self.ana, activity=self.activity)

    def test_R06_clock_read_inside_atomic_after_lock(self):
        from django.db import connections

        def after_lock():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW + timedelta(hours=25)  # pasado el limite NOW+24h

        with patch("activities.services.timezone.now", side_effect=after_lock) as clock:
            self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk), "window_closed")
            clock.assert_called_once()
        self.assertIsNone(Registration.objects.get().cancelled_at)

    def test_R06_clock_inside_window_allows(self):
        from django.db import connections

        def inside():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW

        with patch("activities.services.timezone.now", side_effect=inside):
            self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk), "cancelled")

    def test_L28_locked_is_busy_without_effect(self):
        with patch(
            "activities.services.Registration.objects.filter",
            side_effect=OperationalError("database is locked"),
        ):
            self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk, now=NOW), "busy")
        self.assertIsNone(Registration.objects.get().cancelled_at)

    def test_L29_other_operational_error_propagates(self):
        with patch(
            "activities.services.Registration.objects.filter",
            side_effect=OperationalError("broken schema"),
        ):
            with self.assertRaises(OperationalError):
                cancel(student=self.ana, activity_id=self.activity.pk, now=NOW)
