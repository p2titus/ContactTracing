from django.contrib.gis.db import models
from django.db.models import Count, Max, Min, Avg
from shared.models import People, Test, TestContacted, ContactContacted, Contact
from datetime import date, time, datetime, timedelta
# Create your models here.

class Area(models.Model):
    COUNTRY = "CTRY"
    REGION = "REG"
    COUNTY = "CNTY"
    LA = "LA"
    AREA_TYPES = (
        (COUNTRY, "Country"),
        (REGION, "Region"),
        (COUNTY, "County/Unitary Authority"),
        (LA, "Local Authority District")
    )
    name = models.CharField(max_length=256)
    poly = models.MultiPolygonField(srid=3035)
    type = models.CharField(max_length=4, choices=AREA_TYPES, default=LA)


class Cluster(models.Model):
    cluster_id = models.UUIDField(primary_key=True)
    # A generated polygon around the points in this cluster.
    area = models.PolygonField()
    points_in_cluster = models.IntegerField(default=0)



"""class AggregateData(models.Model):
    timeframe = 0
    tag = 'daily'
    time_threshold = date.today() - timedelta(days=timeframe)
    testObjects = Test.objects.filter(test_date__gt=time_threshold)
    numTests = testObjects.count()
    posTests = testObjects.filter(result=True)
    numPos = posTests.count()
    posRate = numPos / numTests
    peopleObjects = People.objects.filter(test_date__gt=time_threshold)
    people_by_Contacts = peopleObjects.annotate(num_contact=Count('contact'))
    max_contacts = people_by_Contacts.aggregate(max=Max('num_contacts'))['max']
    avg_contacts = people_by_Contacts.aggregate(average=Avg('num_contacts'))['average']
"""