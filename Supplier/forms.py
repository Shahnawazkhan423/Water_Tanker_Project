from django import forms
from Supplier.models import LocationDetail,TankerDetail,WaterTankerDocument
from UserManagement.models import CustomUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import os

class SupplierRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=True,
        validators=[RegexValidator(r'^[6-9]\d{9}$', 'Enter a valid 10-digit phone number')]
    )
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


ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf']  
class WaterTankerForm(forms.ModelForm):

    water_tanker_name = forms.CharField(
        label="Tanker Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = WaterTankerDocument
        fields = [
            'profile_photo', 'driving_license', 'aadhar_card', 'pan_card',
            'registration_cert', 'vechicle_insurance', 'vechicle_permit'
        ]
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'driving_license': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'aadhar_card': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'pan_card': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'registration_cert': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'vechicle_insurance': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'vechicle_permit': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
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
        return self._clean_file_field('vechicle_insurance')

    def clean_vehicle_permit(self):
        return self._clean_file_field('vechicle_permit')

    def _clean_file_field(self, field_name):
        """
        Helper method to validate file extension for a given file field.
        """
        uploaded_file = self.cleaned_data.get(field_name)
        if uploaded_file:
            name, ext = os.path.splitext(uploaded_file.name)
            if ext.lower() not in ALLOWED_FILE_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type for {self.fields[field_name].label}. Only JPG, PNG, and PDF files are allowed."
                )
        return uploaded_file