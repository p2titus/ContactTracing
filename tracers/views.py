from django.http import HttpResponse
from django.shortcuts import render
from . import views_help


def index(request):
    return HttpResponse("Hello, contact tracer!")


def poscase(request):
    """test = views_help.next_test()
    if test is not None:
        context = {'success': True, 'date': test.test_date,
                   'phone': test.person.phone_num, 'name': test.person.name}
    else:
        context = {'success': False, 'error': "No positive case available"}"""
    context = {'success': False, 'error': "Page incomplete..."}
    return render(request, 'tracers/poscase.html', context)


def contact(request):
    """cont = views_help.next_contact()
    if cont is not None:
        context = {'success': True,
                   'phone': cont.person.phone_num, 'name': cont.person.name}
    else:
        context = {'success': False, 'error': "No positive case available"}"""
    context = {'success': False, 'error': "Page incomplete..."}
    return render(request, 'tracers/contact.html', context)