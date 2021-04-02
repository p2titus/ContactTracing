from django import forms
from shared.models import People, Addresses, Contact

class ContactForm(forms.Form):
    case_id = forms.IntegerField(label='caseID', disabled=True)
    case_name = forms.CharField(label='Case Name', disabled=True)
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
                #bit weird because persons address gets saved as the place of contact, which is not necessarily accurate, also their date of birth will be the default
                # TODO: Check this doesn't effect the stats
                p = People(
                    name=self.cleaned_data['contact_name'],
                    phone_num=self.cleaned_data['contact_phone_num'],
                    email=self.cleaned_data['contact_email'],
                    location=Addresses.objects.get(pk=location)
                )
            else:
                p = People(
                    name=self.cleaned_data['name'],
                    phone_num=self.cleaned_data['phone_num'],
                    date_of_birth=self.cleaned_data['date_of_birth'],
                    email=self.cleaned_data['email'],
                    location=possibleAddress.first()
                )
            p.save()
            return p.pk
        else:
            return person.first().pk

    # find if an address already exists in the database. Enter it if not and return the pk.
    def lookup_address(self):
        address = Addresses.objects.filter(addr__exact=self.cleaned_data['place_of_contact'],
                                       phone_num__exact=self.cleaned_data['contact_phone_num'],
                                       email__exact=self.cleaned_data['contact_email'])
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
            positive_case = People.objects.get(pk=self.cleaned_data['case_id']),
            case_contact = People.objects.get(pk=contactID),
            location = Addresses.objects.get(pk=location)
        )
        t.save()

    def add_contact(self):
        # process the data in self.cleaned_data as required
        person = self.lookup_person()
        location = self.lookup_address()
        self.input_test(person, location)