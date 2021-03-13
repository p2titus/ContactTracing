from django.test import TestCase

# tests here are primarily to test the models created.
# these should pass by default. they may be moved to another folder later

from django.test import TestCase
from .models import *


class ModelsTests(TestCase):
    def setUp(self):
        self.create_addresses()
        self.create_people()

    def create_people(self):
        # TODO - are addresses done correctly?
        addrA = Addresses.objects.get(addr="addrA")
        addrB = Addresses.objects.get(addr="addrB")
        People.objects.create(name="Person A", phone_num="A", email="A@example.com", location=addrA)
        People.objects.create(name="Person B", phone_num="B", email="B@example.com", location=addrB)

    def create_addresses(self):
        Addresses.objects.create(addr="addrA", postcode="postcodeA")
        Addresses.objects.create(addr="addrB", postcode="postcodeB")

    def test_people_creation(self):
        b = People.objects.get(email="B@example.com")
        self.assertEqual(b.phone_num, "B")
