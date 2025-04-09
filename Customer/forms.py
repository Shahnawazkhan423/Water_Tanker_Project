from django import forms
from Customer.models import UserDetail,LocationDetail
from Supplier.models import TankerDetail

class UserDetailForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['first_name','last_name','phone_number'] 

class TankerDetailForm(forms.ModelForm):
    class Meta:
        model = TankerDetail
        fields = ['capacity','category','driver']

class LocationDetailForm(forms.ModelForm):
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state', 'country']
