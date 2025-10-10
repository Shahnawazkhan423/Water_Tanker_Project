from django.dispatch import receiver 
from Customer.models import Notification
from .signals import order_accepted_by_supplier,order_canceled_by_supplier,order_delievery_by_supplier,order_on_the_way_by_supplier

@receiver(order_accepted_by_supplier)
def create_accepted_notification_for_customer(sender,supplier_user, customer_instance, **kwargs):
    Notification.objects.create(
        supplier=supplier_user,
        customer=customer_instance,
        message=f"Your Order Has Been Accepted By {supplier_user.user.first_name} {supplier_user.user.last_name}",
        initiated_by='supplier'
    )


@receiver(order_on_the_way_by_supplier)
def  create_on_the_away_notification_for_customer(sender,supplier_user, customer_instance, **kwargs):
    Notification.objects.create(
        supplier=supplier_user,
        customer=customer_instance,
        message=f"Your Order is on the Way! {supplier_user.user.first_name} {supplier_user.user.last_name} has started the Delivery.",
        initiated_by='supplier'
    )

@receiver(order_delievery_by_supplier)
def  create_delivery_notification_for_customer(sender,supplier_user, customer_instance, **kwargs):
    Notification.objects.create(
        supplier=supplier_user,
        customer=customer_instance,
        message=f"Your Order Has Been Delivered By {supplier_user.user.first_name} {supplier_user.user.last_name}.",
        initiated_by='supplier'
    )

@receiver(order_canceled_by_supplier)
def create_canceled_notification_for_customer(sender,supplier_user, customer_instance, **kwargs):
    Notification.objects.create(
        supplier=supplier_user,
        customer=customer_instance,
        message=f"Your Order Has Been Cancel By {supplier_user.user.first_name} {supplier_user.user.last_name}.",
        initiated_by='supplier'
    )