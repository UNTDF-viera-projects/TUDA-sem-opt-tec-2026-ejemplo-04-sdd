"""T04 (DD-07/DD-08 + contexto DD-09): vista cancel_registration + URL cancel.

Convencion: cada test se nombra con el ID de spec/plan que verifica.
"""
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase

from activities.models import Activity, Registration
from activities.services import MESSAGES, cancel
from activities.tests.test_base import NOW, activity


def make_users():
    User = get_user_model()
    return User.objects.create_user("ana", password="test-pass"), User.objects.create_user(
        "bruno", password="test-pass"
    )


def posted_message(response):
    stored = list(response.wsgi_request._messages)
    assert len(stored) == 1
    return stored[0]


def post_cancel(client, url):
    """POST con follow: consume mensajes previas del mismo cliente.

    Cada redirect deja mensajes sin consumir en la sesion; sin follow, el
    segundo POST del mismo test ve los mensajes acumulados. Con follow, el
    GET a mine los renderiza y `context["messages"]` trae solo el actual.
    """
    response = client.post(url, follow=True)
    assert response.redirect_chain == [("/my-registrations/", 302)], response.redirect_chain
    stored = list(response.context["messages"])
    assert len(stored) == 1, [str(m) for m in stored]
    return response, stored[0]


class CancelViewTests(TestCase):
    def setUp(self):
        self.ana, self.bruno = make_users()
        self.activity = activity(starts_at=NOW + timedelta(hours=48), capacity=2)
        self.url = f"/activities/{self.activity.pk}/cancel/"
        self.client.force_login(self.ana)
        # La sesion debe sobrevivir al reloj parchado (NOW=2030): expiracion
        # explicita en el futuro, mismo patron que test_base.py (test_catalog).
        session = self.client.session
        session.set_expiry(NOW + timedelta(days=100))
        session.save()

    def cancel_url(self, pk):
        return f"/activities/{pk}/cancel/"

    # --- E-01: cancelacion efectiva por POST -> 302 a mine con clave/texto ---
    def test_E01_post_cancels_redirects_mine(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        with patch("activities.services.timezone.now", return_value=NOW):
            response, message = post_cancel(self.client, self.url)
        self.assertEqual(response.status_code, 200)  # tras seguir el 302 a mine
        self.assertEqual(message.extra_tags, "cancelled")
        self.assertEqual(str(message), MESSAGES["cancelled"])
        self.assertIsNotNone(Registration.objects.get().cancelled_at)

    # --- Cinco resultados -> 302 unico a mine con su clave (F1-R24) ---
    def test_all_five_results_redirect_mine_with_key(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        for result in ("cancelled", "already_cancelled", "window_closed", "not_cancellable", "busy"):
            with self.subTest(result=result):
                with patch("activities.views.cancel", return_value=result):
                    response, message = post_cancel(self.client, self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(message.extra_tags, result)
                self.assertEqual(str(message), MESSAGES[result])

    # --- E-03/E-04/E-05 identidad de respuesta campo a campo (F1-R01/F1-R03) ---
    def test_E03_E04_E05_identical_response(self):
        other = activity(title="Otra", starts_at=NOW + timedelta(hours=48), capacity=2)
        Registration.objects.create(student=self.bruno, activity=other)  # E-03: ajena
        Registration.objects.create(
            student=self.bruno, activity=self.activity
        )  # E-03: ajena en la misma actividad
        responses = {}
        with patch("activities.services.timezone.now", return_value=NOW):
            responses["E-03"] = post_cancel(self.client, self.cancel_url(other.pk))
            responses["E-04"] = post_cancel(self.client, self.cancel_url(self.activity.pk))
            responses["E-05"] = post_cancel(self.client, self.cancel_url(999999))
        compared = {}
        for key, (response, message) in responses.items():
            compared[key] = (
                message.extra_tags,
                str(message),
                tuple(response.redirect_chain),
            )
            self.assertEqual(response.status_code, 200)
            for url, status in response.redirect_chain:
                self.assertNotEqual(status, 404)
                self.assertEqual(url, "/my-registrations/")
        self.assertEqual(compared["E-03"], compared["E-04"])
        self.assertEqual(compared["E-04"], compared["E-05"])
        self.assertEqual(compared["E-03"][0], "not_cancellable")
        # Sin efecto: ninguna fila tocada.
        self.assertEqual(Registration.objects.filter(cancelled_at__isnull=False).count(), 0)

    # --- E-05/L-30: actividad inexistente o borrada -> not_cancellable sin 404 ---
    def test_E05_missing_activity_no_404(self):
        with patch("activities.services.timezone.now", return_value=NOW):
            response, message = post_cancel(self.client, self.cancel_url(999999))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.extra_tags, "not_cancellable")

    def test_L30_deleted_between_render_and_post(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        page = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertEqual(page.status_code, 200)
        pk = self.activity.pk
        self.activity.delete()  # la cascada borra la inscripcion
        with patch("activities.services.timezone.now", return_value=NOW):
            response, message = post_cancel(self.client, self.cancel_url(pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.extra_tags, "not_cancellable")

    # --- E-14/L-24/L-25/L-26: metodo, CSRF, sesion (F1-R02) ---
    def test_E14_L24_get_is_405_without_effect(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertIsNone(Registration.objects.get().cancelled_at)

    def test_L25_post_without_csrf_is_403(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.ana)
        session = client.session
        session.set_expiry(NOW + timedelta(days=100))
        session.save()
        response = client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(Registration.objects.get().cancelled_at)

    def test_L26_anonymous_redirects_to_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    # --- Doble POST: cancelled -> already_cancelled (L-27 a nivel vista) ---
    def test_double_post_cancelled_then_already(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        with patch("activities.services.timezone.now", return_value=NOW):
            first, first_message = post_cancel(self.client, self.url)
            second, second_message = post_cancel(self.client, self.url)
        for response in (first, second):
            self.assertEqual(response.status_code, 200)
        self.assertEqual(first_message.extra_tags, "cancelled")
        self.assertEqual(second_message.extra_tags, "already_cancelled")

    # --- Contexto DD-09: can_cancel en detail y cancellable_ids en mine ---
    def test_detail_exposes_can_cancel_inside_window(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["can_cancel"])

    def test_detail_can_cancel_false_outside_window(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        late = NOW + timedelta(hours=25)
        with patch("activities.views.timezone.now", return_value=late):
            response = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertFalse(response.context["can_cancel"])

    def test_mine_exposes_cancellable_ids(self):
        reg = Registration.objects.create(student=self.ana, activity=self.activity)
        with patch("activities.views.timezone.now", return_value=NOW):
            response = self.client.get("/my-registrations/")
        self.assertIn(reg.pk, response.context["cancellable_ids"])


class TemplateTests(TestCase):
    """T05 (DD-09): badges, fecha de cancelacion y boton condicionado (F1-R25/R26)."""

    def setUp(self):
        self.ana, self.bruno = make_users()
        self.activity = activity(starts_at=NOW + timedelta(hours=48), capacity=2)
        self.url = f"/activities/{self.activity.pk}/cancel/"
        self.client.force_login(self.ana)
        session = self.client.session
        session.set_expiry(NOW + timedelta(days=100))
        session.save()

    @staticmethod
    def stamp(cancelled_at):
        from django.template.defaultfilters import date as date_filter
        from django.utils import timezone

        # El filtro `date` lleva `expects_localtime=True`: el motor convierte
        # a la zona local antes de formatear; replicarlo aca.
        return date_filter(timezone.localtime(cancelled_at), "d/m/Y H:i:s")

    def test_R25_cancelled_shows_date_not_confirmed(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        with patch("activities.services.timezone.now", return_value=NOW):
            self.assertEqual(cancel(student=self.ana, activity_id=self.activity.pk), "cancelled")
        stamp = self.stamp(Registration.objects.get().cancelled_at)
        detail = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertContains(detail, "Cancelada")
        self.assertContains(detail, stamp)
        self.assertContains(detail, "reinscripci")
        self.assertNotContains(detail, "Tu inscripción está confirmada")
        self.assertNotContains(detail, "Inscribirme")
        self.assertNotContains(detail, "/cancel/")
        mine = self.client.get("/my-registrations/")
        self.assertContains(mine, "Cancelada")
        self.assertContains(mine, stamp)
        self.assertNotContains(mine, "Confirmada")
        self.assertNotContains(mine, "Tu inscripción está confirmada")
        self.assertNotContains(mine, "/cancel/")

    def test_R26_button_hidden_outside_window(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        late = NOW + timedelta(hours=25)  # pasado el limite NOW+24h
        with patch("activities.services.timezone.now", return_value=late):
            detail = self.client.get(f"/activities/{self.activity.pk}/")
            mine = self.client.get("/my-registrations/")
        cancel_path = f"/activities/{self.activity.pk}/cancel/"
        self.assertContains(detail, "Tu inscripción está confirmada")
        self.assertNotContains(detail, cancel_path)
        self.assertContains(detail, "24 h antes del inicio")  # P-01(c): regla en texto
        self.assertContains(mine, "Confirmada")
        self.assertNotContains(mine, cancel_path)
        self.assertContains(mine, "24 h antes del inicio")

    def test_R26_button_matches_service_decision(self):
        cases = ((NOW, True, "cancelled"), (NOW + timedelta(hours=25), False, "window_closed"))
        for now, expected_button, expected_result in cases:
            with self.subTest(now=now):
                act = activity(title=f"Act {now.isoformat()}", starts_at=NOW + timedelta(hours=48))
                Registration.objects.create(student=self.ana, activity=act)
                cancel_path = f"/activities/{act.pk}/cancel/"
                with patch("activities.services.timezone.now", return_value=now):
                    detail = self.client.get(f"/activities/{act.pk}/")
                    mine = self.client.get("/my-registrations/")
                    decision = cancel(student=self.ana, activity_id=act.pk)
                if expected_button:
                    self.assertContains(detail, cancel_path)
                    self.assertContains(mine, cancel_path)
                else:
                    self.assertNotContains(detail, cancel_path)
                    self.assertNotContains(mine, cancel_path)
                self.assertEqual(decision, expected_result)

    def test_L27_double_click_single_date(self):
        Registration.objects.create(student=self.ana, activity=self.activity)
        with patch("activities.services.timezone.now", return_value=NOW):
            _, first_message = post_cancel(self.client, self.url)
            first_date = Registration.objects.get().cancelled_at
            _, second_message = post_cancel(self.client, self.url)
            second_date = Registration.objects.get().cancelled_at
        self.assertEqual(first_message.extra_tags, "cancelled")
        self.assertEqual(second_message.extra_tags, "already_cancelled")
        self.assertEqual(first_date, second_date)  # una sola fecha, sin reescritura
        stamp = self.stamp(second_date)
        mine = self.client.get("/my-registrations/")
        self.assertContains(mine, stamp, count=1)
        detail = self.client.get(f"/activities/{self.activity.pk}/")
        self.assertContains(detail, stamp, count=1)


class AdminTests(TestCase):
    """T06 (etapa 4): `cancelled_at` visible de solo lectura; piso de capacidad.

    E-16/L-21: bajar capacidad hasta el nº de confirmadas (con 1 cancelada)
    guarda. L-22: por debajo → `ValidationError` «No puede reducir…».
    """

    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("ana", password="test-pass")
        self.bruno = User.objects.create_user("bruno", password="test-pass")
        self.carol = User.objects.create_user("carol", password="test-pass")
        self.dave = User.objects.create_user("dave", password="test-pass")
        self.admin = User.objects.create_superuser(
            "docente", "docente@example.test", "test-pass"
        )
        self.activity = activity(capacity=4)
        for user in (self.ana, self.bruno, self.carol, self.dave):
            Registration.objects.create(student=user, activity=self.activity)
        # 1 cancelada → 3 confirmadas (E-16: reducir a 3 guarda).
        Registration.objects.filter(
            student=self.dave, activity=self.activity
        ).update(cancelled_at=NOW)
        self.client.force_login(self.admin)

    def post_capacity(self, capacity):
        return self.client.post(
            f"/admin/activities/activity/{self.activity.pk}/change/",
            {
                "title": "Práctica",
                "description": "Datos",
                "starts_at_0": "2030-10-03",
                "starts_at_1": "09:00:00",
                "capacity": capacity,
                "is_active": "on",
                "_save": "Guardar",
            },
        )

    def test_E16_L21_reduce_to_confirmed_count_saves(self):
        self.assertEqual(
            self.activity.registrations.filter(cancelled_at__isnull=True).count(), 3
        )
        response = self.post_capacity(3)
        self.assertEqual(response.status_code, 302)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.capacity, 3)

    def test_L22_below_confirmed_rejected(self):
        response = self.post_capacity(2)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No puede reducir")
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.capacity, 4)

    def test_cancelled_at_readonly_in_edit_and_present_in_list(self):
        from activities.admin import RegistrationAdmin

        self.assertIn("cancelled_at", RegistrationAdmin.list_display)
        self.assertIn("cancelled_at", RegistrationAdmin.readonly_fields)
        reg = Registration.objects.get(student=self.ana, activity=self.activity)
        self.assertIsNone(reg.cancelled_at)
        # Intento de escritura forjada por POST: debe ignorarse.
        response = self.client.post(
            f"/admin/activities/registration/{reg.pk}/change/",
            {"cancelled_at_0": "2030-10-02", "cancelled_at_1": "10:00:00", "_save": "Guardar"},
        )
        self.assertIn(response.status_code, (200, 302))
        reg.refresh_from_db()
        self.assertIsNone(reg.cancelled_at)
        # Presente en el listado y en el formulario de edición.
        changelist = self.client.get("/admin/activities/registration/")
        self.assertEqual(changelist.status_code, 200)
        self.assertContains(changelist, "cancel")
        changeform = self.client.get(
            f"/admin/activities/registration/{reg.pk}/change/"
        )
        self.assertEqual(changeform.status_code, 200)
        self.assertContains(changeform, "cancel")


class SeedResetTests(TestCase):
    """T07 (etapa 5): seed con 2 altas directas idempotentes + reset reconstruye."""

    def seed(self):
        call_command("seed_demo", reference_time=NOW.isoformat(), stdout=StringIO())

    def extra_regs(self):
        User = get_user_model()
        bruno = User.objects.get(username="bruno")
        ana = User.objects.get(username="ana")
        return (
            Registration.objects.get(
                student=bruno, activity__seed_key="deshabilitada"
            ),
            Registration.objects.get(student=ana, activity__seed_key="iniciada"),
        )

    def test_seed_creates_two_confirmed(self):
        self.seed()
        disabled_reg, started_reg = self.extra_regs()
        self.assertIsNone(disabled_reg.cancelled_at)
        self.assertIsNone(started_reg.cancelled_at)

    def test_second_run_preserves_cancellation(self):
        self.seed()
        disabled_reg, _ = self.extra_regs()
        self.assertEqual(
            cancel(
                student=disabled_reg.student,
                activity_id=disabled_reg.activity_id,
                now=NOW,
            ),
            "cancelled",
        )
        cancelled_at = Registration.objects.get(pk=disabled_reg.pk).cancelled_at
        self.assertIsNotNone(cancelled_at)
        count = Registration.objects.count()
        self.seed()
        again = Registration.objects.get(pk=disabled_reg.pk)
        self.assertEqual(Registration.objects.count(), count)
        self.assertEqual(again.cancelled_at, cancelled_at)
        self.assertEqual(
            Registration.objects.filter(
                student=again.student, activity=again.activity
            ).count(),
            1,
        )

    def test_reset_rebuilds_confirmed(self):
        self.seed()
        disabled_reg, _ = self.extra_regs()
        self.assertEqual(
            cancel(
                student=disabled_reg.student,
                activity_id=disabled_reg.activity_id,
                now=NOW,
            ),
            "cancelled",
        )
        call_command(
            "reset_demo", confirm=True, reference_time=NOW.isoformat(), stdout=StringIO()
        )
        disabled_reg, started_reg = self.extra_regs()
        self.assertIsNone(disabled_reg.cancelled_at)
        self.assertIsNone(started_reg.cancelled_at)
        self.assertEqual(Registration.objects.count(), 6)
