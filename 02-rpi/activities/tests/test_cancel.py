from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone as dt_timezone
from io import StringIO
from threading import Barrier
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import OperationalError, connections, close_old_connections
from django.test import Client, TestCase, TransactionTestCase
from activities.models import Activity, Registration
from activities.services import MESSAGES, cancel, register, with_availability

NOW = datetime(2030, 10, 1, 12, tzinfo=dt_timezone.utc)
LEAD = timedelta(hours=24)

def activity(**kwargs):
    values = dict(title="Práctica", description="Datos de prueba", starts_at=NOW+timedelta(hours=48), capacity=2)
    values.update(kwargs)
    return Activity.objects.create(**values)

class CancelServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("ana", password="test-pass")
        self.bruno = User.objects.create_user("bruno", password="test-pass")
        self.activity = activity()
        self.registration = Registration.objects.create(student=self.ana, activity=self.activity)
    def do_cancel(self, user=None, now=None, **kwargs):
        return cancel(student=user or self.ana, registration_id=self.registration.pk, now=now or NOW, **kwargs)

    def test_only_owner_can_cancel(self):
        other = Registration.objects.create(student=self.bruno, activity=activity())
        self.assertEqual(cancel(student=self.ana, registration_id=other.pk, now=NOW), "not_found")
        other.refresh_from_db()
        self.assertIsNone(other.cancelled_at)

    def test_exactly_24h_is_allowed(self):
        self.activity.starts_at = NOW+LEAD
        self.activity.save()
        self.assertEqual(self.do_cancel(), "cancelled")

    def test_under_24h_is_rejected_without_rounding(self):
        for offset in (LEAD-timedelta(microseconds=1), timedelta(hours=23, minutes=59, seconds=59)):
            self.activity.starts_at = NOW+offset
            self.activity.save()
            self.assertEqual(self.do_cancel(), "too_late")
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_too_late_leaves_row_untouched(self):
        self.activity.starts_at = NOW+timedelta(hours=1)
        self.activity.save()
        self.assertEqual(self.do_cancel(), "too_late")
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)
        self.assertEqual(Registration.objects.count(), 1)

    def test_cancel_keeps_row_and_stamps_date(self):
        self.assertEqual(self.do_cancel(), "cancelled")
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)
        self.assertEqual(Registration.objects.count(), 1)

    def test_cancel_frees_exactly_one_seat(self):
        self.activity.capacity = 1
        self.activity.save()
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 0)
        self.assertEqual(self.do_cancel(), "cancelled")
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)

    def test_repeat_cancel_does_not_free_another_seat(self):
        self.activity.capacity = 1
        self.activity.save()
        self.assertEqual(self.do_cancel(), "cancelled")
        self.assertEqual(self.do_cancel(), "already_cancelled")
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)

    def test_repeat_cancel_is_noop_even_past_deadline(self):
        self.assertEqual(self.do_cancel(), "cancelled")
        # Fuera de la ventana: aun así es no-op y conserva la fecha original.
        self.assertEqual(self.do_cancel(now=NOW+timedelta(hours=47)), "already_cancelled")
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 2)

    def test_disabled_activity_can_be_cancelled_within_window(self):
        self.activity.is_active = False
        self.activity.save()
        self.assertEqual(self.do_cancel(), "cancelled")

    def test_disabled_activity_cannot_be_cancelled_past_window(self):
        self.activity.is_active = False
        self.activity.starts_at = NOW+timedelta(hours=1)
        self.activity.save()
        self.assertEqual(self.do_cancel(), "too_late")

    def test_foreign_and_missing_are_indistinguishable(self):
        other = Registration.objects.create(student=self.bruno, activity=activity())
        foreign = cancel(student=self.ana, registration_id=other.pk, now=NOW)
        missing = cancel(student=self.ana, registration_id=999999, now=NOW)
        self.assertEqual(foreign, missing)
        self.assertEqual(MESSAGES[foreign], MESSAGES[missing])
        other.refresh_from_db()
        self.assertIsNone(other.cancelled_at)

    def test_reregistration_is_rejected_comprehensibly(self):
        self.assertEqual(self.do_cancel(), "cancelled")
        # Sin IntegrityError: el rechazo es explícito y la fila no se duplica.
        self.assertEqual(register(student=self.ana, activity_id=self.activity.pk, now=NOW), "cancelled_no_reenrollment")
        self.assertEqual(Registration.objects.count(), 1)

    def test_active_registration_still_says_already_registered(self):
        self.assertEqual(register(student=self.ana, activity_id=self.activity.pk, now=NOW), "already_registered")

    def test_busy_is_recoverable_other_errors_propagate(self):
        with patch("activities.services.Registration.objects.filter", side_effect=OperationalError("database is locked")):
            self.assertEqual(self.do_cancel(), "busy")
        with patch("activities.services.Registration.objects.filter", side_effect=OperationalError("broken schema")):
            with self.assertRaises(OperationalError):
                self.do_cancel()

    def test_three_count_sites_share_one_definition(self):
        self.assertEqual(self.do_cancel(), "cancelled")  # 1 cancelada
        Registration.objects.create(student=self.bruno, activity=self.activity)  # 1 activa, capacidad 2
        self.assertEqual(self.activity.registrations.count(), 2)
        self.assertEqual(self.activity.active_registrations.count(), 1)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)
        carla = get_user_model().objects.create_user("carla")
        # El cancelado no ocupa cupo: carla entra con el lugar que dejó la cancelación.
        self.assertEqual(register(student=carla, activity_id=self.activity.pk, now=NOW), "registered")
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 0)
        diego = get_user_model().objects.create_user("diego")
        self.assertEqual(register(student=diego, activity_id=self.activity.pk, now=NOW), "full")
        # La cancelada no impide reducir la capacidad: 2 activas toleran capacidad 2.
        self.activity.capacity = 2
        self.activity.full_clean()
        self.activity.capacity = 1
        with self.assertRaises(ValidationError):
            self.activity.full_clean()

    def test_seed_preserves_cancellations(self):
        call_command("seed_demo", reference_time=NOW.isoformat(), stdout=StringIO())
        target = Registration.objects.get(activity__seed_key="taller", student__username="ana")
        count = Registration.objects.count()
        self.assertEqual(cancel(student=target.student, registration_id=target.pk, now=NOW), "cancelled")
        for _ in range(2):
            call_command("seed_demo", stdout=StringIO())
        target.refresh_from_db()
        self.assertEqual(target.cancelled_at, NOW)
        self.assertEqual(Registration.objects.count(), count)

class CancelViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("ana", password="test-pass")
        self.bruno = User.objects.create_user("bruno", password="test-pass")
        self.activity = activity()
        self.registration = Registration.objects.create(student=self.ana, activity=self.activity)
        self.execute = f"/my-registrations/{self.registration.pk}/cancel/confirm/"
        self.confirm = f"/my-registrations/{self.registration.pk}/cancel/"
    def do_cancel(self, **kwargs):
        return cancel(student=self.ana, registration_id=self.registration.pk, now=NOW, **kwargs)
    def freeze_views_clock(self):
        # Un reloj fijo en 2030 expiraría la sesión real: hay que extenderla primero.
        session = self.client.session
        session.set_expiry(NOW+timedelta(days=100))
        session.save()
        return patch("activities.views.timezone.now", return_value=NOW)

    def test_confirmation_page_does_not_cancel(self):
        self.client.force_login(self.ana)
        response = self.client.get(self.confirm)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmar cancelación")
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_confirmation_page_is_404_for_foreign_and_missing(self):
        other = Registration.objects.create(student=self.bruno, activity=activity())
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(f"/my-registrations/{other.pk}/cancel/").status_code, 404)
        self.assertEqual(self.client.get("/my-registrations/999999/cancel/").status_code, 404)

    def test_confirmation_page_out_of_window_has_no_form(self):
        self.activity.starts_at = NOW+timedelta(hours=1)
        self.activity.save()
        self.client.force_login(self.ana)
        with self.freeze_views_clock():
            response = self.client.get(self.confirm)
        self.assertContains(response, "plazo de 24 horas")
        self.assertNotContains(response, "Confirmar cancelación")

    def test_confirmation_page_already_cancelled_has_no_form(self):
        self.assertEqual(self.do_cancel(), "cancelled")
        self.client.force_login(self.ana)
        response = self.client.get(self.confirm)
        self.assertContains(response, "ya está cancelada")
        self.assertNotContains(response, "Confirmar cancelación")

    def test_requires_post_session_and_csrf(self):
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(self.execute).status_code, 405)  # GET no muta
        self.client.logout()
        self.assertRedirects(self.client.post(self.execute), f"/accounts/login/?next={self.execute}")
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.ana)
        self.assertEqual(strict.post(self.execute).status_code, 403)
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_view_cancels_and_reports_message(self):
        self.client.force_login(self.ana)
        response = self.client.post(self.execute)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/my-registrations/")
        self.registration.refresh_from_db()
        # La vista nunca pasa `now`: la fecha real es la del reloj de la petición.
        self.assertIsNotNone(self.registration.cancelled_at)
        self.assertEqual(self.registration.cancelled_at.year, datetime.now(dt_timezone.utc).year)
        # El mensaje sobrevive una redirección; assertRedirects lo consumiría al seguirla.
        self.assertContains(self.client.get(response.url), MESSAGES["cancelled"])

    def test_mine_offers_and_then_hides_cancel(self):
        self.client.force_login(self.ana)
        response = self.client.get("/my-registrations/")
        self.assertContains(response, "Confirmada")
        self.assertContains(response, "Cancelar inscripción")
        self.assertEqual(self.do_cancel(), "cancelled")
        response = self.client.get("/my-registrations/")
        self.assertContains(response, "Cancelada")
        self.assertNotContains(response, "Cancelar inscripción")

    def test_mine_hides_cancel_out_of_window(self):
        self.activity.starts_at = NOW+timedelta(hours=1)
        self.activity.save()
        self.client.force_login(self.ana)
        with self.freeze_views_clock():
            response = self.client.get("/my-registrations/")
        self.assertNotContains(response, "Cancelar inscripción")

    def test_detail_shows_cancelled_state(self):
        self.assertEqual(self.do_cancel(), "cancelled")
        self.client.force_login(self.ana)
        response = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertContains(response, "Tu inscripción está cancelada")
        self.assertNotContains(response, "Inscribirme")

    def test_admin_sees_cancellations_but_cannot_alter_them(self):
        teacher = get_user_model().objects.create_superuser("teacher", "teacher@example.test", "pass")
        self.assertEqual(self.do_cancel(), "cancelled")
        self.client.force_login(teacher)
        self.assertEqual(self.client.get("/admin/activities/registration/").status_code, 200)
        change = self.client.get(f"/admin/activities/registration/{self.registration.pk}/change/")
        self.assertEqual(change.status_code, 200)
        self.assertNotContains(change, 'name="cancelled_at"')
        self.assertEqual(self.client.get(f"/admin/activities/registration/{self.registration.pk}/delete/").status_code, 403)

    def test_admin_can_reduce_capacity_after_cancellation(self):
        teacher = get_user_model().objects.create_superuser("teacher", "teacher@example.test", "pass")
        self.assertEqual(self.do_cancel(), "cancelled")
        Registration.objects.create(student=self.bruno, activity=self.activity)  # 1 activa de 2
        self.client.force_login(teacher)
        form = {"title": "Práctica", "description": "Datos", "starts_at_0": "2030-10-03", "starts_at_1": "09:00:00", "capacity": 1, "is_active": "on", "_save": "Guardar"}
        url = f"/admin/activities/activity/{self.activity.pk}/change/"
        self.assertEqual(self.client.post(url, form).status_code, 302)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.capacity, 1)
        carla = get_user_model().objects.create_user("carla")
        Registration.objects.create(student=carla, activity=self.activity)  # 2 activas con capacidad 1
        rejected = self.client.post(url, form)
        self.assertEqual(rejected.status_code, 200)
        self.assertContains(rejected, "No puede reducir")

class CancelClockTests(TransactionTestCase):
    def test_default_clock_is_read_after_lock(self):
        ana = get_user_model().objects.create_user("a")
        act = activity(capacity=2)
        registration = Registration.objects.create(student=ana, activity=act)
        self.assertFalse(connections["default"].in_atomic_block)
        def after_lock():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW+timedelta(hours=47)  # ya no alcanza el plazo
        with patch("activities.services.timezone.now", side_effect=after_lock) as clock:
            self.assertEqual(cancel(student=ana, registration_id=registration.pk), "too_late")
            clock.assert_called_once()
        registration.refresh_from_db()
        self.assertIsNone(registration.cancelled_at)

class CancelConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.ana = get_user_model().objects.create_user("a")
        self.activity = activity(capacity=2)
        self.registration = Registration.objects.create(student=self.ana, activity=self.activity)
    def race_cancel(self):
        barrier = Barrier(2)
        def worker(_):
            close_old_connections()
            try:
                database = str(connections["default"].settings_dict["NAME"])
                assert database.endswith("test.sqlite3"), database
                assert "memory" not in database, database
                barrier.wait(timeout=10)
                return cancel(student=self.ana, registration_id=self.registration.pk, now=NOW)
            finally:
                connections["default"].close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            return list(executor.map(worker, range(2)))

    def test_two_simultaneous_cancels_produce_one_transition(self):
        self.assertCountEqual(self.race_cancel(), ["cancelled", "already_cancelled"])
        refreshed = Registration.objects.get()
        self.assertEqual(refreshed.cancelled_at, NOW)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 2)

    def test_simultaneous_cancel_and_reregistration_keeps_one_row(self):
        barrier = Barrier(2)
        def canceller():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return cancel(student=self.ana, registration_id=self.registration.pk, now=NOW)
            finally:
                connections["default"].close()
        def registrar():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return register(student=self.ana, activity_id=self.activity.pk, now=NOW)
            finally:
                connections["default"].close()
        # Ambos workers en el mismo executor: si no, la barrera queda sin la segunda parte.
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(canceller), executor.submit(registrar)]
            results = [f.result() for f in futures]
        self.assertEqual(results.count("cancelled"), 1)
        self.assertEqual(Registration.objects.count(), 1)  # ni se duplica ni se pierde