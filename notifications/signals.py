# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from Supplier.models import TankerDetail  # or wherever your order model is
from notifications.models import Notification

@receiver(post_save, sender=TankerDetail)
def create_order_notification(sender, instance, created, **kwargs):
    if not created:  # Only for updates
        # You'll need to adjust this based on your actual models
        if instance.order_status_changed():
            user = instance.user  # The customer who placed the order
            
            if instance.order_status == 'Canceled':
                Notification.objects.create(
                    recipient=user,
                    sender=instance.driver.user if instance.driver else None,
                    message=f"Your order #{instance.id} has been canceled.",
                    notification_type='order_canceled',
                    order_id=instance.id
                )
            elif instance.order_status == 'On the Way':
                Notification.objects.create(
                    recipient=user,
                    sender=instance.driver.user if instance.driver else None,
                    message=f"Your order #{instance.id} is on the way.",
                    notification_type='order_on_way',
                    order_id=instance.id
                )
            elif instance.order_status == 'Delivered':
                Notification.objects.create(
                    recipient=user,
                    sender=instance.driver.user if instance.driver else None,
                    message=f"Your order #{instance.id} has been delivered.",
                    notification_type='order_completed',
                    order_id=instance.id
                )