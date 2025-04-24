from django import forms
from Customer.models import CustomUser,LocationDetail
from Supplier.models import TankerDetail

class UserDetailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','phone_number','email','password','profile_image']
        widgets = {
            'password': forms.PasswordInput()
        } 

class TankerDetailForm(forms.ModelForm):
    class Meta:
        model = TankerDetail
        fields = ['capacity','category']

class LocationDetailForm(forms.ModelForm):
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state', 'country']
