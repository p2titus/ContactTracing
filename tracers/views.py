from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from . import views_help
from .forms import *
import tracer_queues

"""
TODO - it needs to be decided exactly what needs to be pushed to the queue
Currently, __extract_case_data tries to extract data that doesnt exist in the cleaned data
"""


# avoiding duplicate names of functions
def add_contact_to_queue(contact: dict):
    import tracer_queues
    tracer_queues.add_contact(contact)


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
            case = __extract_contact_data(form)
            add_contact_to_queue(case)
            form.add_contact()
            return HttpResponse('<script type="text/javascript">window.close()</script>')
        else:
            return render(request, 'tracers/contactForm.html', context={'form': form})
    else:
        return HttpResponseRedirect('/tracers')


# duplicate of same named function found in testingCentre/views with small changes made
def __extract_case_data(form):
    x = None
    res_field = 'result'  # result field
    if res_field not in form or form.cleaned_data[res_field] is True:
        x = {
            'name': form.cleaned_data['name'],
            'phone_num': form.cleaned_data['phone_num'],
            'date_of_birth': form.cleaned_data['date_of_birth'],
            'email': form.cleaned_data['email'],
            'test_date': form.cleaned_data['test_date']
        }
    return x


def __extract_contact_data(form):
    print(form.cleaned_data)
    return {
        'name': form.cleaned_data['contact_name'],
        'phone_num': form.cleaned_data['contact_phone_num'],
        'postcode': form.cleaned_data['postcode'],
        'address': form.cleaned_data['place_of_contact'],
        'email': form.cleaned_data['contact_email']
    }


# used to query whether a contact has been reached or not
# if a contact is not reached, it is pushed back into the tracer queue
__success_field_name = 'success'


def add_testcontacted(request):
    if request.method == 'POST':
        form = TestContactedForm(request.POST)
        if form.is_valid():
            form.confirm_call()
            succ = form.cleaned_data[__success_field_name]
            print("confirm call in testcontacted")
            print(f"success was {succ}")
            print(type(succ))
            if succ == "False":
                print("hit testcontacted non success branch")
                case = __extract_case_data(form)
                print('case')
                print(case)
                tracer_queues.add_poscase(case)
            """if succ:
                print("successful branch???")"""
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
                tracer_queues.add_contact(case)
            return HttpResponseRedirect('/tracers')
        else:
            return HttpResponseRedirect('/tracers/error')
    else:
        return HttpResponseRedirect('/tracers/error')


def error(request):
    return HttpResponse('There was an error')
