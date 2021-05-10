from django import forms

from government.hooks.dbscan import cluster
from shared.models import *

class Form(forms.Form):
    case_id = forms.IntegerField(widget=forms.HiddenInput)
    case_name = forms.CharField(widget=forms.HiddenInput)

class ContactForm(forms.Form):
    case_id = forms.IntegerField(label='Case ID', widget=forms.HiddenInput)
    case_name = forms.CharField(label='Case Name', widget=forms.HiddenInput)
    contact_name = forms.CharField(label='Contact Name', max_length=256)
    contact_phone_num = forms.CharField(label='Contact Phone number', max_length=13)
    contact_email = forms.EmailField(label='Contact Email')
    place_of_contact = forms.CharField(label='Address of place of contact', max_length=256)
    postcode = forms.CharField(label='Postcode', max_length=8)

    # find if a person already exists in the database. Enter them if not and return the pk.
    def lookup_person(self):
        person = People.objects.filter(name__exact=self.cleaned_data['contact_name'],
                                       phone_num__exact=self.cleaned_data['contact_phone_num'],
                                       email__exact=self.cleaned_data['contact_email'])
        assert (person.count() <= 1)
        if person.count() == 0:
            # add person to model
            # check if address exists
            possibleAddress = Addresses.objects.filter(addr__exact=self.cleaned_data['place_of_contact'],
                                                       postcode=self.cleaned_data['postcode'])
            if possibleAddress.count() == 0:
                location = Addresses(addr=self.cleaned_data['place_of_contact'], postcode=self.cleaned_data['postcode'])
                location.save()
                # bit weird because persons address gets saved as the place of contact, which is not necessarily accurate, also their date of birth will be the default
                # TODO: Check this doesn't effect the stats
                p = People(
                    name=self.cleaned_data['contact_name'],
                    phone_num=self.cleaned_data['contact_phone_num'],
                    email=self.cleaned_data['contact_email'],
                    location=Addresses.objects.get(pk=location.pk)
                )
            else:
                p = People(
                    name=self.cleaned_data['contact_name'],
                    phone_num=self.cleaned_data['contact_phone_num'],
                    email=self.cleaned_data['contact_email'],
                    location=possibleAddress.first()
                )
            p.save()
            return p.pk
        else:
            return person.first().pk

    # find if an address already exists in the database. Enter it if not and return the pk.
    def lookup_address(self):
        address = Addresses.objects.filter(addr__exact=self.cleaned_data['place_of_contact'],
                                       postcode__exact=self.cleaned_data['postcode'])
        assert (address.count() <= 1)
        if address.count() == 0:
            location = Addresses(addr=self.cleaned_data['place_of_contact'], postcode=self.cleaned_data['postcode'])
            location.save()
            return location.pk
        else:
            return address.first().pk


    # assumes that the test has not already been input
    def input_contact(self, contactID, location):
        t = Contact(
            positive_case = Test.objects.get(pk=self.cleaned_data['case_id']),
            case_contact = People.objects.get(pk=contactID),
            location = Addresses.objects.get(pk=location)
        )
        t.save()
        cluster(t)


    def add_contact(self):
        # process the data in self.cleaned_data as required
        person = self.lookup_person()
        location = self.lookup_address()
        self.input_contact(person, location)


FINISHED_CHOICES = [(True, "Yes"), (False, "No")]

# a form for updating TestContacted if successful
class TestContactedForm(forms.Form):
    case_id = forms.IntegerField(label='Case ID', widget=forms.HiddenInput)
    success = forms.ChoiceField(widget=forms.RadioSelect, choices=FINISHED_CHOICES, label='Successfully contacted')

    def confirm_call(self):
        if self.cleaned_data['success']:
            case = Test.objects.get(pk=self.cleaned_data['case_id'])
            c = TestContacted(
                case=case
            )
            c.save()


# a form for updating ContactContacted if successful
class ContactContactedForm(forms.Form):
    contact_id = forms.IntegerField(label='Contact ID', widget=forms.HiddenInput)
    success = forms.ChoiceField(widget=forms.RadioSelect, choices=FINISHED_CHOICES, label='Successfully contacted')

    def confirm_call(self):
        if self.cleaned_data['success']:
            contact = Contact.objects.get(pk=self.cleaned_data['contact_id'])
            c = ContactContacted(
                contact=contact
            )
            c.save()
