from django.core.mail import send_mail 
from django.conf import settings
from django.contrib import messages

def send_forgot_password_mail(request, email, token):
    subject = "Your Password Reset Link"
    reset_link = f"http://127.0.0.1:8000/Customer/reset-password/{token}/"
    message = f"Hi,\n\nClick on the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, please ignore this email."

    email_from = settings.EMAIL_HOST_USER  
    recipient_list = [email]

    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        messages.success(request, "Reset password email sent successfully.")
        return True
    except Exception as e:
        print("Email sending failed:", e)
        messages.error(request, "We couldn't send the email.")
        return False
