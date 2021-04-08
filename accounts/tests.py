from django.test import TestCase
from django.db.utils import IntegrityError

from .models import User
from cis.models import Client


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='new', email='new@example.com')

    def test_is_approved_returns_true_when_user_has_client(self):
        client = Client.objects.create(name='New Client')
        self.user.client = client
        self.assertTrue(self.user.is_approved)

    def test_is_approved_returns_false_when_user_has_no_client(self):
        self.user.client = None
        self.assertFalse(self.user.is_approved)

    def test_user_as_string_returns_email(self):
        self.assertEqual(str(self.user), self.user.email)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            self.user.pk = None
            self.user.save()
        self.user.pk = 1
