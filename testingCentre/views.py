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

def InputSingleTest(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SingleTestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SingleTestForm()

    return render(request, 'testingCentre/singleTest.html', {'form': form})

# from shared.models import People, Addresses, Test
# # find if a person already exists in the database. Enter them if not and return the pk.
# def lookup_person(name, phone, email, address, postcode):
#     pass
#
# # assumes that the test has not already been input
# def input_test(personID, date, res):
#     t = Test(
#         person = personID,
#         test_date = date,
#         result = res
#     )
#     t.save()
#
# def send_text(phone, res):
#     pass