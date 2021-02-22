
from django.db import models


class People(models.Model):
    fname = models.CharField(max_length=32)
    lname = models.CharField(max_length=32)
    addr = models.CharField(max_length=256)
    postcode = models.CharField(max_length=8)
    # max length assumed from https://ideal-postcodes.co.uk/guides/uk-postcode-format
    phone_num = models.CharField(max_length=13)
    # allows for country code (e.g. +44)


class Test(models.Model):
    person = models.ForeignKey(People, on_delete=models.CASCADE)
    # when you delete a person, all their tests are deleted from this table
    test_date = models.DateTimeField
    result = models.BooleanField


class Contact(models.Model):
    positive_case = models.ForeignKey(People, on_delete=models.CASCADE)
    case_contact = models.ForeignKey(People, on_delete=models.CASCADE)


class TestContacted(models.Model):
    case = models.ForeignKey(Test, on_delete=models.CASCADE)
    date_contacted = models.DateTimeField


class ContactContacted(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    date_contacted = models.DateTimeField
