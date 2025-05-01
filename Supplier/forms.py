from django import forms
from Supplier.models import *

class SupplierDetailForm(forms.ModelForm):
    class Meta:
        model = SupplierUser
        fields = ['first_name','last_name','phone_number','email','password','profile_image']
        widgets = {
            'password': forms.PasswordInput()
        } 

class SupplierTankerDetailForm(forms.ModelForm):
    class Meta:
        model = TankerDetail
        fields = ['capacity','category']

class SupplierLocationDetailForm(forms.ModelForm):
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state', 'country']
        
class WaterTankerForm(forms.ModelForm):
    class Meta:
        model = WaterTankerDocument
        fields = [
            'water_tanker_name', 'profile_photo', 'driving_license', 'aadhar_card', 
            'pan_card', 'registration_cert', 'vechicle_insurance', 'vechicle_permit', 
        ]
