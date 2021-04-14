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
    if request.method == 'POST':
        form = SingleTestForm(request.POST)
        if form.is_valid():
            form.add_person()
            return HttpResponseRedirect('/testingCentre/singleTest/thanks/')
    else:
        return HttpResponseRedirect('/testingCentre/singleTest/')

class InputSingleTestView(generic.FormView):
    template_name = 'testingCentre/singleTest.html'
    form_class = SingleTestForm
    success_url = '/thanks/'

