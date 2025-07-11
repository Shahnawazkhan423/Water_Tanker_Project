from django.db import models
from UserManagement.models import CustomUser

# -------------------- Location --------------------
class LocationDetail(models.Model):
    address_line = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
                                    
    def __str__(self):
        return f"{self.address_line}, {self.city}"

class SupplierProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='supplier')
    is_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(LocationDetail,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name},{self.user.email}.{self.user.password}"
# -------------------- Driver --------------------
class DriverAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availabilities')
    availability_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unavailable')
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} {self.status}"

class DriverDetail(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    availability = models.ForeignKey(DriverAvailability, on_delete=models.CASCADE,related_name='supplier')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

# -------------------- Water Tanker Document --------------------
def upload_to(instance, filename):
    return f'media/water_tanker_documents/{filename}'

class WaterTankerDocument(models.Model):
    water_tanker_name = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    is_approved = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    profile_photo = models.ImageField(upload_to='tanker/profile/', blank=True, null=True)
    driving_license = models.FileField(upload_to='tanker/license/', blank=True, null=True)
    aadhar_card = models.FileField(upload_to='tanker/aadhar/', blank=True, null=True)
    pan_card = models.FileField(upload_to='tanker/pan/', blank=True, null=True)
    registration_cert = models.FileField(upload_to='tanker/rc/', blank=True, null=True)
    vehicle_insurance = models.FileField(upload_to='tanker/insurance/', blank=True, null=True)
    vehicle_permit = models.FileField(upload_to='tanker/permit/', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.water_tanker_name
# -------------------- Tanker --------------------
class TankerDetail(models.Model):
    driver = models.ForeignKey(DriverDetail, on_delete=models.CASCADE, null=True, blank=True)
    document = models.ForeignKey(WaterTankerDocument, on_delete=models.CASCADE, null=True, blank=True)

    CAPACITY_CHOICES = [
        (1000, '1000 liters'),
        (2000, '2000 liters'),
        (5000, '5000 liters'),
        (10000, '10000 liters'),
    ]

    CATEGORY_CHOICES = [
        ('DRINKING', 'Drinking Water'),
        ('NON_DRINKING', 'Non-Drinking Water'),
        ('BOTH', 'Drinking & Usage Water'),
    ]

    capacity = models.PositiveIntegerField(choices=CAPACITY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    available = models.BooleanField(default=True)

    @property
    def price_per_liter(self):
        if self.capacity == 1000:
            return 0.15
        elif self.capacity == 2000:
            return 0.12
        elif self.capacity == 5000:
            return 0.10
        elif self.capacity == 10000:
            return 0.08
        return 0.10
    
    def calculate_price(self):
        return self.capacity * self.price_per_liter

    def __str__(self):
        return f"Tanker ({self.capacity}L, {self.category}, Available: {self.available})"