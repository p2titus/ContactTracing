from datetime import date, timedelta

from django.db import connection
from django.db.models import Count, Max, Avg
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from government.hooks.dbscan import MIN_PTS, EPS
from government.models import Area, Cluster
from shared.models import Test, ContactContacted


def index(request):
    return HttpResponse("Hello!")


def get_geographic_data(start_day):
    # Should be fine to use raw SQL as we aren't using user input
    geos_point_type = connection.ops.select % "poly"  # poly is the name of the field in Area
    areas_with_alltime_counts = Area.objects.raw("""
        select ga.id, ga.poly::bytea as poly, ga.type, ga.name, ga.population, count(test) as alltime_count
            from shared_test as test
                join shared_people sp on test.person_id = sp.id
                join shared_addresses sa on sa.id = sp.location_id
                join government_area ga on st_intersects(sa.point, ga.poly)
            where test.result = True and test.test_date>= %s
group by ga.id;
    """, [start_day])

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
        ("Nation", "country", countries),
        ("Region (England only)", "region", regions),
        ("County/Unitary Authority", "county", counties),
        ("Local Authority District", "la", las)
    ]

    return data


def clusters(time_frame):
    data = Cluster.objects.filter(end_date__gte=time_frame)
    return list(data)


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
        # elif time_frame % 30 == 0:
        #    t = "the last %d months" % (time_frame // 30)
        elif time_frame % 7 == 0:
            t = "the last %d weeks" % (time_frame // 7)
        elif time_frame >= 2:
            t = "the last %d days" % time_frame
        else:  # i.e <= 0
            t = "invalid time range"
    if prev:
        return t.replace(" last ", " preceding ")
    else:
        return t


def get_time_statistics(time_frame, offset):
    # i.e. say we want the aggregate data over a week, 4 weeks ago, we would call gts(7,3). zero indexed, i.e. gts(7,0)
    # is the most recent week of stats
    time_threshold_0 = timezone.now() - timedelta(days=time_frame * (offset + 1))
    time_threshold_1 = timezone.now() - timedelta(days=offset * time_frame)
    test_objects = Test.objects.filter(test_date__gt=time_threshold_0).filter(test_date__lte=time_threshold_1)

    num_tests = test_objects.count()
    pos_tests = test_objects.filter(result=True)
    num_pos = pos_tests.count()

    if num_tests == 0:
        pos_rate = 100
    else:
        pos_rate = 100 * num_pos / num_tests

    age_groups = []
    for i in range(0, 90, 10):
        birthday = timezone.now() - timedelta(days=i * 365)
        age_groups.append(birthday)
    # by this point, age_groups is a list of the dates today, 10 years ago... up to 80 years ago
    age_test_data = []
    for i in range(0, 8, 1):
        birthday0 = age_groups[i] ; birthday1 = age_groups[i+1]
        age_test_data.append(test_objects.filter(person__date_of_birth__lte=birthday0).filter(person__date_of_birth__gt=birthday1).count()) #i.e. their birthday is in the 10 year window from birthday0 to birthday1
    age_test_data.append(test_objects.filter(person__date_of_birth__lte=age_groups[8]).count())

    age_pos_data = []
    for i in range(0, 8, 1):
        birthday0 = age_groups[i] ; birthday1 = age_groups[i+1]
        age_pos_data.append(pos_tests.filter(person__date_of_birth__gt=birthday1).filter(person__date_of_birth__lte=birthday0).count())
    age_pos_data.append(pos_tests.filter(person__date_of_birth__lte=age_groups[8]))

    # age_pos_data is now a list of size 9 with the number of positive cases for people in each age group

    # can use same queryset thing for both max and avg
    positives_with_contact_count = pos_tests.annotate(no_contacts=Count('contact'))
    max_contacts = positives_with_contact_count.aggregate(max=Max('no_contacts'))['max']
    if max_contacts is None:
        max_contacts = 0

    avg_contacts = positives_with_contact_count.aggregate(average=Avg('no_contacts'))['average']
    if avg_contacts is None:
        avg_contacts = 0

    contacted = ContactContacted.objects.filter(date_contacted__gt=time_threshold_0).filter(
        date_contacted__lte=time_threshold_1).count()

    tests_by_day = test_objects.annotate(day=TruncDate("test_date")).values("day").order_by("day").annotate(count=Count("id")).values(
        "day", "count")
    pos_by_day = pos_tests.annotate(day=TruncDate("test_date")).values("day").order_by("day").annotate(count=Count("id")).values(
        "day", "count")
    rate_by_day = []
    for (pos, tests) in zip(pos_by_day, tests_by_day):
        if pos["count"] > 0:
            rate = pos["count"] / tests["count"]
        else:
            rate = 0
        rate_by_day.append({"day": pos["day"],
                            "count": rate})

    return {'max': max_contacts, 'avg': avg_contacts, 'age_test_data': age_test_data, 'age_pos_data': age_pos_data,
            'num': num_tests, 'pos': num_pos, 'rate': pos_rate, 'contacted': contacted, 'tests_by_day': tests_by_day,
            'pos_by_day': pos_by_day, 'rate_by_day': rate_by_day}


def timebased(request, time_frame):
    # stats now, i.e. in the last time_frame days
    sn = get_time_statistics(time_frame, 0)
    # stats then, i.e. in the time_frame days before the start of the most recent time_frame
    sp = get_time_statistics(time_frame, 1)
    time_threshold = date.today() - timedelta(days=time_frame)

    return render(request, 'government/timebased.html',
                  {
                      # Data for this time frame
                      'num_tests': sn['num'],
                      'num_pos': sn['pos'],
                      'max_contacts': sn['max'],
                      'avg_contacts': sn['avg'],
                      'pos_rate': sn['rate'],
                      'cases_contacted': sn['contacted'],
                      'age_test_data': sn['age_test_data'],
                      'age_pos_data': sn['age_pos_data'],
                      # Data for previous time frame
                      'prev_num_tests': sp['num'],
                      'prev_num_pos': sp['pos'],
                      'prev_max_contacts': sp['max'],
                      'prev_avg_contacts': sp['avg'],
                      'prev_pos_rate': sp['rate'],
                      'prev_cases_contacted': sp['contacted'],
                      'prev_age_test_data': sp['age_test_data'],
                      'prev_age_pos_data': sp['age_pos_data'],
                      # Time information
                      'time_frame': time_frame,
                      'time_description': get_time_description(time_frame),
                      'prev_time_description': get_time_description(time_frame, True),
                      'days_range': [time_threshold + timedelta(days=x) for x in range(time_frame)],
                      # Charting information
                      'charts_data': [(sn["pos_by_day"], sp["pos_by_day"], "Positive cases", "pos_case_canvas"),
                                      (sn["tests_by_day"], sp["tests_by_day"], "Tests performed", "num_tests_canvas"),
                                      (sn["rate_by_day"], sp["rate_by_day"], "Positivity rate", "pos_rate_canvas")],
                      # Clustering parameters
                      'min_cases_in_cluster': MIN_PTS,
                      'cluster_radius': EPS,
                      # clustering data
                      "clusters": clusters(time_threshold),
                      # geographic areas data
                      "areas": get_geographic_data(time_threshold)

                  })
