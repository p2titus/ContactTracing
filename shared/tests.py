from django.test import TestCase

# tests here are primarily to test the models created.
# these should pass by default. they may be moved to another folder later

from django.test import TestCase
from .models import *


class ModelsTests(TestCase):
    def setup(self):
        self.create_addresses()
        self.create_people()

    def create_people(self):
        People.object.create(fname="Person", lname="A", addr=1, phone_num="A")
        People.object.create(fname="Person", lname="B", addr=2, phone_num="B")

    def create_addresses(self):
        Addresses.objects.create(addr="addrA", postcode="postcodeA")
        Addresses.objects.create(addr="addrB", postcode="postcodeB")

    def test_people_creation(self):
        b = People.objects.get(lname="B")
        self.assertEqual(b.phone_num, "B")
