# notifications/utils.py
from .models import Notification

def get_unread_notifications_count(user):
    return Notification.objects.filter(recipient=user, is_read=False).count()

def get_recent_notifications(user, limit=5):
    return Notification.objects.filter(recipient=user).order_by('-created_at')[:limit]