from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from . import views_help
from .forms import *



def index(request):
    return HttpResponse("Hello, contact tracer!")

# ideally add a warning before leaving page (here & for contact)
# TODO: display the 'confirm' forms embedded in the pages
def poscase(request):
    """test = views_help.next_test()
    if test is not None:
        context = {'success': True, 'date': test.test_date,
                   'phone': test.person.phone_num, 'name': test.person.name,
                    'form_addcontact': Form({'case_id': test.id, 'case_name': test.person.name})
                    'form_confirm': Form({'case_id': test.id})
                    }
    else:
        context = {'success': False, 'error': "No positive case available"}"""
    context = {'success': False, 'error': "Page incomplete..."}
    return render(request, 'tracers/poscase.html', context)


def contact(request):
    """cont = views_help.next_contact()
    if cont is not None:
        context = {'success': True,
                   'phone': cont.person.phone_num, 'name': cont.person.name,
                   'form_confirm': Form({'case_id': test.id})
                   }
    else:
        context = {'success': False, 'error': "No positive case available"}"""
    context = {'success': False, 'error': "Page incomplete..."}
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