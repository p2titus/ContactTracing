from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from . import views_help
from .forms import *



def index(request):
    return render(request, 'tracers/index.html')

# TODO: add a warning before leaving page (here & for contact)
def poscase(request):
    test = views_help.next_test()
    if test is not None:
        context = {'success': True, 'date': test.test_date,
                   'phone': test.person.phone_num, 'name': test.person.name,
                    'form_addcontact': Form({'case_id': test.id, 'case_name': test.person.name}),
                    'form_confirm': TestContactedForm({'case_id': test.id})
                    }
    else:
        context = {'success': False, 'error': "No new positive case available"}
    return render(request, 'tracers/poscase.html', context)


def contact(request):
    cont = views_help.next_contact()
    if cont is not None:
        context = {'success': True,
                   'phone': cont.case_contact.phone_num, 'name': cont.case_contact.name,
                   'form_confirm': TestContactedForm({'case_id': cont.id})
                   }
    else:
        context = {'success': False, 'error': "No new contact available"}
    return render(request, 'tracers/contact.html', context)

# TODO: make the addcontact form appear in new smaller window

def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.add_contact()
            return HttpResponseRedirect('/tracers')
        else:
            return render(request, 'tracers/contactForm.html', context={'form': form})
    else:
        return HttpResponseRedirect('/tracers')

def add_testcontacted(request):
    if request.method == 'POST':
        form = TestContactedForm(request.POST)
        if form.is_valid():
            form.confirm_call()
            return HttpResponseRedirect('/tracers')
        else:
            return HttpResponseRedirect('/tracers')
    else:
        return HttpResponseRedirect('/tracers')

def add_contactcontacted(request):
    if request.method == 'POST':
        form = ContactContactedForm(request.POST)
        if form.is_valid():
            form.confirm_call()
            return HttpResponseRedirect('/tracers')
        else:
            return HttpResponseRedirect('/tracers')
    else:
        return HttpResponseRedirect('/tracers')
