from django.db import models
from Customer.models import Feedback, UserDetail  

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

class DriverDetail(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    availability = models.ForeignKey(DriverAvailability, on_delete=models.SET_NULL, null=True)
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, null=True)

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
    capacity = models.IntegerField()
    category = models.CharField(max_length=50)
    available = models.BooleanField(default=True)
