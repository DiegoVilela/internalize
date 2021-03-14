from django.test import TestCase
from django.shortcuts import reverse

from cis.models import Client, Site, User


class SiteViewTest(TestCase):
    users = {}

    @classmethod
    def setUpTestData(cls):
        """Create Client A and Client B with their respective users"""

        for letter in ['a', 'b']:
            client = Client.objects.create(name=f'Client {letter.upper()}')
            client.site_set.create(client=client, name=f'Site Client {letter.upper()}')
            user = User.objects.create_user(f'user_{letter}', password='faith', client=client)
            cls.users.update({letter: user})

    def test_shows_correct_client_sites(self):
        for k, user in self.users.items():
            self.client.force_login(user)
            response = self.client.get(reverse('cis:manage_client_sites'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'cis/manage_client_sites.html')
            self.assertContains(response, f'Site Client {k.upper()}', count=1)
            letter = 'A'
            if k == 'a':
                letter = 'B'
            self.assertNotContains(response, f'Site Client {letter}')
            response.client.logout()

    def test_raises_exception_unapproved_user(self):
        client_a = self.users['a'].client
        self.users['a'].client = None
        self.users['a'].save()
        self.client.force_login(self.users['a'])
        response = self.client.get(reverse('cis:manage_client_sites'))
        self.assertEqual(response.status_code, 403)
        self.users['a'].client = client_a
        self.users['a'].save()

    def test_no_site_found(self):
        Site.objects.all().delete()
        self.client.force_login(self.users['a'])
        response = self.client.get(reverse('cis:manage_client_sites'))
        self.assertContains(response, 'No site found.', count=1)
        self.assertNotContains(response, 'Site Client A Description')
        self.assertNotContains(response, 'Site Client B Description')

    def test_create_site(self):
        self.client.force_login(self.users['a'])
        data = {'name': "Paulista Avenue"}
        response = self.client.post(reverse('cis:site_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cis/site_form.html')
        self.assertContains(response, "The site Paulista Avenue was created successfully.", count=1)
        self.assertContains(response, '<form method="post">', count=1)
