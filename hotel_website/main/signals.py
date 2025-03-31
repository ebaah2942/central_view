from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, Inquiry, Notification

# Utility function to send emails
def send_notification_email(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )

# 1️⃣ Send Welcome Email After User Registers
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Only send email when a new user is created
        subject = "Welcome to Our Hotel!"
        message = f"Dear {instance.username},\n\nThank you for signing up!\n\nBest regards,\nHotel Team"
        send_notification_email(subject, message, instance.email)

# 2️⃣ Send Confirmation Email When a Booking is Made
@receiver(post_save, sender=Booking)
def send_booking_confirmation(sender, instance, created, **kwargs):
    if created:
        subject = "Your Booking is Confirmed!"
        message = f"Dear {instance.user.username},\n\nYour booking for {instance.room} is confirmed.\n\nCheck-in: {instance.check_in}\nCheck-out: {instance.check_out}\n\n Kindly call to confirm availability and make payment: +233 59 433 2382/+233 30 223 1759\nThank you for choosing us!"
        send_notification_email(subject, message, instance.user.email)

# 3️⃣ Notify Users When Admin Responds to an Inquiry
@receiver(post_save, sender=Inquiry)
def send_inquiry_response_notification(sender, instance, **kwargs):
    if instance.response:  # Only send email if a response is added
        subject = "Response to Your Inquiry"
        message = f"Dear {instance.user.username},\n\nOur team has responded to your inquiry: {instance.response}\n\nThank you!"
        send_notification_email(subject, message, instance.user.email)


ADMIN_EMAIL = "acvh@accracentralviewhotels.com"

# 1️⃣ Notify Admin When a New Booking is Made
@receiver(post_save, sender=Booking)
def notify_admin_new_booking(sender, instance, created, **kwargs):
    if created:
        subject = "New Booking Received"
        message = f"A new booking has been made by {instance.user.username}.\n\nRoom: {instance.room}\nCheck-in: {instance.check_in}\nCheck-out: {instance.check_out}\n\nPlease review it in the admin panel."
        send_notification_email(subject, message, ADMIN_EMAIL)

# 2️⃣ Notify Admin When a New Inquiry is Submitted
@receiver(post_save, sender=Inquiry)
def notify_admin_new_inquiry(sender, instance, created, **kwargs):
    if created:
        subject = "New Inquiry Received"
        message = f"A new inquiry has been submitted by {instance.user.username}.\n\nMessage: {instance.message}\n\nPlease review it in the admin panel."
        send_notification_email(subject, message, ADMIN_EMAIL)   



@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance, created, **kwargs):
    """
    Sends an email when a new notification is created.
    """
    if created:  # Only send email for new notifications
        send_mail(
            "New Notification from Accra Central View Hotel",
            f"Hello {instance.user.username},\n\n{instance.message}",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=False,
        )