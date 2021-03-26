from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from ..models import User, Client

PASSWORD = 'DUfTWSSxtQ'


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
