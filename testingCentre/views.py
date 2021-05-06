from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
import json

from .forms import SingleTestForm, MultipleTestsForm

# Create your views here.
class LoginView(generic.TemplateView):
    pass

class ChooseInputMethodView(generic.TemplateView):
    template_name = "testingCentre/chooseInputMethod.html"

class InputMultipleTestsView(generic.FormView):
    template_name = "testingCentre/multipleTests.html"
    form_class = MultipleTestsForm
    success_url = "/testingCentre/multipleTests/thanks"

    def form_valid(self, form):
        data = json.load(form.cleaned_data['tests_file'])
        try:
            form.check_data(data)
        except:
            return HttpResponseRedirect('/testingCentre/multipleTests/error')
        form.add_tests(data)
        return super().form_valid(form)

class DataFormatErrorView(generic.TemplateView):
    template_name = "testingCentre/error.html"

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

