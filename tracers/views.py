from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from . import views_help
from .forms import *
from tracer_queues import add_contact, add_poscase


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
        print("test id is")
        print(test.id)
    else:
        context = {'success': False, 'error': "No new positive case available"}
    return render(request, 'tracers/poscase.html', context)


def contact(request):
    cont = views_help.next_contact()
    if cont is not None:
        context = {'success': True,
                   'phone': cont.case_contact.phone_num, 'name': cont.case_contact.name,
                   'form_confirm': ContactContactedForm({'contact_id': cont.id})
                   }
        print("contact id is")
        print(cont.id)
    else:
        context = {'success': False, 'error': "No new contact available"}
    return render(request, 'tracers/contact.html', context)

# TODO: make the addcontact form appear in new smaller window

def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            case = __extract_case_data(form)
            add_contact(case)
            form.add_contact()
            return HttpResponse('<script type="text/javascript">window.close()</script>')
        else:
            return render(request, 'tracers/contactForm.html', context={'form': form})
    else:
        return HttpResponseRedirect('/tracers')


# duplicate of same named function found in testingCentre/views
def __extract_case_data(form):
    x = None
    if form.cleaned_data['result'] is True:
        x = {
            'name': form.cleaned_data['name'],
            'phone_num': form.cleaned_data['phone_num'],
            'date_of_birth': form.cleaned_data['date_of_birth'],
            'email': form.cleaned_data['email'],
            'test_date': form.cleaned_data['test_date']
        }
    return x


# used to query whether a contact has been reached or not
# if a contact is not reached, it is pushed back into the tracer queue
__success_field_name = 'success'


def add_testcontacted(request):
    if request.method == 'POST':
        form = TestContactedForm(request.POST)
        if form.is_valid():
            form.confirm_call()
            if form.cleaned_data[__success_field_name] is False:
                case = __extract_case_data(form)
                add_poscase(case)
            return HttpResponseRedirect('/tracers')
        else:
            return HttpResponseRedirect('/tracers/error')
    else:
        return HttpResponseRedirect('/tracers/error')

def add_contactcontacted(request):
    if request.method == 'POST':
        form = ContactContactedForm(request.POST)
        if form.is_valid():
            form.confirm_call()
            if form.cleaned_data[__success_field_name] is False:  # TODO - ensure correct
                case = __extract_case_data(form)
                add_contact(case)
            return HttpResponseRedirect('/tracers')
        else:
            return HttpResponseRedirect('/tracers/error')
    else:
        return HttpResponseRedirect('/tracers/error')


def error(request):
    return HttpResponse('There was an error')
