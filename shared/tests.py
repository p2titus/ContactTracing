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
        setup.setup()
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
        tests = Test.objects.all()
        ts = list(tests)
        tests_person = list(map(lambda a: a.person, ts))
        expected = [self._pos_case_non_contact, self._pos_case_contact]
        self.__check_lists_equal(tests_person, expected)

    # performs pairwise element check to see if two lists are equal
    def __check_lists_equal(self, xs, ys):
        self.assertEqual(len(xs), len(ys))
        for x in xs:
            self.assertEqual(self.__is_mem_of(x, ys), (True, None))
            ys.remove(x)

    @staticmethod
    def __is_mem_of(y, xs):
        count = 0
        for x in xs:
            count += 1
            if x == y:
                return True, None
        return False, y

    def test_contacts(self):
        test = Test.objects.get(person=self._pos_case_non_contact)
        contact = Contact.objects.get(positive_case=test)
        self.assertEqual(contact.case_contact, self._contact_non_contact)

    def test_contacts_not_empty(self):
        con = Contact.objects.all()
        cs = list(con)
        ex = [self._contact_contact]
        self.__check_lists_equal(cs, ex)

    def test_uncontacted(self):
        con = Contact.get_uncontacted()
        expected = [self._pos_case_non_contact]
        print(con[0].case_contact.name)
        print(con[1].case_contact.name)
        self.__check_lists_equal(con, expected)
