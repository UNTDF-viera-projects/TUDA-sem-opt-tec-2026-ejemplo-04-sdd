from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone as dt_timezone
from threading import Barrier
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.db import connections, close_old_connections
from django.test import Client, TestCase, TransactionTestCase
from activities.models import Activity, Registration
from activities.services import MESSAGES, can_cancel, cancel_registration, cancellation_deadline, register, with_availability

NOW = datetime(2030, 10, 1, 12, tzinfo=dt_timezone.utc)
DEADLINE = NOW + timedelta(hours=24)  # NOW+48h de inicio menos 24h de ventana.

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
    def cancel(self, user=None, **kwargs):
        return cancel_registration(student=user or self.ana, registration_id=self.registration.pk, **{"now": NOW, **kwargs})
    def available(self):
        return with_availability().get(pk=self.activity.pk).available

    def test_success_keeps_row_with_date_and_frees_exactly_one_seat(self):
        created_at = self.registration.created_at
        self.assertEqual(self.cancel(), "cancelled")
        self.registration.refresh_from_db()
        self.assertTrue(self.registration.is_cancelled)
        self.assertEqual(self.registration.cancelled_at, NOW)
        self.assertEqual(self.registration.created_at, created_at)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(self.activity.registrations.filter(cancelled_at__isnull=True).count(), 0)
        self.assertEqual(self.available(), 2)

    def test_window_is_inclusive_at_exactly_24_hours(self):
        self.assertEqual(self.cancel(now=DEADLINE), "cancelled")

    def test_window_closed_one_second_after_deadline(self):
        self.assertEqual(self.cancel(now=DEADLINE+timedelta(seconds=1)), "window_closed")
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)
        self.assertEqual(self.available(), 1)

    def test_started_activity_is_out_of_window(self):
        self.activity.starts_at = NOW-timedelta(hours=2); self.activity.save()
        self.assertEqual(self.cancel(now=NOW), "window_closed")
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.is_cancelled)

    def test_repeat_keeps_original_date_and_frees_nothing(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.assertEqual(self.cancel(now=NOW+timedelta(hours=1)), "already_cancelled")
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)
        self.assertEqual(self.available(), 2)

    def test_repeat_outside_window_still_reports_already_cancelled(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.assertEqual(self.cancel(now=NOW+timedelta(days=3)), "already_cancelled")
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)
        self.assertEqual(self.available(), 2)

    def test_disabled_activity_allows_cancellation_within_window(self):
        self.activity.is_active = False; self.activity.save()
        self.assertEqual(self.cancel(), "cancelled")

    def test_freed_seat_is_reusable_by_another_student(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.assertEqual(register(student=self.bruno, activity_id=self.activity.pk, now=NOW), "registered")
        self.assertEqual(Registration.objects.count(), 2)
        self.assertEqual(self.available(), 1)

    def test_capacity_validation_ignores_cancelled(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.assertEqual(register(student=self.bruno, activity_id=self.activity.pk, now=NOW), "registered")
        self.activity.capacity = 1
        self.activity.full_clean()  # 1 confirmada, capacidad 1: la cancelada no cuenta.

    def test_capacity_may_drop_to_confirmed_only(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.activity.capacity = 1
        self.activity.full_clean()  # La cancelada no impide reducir la capacidad.

    def test_only_the_holder_can_cancel(self):
        self.assertEqual(self.cancel(self.bruno), "unavailable")
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.is_cancelled)
        self.assertEqual(self.available(), 1)

    def test_unknown_registration_is_indistinguishable_from_foreign_one(self):
        missing = cancel_registration(student=self.ana, registration_id=999999, now=NOW)
        foreign = self.cancel(self.bruno)
        self.assertEqual(missing, "unavailable")
        self.assertEqual(foreign, missing)

    def test_reinscription_is_rejected_and_creates_nothing(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.assertEqual(register(student=self.ana, activity_id=self.activity.pk, now=NOW), "reinscription_unavailable")
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(self.available(), 2)

    def test_reinscription_message_wins_over_disabled_and_started(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.activity.is_active = False
        self.activity.starts_at = NOW-timedelta(hours=2)
        self.activity.save()
        self.assertEqual(register(student=self.ana, activity_id=self.activity.pk, now=NOW), "reinscription_unavailable")

    def test_busy_is_recoverable_and_other_errors_propagate(self):
        from django.db import OperationalError
        with patch("activities.services.Registration.objects.filter", side_effect=OperationalError("database is locked")):
            self.assertEqual(self.cancel(), "busy")
        with patch("activities.services.Registration.objects.filter", side_effect=OperationalError("broken schema")):
            with self.assertRaises(OperationalError):
                self.cancel()
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_deadline_helper_and_button_predicate(self):
        self.assertEqual(cancellation_deadline(self.activity), self.activity.starts_at-timedelta(hours=24))
        self.assertTrue(can_cancel(registration=self.registration, now=NOW))
        self.assertTrue(can_cancel(registration=self.registration, now=DEADLINE))
        self.assertFalse(can_cancel(registration=self.registration, now=DEADLINE+timedelta(seconds=1)))

    def test_button_predicate_hides_cancelled_registration(self):
        self.assertEqual(self.cancel(), "cancelled")
        self.registration.refresh_from_db()
        self.assertFalse(can_cancel(registration=self.registration, now=NOW))

    def test_default_clock_reads_the_real_deadline(self):
        with patch("activities.services.timezone.now", return_value=DEADLINE+timedelta(seconds=1)) as clock:
            self.assertEqual(cancel_registration(student=self.ana, registration_id=self.registration.pk), "window_closed")
            clock.assert_called_once()
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_default_clock_is_evaluated_inside_atomic_block(self):
        def after_lock():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW
        with patch("activities.services.timezone.now", side_effect=after_lock):
            self.assertEqual(cancel_registration(student=self.ana, registration_id=self.registration.pk), "cancelled")

class CancelViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("ana", password="test-pass")
        self.bruno = User.objects.create_user("bruno", password="test-pass")
        self.activity = activity()
        self.registration = Registration.objects.create(student=self.ana, activity=self.activity)
        self.login(self.client, self.ana)
    def login(self, client, user):
        # El reloj de pruebas es 2030 y la sesión nace en 2026: sin extender el
        # vencimiento, el backend la da por expirada en toda prueba con reloj fijo.
        client.force_login(user)
        session = client.session; session.set_expiry(timedelta(days=365*10)); session.save()
    @property
    def url(self):
        return f"/my-registrations/{self.registration.pk}/cancel/"

    def test_confirmation_page_does_not_mutate(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmar cancelación")
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_confirmation_page_shows_activity_start_and_deadline(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get(self.url)
        self.assertContains(response, "03/10/2030 09:00")  # Inicio en Ushuaia.
        self.assertContains(response, "02/10/2030 09:00")  # Límite: 24h antes.

    def test_confirmation_page_outside_window_offers_no_action(self):
        with patch("activities.views.timezone.now", return_value=DEADLINE+timedelta(seconds=1)):
            response = self.client.get(self.url)
        self.assertNotContains(response, "Confirmar cancelación")
        self.assertContains(response, "plazo venció")

    def test_post_cancels_and_redirects_to_mine(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.post(self.url)
        self.assertRedirects(response, "/my-registrations/")
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)

    def test_post_requires_csrf_and_other_verbs_are_rejected(self):
        client = Client(enforce_csrf_checks=True); self.login(client, self.ana)
        with patch("activities.views.timezone.now", return_value=NOW):
            self.assertEqual(client.get(self.url).status_code, 200)
            self.assertEqual(client.post(self.url).status_code, 403)
            # Con token válido el PUT llega a la vista, que responde 405.
            self.assertEqual(client.put(self.url, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value).status_code, 405)
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_post_outside_window_reports_closed_window(self):
        with patch("activities.views.timezone.now", return_value=DEADLINE+timedelta(seconds=1)):
            response = self.client.post(self.url, follow=True)
        self.assertContains(response, "plazo para cancelar venció")
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)

    def test_repeat_post_does_not_change_original_date(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            self.client.post(self.url)
        with patch("activities.views.timezone.now", return_value=NOW+timedelta(days=2)):
            response = self.client.post(self.url, follow=True)
        self.assertContains(response, MESSAGES["already_cancelled"])
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)

    def test_confirmation_page_of_cancelled_registration_offers_no_action(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            self.client.post(self.url)
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get(self.url)
        self.assertContains(response, "ya estaba cancelada")
        self.assertNotContains(response, "Confirmar cancelación")

    def test_foreign_and_unknown_registration_answer_identically(self):
        # "Ajena" es la inscripción de Ana solicitada por Bruno; "inexistente" no existe.
        client = Client(); self.login(client, self.bruno)
        foreign = self.outcome(client, f"/my-registrations/{self.registration.pk}/cancel/")
        missing = self.outcome(client, "/my-registrations/999999/cancel/")
        self.assertEqual(foreign[0], 200)  # La cadena seguida termina en la página de "mine".
        self.assertEqual(foreign, missing)
        self.assertEqual(foreign[1], "/my-registrations/")
        self.assertEqual(foreign[2], MESSAGES["unavailable"])
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.cancelled_at)
    def outcome(self, client, url):
        response = client.get(url, follow=True)
        text = "".join(str(message) for message in response.context["messages"])
        return (response.status_code, response.redirect_chain[0][0] if response.redirect_chain else None, text)

    def test_mine_shows_state_date_and_cancel_entry(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            self.client.post(self.url)
        other = Registration.objects.create(student=self.ana, activity=activity(title="Otra", starts_at=NOW+timedelta(hours=72)))
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get("/my-registrations/")
        self.assertContains(response, "Confirmada")
        self.assertContains(response, "Cancelada el")
        self.assertContains(response, f"/my-registrations/{other.pk}/cancel/")
        self.assertNotContains(response, f"/my-registrations/{self.registration.pk}/cancel/")

    def test_mine_hides_cancel_entry_outside_window_and_for_cancelled(self):
        soon = Registration.objects.create(student=self.ana, activity=activity(title="Próxima", starts_at=NOW+timedelta(hours=2)))
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get("/my-registrations/")
            self.assertNotContains(response, f"/my-registrations/{soon.pk}/cancel/")
            self.assertContains(response, f"/my-registrations/{self.registration.pk}/cancel/")
            self.client.post(self.url)
            after = self.client.get("/my-registrations/")
        self.assertNotContains(after, f"/my-registrations/{self.registration.pk}/cancel/")

    def test_mine_never_exposes_other_students_entries(self):
        Registration.objects.create(student=self.bruno, activity=activity(title="De Bruno"))
        self.assertNotContains(self.client.get("/my-registrations/"), "De Bruno")

    def test_detail_of_cancelled_registration_has_no_reinscription(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            self.client.post(self.url)
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertContains(response, "Tu inscripción está cancelada")
        self.assertContains(response, "reinscripción no está disponible")
        self.assertNotContains(response, "Inscribirme")

    def test_detail_of_confirmed_registration_has_no_cancel_form(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertContains(response, "Tu inscripción está confirmada")
        self.assertNotContains(response, "Confirmar cancelación")
        self.assertNotContains(response, "Inscribirme")

    def test_register_after_cancellation_is_refused_with_clear_message(self):
        with patch("activities.views.timezone.now", return_value=NOW):
            self.client.post(self.url)
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.post(f"/activities/{self.activity.pk}/register/", follow=True)
        self.assertContains(response, MESSAGES["reinscription_unavailable"])
        self.assertEqual(Registration.objects.count(), 1)

    def test_admin_keeps_cancelled_registration_read_only(self):
        with patch("activities.services.timezone.now", return_value=NOW):
            self.client.post(self.url)
        admin = get_user_model().objects.create_superuser("teacher", "teacher@example.test", "pass")
        self.client.force_login(admin)
        self.assertContains(self.client.get("/admin/activities/registration/"), "cancelada")
        self.assertEqual(self.client.get(f"/admin/activities/registration/{self.registration.pk}/delete/").status_code, 403)
        self.assertEqual(self.client.get("/admin/activities/registration/add/").status_code, 403)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)

    def test_cancel_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

class CancelConcurrencyTests(TransactionTestCase):
    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("a")
        self.activity = activity(capacity=2)
        self.registration = Registration.objects.create(student=self.ana, activity=self.activity)
    def race(self, jobs):
        barrier = Barrier(len(jobs))
        def worker(job):
            close_old_connections()
            try:
                database = str(connections["default"].settings_dict["NAME"])
                assert database.endswith("test.sqlite3"), database
                assert "memory" not in database, database
                barrier.wait(timeout=10)
                return cancel_registration(student=self.ana, registration_id=self.registration.pk, now=NOW)
            finally: connections["default"].close()
        with ThreadPoolExecutor(max_workers=len(jobs)) as executor: return list(executor.map(worker, jobs))
    def test_two_simultaneous_cancellations_produce_one_transition(self):
        self.assertCountEqual(self.race([0, 1]), ["cancelled", "already_cancelled"])
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.cancelled_at, NOW)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 2)
        self.assertEqual(Registration.objects.count(), 1)
