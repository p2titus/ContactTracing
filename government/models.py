from django.contrib.gis.db import models


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


