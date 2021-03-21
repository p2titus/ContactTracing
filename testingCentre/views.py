from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse

from .forms import SingleTestForm

from shared.models import People, Addresses, Test

# Create your views here.
class LoginView(generic.TemplateView):
    pass

class ChooseInputMethodView(generic.TemplateView):
    template_name = "testingCentre/chooseInputMethod.html"

class InputCSVView(generic.TemplateView):
    template_name = "testingCentre/csv.html"

# find if a person already exists in the database. Enter them if not and return the pk.
def lookup_person(name, phone, age, email, address, postcode):
    person = People.objects.filter(name__exact=name, phone_num__exact=phone, email__exact=email, age__exact=age, location__addr__exact=address, location__postcode__exact=postcode)
    assert(person.count <= 1)
    if person.count == 0:
        # add person to model
        # check if address exists
        possibleAddress = Addresses.objects.filter(addr__exact=address, postcode=postcode)
        if address.count == 0:
            p = People(
                name= name,
                phone_num=phone,
                email= email,
                location= Addresses(addr=address, postcode=postcode)
            )
        else:
            p = People(
                name= name,
                phone_num=phone,
                email= email,
                location= possibleAddress.first.pk
            )
        p.save()
        return p.pk
    else:
        return person.first.pk

# assumes that the test has not already been input
def input_test(personID, date, res):
    t = Test(
        person = personID,
        test_date = date,
        result = res
    )
    t.save()

def send_text(phone, res):
    pass

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
            person = lookup_person(form.cleaned_data['name'],
                                   form.cleaned_data['phone_num'],
                                   form.cleaned_data['age'],
                                   form.cleaned_data['email'],
                                   form.cleaned_data['addr'],
                                   form.cleaned_data['postcode'])
            input_test(person,
                       form.cleaned_data['test_date'],
                       form.cleaned_data['result'])
            send_text(form.cleaned_data['phone'],
                      form.cleaned_data['result'])
            # redirect to a new URL:
            return HttpResponseRedirect('thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SingleTestForm()

    return render(request, 'testingCentre/singleTest.html', {'form': form})