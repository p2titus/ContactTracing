from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse

from .forms import SingleTestForm

# Create your views here.
class LoginView(generic.TemplateView):
    pass

class ChooseInputMethodView(generic.TemplateView):
    template_name = "testingCentre/chooseInputMethod.html"

class InputCSVView(generic.TemplateView):
    template_name = "testingCentre/csv.html"

def thanks(request):
    return HttpResponse("Result Entered")

def add_person(request):
    print('\nstart\n')
    if request.method == 'POST':
        form = SingleTestForm(request.POST)
        print('form put in var')
        if form.is_valid():
            print('\na\n')
            import tracer_queues
            case = extract_case_data(form)
            print('\nflag\n')
            if case is not None:
                tracer_queues.main.add_poscase(case)
            form.add_person()

            return HttpResponseRedirect('/testingCentre/singleTest/thanks/')
        else:
            print('fail')
            return None
    else:
        print('\nb\n')
        return HttpResponseRedirect('/testingCentre/singleTest/')


def extract_case_data(form):
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


class InputSingleTestView(generic.FormView):
    template_name = 'testingCentre/singleTest.html'
    form_class = SingleTestForm
    success_url = '/thanks/'

