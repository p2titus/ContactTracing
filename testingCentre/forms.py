from django import forms

class SingleTestForm(forms.Form):
    name = forms.CharField(label='Name', max_length=256)
    # date_of_birth = forms.DateField(label='Date of Birth')
    # get rid of age here
    age = forms.IntegerField(label='Age')
    phone_num = forms.CharField(label='Phone number', max_length=13)
    email = forms.EmailField(label='Email')
    addr = forms.CharField(label='Address', max_length=256)
    postcode = forms.CharField(label='Postcode', max_length=8)
    test_date = forms.DateTimeField(label='Date of Test (mm/dd/yyyy)')
    result = forms.BooleanField(label='Positive test?', required=False)