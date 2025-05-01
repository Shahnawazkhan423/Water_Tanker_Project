from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission

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
# -------------------- Supplier --------------------
class SupplierUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class SupplierUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    location = models.ForeignKey(LocationDetail, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        related_name='supplier_users',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='supplier_user_permissions',
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    objects = SupplierUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# -------------------- Driver --------------------
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
    user = models.ForeignKey(SupplierUser, on_delete=models.CASCADE)
    availability = models.ForeignKey(DriverAvailability, on_delete=models.SET_NULL, null=True, related_name='drivers')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

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
    driver = models.ForeignKey(DriverDetail, on_delete=models.CASCADE, null=True, blank=True)
    document = models.ForeignKey(WaterTankerDocument, on_delete=models.CASCADE,null=True, blank=True)

    CATEGORY_CHOICES = [
        ('DRINKING', 'Drinking Water'),
        ('NON_DRINKING', 'Non-Drinking Water'),
        ('BOTH', 'Drinking & Usage Water'),
    ]

    capacity = models.IntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    available = models.BooleanField(default=True)

    