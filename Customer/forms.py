from django import forms
from UserManagement.models import CustomUser
from Customer.models import LocationDetail
from Supplier.models import TankerDetail
from django.core.validators import RegexValidator
import re
class UserDetailForm(forms.ModelForm):
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
            'pattern': '^(?!.*(\d)\1{9})[6-9]\d{9}$',
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
        user.user_type = 'customer'  # Auto set
        if commit:
            user.save()
        return user     

class BookingUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number']

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'pattern': '[A-Za-z\\s]{2,30}',
                'required': True,
                'id': 'id_first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'pattern': '[A-Za-z\\s]{2,30}',
                'required': True,
                'id': 'id_last_name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'pattern': '[0-9]{10}',
                'required': True,
                'id': 'id_phone_number'
            }),
        }

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

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not re.match(r'^[0-9]{10}$', phone):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone
# -------------------- TANKER FORM --------------------
class TankerDetailForm(forms.ModelForm):
    class Meta:
        model = TankerDetail
        fields = ['capacity', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Price logic per liter
        price_per_liter = {
            1000: 0.15,
            2000: 0.12,
            5000: 0.10,
            10000: 0.08
        }

        # Update capacity label with price
        capacity_choices = []
        for capacity, label in TankerDetail.CAPACITY_CHOICES:
            price = capacity * price_per_liter.get(capacity, 0.10)
            label_with_price = f"{label} - ₹{price:.2f}"
            capacity_choices.append((capacity, label_with_price))

        self.fields['capacity'].choices = capacity_choices
        self.fields['capacity'].widget.attrs.update({
            'class': 'form-select',
            'id': 'id_capacity'
        })

        self.fields['category'].widget.attrs.update({
            'class': 'form-select',
            'id': 'id_category'
        })

# -------------------- LOCATION FORM --------------------
class LocationDetailForm(forms.ModelForm):
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state','pincode']

        widgets = {
            'address_line': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line',
                'pattern': '^[A-Za-z0-9\s,.-]{5,100}$',
                'required': True,
                'id': 'id_address_line'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street',
                'pattern': '^[A-Za-z\s]{3,50}$',
                'required': True,
                'id': 'id_street'
            }),
            'landmark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Landmark (optional)',
                'pattern': '^[A-Za-z0-9\s,.-]{0,100}$',
                'id': 'id_landmark'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'pattern': '^[A-Za-z\s]{2,50}$',
                'required': True,
                'id': 'id_city'
            }),
            'state': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_state'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pincode',
                'pattern': '^(?!([0-9])\1{5})[0-9]{6}$',
                'required': True,
                'id': 'id_pincode'
            }),
        }
