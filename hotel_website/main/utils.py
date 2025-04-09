from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site

def send_notification_email(request, user, subject, template, context):
    if not user.wants_emails:
        return  # Respect the user's preference

    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    unsubscribe_link = f"http://{domain}/unsubscribe/{uid}/"

    context['unsubscribe_link'] = unsubscribe_link

    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'acvh@accracentralviewhotels.com',
        [user.email],
        html_message=html_message,
        fail_silently=False
    )




def send_notification_email(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )