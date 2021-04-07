from django.shortcuts import reverse
from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import User, Client, Place, Manufacturer, Contract, Appliance, CI


CLIENT_NAME = 'The Client'
SITE_NAME = 'Main'
MANUFACTURER = 'Cisco'
CONTRACT_NAME = 'BR-001'


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

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(username=self.username)

    def test_object_is_of_user_type(self):
        self.assertIsInstance(self.user, User)


class ClientTest(TestCase):
    fixtures = ['data_models.json']

    def test_client_as_string_returns_name(self):
        client = Client.objects.get(pk=1)
        self.assertEqual(str(client), CLIENT_NAME)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Client.objects.create(name=CLIENT_NAME)


class SiteTest(TestCase):
    fixtures = ['data_models.json']

    def test_as_string_returns_client_plus_site_name(self):
        site = Place.objects.get(pk=1)
        self.assertEqual(str(site), f'{CLIENT_NAME} | {SITE_NAME}')

    def test_duplicate_name_by_client_raises_exception(self):
        client = Client.objects.get(pk=1)
        with self.assertRaises(IntegrityError):
            Place.objects.create(name=SITE_NAME, client=client)

    def test_duplicate_name_different_client_is_ok(self):
        client = Client.objects.create(name='Different Client')
        self.assertIsNotNone(Place.objects.create(name=SITE_NAME, client=client))

    def test_absolute_url_returns_correct_url(self):
        site = Place.objects.get(pk=1)
        self.assertEqual(
            site.get_absolute_url(),
            reverse('cis:site_update', args=[site.pk])
        )


class ManufacturerTest(TestCase):
    fixtures = ['data_models.json']

    def test_as_string_returns_name(self):
        manufacturer = Manufacturer.objects.get(pk=1)
        self.assertEqual(str(manufacturer), MANUFACTURER)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Manufacturer.objects.create(name=MANUFACTURER)


class ContractTest(TestCase):
    fixtures = ['data_models.json']

    def test_as_string_returns_name(self):
        contract = Contract.objects.get(pk=1)
        self.assertEqual(str(contract), CONTRACT_NAME)


class ApplianceTest(TestCase):
    fixtures = ['data_models.json']

    def test_as_string_returns_full_name(self):
        appliance = Appliance.objects.get(pk=1)
        self.assertEqual(
            str(appliance),
            f'{MANUFACTURER} | {appliance.model} | {appliance.serial_number}'
        )

    def test_duplicate_serial_number_raises_exception(self):
        appliance = Appliance.objects.get(pk=1)
        appliance.pk = None
        with self.assertRaises(IntegrityError):
            appliance.save()

    def test_absolute_url_returns_correct_url(self):
        appliance = Appliance.objects.get(pk=1)
        self.assertEqual(
            appliance.get_absolute_url(),
            reverse('cis:appliance_update', args=[appliance.pk])
        )


class CITest(TestCase):
    fixtures = ['data_models.json']

    def test_as_string_returns_full_name(self):
        ci = CI.objects.get(pk=1)
        self.assertEqual(
            str(ci),
            f'{CLIENT_NAME} | {SITE_NAME} | {ci.hostname} | {ci.ip}'
        )

    def test_unique_constraint_raises_exception(self):
        ci = CI.objects.get(pk=1)
        ci.pk = None
        ci.credential_id = None
        with self.assertRaises(IntegrityError):
            ci.save()

    def test_duplicate_hostname_with_different_client_is_ok(self):
        new_client = Client.objects.create(name='Different Client')
        ci = CI.objects.get(pk=1)
        ci.pk = None
        ci.credential_id = None
        ci.client = new_client
        ci.save()
        self.assertIsNotNone(ci.pk)

    def test_absolute_url_returns_correct_url(self):
        ci = CI.objects.get(pk=1)
        self.assertEqual(
            ci.get_absolute_url(),
            reverse('cis:ci_detail', args=[ci.pk])
        )
