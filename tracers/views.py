from django.http import HttpResponse
from django.shortcuts import render, redirect
from . import views_help


def index(request):
    return HttpResponse("Hello, contact tracer!")


# TODO - redirect to home page if logged in already
def login(request):
    return redirect('accounts/login')


def poscase(request):
    test = views_help.next_test()
    if test is not None:
        context = {'success': True, 'date': test.test_date,
                   'phone': test.person.phone_num, 'name': test.person.name}
    else:
        context = {'success': False, 'error': "No positive case available"}
    return render(request, 'tracers/poscase.html', context)
