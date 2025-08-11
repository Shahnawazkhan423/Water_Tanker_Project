from django.db import models
from Supplier.models import DriverDetail,TankerDetail,SupplierProfile
from UserManagement.models import CustomUser

# Create your models here.
class LocationDetail(models.Model): 
    address_line = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255,default="India")
    pincode = models.CharField(max_length=6,blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.address_line}, {self.city}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='customer')
    email = models.EmailField(unique=True)
    forgot_password_token = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(LocationDetail,on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        # Auto-fill email from CustomUser
        if self.user:
            self.email = self.user.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    # -------------------- Orders --------------------
class OrderDetail(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    driver = models.ForeignKey(DriverDetail, on_delete=models.SET_NULL, null=True)
    tanker = models.ForeignKey(TankerDetail, on_delete=models.SET_NULL, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    delivery_date = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(LocationDetail, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # Quantity in liters
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)  # Price based on quantity

    def __str__(self):
        return f"Order #{self.id} - {self.user.first_name}"

# -------------------- Payment --------------------
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'Paypal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash')
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled')
    ]
    order = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Payment of {self.amount} for Order {self.order.id}"


class Notification(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    initiated_by = models.CharField(max_length=10, choices=(('customer', 'Customer'), ('supplier', 'Supplier')), default='customer')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.supplier.user.first_name} to {self.customer.first_name}"