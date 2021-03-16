from django.test import TestCase

"""" tests here are primarily to test the models created.
consequently, they are a fairly minimal set of tests. These are only designed to test correctness and adherence to the
spec of the models
these should pass by default. they may be moved to another folder later
"""

from django.test import TestCase
from .models import *
from . import test_db_setup


class ModelsTests(TestCase):
    _pos_case = None
    _contact = None

    # details of the entities populating the database can be found in test_db_setup.py
    def setUp(self):
        setup = test_db_setup.DBSetup()
        setup.setup()

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
