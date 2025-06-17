from django import forms
from UserManagement.models import CustomUser
from Customer.models import LocationDetail
from Supplier.models import TankerDetail
from django.core.validators import RegexValidator

class UserDetailForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=True,
        validators=[RegexValidator(r'^[6-9]\d{9}$', 'Enter a valid 10-digit phone number')]
    )
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','phone_number','email','password','profile_image']
        widgets = {
            'password': forms.PasswordInput()
        }
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


class TankerDetailForm(forms.ModelForm):
    class Meta:
        model = TankerDetail
        fields = ['capacity','category']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        price_per_liter = {
                1000: 0.15,
                2000: 0.12,
                5000: 0.10,
                10000: 0.08
            }

        capacity_choices = []
        for capacity, label in TankerDetail.CAPACITY_CHOICES:
            price = capacity * price_per_liter.get(capacity, 0.10)
            label_with_price = f"{label} - ₹{price:.2f}"
            capacity_choices.append((capacity, label_with_price))

        self.fields['capacity'].choices = capacity_choices
class LocationDetailForm(forms.ModelForm):
    pincode = forms.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pincode')]
    )
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state', 'country','pincode']
