from django import forms
from shared.models import People, Addresses, Test
from django.core.validators import validate_email
import datetime

# will run into problems if people start living more than 150 years
current_year = datetime.datetime.today().year
possible_years = list(range(current_year, current_year-150, -1))

max_name_len = 256
max_phone_len = 13
max_addr_len = 256
max_post_len = 8

class SingleTestForm(forms.Form):
    name = forms.CharField(label='Name', max_length=max_name_len)
    date_of_birth = forms.DateField(label='Date of Birth', widget=forms.SelectDateWidget(years=possible_years))
    phone_num = forms.CharField(label='Phone number', max_length=max_phone_len)
    email = forms.EmailField(label='Email')
    addr = forms.CharField(label='Address', max_length=max_addr_len)
    postcode = forms.CharField(label='Postcode', max_length=max_post_len)
    test_date = forms.DateTimeField(label='Date of Test', widget=forms.SelectDateWidget(years=possible_years))
    result = forms.BooleanField(label='Positive test?', required=False)

    # find if a person already exists in the database. Enter them if not and return the pk.
    def lookup_person(self):
        person = People.objects.filter(name__exact=self.cleaned_data['name'],
                                       phone_num__exact=self.cleaned_data['phone_num'],
                                       email__exact=self.cleaned_data['email'],
                                       date_of_birth__exact=self.cleaned_data['date_of_birth'],
                                       location__addr__exact=self.cleaned_data['addr'],
                                       location__postcode__exact=self.cleaned_data['postcode'])
        assert (person.count() <= 1)
        if person.count() == 0:
            # add person to model
            # check if address exists
            possibleAddress = Addresses.objects.filter(addr__exact=self.cleaned_data['addr'],
                                                       postcode=self.cleaned_data['postcode'])
            if possibleAddress.count() == 0:
                location = Addresses(addr=self.cleaned_data['addr'], postcode=self.cleaned_data['postcode'])
                location.save()
                p = People(
                    name=self.cleaned_data['name'],
                    phone_num=self.cleaned_data['phone_num'],
                    date_of_birth=self.cleaned_data['date_of_birth'],
                    email=self.cleaned_data['email'],
                    location=location
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

    # assumes that the test has not already been input
    def input_test(self, personID):
        t = Test(
            person=People(pk=personID),
            result=self.cleaned_data['result']
        )
        t.save()
        t.test_date = self.cleaned_data['test_date']
        t.save()

    def send_text(self):
        pass

    def add_person(self):
        # process the data in self.cleaned_data as required
        person = self.lookup_person()
        self.input_test(person)
        self.send_text()

class MultipleTestsForm(forms.Form):
    tests_file = forms.FileField()
    date_format = "%d/%m/%y"

    # ensure that the data in the JSON file is convertible to Addresses, People, and Test objects
    def check_data(self, data):
        for test_dict in data:            
            assert(type(test_dict) is dict)
            assert(type(test_dict['name']) is str and len(test_dict['name']) <= max_name_len)
            assert(datetime.datetime.strptime(test_dict['date of birth'], self.date_format).date().year in possible_years)
            assert(type(test_dict['phone']) is str and len(test_dict['phone']) <= max_phone_len)
            validate_email(test_dict['email'])
            assert(type(test_dict['address']) is str and len(test_dict['address']) <= max_addr_len)
            assert(type(test_dict['postcode']) is str and len(test_dict['postcode']) <= max_post_len)
            assert(datetime.datetime.strptime(test_dict['test date'], self.date_format).date().year in possible_years)
            assert(type(test_dict['test result']) is bool)

    # convert the data to the corresponding model objects and save them
    def add_tests(self, data):
        for test_dict in data:
            date_of_birth = datetime.datetime.strptime(test_dict['date of birth'], self.date_format).date()
            test_date = datetime.datetime.strptime(test_dict['test date'], self.date_format).date()
            
            existing_address = Addresses.objects.filter(addr__exact=test_dict['address'],
                                                        postcode__exact=test_dict['postcode'])
            assert(existing_address.count() <= 1)
            if existing_address.count() == 1:
                location = existing_address.first()
                existing_person = location.people_set.filter(name__exact=test_dict['name'],
                                                             phone_num__exact=test_dict['phone'],
                                                             email__exact=test_dict['email'],
                                                             date_of_birth__exact=date_of_birth)
                assert(existing_person.count() <= 1)
                if existing_person.count() == 1:
                    person = existing_person.first()
                else:
                    person = None
            else:
                location = Addresses(addr=test_dict['address'], postcode=test_dict['postcode'])
                person = None
            
            location.save()
            if person == None:
                person = People(name = test_dict['name'],
                                phone_num = test_dict['phone'],
                                date_of_birth = date_of_birth,
                                email = test_dict['email'],
                                location = location)
            person.save()
            
            test = Test(person=person,
                        result=test_dict['test result'])
            test.save()
            test.test_date = test_date
            test.save()
