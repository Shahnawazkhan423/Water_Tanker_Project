from __future__ import absolute_import,unicode_literals 
from celery import shared_task 
from celery.utils.log import get_task_logger 
from django.core.mail import send_mail, BadHeaderError
from Water_Tanker_Project.settings import EMAIL_HOST_USER
from UserManagement.models import CustomUser
logger = get_task_logger(__name__)


@shared_task(name='Customer.tasks.send_email_task')
def send_email_task(to, subject, message):
    try:
        send_mail(subject,message,EMAIL_HOST_USER,[to],fail_silently=False)
    except BadHeaderError:
        logger.error("Invalid header in email.")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")

@shared_task(name='Customer.tasks.send_mail_every_day')
def send_mail_every_day():
    users = CustomUser.objects.all()
    for user in users:
        subject = f"Good Evening, {user.first_name}!"       
        message = f"""
            Good Evening {user.first_name},
                    
            We appreciate you choosing our service 😊

            Your Registered Email: {user.email}

            Regards,
            Water Tanker Team
        """
    try:
        send_mail(subject,message,EMAIL_HOST_USER,[user.email],fail_silently=False)
    except BadHeaderError:
        logger.error("Invalid header in email.")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
