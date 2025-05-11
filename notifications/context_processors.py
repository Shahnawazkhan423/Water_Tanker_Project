# notifications/context_processors.py
from .utils import get_unread_notifications_count,get_recent_notifications

def notifications(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': get_unread_notifications_count(request.user),
            'recent_notifications': get_recent_notifications(request.user)
        }
    return {}