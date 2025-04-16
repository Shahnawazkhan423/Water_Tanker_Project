from django.db import models

# Create your models here.
class LocationDetail(models.Model): 
    address_line = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

class UserDetail(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    passwords = models.CharField(max_length=255, unique=True) 
    location = models.ForeignKey(LocationDetail, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    rating_value = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    feedback_date = models.DateTimeField(auto_now_add=True)
    feedback_comment = models.TextField(blank=True)
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    def __str__(self):
        return self.feedback_comment

class OrderDetail(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled')
    ]
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    driver = models.ForeignKey('Supplier.DriverDetail', on_delete=models.SET_NULL, null=True)
    tanker = models.ForeignKey('Supplier.TankerDetail', on_delete=models.SET_NULL, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    delivery_date = models.DateTimeField(null=True, blank=True)
    Location = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "

    

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'Paypal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    order = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    