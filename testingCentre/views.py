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


class InputSingleTestView(generic.FormView):
    template_name = 'testingCentre/singleTest.html'
    form_class = SingleTestForm
    success_url = '/thanks/'

    def form_valid(self, form):
        form.add_person()
        return super.form_valid(form)