from django.http import HttpResponse
from shared.models import Test
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, contact tracer!")


def poscase(request):
    test, details = Test().next_info()

    # I'd like to do a pattern match for the Nones or.. some better system
    if test is not None:
        if details is not None:
            context = {'success': True, 'date': test.test_date,
                       'phone': details.phone_num, 'name': details.name}
        else:
            context = {'success': False, 'error': "Unable to retrieve case's details"}
    else:
        context = {'success': False, 'error': "No positive case available"}
    return render(request, 'poscase.html', context)
