from django import forms
from shared.models import People, Addresses, Test

class SingleTestForm(forms.Form):
    name = forms.CharField(label='Name', max_length=256)
    # date_of_birth = forms.DateField(label='Date of Birth')
    # get rid of age here
    date_of_birth = forms.IntegerField(label='Date of Birth', widget=forms.SelectDateWidget)
    phone_num = forms.CharField(label='Phone number', max_length=13)
    email = forms.EmailField(label='Email')
    addr = forms.CharField(label='Address', max_length=256)
    postcode = forms.CharField(label='Postcode', max_length=8)
    test_date = forms.DateTimeField(label='Date of Test', widget=forms.SelectDateWidget)
    result = forms.BooleanField(label='Positive test?', required=False)

    # find if a person already exists in the database. Enter them if not and return the pk.
    def lookup_person(self):
        person = People.objects.filter(name__exact=self.cleaned_data['name'],
                                       phone_num__exact=self.cleaned_data['phone_num'],
                                       email__exact=self.cleaned_data['email'],
                                       age__exact=self.cleaned_data['date_of_birth'],
                                       location__addr__exact=self.cleaned_data['address'],
                                       location__postcode__exact=self.cleaned_data['postcode'])
        assert (person.count <= 1)
        if person.count == 0:
            # add person to model
            # check if address exists
            possibleAddress = Addresses.objects.filter(addr__exact=self.cleaned_data['address'],
                                                       postcode=self.cleaned_data['postcode'])
            if possibleAddress.count == 0:
                p = People(
                    name=self.cleaned_data['name'],
                    phone_num=self.cleaned_data['phone_num'],
                    email=self.cleaned_data['email'],
                    location=Addresses(addr=self.cleaned_data['address'], postcode=self.cleaned_data['postcode'])
                )
            else:
                p = People(
                    name=self.cleaned_data['name'],
                    phone_num=self.cleaned_data['phone_num'],
                    email=self.cleaned_data['email'],
                    location=possibleAddress.first.pk
                )
            p.save()
            return p.pk
        else:
            return person.first.pk

    # assumes that the test has not already been input
    def input_test(self, personID):
        t = Test(
            person=personID,
            test_date=self.cleaned_data['test_date'],
            result=self.cleaned_data['result']
        )
        t.save()

    def send_text(self):
        pass

    def add_person(self):
        # process the data in self.cleaned_data as required
        person = self.lookup_person()
        self.input_test(person)
        self.send_text()