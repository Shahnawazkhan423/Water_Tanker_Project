from django.db import models
from Customer.models import Feedback, UserDetail,OrderDetail  
from django.utils import timezone

class DriverAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable')
    ]
    availability_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.status

    
class DriverDetail(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    availability = models.ForeignKey(DriverAvailability, on_delete=models.SET_NULL, null=True)
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "

class WaterTankerDocument(models.Model):
    water_tanker_name = models.CharField(max_length=255)
    profile_photo = models.BinaryField()
    driving_license = models.BinaryField()
    aadhar_card = models.BinaryField()
    pan_card = models.BinaryField()
    registration_cert = models.BinaryField()
    vechicle_insurance = models.BinaryField()
    vechicle_permit = models.BinaryField()
    upload_date = models.DateTimeField(auto_now_add=True)

class TankerDetail(models.Model):
    driver = models.ForeignKey(DriverDetail, on_delete=models.CASCADE)
    document = models.ForeignKey(WaterTankerDocument, on_delete=models.CASCADE)
    tanker_name = models.CharField(max_length=50)
    CATEGORY_CHOICES = [
        ('DRINKING', 'Drinking Water'),
        ('NON_DRINKING', 'Non-Drinking Water'),
        ('BOTH', 'Drinking & Usage Water'),
    ]

    capacity = models.IntegerField()
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES)
    available = models.BooleanField(default=True)
    def __str__(self):
        return self.tanker_name 

class Earning(models.Model):
    supplier = models.ForeignKey('DriverDetail', on_delete=models.CASCADE, related_name='earnings')
    order = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    earning_date = models.DateField(default=timezone.now)
    payment_status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Earning #{self.id} - Supplier: {self.supplier} - ₹{self.amount}"
