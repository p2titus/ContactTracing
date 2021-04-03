from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from . import views_help
from .forms import ContactForm, Form



def index(request):
    return HttpResponse("Hello, contact tracer!")


def poscase(request):
    test = views_help.next_test()
    if test is not None:
        context = {'success': True, 'date': test.test_date,
                   'phone': test.person.phone_num, 'name': test.person.name,
                    'form': Form({'case_id': test.id, 'case_name': test.person.name})}
    else:
        context = {'success': False, 'error': "No positive case available"}
    return render(request, 'tracers/poscase.html', context)

def thanks(request):
    return HttpResponse("Result Entered")

def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.add_contact()
            return HttpResponseRedirect('/tracers/poscase/')
        else:
            return render(request, 'tracers/contactForm.html', context= {'form' : form})
    else:
        return HttpResponseRedirect('/tracers/poscase/')