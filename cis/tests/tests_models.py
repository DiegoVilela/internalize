from django.shortcuts import reverse
from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import User, Client, Site, Manufacturer, Contract, Appliance, CI


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
    @classmethod
    def setUpTestData(cls):
        cls.name = 'New Client'
        cls.company_client = Client.objects.create(name=cls.name)

    def test_client_as_string_returns_name(self):
        self.assertEqual(str(self.company_client), self.name)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Client.objects.create(name=self.name)

    def test_object_is_of_client_type(self):
        self.assertIsInstance(self.company_client, Client)


class SiteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = 'New Site'
        cls.company_client = Client.objects.create(name=cls.name)
        cls.site = Site.objects.create(name=cls.name, client=cls.company_client)

    def test_as_string_returns_client_plus_site_name(self):
        self.assertEqual(
            str(self.site), f'{self.company_client.name} | {self.name}'
        )

    def test_duplicate_name_by_client_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Site.objects.create(name=self.name, client=self.company_client)

    def test_duplicate_name_different_client_is_ok(self):
        client = Client.objects.create(name='Different Client')
        self.assertIsNotNone(Site.objects.create(name=self.name, client=client))

    def test_object_is_of_site_type(self):
        self.assertIsInstance(self.site, Site)

    def test_absolute_url_returns_correct_url(self):
        self.assertEqual(
            self.site.get_absolute_url(),
            reverse('cis:site_update', args=[self.site.pk])
        )


class ManufacturerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = 'New Manufacturer'
        cls.manufacturer = Manufacturer.objects.create(name=cls.name)

    def test_as_string_returns_name(self):
        self.assertEqual(str(self.manufacturer), self.name)

    def test_duplicate_name_raises_exception(self):
        with self.assertRaises(IntegrityError):
            Manufacturer.objects.create(name=self.name)

    def test_object_is_of_manufacturer_type(self):
        self.assertIsInstance(self.manufacturer, Manufacturer)


class ContractTest(TestCase):
    def test_as_string_returns_name(self):
        name = 'CT-001'
        contract = Contract.objects.create(
            name=name,
            begin='2021-01-01',
            end='2022-01-01',
            description='Contract description',
        )
        self.assertEqual(str(contract), name)


class ApplianceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.serial_number = 'NEW123'
        cls.model = 'ABC'
        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer')
        cls.company_client = Client.objects.create(name='Client')
        cls.appliance = _create_appliance(
            cls.company_client, cls.serial_number, cls.manufacturer, cls.model
        )

    def test_as_string_returns_full_name(self):
        self.assertEqual(
            str(self.appliance),
            f'{self.manufacturer.name} | {self.model} | {self.serial_number}'
        )

    def test_duplicate_serial_raises_exception(self):
        with self.assertRaises(IntegrityError):
            _create_appliance(
                self.company_client,
                self.serial_number,
                self.manufacturer,
                self.model
            )

    def test_object_is_of_appliance_type(self):
        self.assertIsInstance(self.appliance, Appliance)

    def test_absolute_url_returns_correct_url(self):
        self.assertEqual(
            self.appliance.get_absolute_url(),
            reverse('cis:appliance_update', args=[self.appliance.pk])
        )


class CITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company_client = Client.objects.create(name='New Client')
        cls.ci = _create_ci(cls.company_client)

    def test_as_string_returns_full_name(self):
        self.assertEqual(
            str(self.ci),
            f'{self.ci.client.name} | {self.ci.site.name} | {self.ci.hostname} | {self.ci.ip}'
        )

    def test_duplicate_hostname_by_client_raises_exception(self):
        with self.assertRaises(IntegrityError):
            _create_ci(self.company_client)

    def test_duplicate_hostname_different_client_is_ok(self):
        client = Client.objects.create(name='Different Client')
        self.assertIsNotNone(_create_ci(client))

    def test_object_is_of_site_type(self):
        self.assertIsInstance(self.ci, CI)

    def test_absolute_url_returns_correct_url(self):
        self.assertEqual(
            self.ci.get_absolute_url(),
            reverse('cis:ci_detail', args=[self.ci.pk])
        )

    def test_appliances_many_to_many(self):
        manufacturer = Manufacturer.objects.create(name='Cisco')
        appliances = set()
        for i in range(1, 3):
            appliances.add(Appliance.objects.create(
                client=self.company_client,
                serial_number=f'SERIAL_{i}',
                manufacturer=manufacturer,
                model='ABC123'
            ))
        self.ci.appliances.set(appliances)
        self.assertEqual(len(self.ci.appliances.all()), 2)


def _create_appliance(client, serial, manufacturer, model):
    return Appliance.objects.create(
        client=client,
        serial_number=serial,
        manufacturer=manufacturer,
        model=model,
    )


def _create_ci(client: Client) -> CI:
    site = Site.objects.create(name='New Site', client=client)
    contract = Contract.objects.create(
        name='CT-001',
        begin='2021-01-01',
        end='2022-01-01',
        description='Contract description.',
    )
    return CI.objects.create(
        client=client,
        site=site,
        hostname='NEW_HOST',
        ip='10.10.20.20',
        description='The description.',
        contract=contract,
    )
