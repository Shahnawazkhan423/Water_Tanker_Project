from django.dispatch import receiver 
from .signals import order_canceled_by_customer
from .models import Notification
@receiver(order_canceled_by_customer)
def create_cancel_notification_for_supplier(sender, order_instance, customer_user, supplier_instance, **kwargs): 
    Notification.objects.create(
        customer=customer_user,
        supplier=supplier_instance,  
        message=f"Order ID {order_instance.id} has been cancelled by customer {customer_user.name}.",
        initiated_by='customer'
    )
