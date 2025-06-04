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
                                    
    def __str__(self):
        return f"{self.address_line}, {self.city}"

class SupplierProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='supplier')
    is_available = models.BooleanField(default=True)
    location = models.ForeignKey(LocationDetail,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name}, {self.user.last_name}"
# -------------------- Driver --------------------
class DriverAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable')
    ]
    user = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='availabilities')
    availability_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unavailable')
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.status

class DriverDetail(models.Model):
    user = models.OneToOneField(SupplierProfile, on_delete=models.CASCADE)
    availability = models.ForeignKey(DriverAvailability, on_delete=models.SET_NULL, null=True, related_name='drivers')

    def __str__(self):
        return f"{self.user.user.first_name} {self.user.user.last_name}"

# -------------------- Water Tanker Document --------------------
class WaterTankerDocument(models.Model):
    water_tanker_name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    driving_license = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    aadhar_card = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    pan_card = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    registration_cert = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    vechicle_insurance = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    vechicle_permit = models.ImageField(upload_to="media/profile_image.jpg",null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
       return self.water_tanker_name
# -------------------- Tanker --------------------
class TankerDetail(models.Model):
    driver = models.ForeignKey('DriverDetail', on_delete=models.CASCADE, null=True, blank=True)
    document = models.ForeignKey('WaterTankerDocument', on_delete=models.CASCADE, null=True, blank=True)

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