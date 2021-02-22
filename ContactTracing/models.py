
from django.db import models


class People(models.Model):
    fname = models.CharField(max_length=32)
    lname = models.CharField(max_length=32)
    sex = models.BooleanField
    addr = models.CharField(max_length=256)
    postcode = models.CharField(max_length=8)  # max length assumed from https://ideal-postcodes.co.uk/guides/uk-postcode-format
    phone_num = models.CharField(max_length=13)  # allows for country code
