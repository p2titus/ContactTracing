from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from shared.models import Test, Addresses, People
from government.models import Area
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import PointOnSurface
import random
from datetime import date

UK_lon_range = [-10.92, 1.845]
UK_lat_range = [49.795, 58.87]

from datetime import timedelta


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def generate_case(lon, lat, i):
    addr = Addresses(addr="Address #%s" % i, postcode=str(i))
    addr.point = Point(x=lon, y=lat)
    addr.save()
    p = People(name="P %s" % i, location=addr, phone_num=i, )
    p.age = i
    p.email = "lady%s@ox.ac.uk" % i
    p.save()
    t = Test(person=p)
    t.result = bool(random.getrandbits(1))
    t.test_date = date.today()
    t.save()


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--fix_bools',  action='store_true')

        parser.add_argument('--fill_las',  action='store_true')


    def handle(self, *args, **options):
        if options["fix_bools"]:
            print("Fixing!")
            for t in Test.objects.all():
                t.result = bool(random.getrandbits(1))
                t.test_date = random_date(date.fromisoformat("2021-01-01"),date.today())
                t.save()
        elif options["fill_las"]:
            print("Filling LAs")
            # add in some data for every local authority so I can be sure they all show up on the map
            las = Area.objects.filter(type="LA").annotate(interiorpoint=PointOnSurface("poly"))
            i = 0
            for la in las:

                generate_case(la.interiorpoint.x, la.interiorpoint.y, i)
                i += 1
        else:
            # ignores all options/args
            for i in range(0, 4000):
                generate_case(random.uniform(UK_lon_range[0], UK_lon_range[1]),
                       random.uniform(UK_lat_range[0], UK_lat_range[1]), i)


