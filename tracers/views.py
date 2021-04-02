from django.http import HttpResponse
from shared.models import Test
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, contact tracer!")


def poscase(request):
    test = Test().get_next()

    if test is not None:
        context = {'success': True, 'date': test.test_date,
                   'phone': test.person.phone_num, 'name': test.person.name}
    else:
        context = {'success': False, 'error': "No positive case available"}
    return render(request, 'tracers/poscase.html', context)
