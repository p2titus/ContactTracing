from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Max, Min, Avg
from shared.models import People, Test, TestContacted, ContactContacted, Contact
from datetime import date, time, datetime, timedelta

def index(request):
    return HttpResponse("Hello, Government user!.")

def timebased(request, time_frame):
    time_threshold = date.today() - timedelta(days=time_frame)
    testObjects = Test.objects.filter(test_date__gt=time_threshold)
    numTests = testObjects.count()
    posTests = testObjects.filter(result=True)
    numPos = posTests.count()
#    posRate = numPos / numTests
    peopleObjects = People.objects.filter(test__test_date__gt=time_threshold)
    people_by_Contacts = peopleObjects.annotate(Count('contact'))
    max_contacts = people_by_Contacts.aggregate(max=Max('contact__count'))['max']
    avg_contacts = people_by_Contacts.aggregate(average=Avg('contact__count'))['average']
    return render(request, 'government/timebased.html', {'numTests':numTests, 'numPos': numPos, 'max_contacts': max_contacts, 'avg_contacts': avg_contacts, 'time_frame':time_frame})
