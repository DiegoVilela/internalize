"""
Functional tests.

Requires Selenium and geckodriver.
"""

from django.conf import settings
from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from accounts.models import User
from ..models import Client, CI
from ..urls import app_name

LOGIN = 'user1@example.com'
PASSWORD = '123456'
SESSION_COOKIE = settings.SESSION_COOKIE_NAME


class CommonTestMixin:
    """
    Add common fixtures and methods to TestCases.

    A user is logged in before each test.

    Place the mixin early in the MRO in order to isolate
    setUpClass()/tearDownClass().
    """

    fixtures = ['users.json']

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

    @staticmethod
    def _get_alert_success_text(driver: WebDriver) -> str:
        msg = WebDriverWait(driver, 2).until(
            lambda d: d.find_element(By.CSS_SELECTOR, '.alert-success')
        )
        return msg.text


@tag('functional')
class LoginTest(CommonTestMixin, StaticLiveServerTestCase):

    def setUp(self):
        pass

    def test_login_unapproved_user_shows_alert(self):
        user = User.objects.get(pk=1)
        user.client = None
        user.save()

        self._login_user(LOGIN)
        message = self.driver.find_element(By.CSS_SELECTOR, '.alert-warning')
        self.assertEqual(
            'Your account needs to be approved. Please contact you Account Manager.',
            message.text[2:]
        )
        self._logout()

    def test_login_approved_user_does_not_show_alert(self):
        self._login_user(LOGIN)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CSS_SELECTOR, '.alert-warning')
        home = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(home.text, 'Homepage')
        self._logout()

    def _login_user(self, email):
        self.driver.get(f'{self.live_server_url}/accounts/login/')
        username_input = self.driver.find_element(By.ID, 'id_login')
        username_input.send_keys(email)
        password_input = self.driver.find_element(By.ID, 'id_password')
        password_input.send_keys(PASSWORD)
        self.driver.find_element(By.XPATH, '//input[@type="submit"]').click()

    def _logout(self):
        self.driver.find_element(By.LINK_TEXT, 'Logout').click()
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()


@tag('functional')
class SiteTest(CommonTestMixin, StaticLiveServerTestCase):
    """Test all features related to the Place model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixtures.append('places.json')

    def test_create_place(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/place/create/')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, 'Place')

        new_place_name = 'Paulista'
        name = self.driver.find_element(By.ID, 'id_name')
        name.send_keys(new_place_name)
        description = self.driver.find_element(By.ID, 'id_description')
        description.send_keys('Place description' + Keys.ENTER)

        msg = self._get_alert_success_text(self.driver)
        self.assertTrue(f'The place {new_place_name} was created successfully.' in msg)

    def test_viewing_place(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/place/1')
        new_place = self.driver.find_element(By.ID, 'id_name')
        self.assertEqual(new_place.get_attribute('value'), 'Place 1')

    def test_listing_places(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/places/')
        for i in range(3):
            place = self.driver.find_element(By.ID, f'id_place_set-{i}-name')
            self.assertEqual(place.get_attribute('value'), f'Place {i+1}')

    def test_deleting_place(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/places/')
        self.driver.find_element(By.ID, 'id_place_set-0-DELETE').click()
        self.driver.find_element(By.XPATH, '//input[@value="Save"]').click()
        msg = self._get_alert_success_text(self.driver)
        self.assertTrue('The places were updated successfully.' in msg)


@tag('functional')
class ApplianceTest(CommonTestMixin, StaticLiveServerTestCase):
    """Test all features related to the Appliance model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixtures.append('appliances.json')

    def test_create_appliance(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/appliance/create/')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, 'Appliance')

        the_serial_number = 'DEF456'
        serial = self.driver.find_element(By.ID, 'id_serial_number')
        serial.send_keys(the_serial_number)

        manufacturer = self.driver.find_element(By.ID, 'id_manufacturer')
        manufacturer_select = Select(manufacturer)
        manufacturer_select.select_by_index(1)

        model = self.driver.find_element(By.ID, 'id_model')
        model.send_keys('C9000')

        serial = self.driver.find_element(By.ID, 'id_serial_number')
        self.assertEqual(serial.get_attribute('value'), the_serial_number)

    def test_viewing_appliance(self):
        _id = 3
        self.driver.get(f'{self.live_server_url}/{app_name}/appliance/{_id}')
        serial = self.driver.find_element(By.ID, 'id_serial_number')
        self.assertEqual(serial.get_attribute('value'), f'ABC12{_id}')

    def test_listing_appliances(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/appliances/')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, 'Appliances')

        serials = self.driver.find_elements(By.CSS_SELECTOR, 'td>a')
        for i, serial in enumerate(serials):
            self.assertEqual(serial.text, f'ABC12{i + 1}')

    def test_view_appliance_from_listing(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/appliances/')
        serial_origin = self.driver.find_element(By.CSS_SELECTOR, 'td>a')
        serial = serial_origin.text
        serial_origin.click()
        serial_target = self.driver.find_element(By.ID, 'id_serial_number')
        self.assertEqual(serial, serial_target.get_attribute('value'))


@tag('functional')
class CITest(CommonTestMixin, StaticLiveServerTestCase):
    """Test all features related to the CI model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixtures.extend(['places.json', 'appliances.json', 'cis.json'])

    def test_create_ci(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/ci/create/')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, 'Configuration Item')

        self.driver.find_element(By.ID, 'id_hostname').send_keys('NEW_HOST')
        place_select = Select(self.driver.find_element(By.ID, 'id_place'))
        place_select.select_by_value('1')
        self.driver.find_element(By.ID, 'id_ip').send_keys('10.10.20.20')
        contract_select = Select(self.driver.find_element(By.ID, 'id_contract'))
        contract_select.select_by_index(1)
        self.driver.find_element(By.ID, 'id_description').send_keys('Some text.')
        appliances_select = Select(self.driver.find_element(By.ID, 'id_appliances'))
        appliances_select.select_by_value('1')
        appliances_select.select_by_value('2')
        self.driver.find_element(By.ID, 'id_username').send_keys('admin')
        self.driver.find_element(By.ID, 'id_password').send_keys('123')
        self.driver.find_element(By.ID, 'id_enable_password').send_keys('enable123' + Keys.RETURN)

        msg = self._get_alert_success_text(self.driver)
        self.assertTrue('success' in msg)

    def test_viewing_ci(self):
        ci = CI.objects.get(pk=3)
        self.driver.get(f'{self.live_server_url}/{app_name}/ci/3')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, str(ci))

    def test_listing_cis(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/cis/0/')
        h1 = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(h1.text, 'Configuration Items Created')

        cis = self.driver.find_elements(By.CSS_SELECTOR, 'td>a')
        for hostname in cis:
            hostnames = ('SW-CORE', 'SW-FL1', 'SW-FL2')
            self.assertTrue(hostname.text in hostnames)

    def test_view_ci_from_listing(self):
        self.driver.get(f'{self.live_server_url}/{app_name}/cis/0/')
        ci_origin = self.driver.find_element(By.CSS_SELECTOR, 'td>a')
        ci_hostname_origin = ci_origin.text
        ci_origin.click()
        ci_hostname_target = self.driver.find_element(By.ID, 'hostname')
        self.assertEqual(ci_hostname_target.text, ci_hostname_origin)
