from django import forms
from Supplier.models import LocationDetail,TankerDetail,WaterTankerDocument
from UserManagement.models import CustomUser

class SupplierRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','phone_number','email','password','profile_image']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'supplier'  
        if commit:
            user.save()
        return user

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
