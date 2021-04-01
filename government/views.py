from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Max, Min, Avg
from shared.models import People, Test, TestContacted, ContactContacted, Contact
from datetime import date, time, datetime, timedelta
from government.hooks.dbscan import MIN_PTS,EPS

def index(request):
    return HttpResponse("Hello, Government user!.")


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

def get_time_statistics(time_frame,offset):
    #i.e. say we want the aggregate data over a week, 4 weeks ago, we would call gts(7,3). zero indexed, i.e. gts(7,0) is the most recent week of stats
    time_threshold_0 = date.today() - timedelta(days=time_frame*(offset+1))
    time_threshold_1 = date.today() - timedelta(days=offset*time_frame)
    test_objects = Test.objects.filter(test_date__gt=time_threshold_0).filter(test_date__lte=time_threshold_1)
    num_tests = test_objects.count()
    pos_tests = test_objects.filter(result=True)
    num_pos = pos_tests.count()

    if num_tests == 0:
        pos_rate = 100
    else:
        pos_rate = 100 * num_pos / num_tests

    people_objects = People.objects.filter(test__test_date__gt=time_threshold_0).filter(test__test_date__lte=time_threshold_1)
    people_by_contacts = people_objects.annotate(Count('contact'))

    age_groups = []
    for i in range (0,90,10):
        birthday = date.today() - timedelta(days=i*365)
        age_groups.append(birthday)

    age_data = []
    for i in range(8,-1,-1):
        birthday = age_groups[i]
        age_data.append(people_objects.filter(date_of_birth__gte=birthday).count())
        if i<8:
            age_data[i] -= age_data[i+1]

    max_contacts = people_by_contacts.aggregate(max=Max('contact__count'))['max']
    if max_contacts is None:
        max_contacts = 0
    avg_contacts = people_by_contacts.aggregate(average=Avg('contact__count'))['average']
    if avg_contacts is None:
        avg_contacts = 0
    return {'max': max_contacts, 'avg': avg_contacts, 'age_data': age_data, 'num' : num_tests, 'pos' : pos_tests, 'rate' : pos_rate }

def timebased(request, time_frame):

    sn = get_time_statistics(time_frame, 0) #stats now, i.e. in the last time_frame days
    sp = get_time_statistics(time_frame,1) # stats then, i.e. in the time_frame days before the start of the most recent time_frame
    time_threshold = date.today() - timedelta(days=time_frame)

    return render(request, 'government/timebased.html',
                  {
                      # Data for this time frame
                      'num_tests': sn['num'],
                      'num_pos': sn['pos'],
                      'max_contacts': sn['max'],
                      'avg_contacts': sn['avg'],
                      'pos_rate': sn['rate'],
                      'cases_contacted': 78.45,
                      # Data for previous time frame
                      'prev_num_tests': sp['num'],
                      'prev_num_pos': sp['pos'],
                      'prev_max_contacts': sp['max'],
                      'prev_avg_contacts': sp['avg'],
                      'prev_pos_rate': sp['rate'],
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
