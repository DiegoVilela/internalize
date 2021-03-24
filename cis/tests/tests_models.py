from django.test import TestCase
from ..models import User, Client


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'new_user'
        cls.user = User.objects.create_user(username=cls.username)

    def test_is_approved_returns_true_when_user_has_client(self):
        client = Client.objects.create(name='New Client')
        self.user.client = client
        self.assertTrue(self.user.is_approved)

    def test_is_approved_returns_false_when_user_has_no_client(self):
        self.user.client = None
        self.assertFalse(self.user.is_approved)

    def test_user_as_string_returns_username(self):
        self.assertEqual(str(self.user), self.username)
