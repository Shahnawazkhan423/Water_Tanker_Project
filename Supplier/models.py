from django.db import models
from Customer.models import*
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
    availability = models.ForeignKey(DriverAvailability, on_delete=models.SET_NULL, null=True,related_name='drivers')
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "

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

