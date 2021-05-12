from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase
from shared.models import Addresses, People, Test
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
import os

# Create your tests here.

class SuperLiveServerTestCase(LiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver(executable_path=os.getcwd()+"/testingCentre/tests/chromedriver")
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def create_user_and_login(self):
        username = "terry"
        password = "yrret"
        User.objects.create_user(username=username, password=password)
        self.selenium.get(self.live_server_url+reverse('testingCentre:login'))
        self.selenium.find_element_by_name("username").send_keys(username)
        self.selenium.find_element_by_name("password").send_keys(password)
        self.selenium.find_element_by_name("submit").send_keys(Keys.RETURN)

class ChooseInputMethodViewTests(SuperLiveServerTestCase):

    def test_choose_single_test(self):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse('testingCentre:chooseInputMethod'))
        self.selenium.find_element_by_name("single_test_button").send_keys(Keys.RETURN)
        assert(self.selenium.current_url.startswith(self.live_server_url+reverse('testingCentre:singleTest')+"?single_test_button="))

    def test_choose_multiple_tests(self):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse('testingCentre:chooseInputMethod'))
        self.selenium.find_element_by_name("multiple_tests_button").send_keys(Keys.RETURN)
        assert(self.selenium.current_url.startswith(self.live_server_url+reverse('testingCentre:multipleTests')+"?multiple_tests_button="))

class InputSingleTestViewTests(SuperLiveServerTestCase):

    def test_input_correct_information(self):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse('testingCentre:singleTest'))
        self.selenium.find_element_by_name("name").send_keys('Tianwei Cheng')
        self.selenium.find_element_by_name("phone_num").send_keys('8614706189156')
        self.selenium.find_element_by_name("email").send_keys('terrycheng2001@gmail.com')
        self.selenium.find_element_by_name("addr").send_keys('1 Linghu Avenue, Wuxi')
        self.selenium.find_element_by_name("postcode").send_keys('214000')
        self.selenium.find_element_by_name("submit").send_keys(Keys.RETURN)
        assert(self.selenium.current_url == self.live_server_url+reverse('testingCentre:thanks'))

        assert(Addresses.objects.count() == 1)
        address = Addresses.objects.first()
        assert(address.addr=="1 Linghu Avenue, Wuxi" and address.postcode=="214000" and address.people_set.count()==1)
        person = address.people_set.first()
        assert(person.name=="Tianwei Cheng" and person.phone_num=="8614706189156" and person.email=="terrycheng2001@gmail.com" and person.date_of_birth==datetime.date(year=2021, month=1, day=1) and person.test_set.count()==1)
        test = person.test_set.first()
        assert(test.test_date.date()==datetime.date(year=2021, month=1, day=1) and test.result==False)

class InputMultipleTestsViewTests(SuperLiveServerTestCase):

    def test_input_correct_file(self):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse('testingCentre:multipleTests'))
        self.selenium.find_element_by_name("tests_file").send_keys(os.getcwd()+"/testingCentre/tests/tests.json")
        self.selenium.find_element_by_name("submit").send_keys(Keys.RETURN)
        assert(self.selenium.current_url == self.live_server_url+reverse('testingCentre:multipleTestsThanks'))

        addresses = Addresses.objects.all()
        assert(addresses.count() == 2)

        address1 = addresses[0]
        assert(address1.addr=="Hefei" and address1.postcode=="214000" and address1.people_set.count()==1)
        person1 = address1.people_set.first()
        assert(person1.name=="James Zhang" and person1.phone_num=="12345678" and person1.email=="yinjie@qq.com" and person1.date_of_birth==datetime.date(year=2001, month=1, day=30) and person1.test_set.count()==2)
        assert(person1.test_set.first().test_date.date()==datetime.date(year=2020, month=3, day=18) and person1.test_set.first().result==False)
        assert(person1.test_set.last().test_date.date()==datetime.date(year=2020, month=4, day=21) and person1.test_set.last().result==False)

        address2 = addresses[1]
        assert(address2.addr=="Allianz Arena" and address2.postcode=="80000" and address2.people_set.count()==2)
        person2 = address2.people_set.first()
        assert(person2.name=="Serge Gnabry" and person2.phone_num=="4912345654321" and person2.email=="serge.gnabry@fcbayern.com" and person2.date_of_birth==datetime.date(year=1995, month=7, day=14) and person2.test_set.count()==1)
        assert(person2.test_set.first().test_date.date()==datetime.date(year=2021, month=4, day=6) and person2.test_set.first().result==True)
        person3 = address2.people_set.last()
        assert(person3.name=="Thomas Muller" and person3.phone_num=="4925252525250" and person3.email=="thomas.muller@fcbayern.com" and person3.date_of_birth==datetime.date(year=1989, month=9, day=13) and person3.test_set.count()==1)
        assert(person3.test_set.first().test_date.date()==datetime.date(year=2021, month=2, day=11) and person3.test_set.first().result==True)

    def test_input_file_with_invalid_email(self):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse('testingCentre:multipleTests'))
        self.selenium.find_element_by_name("tests_file").send_keys(os.getcwd()+"/testingCentre/tests/testsWithInvalidEmail.json")
        self.selenium.find_element_by_name("submit").send_keys(Keys.RETURN)
        assert(self.selenium.current_url == self.live_server_url+reverse('testingCentre:multipleTestsError'))
        assert(Addresses.objects.count() == 0)

class DataFormatErrorViewTests(SuperLiveServerTestCase):

    def test_upload_another_file(self):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse('testingCentre:multipleTestsError'))
        self.selenium.find_element_by_name("return").send_keys(Keys.RETURN)
        assert(self.selenium.current_url == self.live_server_url+reverse('testingCentre:multipleTests')+"?return=")

class NavigationBarTests(SuperLiveServerTestCase):

    def click_brand_link_and_return_to_homepage_from(self, from_url):
        self.create_user_and_login()
        self.selenium.get(self.live_server_url+reverse(from_url))
        self.selenium.find_element_by_name("brand").send_keys(Keys.RETURN)
        assert(self.selenium.current_url==self.live_server_url+reverse('testingCentre:chooseInputMethod'))

    def test_choose_input_method_view_navigation_bar(self):
        self.click_brand_link_and_return_to_homepage_from("testingCentre:chooseInputMethod")

    def test_single_test_view_navigation_bar(self):
        self.click_brand_link_and_return_to_homepage_from("testingCentre:singleTest")

    def test_multiple_tests_view_navigation_bar(self):
        self.click_brand_link_and_return_to_homepage_from("testingCentre:multipleTests")

    def test_single_test_thanks_view_navigation_bar(self):
        self.click_brand_link_and_return_to_homepage_from("testingCentre:thanks")

    def test_multiple_tests_thanks_view_navigation_bar(self):
        self.click_brand_link_and_return_to_homepage_from("testingCentre:multipleTestsThanks")

    def test_json_data_format_error_view_navigation_bar(self):
        self.click_brand_link_and_return_to_homepage_from("testingCentre:multipleTestsError")

class LoginSystemTests(SuperLiveServerTestCase):

    def cannot_visit_sites(self):
        self.selenium.get(self.live_server_url+reverse('testingCentre:chooseInputMethod'))
        assert(self.selenium.find_element_by_name("message").text == "You are not logged in")
        self.selenium.get(self.live_server_url+reverse('testingCentre:singleTest'))
        assert(self.selenium.find_element_by_name("message").text == "You are not logged in")
        self.selenium.get(self.live_server_url+reverse('testingCentre:thanks'))
        assert(self.selenium.find_element_by_name("message").text == "You are not logged in")
        self.selenium.get(self.live_server_url+reverse('testingCentre:multipleTests'))
        assert(self.selenium.find_element_by_name("message").text == "You are not logged in")
        self.selenium.get(self.live_server_url+reverse('testingCentre:multipleTestsThanks'))
        assert(self.selenium.find_element_by_name("message").text == "You are not logged in")
        self.selenium.get(self.live_server_url+reverse('testingCentre:multipleTestsError'))
        assert(self.selenium.find_element_by_name("message").text == "You are not logged in")

    def test_cannot_visit_sites_without_login(self):
        self.cannot_visit_sites()

    def test_login_with_wrong_username_and_password(self):
        self.selenium.get(self.live_server_url+reverse('testingCentre:login'))
        self.selenium.find_element_by_name("username").send_keys("terry")
        self.selenium.find_element_by_name("password").send_keys("yrret")
        self.selenium.find_element_by_name("submit").send_keys(Keys.RETURN)
        assert(self.selenium.current_url == self.live_server_url+reverse('testingCentre:login'))

    def test_logout(self):
        self.create_user_and_login()
        self.selenium.find_element_by_name("logout").send_keys(Keys.RETURN)
        self.cannot_visit_sites()
