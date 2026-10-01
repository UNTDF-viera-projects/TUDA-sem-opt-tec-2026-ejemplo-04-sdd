from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone as dt_timezone
from io import StringIO
from threading import Barrier
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connections, close_old_connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from activities.models import Activity, DemoSeed, Registration
from activities.services import register, with_availability

NOW = datetime(2030, 10, 1, 12, tzinfo=dt_timezone.utc)

def activity(**kwargs):
    values = dict(title="Práctica", description="Datos de prueba", starts_at=NOW+timedelta(hours=48), capacity=2)
    values.update(kwargs)
    return Activity.objects.create(**values)

class BaseTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("ana", password="test-pass")
        self.bruno = User.objects.create_user("bruno", password="test-pass")
        self.activity = activity()
    def enroll(self, user=None, **kwargs):
        return register(student=user or self.ana, activity_id=self.activity.pk, now=NOW, **kwargs)
    def test_success_and_availability(self):
        self.assertEqual(self.enroll(), "registered")
        self.assertEqual(with_availability().get(pk=self.activity.pk).available, 1)
    def test_duplicate_even_when_now_full_or_started(self):
        self.enroll()
        self.activity.capacity=1; self.activity.starts_at=NOW; self.activity.is_active=False; self.activity.save()
        self.assertEqual(self.enroll(), "already_registered")
        self.assertEqual(Registration.objects.count(), 1)
    def test_full(self):
        self.activity.capacity=1; self.activity.save(); self.enroll()
        self.assertEqual(self.enroll(self.bruno), "full")
        self.assertEqual(Registration.objects.count(), 1)
    def test_exact_start_rejected(self):
        self.activity.starts_at=NOW; self.activity.save()
        self.assertEqual(self.enroll(), "started")
        self.assertFalse(Registration.objects.exists())
    def test_past_rejected(self):
        self.activity.starts_at=NOW-timedelta(seconds=1); self.activity.save()
        self.assertEqual(self.enroll(), "started")
    def test_disabled(self):
        self.activity.is_active=False; self.activity.save()
        self.assertEqual(self.enroll(), "disabled")
        self.assertFalse(Registration.objects.exists())
    def test_unknown_activity(self):
        self.assertEqual(register(student=self.ana, activity_id=999999, now=NOW), "not_available")
    def test_capacity_validation(self):
        self.enroll(); self.enroll(self.bruno)
        self.activity.capacity=1
        with self.assertRaises(ValidationError): self.activity.full_clean()
    def test_positive_capacity_database_constraint(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError), transaction.atomic(): activity(capacity=0)
    def test_busy_is_recoverable_other_errors_propagate(self):
        from django.db import OperationalError
        with patch("activities.services.Activity.objects.filter", side_effect=OperationalError("database is locked")):
            self.assertEqual(self.enroll(), "busy")
        with patch("activities.services.Activity.objects.filter", side_effect=OperationalError("broken schema")):
            with self.assertRaises(OperationalError): self.enroll()
    def test_session_login_and_logout_post(self):
        self.assertRedirects(self.client.get("/activities/"), "/accounts/login/?next=/activities/")
        response=self.client.post("/accounts/login/?next=/activities/", {"username":"ana","password":"test-pass","next":"/activities/"})
        self.assertRedirects(response, "/activities/")
        self.assertEqual(self.client.get("/accounts/logout/").status_code, 405)
        self.assertRedirects(self.client.post("/accounts/logout/"), "/accounts/login/")
    def test_csrf_and_no_get_mutation(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.ana)
        url=f"/activities/{self.activity.pk}/register/"
        self.assertEqual(client.get(url).status_code, 405)
        self.assertEqual(client.post(url).status_code, 403)
        page=client.get(f"/activities/{self.activity.pk}/")
        self.assertEqual(page.status_code, 200)
        with patch("activities.views.register", side_effect=lambda **kwargs: register(now=NOW, **kwargs)):
            response=client.post(url, {"csrfmiddlewaretoken":client.cookies['csrftoken'].value,"student":self.bruno.pk})
        self.assertEqual(response.status_code,302)
        self.assertEqual(Registration.objects.get().student,self.ana)
    def test_catalog_filters_and_full_visible(self):
        self.client.force_login(self.ana)
        full=activity(title="Completa",capacity=1)
        Registration.objects.create(student=self.ana,activity=full)
        activity(title="Oculta",is_active=False); activity(title="Pasada",starts_at=NOW-timedelta(hours=2))
        session=self.client.session;session.set_expiry(NOW+timedelta(days=100));session.save()
        with patch("activities.views.timezone.now",return_value=NOW): response=self.client.get("/activities/")
        self.assertContains(response,"Completa");self.assertNotContains(response,"Oculta");self.assertNotContains(response,"Pasada")
    def test_mine_isolated_and_retains_past_disabled(self):
        self.enroll(); other=activity(title="Privada Bruno");Registration.objects.create(student=self.bruno,activity=other)
        self.activity.is_active=False;self.activity.starts_at=NOW-timedelta(hours=2);self.activity.save()
        self.client.force_login(self.ana); response=self.client.get("/my-registrations/")
        self.assertContains(response,"Práctica");self.assertNotContains(response,"Privada Bruno")
    def test_admin_rejects_capacity_and_read_only_registration(self):
        self.enroll();self.enroll(self.bruno)
        admin=get_user_model().objects.create_superuser("teacher","teacher@example.test","pass")
        self.client.force_login(admin)
        response=self.client.post(f"/admin/activities/activity/{self.activity.pk}/change/", {"title":"Práctica","description":"Datos","starts_at_0":"2030-10-03","starts_at_1":"09:00:00","capacity":1,"is_active":"on","_save":"Guardar"})
        self.assertEqual(response.status_code,200);self.assertContains(response,"No puede reducir")
        self.activity.refresh_from_db();self.assertEqual(self.activity.capacity,2)
        self.assertEqual(self.client.get("/admin/activities/registration/add/").status_code,403)
    def test_seed_idempotent_preserves_changes_and_anchor(self):
        call_command("seed_demo",reference_time=NOW.isoformat(),stdout=StringIO())
        seeded=Activity.objects.get(seed_key="taller");before=seeded.starts_at
        ana=get_user_model().objects.get(username="ana");old_password=ana.password
        seeded.title="Edición docente";seeded.save()
        count=Registration.objects.count()
        call_command("seed_demo",reference_time=(NOW+timedelta(days=3)).isoformat(),stdout=StringIO())
        seeded.refresh_from_db();ana.refresh_from_db()
        self.assertEqual(seeded.title,"Edición docente");self.assertEqual(seeded.starts_at,before)
        self.assertEqual(ana.password,old_password);self.assertEqual(Registration.objects.count(),count)
        self.assertEqual(DemoSeed.objects.get().reference_time,NOW)
    def test_seed_missing_data_does_not_overbook(self):
        call_command("seed_demo",reference_time=NOW.isoformat(),stdout=StringIO())
        seeded=Activity.objects.get(seed_key="taller")
        Registration.objects.filter(activity=seeded,student__username="bruno").delete()
        seeded.capacity=1;seeded.save(); warning=StringIO()
        call_command("seed_demo",stdout=StringIO(),stderr=warning)
        self.assertIn("full",warning.getvalue());self.assertEqual(seeded.registrations.count(),1)
    def test_reset_scoped_and_requires_confirmation(self):
        call_command("seed_demo",reference_time=NOW.isoformat(),stdout=StringIO())
        with self.assertRaises(CommandError):call_command("reset_demo",stdout=StringIO())
        call_command("reset_demo",confirm=True,reference_time=(NOW+timedelta(days=5)).isoformat(),stdout=StringIO())
        self.assertTrue(Activity.objects.filter(pk=self.activity.pk).exists())
        self.assertEqual(DemoSeed.objects.get().reference_time,NOW+timedelta(days=5))
    def test_seed_rejects_naive_reference(self):
        with self.assertRaises(CommandError):call_command("seed_demo",reference_time="2030-01-01T00:00:00",stdout=StringIO())

class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.ana=get_user_model().objects.create_user("a");self.bruno=get_user_model().objects.create_user("b")
        self.activity=activity(capacity=1)
    def test_default_clock_after_lock_rejects_activity_that_started(self):
        self.activity.starts_at=NOW+timedelta(seconds=1);self.activity.save()
        self.assertFalse(connections["default"].in_atomic_block)
        def after_lock():
            self.assertTrue(connections["default"].in_atomic_block)
            return NOW+timedelta(seconds=2)
        with patch("activities.services.timezone.now",side_effect=after_lock) as clock:
            self.assertEqual(register(student=self.ana,activity_id=self.activity.pk),"started")
            clock.assert_called_once()
        self.assertEqual(Registration.objects.count(),0)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available,1)

    def race(self, users):
        barrier=Barrier(2)
        def worker(user):
            close_old_connections()
            try:
                database=str(connections["default"].settings_dict["NAME"])
                assert database.endswith("test.sqlite3"), database
                assert "memory" not in database, database
                barrier.wait(timeout=10)
                return register(student=user,activity_id=self.activity.pk,now=NOW)
            finally:connections["default"].close()
        with ThreadPoolExecutor(max_workers=2) as executor: return list(executor.map(worker, users))
    def test_two_students_last_seat(self):
        self.assertCountEqual(self.race([self.ana,self.bruno]),["registered","full"])
        self.assertEqual(Registration.objects.count(),1)
        self.assertEqual(with_availability().get(pk=self.activity.pk).available,0)
    def test_simultaneous_duplicate(self):
        self.assertCountEqual(self.race([self.ana,self.ana]),["registered","already_registered"])
        self.assertEqual(Registration.objects.count(),1)
