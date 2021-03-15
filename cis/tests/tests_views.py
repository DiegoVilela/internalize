from django.test import TestCase
from django.shortcuts import reverse

from cis.models import Client, Site, User, Appliance, Manufacturer


class SiteAndApplianceViewTest(TestCase):
    """
    Test both Site and Appliance views.
    """
    users = {}

    @classmethod
    def setUpTestData(cls):
        """
        Set up the database to be used in all testes in this class.

        Client A (plus user_a, Site Client A, and Appliance SERIAL_CLIENT_A)
        Client B (plus user_b, Site Client B, and Appliance SERIAL_CLIENT_B)
        cls.users = {'a': user_a, 'b': user_b}
        """

        manufacturer = Manufacturer.objects.create(name='Cisco')
        for letter in ['a', 'b']:
            client = Client.objects.create(name=f'Client {letter.upper()}')
            client.site_set.create(client=client, name=f'Site Client {letter.upper()}')
            Appliance.objects.create(
                client=client,
                serial_number=f'SERIAL_CLIENT_{letter.upper()}',
                manufacturer=manufacturer,
                model='ABC123',
                virtual=True,
            )
            user = User.objects.create_user(f'user_{letter}', password='faith', client=client)
            cls.users.update({letter: user})
            cls.manufacturer = manufacturer

    def test_show_correct_items_by_client(self):

        def other_client(current_client):
            """Return the other client based on the current one"""
            client = 'A'
            if current_client == 'a':
                client = 'B'
            return client

        # for client 'a' and client 'b'
        for k, user in self.users.items():

            # login the current user
            self.client.force_login(user)

            # test Site
            response = self.client.get(reverse('cis:manage_client_sites'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'cis/manage_client_sites.html')
            self.assertEqual(len(response.context['formset']), 1)
            self.assertContains(response, f'Site Client {k.upper()}', count=1)
            self.assertNotContains(response, f'Site Client {other_client(k)}')

            # test Appliance
            response = self.client.get(reverse('cis:appliance_list'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'cis/appliance_list.html')
            self.assertEqual(len(response.context['appliance_list']), 1)
            self.assertContains(response, f'SERIAL_CLIENT_{k.upper()}', count=1)
            self.assertNotContains(response, f'SERIAL_CLIENT_{other_client(k)}')

            # logout the current user
            response.client.logout()

    def test_raise_exception_on_unapproved_user(self):
        user = self.users['a']
        user.client = None
        user.save()
        self.client.force_login(user)

        # test Site
        response = self.client.get(reverse('cis:manage_client_sites'))
        self.assertIsNone(response.context)
        self.assertEqual(response.status_code, 403)

        # test Appliance
        response = self.client.get(reverse('cis:appliance_list'))
        self.assertIsNone(response.context)
        self.assertEqual(response.status_code, 403)

        user.client = self.users['a'].client
        user.save()

    def test_no_found(self):
        client = Client.objects.create(name=f'Client C')
        user = User.objects.create_user(f'user_c', password='faith', client=client)
        self.client.force_login(user)

        # test Site
        response = self.client.get(reverse('cis:manage_client_sites'))
        self.assertContains(response, 'No site was found.', count=1)
        self.assertEqual(len(response.context['formset']), 0)
        self.assertNotContains(response, 'Site Client A')
        self.assertNotContains(response, 'Site Client B')

        # test Appliance
        response = self.client.get(reverse('cis:appliance_list'))
        self.assertContains(response, 'No appliance was found.')
        self.assertEqual(len(response.context['appliance_list']), 0)
        self.assertNotContains(response, 'SERIAL_CLIENT_A')
        self.assertNotContains(response, 'SERIAL_CLIENT_B')

    def test_create(self):
        self.client.force_login(self.users['a'])

        # test Site
        data = {'name': "Paulista Avenue"}
        response = self.client.post(reverse('cis:site_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cis/site_form.html')
        self.assertContains(response, "The site Paulista Avenue was created successfully.", count=1)

        # test Appliance
        data = {
            'serial_number': 'SERIAL_1',
            'manufacture': self.manufacturer,
            'model': 'ABC123',
            'virtual': True,
        }
        response = self.client.post(reverse('cis:appliance_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cis/appliance_form.html')
        self.assertContains(response, 'SERIAL_1', count=1)
