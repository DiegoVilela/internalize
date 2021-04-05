from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from ..models import User, Client, Site
from ..urls import app_name

USERNAME = 'user1'
PASSWORD = '123'
SESSION_COOKIE = settings.SESSION_COOKIE_NAME


class LoginTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login_unapproved_user_shows_alert(self):
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password=PASSWORD,
        )
        self._login_user('user1')
        message = self.driver.find_element(By.CSS_SELECTOR, '.alert-warning')
        self.assertEqual(
            'Your account needs to be approved. Please contact you Account Manager.',
            message.text[2:]
        )
        self._logout()

    def test_login_approved_user_does_not_show_alert(self):
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password=PASSWORD,
            client=Client.objects.create(name='The Client'),
        )
        self._login_user('user2')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CSS_SELECTOR, '.alert-warning')
        home = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(home.text, 'Homepage')
        self._logout()

    def _login_user(self, username):
        self.driver.get(f'{self.live_server_url}/accounts/login/')
        username_input = self.driver.find_element(By.ID, 'id_username')
        username_input.send_keys(username)
        password_input = self.driver.find_element(By.ID, 'id_password')
        password_input.send_keys(PASSWORD)
        self.driver.find_element(By.XPATH, '//input[@value="Login"]').click()

    def _logout(self):
        self.driver.find_element(By.LINK_TEXT, 'Logout').click()


class SiteTest(StaticLiveServerTestCase):
    fixtures = ['data_functional.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()

    def setUp(self):
        # Login via Django
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        cookie = self.client.cookies[SESSION_COOKIE]

        # Selenium will use the current domain to set the cookie
        self.driver.get(f'{self.live_server_url}/any-404')
        self.driver.add_cookie({
            'name': SESSION_COOKIE,
            'value': cookie.value,
            'secure': False,
        })

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_create_site(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/site/create/')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, 'Site')

        new_site_name = 'Paulista'
        name = self.driver.find_element(By.ID, 'id_name')
        name.send_keys(new_site_name)
        description = self.driver.find_element(By.ID, 'id_description')
        description.send_keys('Site description' + Keys.ENTER)

        msg = self._get_alert_success_text(self.driver)
        self.assertTrue(f'The site {new_site_name} was created successfully.' in msg)

    def test_viewing_site(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/site/1')
        new_site = self.driver.find_element(By.ID, 'id_name')
        self.assertEqual(new_site.get_attribute('value'), 'Site 1')

    def test_listing_sites(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/sites/')
        for i in range(3):
            site = self.driver.find_element(By.ID, f'id_site_set-{i}-name')
            self.assertEqual(site.get_attribute('value'), f'Site {i+1}')

    def test_deleting_site(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/sites/')
        self.driver.find_element(By.ID, 'id_site_set-0-DELETE').click()
        self.driver.find_element(By.XPATH, '//input[@value="Save"]').click()
        msg = self._get_alert_success_text(self.driver)
        self.assertTrue('The sites were updated successfully.' in msg)

    @staticmethod
    def _get_alert_success_text(driver: WebDriver) -> str:
        msg = WebDriverWait(driver, 2).until(
            lambda d: d.find_element(By.CSS_SELECTOR, '.alert-success')
        )
        return msg.text
