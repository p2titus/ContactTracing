from django.http import HttpResponse
from django.template import loader
from government.models import Area, Cluster
from django.db import connection


def index(request):
    # Mimicking, but with tests instead of addresses
    # select ga.*, count(a) from government_area as ga
    #   join shared_addresses as a on st_intersects(ga.poly, a.point)
    #   group by ga.id

    # Should be fine to use raw SQL as we aren't using user input
    geos_point_type = connection.ops.select % "poly"  # poly is the name of the field in Area
    areas_with_alltime_counts = Area.objects.raw("""
        select ga.id, ga.%s as poly, ga.type, ga.name, count(test) as alltime_count
            from shared_test as test
                join shared_people sp on test.person_id = sp.id
                join shared_addresses sa on sa.id = sp.location_id
                join government_area ga on st_intersects(sa.point, ga.poly)
            where test.result = True
group by ga.id;
    """ % geos_point_type)

    countries = []
    regions = []
    counties = []
    las = []
    for area in areas_with_alltime_counts:
        if area.type == Area.COUNTRY:
            countries.append(area)
        if area.type == Area.REGION:
            regions.append(area)
        if area.type == Area.COUNTY:
            counties.append(area)
        if area.type == Area.LA:
            las.append(area)

    # TODO: need to add timestamps to database

    data = [
        ("Nation", "nations", countries),
        ("Region (England only)", "regions", regions),
        ("County/Unitary Authority", "counties", counties),
        ("Local Authority District", "las", las)
    ]

    template = loader.get_template("government/index.html")
    return HttpResponse(template.render({"areas": data}, request))


def clusters(request):
    data = Cluster.objects.all()

    template = loader.get_template("government/clusters.html")
    return HttpResponse(template.render({"clusters": list(data)}, request))