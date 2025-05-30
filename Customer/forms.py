from django import forms
from UserManagement.models import CustomUser
from Customer.models import LocationDetail
from Supplier.models import TankerDetail
class UserDetailForm(forms.ModelForm):
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
        
        capacity_choices = []
        for capacity, label in TankerDetail.CAPACITY_CHOICES:
            price = capacity * {
                1000: 0.15,
                2000: 0.12,
                5000: 0.10,
                10000: 0.08
            }.get(capacity, 0.10)
            capacity_choices.append((capacity, f"{label} - ₹{price:.2f}"))
        self.fields['capacity'].choices = capacity_choices

class LocationDetailForm(forms.ModelForm):
    class Meta:
        model = LocationDetail
        fields = ['address_line', 'street', 'landmark', 'city', 'state', 'country']
