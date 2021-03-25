from datetime import timedelta
from collections import namedtuple
from dataclasses import dataclass
from django.utils import timezone
from django.test import TestCase
from django.shortcuts import reverse

from cis.models import Client, Site, User, Appliance, Manufacturer, CI, Contract


@dataclass
class ListInfo:
    """
    Wraps the details of each test.

    Applied to Site, Appliance, and CI.
    """

    message: str
    context_object_name: str
    template_name: str
    lookup_text: str
    letter: str = 'A'

    @property
    def contains(self):
        return f'{self.lookup_text}{self.letter}'

    @property
    def not_contains(self):
        return f"{self.lookup_text}{'B' if self.letter == 'A' else 'A'}"


class SiteApplianceAndCIViewTest(TestCase):
    """
    Test CI, Site and Appliance views.
    """
    users = {}
    sites = {}
    appliances = {}

    @classmethod
    def setUpTestData(cls):
        """
        Set up the database to be used in all testes in this class.

        Client A and Client B will have their respective User, CI, and Site.
        cls.users = {'a': user_A, 'b': user_B}
        """

        manufacturer = Manufacturer.objects.create(name='Cisco')
        contract = create_contract()
        for letter in {'A', 'B'}:
            client = Client.objects.create(name=f'Client {letter}')
            site = Site.objects.create(client=client, name=f'Site Client {letter}')
            appliance = create_appliance(client, manufacturer, letter)
            create_ci(client, site, letter, contract)
            user = User.objects.create_user(f'user_{letter}', password='faith', client=client)
            cls.users.update({letter: user})
            cls.sites.update({letter: site})
            cls.appliances.update({letter: appliance})
            cls.manufacturer = manufacturer
            cls.contract = contract

        # Maps the details of the tests applied to
        # Site, Appliance, and, CI list views, respectively.
        cls.list_details = {
            reverse('cis:manage_client_sites'): ListInfo(
                'No site was found.',
                'formset',
                'cis/manage_client_sites.html',
                'Site Client ',
            ),
            reverse('cis:appliance_list'): ListInfo(
                'No appliance was found.',
                'appliance_list',
                'cis/appliance_list.html',
                'SERIAL_CLIENT_',
            ),
            reverse('cis:ci_list', args=(0,)): ListInfo(
                'No configuration item was found.',
                'ci_list',
                'cis/ci_list.html',
                'HOST_',
            ),
        }

    def test_show_correct_items_by_client(self):

        # for client 'A' and client 'B'
        for k, user in self.users.items():
            self.client.force_login(user)

            # test Site, Appliance, and CI
            for url, test in self.list_details.items():
                test.letter = k
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, test.template_name)
                self.assertEqual(len(response.context[test.context_object_name]), 1)
                self.assertContains(response, test.contains, count=1)
                self.assertNotContains(response, test.not_contains)

            self.client.logout()

    def test_raise_exception_on_unapproved_user(self):
        user = self.users['A']
        user.client = None
        user.save()
        self.client.force_login(user)

        # test Site, Appliance, and CI
        for url in self.list_details.keys():
            response = self.client.get(url)
            self.assertIsNone(response.context)
            self.assertEqual(response.status_code, 403)

    def test_not_found(self):
        client = Client.objects.create(name=f'Client C')
        user = User.objects.create_user(f'user_c', password='faith', client=client)
        self.client.force_login(user)

        # test Site, Appliance, and CI
        for url, test in self.list_details.items():
            response = self.client.get(url)
            self.assertContains(response, test.message, count=1)
            self.assertEqual(len(response.context[test.context_object_name]), 0)
            self.assertNotContains(response, test.not_contains)

    def test_create(self):
        self.client.force_login(self.users['A'])

        # map urls to info that needs to be checked
        CreateInfo = namedtuple('CreateInfo', ['data', 'template_name', 'contains'])
        details = {
            'cis:site_create': CreateInfo(
                {'name': "New Site"},
                'cis/site_form.html',
                ['The site New Site was created successfully.'],
            ),
            'cis:appliance_create': CreateInfo(
                {
                    'serial_number': 'NEW_SERIAL',
                    'manufacture': self.manufacturer,
                    'model': 'ABC123',
                    'virtual': True,
                },
                'cis/appliance_form.html',
                ['NEW_SERIAL', 'Cisco', 'ABC123'],
            ),
            'cis:ci_create': CreateInfo(
                {
                    'site': self.sites['A'].id,
                    'appliances': (self.appliances['A'].id,),
                    'hostname': 'NEW_HOST',
                    'ip': '10.10.10.254',
                    'description': 'New Configuration Item',
                    'deployed': True,
                    'business_impact': 'high',
                    'contract': self.contract,
                },
                'cis/ci_form.html',
                ['NEW_HOST', self.appliances['A'].serial_number],
            )
        }
        # test Site, Appliance, and CI
        for url, info in details.items():
            response = self.client.post(reverse(url), info.data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, info.template_name)
            for text in info.contains:
                self.assertContains(response, text, count=1)


def create_appliance(client, manufacturer, letter):
    return Appliance.objects.create(
        client=client,
        serial_number=f'SERIAL_CLIENT_{letter}',
        manufacturer=manufacturer,
        model='ABC123',
        virtual=True,
    )


def create_contract():
    return Contract.objects.create(
        name='CONTRACT',
        begin=timezone.now(),
        end=timezone.now() + timedelta(days=356),
        description='Contract Description',
    )


def create_ci(client, site, letter, contract):
    CI.objects.create(
        client=client,
        site=site,
        hostname=f'HOST_{letter}',
        ip='10.10.20.20',
        description=f'Configuration Item {letter}',
        deployed=True,
        contract=contract,
    )
