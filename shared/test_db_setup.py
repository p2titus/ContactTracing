"""
we instantiate with two people - persons A and B
A has had a positive test case, and B has recently come into contact with A and thus must be tracked
various expected retrievals of data from the database are carried out to ensure they work as expected
the variable namings of the contact makes it fairly clear which is which

as this is to construct a test database, this is not done most efficiently - specifically, there will be more calls to
the database than are required
"""

from .models import *


class DBSetup:
    # have not been contacted yet
    pos_case_non_contact = None
    contact_non_contact = None

    # have both been contacted once
    pos_case_contact = None
    contact_contact = None

    def setup(self):
        self.create_addresses()
        self.create_people()
        self.create_test_inst()

    @staticmethod
    def _gen_addr(id: str):
        return Addresses.objects.create(addr="addr"+id, postcode="postcode"+id)

    def create_addresses(self):
        self._gen_addr('A')
        self._gen_addr('B')
        self._gen_addr('C')
        self._gen_addr('D')

    @staticmethod
    def _gen_person(id: str):
        addr = Addresses.objects.get(addr="addr"+id)
        return People.objects.create(name="Person "+id, age=30, phone_num=id, email=id+"@example.com", location=addr)

    def create_people(self):
        self.pos_case_non_contact = self._gen_person('A')
        self.contact_non_contact = self._gen_person('B')
        self.pos_case_contact = self._gen_person('C')
        self.contact_contact = self._gen_person('D')

    @staticmethod
    def _gen_test(id: str):
        case = People.objects.get(name="Person "+id)
        return Test.objects.create(person=case, result=True)

    def create_test_inst(self):
        a = self._gen_test('A')
        c = self._gen_test('C')
        self.create_contact_inst(a, self.contact_non_contact)
        self.create_contact_inst(c, self.contact_contact)

    @staticmethod
    def _gen_contact(test, contact):
        return Contact.objects.create(case_contact=contact, positive_case=test, location=contact.location)

    # location on create_contact_inst only used for stats - use dummy value for testing
    def create_contact_inst(self, test, contact):
        return self._gen_contact(test, contact)
