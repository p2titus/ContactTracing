import datetime

from django.db import models
from django.utils import timezone

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
    # date_of_birth = models.DateField
    # get rid of age here
    age = models.IntegerField
    location = models.ForeignKey(Addresses, on_delete=models.CASCADE)
    phone_num = models.CharField(max_length=13)
    email = models.EmailField
    # allows for country code (e.g. +44)

    # def age(self):
    #     now = timezone.now()
    #     return int((now - self.date_of_birth).days / 365.25)

class Test(models.Model):
    person = models.ForeignKey(People, on_delete=models.CASCADE)
    # when you delete a person, all their tests are deleted from this table
    test_date = models.DateTimeField
    result = models.BooleanField



class Contact(models.Model):
    positive_case = models.ForeignKey(Test, on_delete=models.CASCADE)
    case_contact = models.ForeignKey(People, on_delete=models.CASCADE)
    location = models.ForeignKey(Addresses, on_delete=models.CASCADE, related_name="loc")



class TestContacted(models.Model):
    case = models.ForeignKey(Test, on_delete=models.CASCADE)
    date_contacted = models.DateTimeField


class ContactContacted(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    date_contacted = models.DateTimeField
