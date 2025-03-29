from .models import Notification, Inquiry


def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {'unread_count': unread_count}



# context_processors.py

from .models import Inquiry

def unread_inquiries_count(request):
    if request.user.is_authenticated:
        unread_count = Inquiry.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {'inquiry_unread_count': unread_count}
