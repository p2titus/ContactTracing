from django.db import models
from django.db.models import Exists

"""
The basic models used by the application
This automatically generates the relevant tables, completely removing any need for raw SQL
Care should still be taken to ensure data cannot be accessed when not required
"""


# more granularity may be required with some addresses than others: this can be dealt with by code using the database
class Addresses(models.Model):
    addr = models.CharField(max_length=256)
    postcode = models.CharField(max_length=8)
    # max length assumed from https://ideal-postcodes.co.uk/guides/uk-postcode-format


class People(models.Model):
    name = models.CharField(max_length=256)
    age = models.IntegerField()
    location = models.ForeignKey(Addresses, on_delete=models.CASCADE)
    phone_num = models.CharField(max_length=13)
    email = models.EmailField()
    # allows for country code (e.g. +44)

    # gets all tests the current person has had that are on the system
    def get_tests(self):
        x = Test.object.get(person=self)
        return x.order_by('-test_date')


class Test(models.Model):
    person = models.ForeignKey(People, on_delete=models.CASCADE)
    # when you delete a person, all their tests are deleted from this table
    test_date = models.DateTimeField(auto_now_add=True)
    result = models.BooleanField()

    def get_contacts(self):
        return Contact.objects.get(positive_case=self)

    # returns all uncontacted test cases
    @staticmethod
    def get_uncontacted():
        xs = TestContacted.objects.all()
        return Test.objects.exclude(person__in=xs.values_list('case', flat=True))


class Contact(models.Model):
    positive_case = models.ForeignKey(Test, on_delete=models.CASCADE)
    # the person who came into contact with the person who tested positive
    case_contact = models.ForeignKey(People, on_delete=models.CASCADE)
    # this separate location is necessary for statistics - used to show where contact happened
    location = models.ForeignKey(Addresses, on_delete=models.CASCADE, related_name="loc")

    # returns all uncontacted contacts
    @staticmethod
    def get_uncontacted():
        xs = ContactContacted.objects.all()
        return Contact.objects.exclude(case_contact__in=xs.values_list('contact', flat=True))


class TestContacted(models.Model):
    case = models.ForeignKey(Test, on_delete=models.CASCADE)
    date_contacted = models.DateTimeField(auto_now_add=True)


class ContactContacted(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    date_contacted = models.DateTimeField(auto_now_add=True)
