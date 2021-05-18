"""Hook to call when you add stuff to the database"""
import requests
from django.contrib.gis.geos import Point
from .dbscan import cluster


def contact_hook(contact):
    point = get_coords(contact.location.addr, contact.location.postcode)
    if point is not None:
        contact.location.point = point
        contact.location.save()
    cluster(contact)


def get_coords(addr, postcode):
    """Change this function to use your choice of geocoding API. `addr` is a freeform text input for the address """
    url = 'https://api.postcodes.io/postcodes/{postcode}'.format(postcode=postcode)
    response = requests.get(url)
    if response.status_code == 200:
        json = response.json()["result"]
        return Point(y=json["latitude"], x=json["longitude"], srid=4326)
    return None


