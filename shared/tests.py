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
    # aliased for variables in setup
    # haven't been contacted according to database
    _pos_case_non_contact = None
    _contact_non_contact = None

    # have been contacted according to database
    _pos_case_contact = None
    _contact_contact = None

    # details of the entities populating the database can be found in test_db_setup.py
    def setUp(self):
        setup = test_db_setup.DBSetup()
        print("start setup")
        setup.setup()
        print("setup")
        self._pos_case_non_contact = setup.pos_case_non_contact
        self._contact_non_contact = setup.contact_non_contact
        self._pos_case_contact = setup.pos_case_contact
        self._contact_contact = setup.contact_contact

    # basic check on whether the database has been created successfully - non exhaustive
    def test_people_creation(self):
        b = People.objects.get(email="B@example.com")
        self.assertEqual(b.phone_num, "B")

    # checks
    def test_get_tests(self):
        tests = Test.objects.get()
        self.assertEqual(tests.person, self._pos_case_non_contact)

    def test_contacts(self):
        test = Test.objects.get(person=self._pos_case_non_contact)
        contact = Contact.object.get(positive_case=test)
        self.assertEqual(contact.case_contact, self._contact_non_contact)

    def test_uncontacted(self):
        con = Contact.get_uncontacted()
        self.assertEqual(self._contact_non_contact, con)
