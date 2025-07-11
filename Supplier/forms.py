from django import forms
from Supplier.models import LocationDetail,TankerDetail,WaterTankerDocument
from UserManagement.models import CustomUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import os
import re

class SupplierRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','phone_number','email','password','profile_image']
    first_name = forms.CharField(
        max_length=30,
        min_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_first_name',
            'placeholder': 'First Name',
            'pattern': '[A-Za-z\\s]+',
            'title': 'Only letters and spaces allowed.',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        min_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_last_name',
            'placeholder': 'Last Name',
            'pattern': '[A-Za-z\\s]+',
            'title': 'Only letters and spaces allowed.',
        })
    )
    phone_number = forms.CharField(
        label="Phone Number",
        min_length=10,
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'pattern': '[0-9]{10}',
            'title': 'Enter a 10-digit phone number',
            'id': 'id_phone_number'
        })
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'pattern': '^[a-zA-Z0-9._%+-]+@gmail\\.com$',
            'title': 'Only Gmail addresses allowed',
            'id': 'id_email'
        })
    )

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not re.match(r'^[0-9]{10}$', phone):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            raise forms.ValidationError("Only Gmail addresses are allowed.")
        return email
    
    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if not re.match(r'^[A-Za-z\s]+$', data):
            raise forms.ValidationError("First name can only contain letters and spaces.")
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if not re.match(r'^[A-Za-z\s]+$', data):
            raise forms.ValidationError("Last name can only contain letters and spaces.")
        return data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'supplier'  
        if commit:
            user.save()
        return user

class SupplierTankerDetailForm(forms.ModelForm):
    class Meta:
        model = TankerDetail
        fields = ['capacity', 'category']
        widgets = {
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'capacity': 'Capacity',
            'category': 'Category',
        }

class SupplierLocationDetailForm(forms.ModelForm):
    pincode = forms.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pincode')]
    )
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state', 'country','pincode']


ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']  
class WaterTankerForm(forms.ModelForm):

    water_tanker_name = forms.CharField(
        label="Tanker Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = WaterTankerDocument
        fields = [
            'water_tanker_name',
            'profile_photo', 'driving_license', 'aadhar_card', 'pan_card',
            'registration_cert', 'vehicle_insurance', 'vehicle_permit'
        ]
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'driving_license': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'aadhar_card': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'pan_card': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'registration_cert': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'vehicle_insurance': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'vehicle_permit': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    # Custom clean methods for each file field
    def clean_profile_photo(self):
        return self._clean_file_field('profile_photo')

    def clean_driving_license(self):
        return self._clean_file_field('driving_license')

    def clean_aadhar_card(self):
        return self._clean_file_field('aadhar_card')

    def clean_pan_card(self):
        return self._clean_file_field('pan_card')

    def clean_registration_cert(self):
        return self._clean_file_field('registration_cert')

    def clean_vehicle_insurance(self):
        return self._clean_file_field('vehicle_insurance')

    def clean_vehicle_permit(self):
        return self._clean_file_field('vehicle_permit')

    def _clean_file_field(self, field_name):
        """
        Helper method to validate file extension for a given file field.
        """
        uploaded_file = self.cleaned_data.get(field_name)
        if uploaded_file:
            name, ext = os.path.splitext(uploaded_file.name)
            if ext.lower() not in ALLOWED_FILE_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type for {self.fields[field_name].label}. Only JPG, PNG,files are allowed."
                )
        return uploaded_file