from .models import *


class DBSetup:
    _pos_case = None
    _contact = None

    def setup(self):
        self.create_addresses()
        self.create_people()
        test = self.create_test_inst()
        self.create_contact_inst(test)

    def create_addresses(self):
        Addresses.objects.create(addr="addrA", postcode="postcodeA")
        Addresses.objects.create(addr="addrB", postcode="postcodeB")

    def create_people(self):
        addrA = Addresses.objects.get(addr="addrA")
        addrB = Addresses.objects.get(addr="addrB")
        a = People.objects.create(name="Person A", phone_num="A", email="A@example.com", location=addrA)
        b = People.objects.create(name="Person B", phone_num="B", email="B@example.com", location=addrB)
        return (a, b)

    def create_test_inst(self):
        return Test.objects.create(person=self._pos_case, result=True)

    def create_contact_inst(self, test):
        addr_b = Addresses.objects.get(addr="addrB")
        Contact.objects.create(case_contact=self._contact, positive_case=test, location=addr_b)
