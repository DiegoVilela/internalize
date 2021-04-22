from django.shortcuts import reverse
from django.test import TestCase
from django.db.utils import IntegrityError

from accounts.models import User
from ..models import Client, Place, Manufacturer, Contract, Appliance, CI, CIPack

CLIENT_NAME = 'The Client'
PLACE_NAME = 'Main'
MANUFACTURER = 'Cisco'
CONTRACT_NAME = 'BR-001'


class FixtureMixin:
    """Add the same fixture to all TestCase"""

    fixtures = ['all.json']


class ClientTest(FixtureMixin, TestCase):

    def test_client_as_string_returns_name(self):
        client = Client.objects.get(pk=1)
        self.assertEqual(str(client), CLIENT_NAME)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Client.objects.create(name=CLIENT_NAME)


class PlaceTest(FixtureMixin, TestCase):

    def test_as_string_returns_client_plus_place_name(self):
        place = Place.objects.get(pk=1)
        self.assertEqual(str(place), f'{CLIENT_NAME} | {PLACE_NAME}')

    def test_duplicate_name_by_client_raises_exception(self):
        client = Client.objects.get(pk=1)
        with self.assertRaises(IntegrityError):
            Place.objects.create(name=PLACE_NAME, client=client)

    def test_duplicate_name_different_client_is_ok(self):
        client = Client.objects.create(name='Different Client')
        self.assertIsNotNone(Place.objects.create(name=PLACE_NAME, client=client))

    def test_absolute_url_returns_correct_url(self):
        place = Place.objects.get(pk=1)
        self.assertEqual(
            place.get_absolute_url(),
            reverse('cis:place_update', args=[place.pk])
        )


class ManufacturerTest(FixtureMixin, TestCase):

    def test_as_string_returns_name(self):
        manufacturer = Manufacturer.objects.get(pk=1)
        self.assertEqual(str(manufacturer), MANUFACTURER)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Manufacturer.objects.create(name=MANUFACTURER)


class ContractTest(FixtureMixin, TestCase):

    def test_as_string_returns_name(self):
        contract = Contract.objects.get(pk=1)
        self.assertEqual(str(contract), CONTRACT_NAME)


class ApplianceTest(FixtureMixin, TestCase):

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


class CITest(FixtureMixin, TestCase):

    def test_as_string_returns_full_name(self):
        ci = CI.objects.get(pk=1)
        self.assertEqual(
            str(ci),
            f'{CLIENT_NAME} | {PLACE_NAME} | {ci.hostname} | {ci.ip}'
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


class CIPackTest(FixtureMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.get(pk=2)
        cls.user = User.objects.get(pk=1)
        cls.pack = CIPack.objects.get(pk=1)
        cls.cis = CI.objects.all()

    def test_as_string_returns_responsible_plus_local_data(self):
        self.assertEqual(
            str(self.pack),
            f"{self.user} 2021-04-20 09:25:38"  # UTC-3
        )

    def test_percentage_of_cis_approved(self):
        # Approve 0 of 3 CIs
        self.assertEqual(self.pack.percentage_of_cis_approved, 0)

        # Approve 1 of 3 CIs
        self.pack.ci_set.filter(pk__in=(1,)).update(status=2)
        self.assertEqual(self.pack.percentage_of_cis_approved, 33)

        # Approve 2 of 3 CIs
        self.pack.ci_set.filter(pk__in=(1, 2)).update(status=2)
        self.assertEqual(self.pack.percentage_of_cis_approved, 67)

        # Approve 3 of 3 CIs
        self.pack.ci_set.filter(pk__in=(1, 2, 3)).update(status=2)
        self.assertEqual(self.pack.percentage_of_cis_approved, 100)

    def test_approved_by_returns_the_right_superuser(self):
        self.pack.approved_by = self.admin
        self.pack.save()
        self.assertEqual(self.pack.approved_by, self.admin)

    def test_send_cis_to_production(self):
        ci_pks = (ci.pk for ci in self.cis)
        self.pack.send_to_production(ci_pks)

        for ci in self.pack.ci_set.all():
            self.assertEqual(ci.status, 1)

    def test_len_returns_count_of_ci_set(self):
        self.assertEqual(len(self.pack), 3)
