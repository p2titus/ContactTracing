from django.test import TestCase

"""" tests here are primarily to test the models created.
consequently, they are a fairly minimal set of tests. These are only designed to test correctness and adherence to the
spec of the models
these should pass by default. they may be moved to another folder later

we instantiate with two people - persons A and B
A has had a positive test case, and B has recently come into contact with A and thus must be tracked
various expected retrievals of data from the database are carried out to ensure they work as expected"""

from django.test import TestCase
from .models import *


class ModelsTests(TestCase):
    _pos_case = None
    _contact = None

    def setUp(self):
        self.create_addresses()
        (self._pos_case, self._contact) = self.create_people()
        x = self.create_test_inst()
        self.create_contact_inst(x)

    def test_people_creation(self):
        b = People.objects.get(email="B@example.com")
        self.assertEqual(b.phone_num, "B")

    def get_tests(self):
        tests = Test.objects.get()
        self.assertEqual(tests.person, self._pos_case)

    def check_contacts(self):
        test = Test.objects.get(person=self._pos_case)
        contact = Contact.object.get(positive_case=test)
        self.assertEqual(contact.case_contact, self._contact)

    def check_uncontacted(self):
        con = Contact.get_uncontacted()
        self.assertEqual(self._contact, con)
