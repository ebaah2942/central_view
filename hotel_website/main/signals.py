from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CustomUser, LoginRecord
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from .models import Booking, Inquiry, Notification
from django.db.models.signals import pre_save
import uuid
from .views import email_receipt
from django.db.models.signals import post_delete
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.signals import user_logged_in
from django.core.mail import EmailMessage
from django.utils import timezone



# Utility function to send emails

def send_notification_email(subject, message, recipient_email, request=None):
    user = CustomUser.objects.filter(email=recipient_email).first()
    if user and user.wants_emails:

        unsubscribe_link = ""
        if request:
            domain = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            unsubscribe_link = f"https://{domain}/unsubscribe/{uid}/"

        # Build full message with optional unsubscribe link
        full_message = f"{message}\n\nIf you no longer want to receive these emails, you can unsubscribe here: {unsubscribe_link}" if unsubscribe_link else message

        send_mail(
            subject,
            strip_tags(full_message),
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in) 
def handle_login(sender, request, user, **kwargs):
    login_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    session_key = request.session.session_key
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip = get_client_ip(request)     
    
    existing =LoginRecord.objects.filter(user=user, session_key=session_key).first()
    if not existing:
        context = {
            'user': user,
            'session_key': session_key,
            'ip_address': ip,
            'user_agent': user_agent,
            'login_time': login_time,
        }
        html_message = render_to_string("main/login_record.html", context)
        email = EmailMessage(
            subject="Login Record",
            body=html_message,
            from_email="acvh@accracentralviewhotels.com",
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        LoginRecord.objects.create(user=user, session_key=session_key, ip_address=ip, user_agent=user_agent, timestamp=login_time)





# 1️⃣ Send Welcome Email After User Registers
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Only send email when a new user is created
        subject = "Welcome to Accra Central View Hotel!"
        message = f"Dear {instance.username},\n\nThank you for signing up!\n\nBest regards,\nAccra Central View Hotel"
        send_notification_email(subject, message, instance.email)

# 2️⃣ Send Confirmation Email When a Booking is Made
@receiver(post_save, sender=Booking)
def send_booking_confirmation(sender, instance, created, **kwargs):
    if created:
        subject = "Your Booking is Confirmed!"
        to_email = instance.user.email
        from_email = "acvh@accracentralviewhotels.com"

        context = {
            'user': instance.user,
            'booking': instance,
        }

        html_content = render_to_string("main/booking_confirmation.html", context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()


# 3️⃣ Notify Users When Admin Responds to an Inquiry
@receiver(post_save, sender=Inquiry)
def send_inquiry_response_notification(sender, instance, **kwargs):
    if instance.response:  # Only send email if a response is added
        subject = "Response to Your Inquiry"
        message = f"Dear {instance.user.username},\n\nThe hotel has responded to your inquiry: {instance.response}\n\nThank you!"
        send_notification_email(subject, message, instance.user.email)


ADMIN_EMAIL = "acvh@accracentralviewhotels.com"

# 1️⃣ Notify Admin When a New Booking is Made
@receiver(post_save, sender=Booking)
def notify_admin_new_booking(sender, instance, created, **kwargs):
    if created:
        subject = "New Booking Received"
        message = f"A new booking has been made by {instance.user.first_name}.\n\nRoom: {instance.room}\n Contact: {instance.user.phone_number}\nQuantity: {instance.quantity}\nRoom Type: {instance.room.types.category}\nCheck-in: {instance.check_in}\nCheck-out: {instance.check_out}\n\nPlease review it in the admin panel."
        send_notification_email(subject, message, ADMIN_EMAIL)

# 2️⃣ Notify Admin When a New Inquiry is Submitted
@receiver(post_save, sender=Inquiry)
def notify_admin_new_inquiry(sender, instance, created, **kwargs):
    if created:
        subject = "New Inquiry Received"
        message = f"A new inquiry has been submitted by {instance.user.username}.\n\nMessage: {instance.message}\n\nPlease review it in the admin panel."
        send_notification_email(subject, message, ADMIN_EMAIL)   

# 3️⃣ Notify Users When a New Notification is Created
@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance, created, **kwargs):
    """
    Sends an email when a new notification is created.
    Includes unsubscribe link if the user prefers emails.
    """
    if created and instance.user.wants_emails:
        user = instance.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Safely get the domain
        try:
            domain = get_current_site(None).domain
        except:
            domain = 'accracentralviewhotels.com'  # fallback domain
       
        manage_link = f"https://{domain}/preferences/email/"

        # unsubscribe_link = f"http://{domain}/unsubscribe/{uid}/"

        # Build the message with unsubscribe
        full_message = (
            f"Hello {user.username},\n\n"
            f"{instance.message}\n\n"
            f"If you want to update your email settings, visit: {manage_link}"

            # f"If you no longer want to receive these emails, you can unsubscribe here:\n{unsubscribe_link}"
        )

        send_mail(
            "New Notification from Accra Central View Hotel",
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

# 4️⃣ Generate Invoice Number
@receiver(pre_save, sender=Booking)
def generate_invoice_number(sender, instance, **kwargs):
    if instance.is_paid and not instance.invoice_number:
        instance.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"  

# 5️⃣ Send Email Receipt
@receiver(post_save, sender=Booking)
def send_receipt_email(sender, instance, **kwargs):
    if instance.is_paid and not instance.receipt_sent:
        email_receipt(instance.user, instance)
        instance.receipt_sent = True
        instance.save()        
              

@receiver(post_delete, sender=Booking)
def restore_available_room(sender, instance, **kwargs):
    # Only increase availability if check-out is in the past
    if instance.check_out and instance.check_out <= now().date():
        category = instance.room.types
        category.available_rooms += 1
        category.save()              




