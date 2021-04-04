from django.utils import timezone
from datetime import timedelta
import random

from django.core.management.base import BaseCommand
from shared.models import Test, Addresses, People, Contact
from government.models import Area
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import PointOnSurface
from government.hooks.dbscan import cluster

UK_eastings_range = [3530514.28, 3570579.82]
UK_northings_range = [3288094.49, 3219949.68]


def random_date(start, end):
    delta = end - start

    if delta.days < 0:
        random_day = 0
    else:
        random_day = random.randrange(0, delta.days)

    return start + timedelta(days=random_day)


def generate_case(lon, lat, i):
    addr = Addresses(addr="Address for case #%s" % i, postcode=str(i))
    addr.point = Point(x=lon, y=lat)

    p = People(name="P %s" % i, location=addr, phone_num=i, )
    p.date_of_birth = random_date(timezone.now() - timedelta(days=365 * ((i + 1) % 100)),
                                  timezone.now() - timedelta(days=365 * (i % 100)))

    p.email = "lady%s@ox.ac.uk" % i

    t = Test(person=p)
    t.result = bool(random.getrandbits(1))
    t.test_date = random_date(timezone.now() - timedelta(days=i + 1), timezone.now())

    return addr, p, t


def generate_contact(lon, lat, i, positive):
    addr = Addresses(addr="Address for contact #%s" % i, postcode=str(i))
    addr.point = Point(x=lon, y=lat)

    p = People(name="Contact person %s" % i, location=addr, phone_num=i, )
    p.date_of_birth = random_date(timezone.now() - timedelta(days=365 * (i % 100)),
                                  timezone.now() - timedelta(days=365 * ((i + 1) % 100)))

    p.email = "contact%s@ox.ac.uk" % i

    c = Contact(case_contact=p, positive_case=positive, location=addr)
    return addr, p, c


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--fill_las_with_cases', action='store_true')
        parser.add_argument("--generate_random_cases", action="store_true")
        parser.add_argument("--generate_random_contacts", action="store_true")
        parser.add_argument("--fix_missing_clusters", action="store_true")

    def handle(self, *args, **options):
        if options["fill_las_with_cases"]:
            print("Ensuring every LA has at least 1 case")
            # add in some data for every local authority so I can be sure they all show up on the map
            las = Area.objects.filter(type="LA").annotate(interiorpoint=PointOnSurface("poly"))
            i = 0
            for la in las:
                generate_case(la.interiorpoint.x, la.interiorpoint.y, i)
                i += 1

        elif options["generate_random_cases"]:
            print("Generating random cases")
            addr = []
            people = []
            tests = []

            for i in range(0, 4000):
                a, p, t = generate_case(random.uniform(UK_eastings_range[0], UK_eastings_range[1]),
                                        random.uniform(UK_northings_range[0], UK_northings_range[1]), i)
                addr.append(a)
                people.append(p)
                tests.append(t)

            Addresses.objects.bulk_create(addr)
            last_id = Addresses.objects.latest("id").id
            for i in range(0, 4000):
                people[i].location_id = last_id - i
            People.objects.bulk_create(people)
            last_id = People.objects.latest("id").id
            for i in range(0, 4000):
                tests[i].person_id = last_id - i
            Test.objects.bulk_create(tests)
            last_id = Test.objects.latest("id").id
            for i in range(0, 4000):
                t = Test.objects.get(id=last_id - i)
                t.test_date = random_date(timezone.now() - timedelta(days=i + 1), timezone.now())
                t.save()

        elif options["generate_random_contacts"]:
            print("Generating random contacts")
            positive_cases = Test.objects.all()[:4000]
            addr = []
            people = []
            contacts = []
            for i in range(0, 4000):
                a, p, c = generate_contact(random.uniform(UK_eastings_range[0], UK_eastings_range[1]),
                                           random.uniform(UK_northings_range[0], UK_northings_range[1]),
                                           i, positive_cases[i])
                addr.append(a)
                people.append(p)
                contacts.append(c)

            Addresses.objects.bulk_create(addr)
            for i in range(0, 4000):
                people[i].location_id = addr[i].id
            People.objects.bulk_create(people)
            for i in range(0, 4000):
                contacts[i].location_id = addr[i].id
                contacts[i].case_contact_id = people[i].id
            Contact.objects.bulk_create(contacts)

        elif options["fix_missing_clusters"]:
            print("Fixing missing clusters")
            max_index = Contact.objects.all().order_by("-id")[0].id
            for i in range(1, max_index):
                c = Contact.objects.filter(id=i)
                if c:
                    cluster(c[0])
                if i % 50 == 0:
                    print(i)

        else:
            print("You need to provide an option.")
