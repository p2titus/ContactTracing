from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from government.models import Area, Cluster
from django.db import connection
from django.db.models import Count, Max, Min, Avg
from shared.models import People, Test, TestContacted, ContactContacted, Contact
from datetime import date, time, datetime, timedelta
from government.hooks.dbscan import MIN_PTS,EPS

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


pretty_times = {
    1: "the last day",
    7: "the last week",
    14: "the last fortnight",
    30: "the last month",
    365: "the last year"
}


def get_time_description(time_frame, prev=False):
    if time_frame in pretty_times.keys():
        t = pretty_times[time_frame]
    else:
        if time_frame % 365 == 0:
            t = "the last %d years" % (time_frame // 365)
        if time_frame % 30 == 0:
            t = "the last %d months" % (time_frame // 30)
        if time_frame % 7 == 0:
            t = "the last %d weeks" % (time_frame // 7)
        if time_frame >= 2:
            t = "the last %d days" % time_frame
        else:  # i.e <= 0
            t = "invalid time range"
    if prev:
        return t.replace(" last ", " preceding ")
    else:
        return t


def timebased(request, time_frame):
    time_threshold = date.today() - timedelta(days=time_frame)
    test_objects = Test.objects.filter(test_date__gt=time_threshold)
    num_tests = test_objects.count()
    pos_tests = test_objects.filter(result=True)
    num_pos = pos_tests.count()

    if num_tests == 0:
        pos_rate = 100
    else:
        pos_rate = 100 * num_pos / num_tests

    people_objects = People.objects.filter(test__test_date__gt=time_threshold)
    people_by_contacts = people_objects.annotate(Count('contact'))
    max_contacts = people_by_contacts.aggregate(max=Max('contact__count'))['max']
    if max_contacts is None:
        max_contacts = 0
    avg_contacts = people_by_contacts.aggregate(average=Avg('contact__count'))['average']
    if avg_contacts is None:
        avg_contacts = 0
    return render(request, 'government/timebased.html',
                  {
                      # Data for this time frame
                      'num_tests': num_tests,
                      'num_pos': num_pos,
                      'max_contacts': max_contacts,
                      'avg_contacts': avg_contacts,
                      'pos_rate': pos_rate,
                      'cases_contacted': 78.45,
                      # Data for previous time frame
                      'prev_num_tests': 1234,
                      'prev_num_pos': -1234,
                      'prev_max_contacts': -2,
                      'prev_avg_contacts': 1,
                      'prev_pos_rate': 1.45,
                      'prev_cases_contacted': 96.34,
                      # Time information
                      'time_frame': time_frame,
                      'time_description': get_time_description(time_frame),
                      'prev_time_description': get_time_description(time_frame, True),
                      'days_range': [time_threshold + timedelta(days=x) for x in range(time_frame)],
                      # Charting information
                      'charts_data': [(None, "Positive cases", "pos_case_canvas"),
                                      (None, "Tests performed", "num_tests_canvas"),
                                      (None, "Positivity rate", "pos_rate_canvas")],
                      # Clustering parameters
                      'min_cases_in_cluster': MIN_PTS,
                      'cluster_radius': EPS
                  })