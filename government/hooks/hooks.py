"""Hook to call when you add stuff to the database"""
import requests
from django.contrib.gis.geos import Point
from .dbscan import cluster


def contact_hook(contact):
    point = get_coords(contact.location)
    if point is not None:
        contact.location.point = point
        contact.location.save()
    cluster(contact)


def get_coords(location):
    """Change this function to use your choice of geocoding API. `location` has an `addr` field and a `postcode` field. """
    url = 'https://api.postcodes.io/postcodes/{postcode}'.format(postcode=location.postcode)
    response = requests.get(url)
    if response.status_code == 200:
        json = response.json()["result"]
        return Point(y=json["latitude"], x=json["longitude"], srid=4326)
    return None


