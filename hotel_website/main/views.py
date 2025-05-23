from django.shortcuts import render, redirect
from . models import Room, Amenity, Booking, Inquiry, Review, Notification, CustomUser, Inquiry, RoomCategory
from django.contrib.auth.decorators import login_required, permission_required
from . forms import BookingForm, CustomUserCreationForm, CustomLoginForm, InquiryForm, ResponseForm, UserUpdateForm, ChangePasswordForm, EmailPreferenceForm, ReviewForm 
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import timedelta
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import weasyprint
from django.core.mail import EmailMessage
from weasyprint import HTML
from io import BytesIO   
from django.utils.timezone import now
from django.db import models
from django.db.models import Sum
from django.db.models import Avg
from datetime import datetime



# Create your views here.
def home(request):
    rooms = Room.objects.all().order_by('price')
    user_role = None
    room = Room.objects.first()
    top_reviews = (
        Review.objects.select_related('room', 'user')
        .order_by('-rating', '-created_at')[:3]
    )
    if request.user.is_authenticated:
        user_role = request.user.role
    messages.info(request, "Check-in time: 12:00 PM | Check-out time: 12:00 PM(The folowing day) Please note that regardless of your check-in time, check-out time is required by 12:00 Noon.")
    return render(request, 'main/home.html', {'user_role': user_role , 'room': room, 'top_reviews': top_reviews, 'rooms': rooms})

def privacy_policy(request):
    
    return render(request, 'main/privacy.html')



def rooms(request):
    all_rooms = Room.objects.select_related('types').order_by('price')
    all_categories = RoomCategory.objects.all()
    reviews = Review.objects.filter(room=all_rooms [0])
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    today = now().date()
    bookings_today = Booking.objects.filter(created_at__date=today).count()

    # Calculate available_rooms for each category
    for category in all_categories:
        total = category.total_rooms
        booked = Booking.objects.filter(category=category, is_checked_out=False).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        category.available_rooms = max(total - booked, 0)

    for room in all_rooms:
        room.average_rating = room.review_set.aggregate(avg=Avg('rating'))['avg'] or 0

    # Calculate available_rooms for each room
    for room in all_rooms:
        category = room.types
        total = category.total_rooms
        booked = Booking.objects.filter(category=category, is_checked_out=False).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        room.available_rooms = max(total - booked, 0)

    messages.info(request, "Check-in time: 12:00 PM | Check-out time: 12:00 PM (The following day). Regardless of check-in time, check-out is required by 12:00 Noon.")
    return render(request, 'main/rooms.html', {
        'rooms': all_rooms,
        'types': all_categories,
        'bookings_today': bookings_today,
        'average_rating': round(average_rating, 1) if average_rating else "No ratings yet",
        'reviews': reviews

    })




def amenity(request):
    all_amenities = Amenity.objects.all()

    return render(request, 'main/amenities.html' , {'amenities': all_amenities})


# View to send verification email
def send_verification_email(request, user):
    """
    Sends a verification email to the user with a unique activation link.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    link = f"http://{domain}/activate/{uid}/{token}/"

    subject = "Verify Your Email - Accra Central View Hotel"
    message = render_to_string('main/email_verification.html', {'user': user, 'link': link})
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

# View to unsubscribe from email notifications
def unsubscribe_view(request, uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
        user.wants_emails = False
        user.save()
        return render(request, 'main/unsubscribe_success.html', {'user': user})
    except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
        messages.error(request, "Invalid unsubscribe link.")
        return render(request, 'main/unsubscribe_invalid.html')

# View to generate and download PDF receipt
def generate_receipt_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    template = get_template('main/receipt_pdf.html')
    html = template.render({'booking': booking})

    # Check if user wants to download
    if 'download' in request.GET:
        pdf_file = weasyprint.HTML(string=html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{booking.id}.pdf"'
        return response

    # Just render the HTML in browser
    return HttpResponse(html)

# Function to send receipt email
def email_receipt(user, booking):
    # Render the receipt template to HTML
    html_string = render_to_string('main/receipt_pdf.html', {'booking': booking})
    
    # Generate PDF in memory
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)

    # Create the email
    subject = "Your Booking Receipt - Accra Central View Hotel"
    body = f"Hello {user.username},\n\nAttached is your receipt for your recent booking.\n\nThank you for choosing us!"

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email='acvh@accracentralviewhotels.com',
        to=[user.email],
    )

    # Attach PDF
    email.attach(f"receipt_{booking.invoice_number or booking.id}.pdf", pdf_file.read(), 'application/pdf')

    # Send it
    email.send(fail_silently=False)



# Function to send email
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


# View to activate account
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been verified. You can now log in.")
        return redirect("login")
    else:
        messages.error(request, "Invalid or expired activation link.")
        return redirect("register")

# View to register
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Prevent login until email is verified
            user.save()

            send_verification_email(request, user)

            messages.success(request, "Account created successfully. Please check your email to verify your account.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed")
    
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'main/register.html', {'form': form, "hide_nav": True})


# View to login
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully")
                return redirect('home')
            else:
                messages.error(request, "Invalid login credentials")
                return render(request, 'main/login.html', {'form': form})
        else:
            messages.error(request, "Invalid login credentials")
            return render(request, 'main/login.html', {'form': form, "hide_nav": True})
    else:
        form = CustomLoginForm()
        return render(request, 'main/login.html', {'form': form, "hide_nav": True})



    # user booking delete view
@login_required
def delete_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        category = booking.room.types
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found or you do not have permission to delete this booking")
        return redirect('booking_list')

    if request.method == 'POST':
        try:
            category.available_rooms += booking.quantity
            category.save()
            booking.delete()
            messages.success(request, "Booking deleted successfully")
            return redirect('booking_list')
        except Exception as e:
            messages.error(request, f"Error deleting booking: {str(e)}")
            return redirect('booking_list')
    else:
        return render(request, 'main/delete_booking.html', {'booking': booking})    


# viewing all the booked rooms
@login_required
def booking_list(request):
    user = request.user
    name = user.username
    phone_number = user.phone_number
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for booking in bookings:
        booking.num_of_day = (booking.check_out - booking.check_in).days
        booking.total_price = booking.room.price * booking.num_of_day
        booking.grand_total = booking.total_price * booking.quantity
    return render(request, 'main/my_booking.html', {'bookings': bookings, 'name': name, 'phone_number': phone_number, 'page_obj': page_obj}) 


# all inquires
@login_required
def inquiry_list(request):
    inquiries = Inquiry.objects.filter(user=request.user).order_by('-created_at')
    unread_count = inquiries.filter(is_read=False).count() 
    return render(request, 'main/user_inquiries.html', {'inquiries': inquiries, 'unread_count': unread_count}) 



@login_required
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    quantity_range = range(1, room.types.available_rooms + 1)
    category = room.types 

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')

            # Total booked so far for this category
            total_booked = Booking.objects.filter(category=category).aggregate(total=Sum('quantity'))['total'] or 0
            available_rooms = category.total_rooms - total_booked

            if quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
           

            elif quantity > available_rooms:
                messages.error(request, f"Only {available_rooms} rooms available for {category.category}.")
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.room = room
                booking.category = category
                booking.save()
                
                messages.success(request, f'Booking successful for {quantity} {room.name}(s)')
                return redirect('booking_list')
    else:
        form = BookingForm()

    messages.info(request, "Check-in time: 12:00 PM | Check-out time: 12:00 PM(The folowing day) Please note that regardless of your check-in time, check-out time is required by 12:00 Noon.")
    return render(request, 'main/booking.html', {
        'room': room,
        'form': form,
        'quantity_range': quantity_range,
        'today': now().date().isoformat(),
    })



@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    room = booking.room
    category = room.types

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            new_quantity = form.cleaned_data.get('quantity')
            old_quantity = booking.quantity

            # Total booked excluding current booking
            total_booked_excluding_current = Booking.objects.filter(category=category).exclude(id=booking.id).aggregate(models.Sum('quantity'))['quantity__sum'] or 0
            available_rooms = category.total_rooms - total_booked_excluding_current

            if new_quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
            elif new_quantity > available_rooms:
                messages.error(request, f"Only {available_rooms} rooms available for {category.category}.")
            else:
                updated_booking = form.save(commit=False)
                updated_booking.user = request.user
                updated_booking.room = room
                updated_booking.category = category
                updated_booking.save()

                messages.success(request, "Your booking has been updated successfully.")
                return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'main/update_booking.html', {
        'form': form,
        'booking': booking
    })



# administrative page
@login_required
def reception_dashboard(request):
    user_role = request.user.role.lower()
    if user_role not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home') 
    booking = Booking.objects.select_related('user', 'room').all().order_by('-created_at')
    inquiries = Inquiry.objects.filter(is_archived=False).order_by('-created_at')
    users = CustomUser.objects.all()
    notifications = Notification.objects.all()
    if request.method == "POST":
        # Handle sending notifications
        user_id = request.POST.get("user_id")
        message = request.POST.get("message")
        if user_id and message:
            user = get_object_or_404(CustomUser, id=user_id)
            Notification.objects.create(user=user, message=message)
            messages.success(request, "Notification sent successfully.")
            return redirect('reception_dashboard')
        # print("Notifications:", notifications)
    return render(request, 'main/receptionist_dashboard.html', {
        'user_role': user_role, 
        'inquiries': inquiries, 
        'users': users, 
        'notifications': notifications, 
        'bookings': booking})

# view to send an inquiry
@login_required
def send_inquiry(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user  # Assign logged-in user
            inquiry.save()
            messages.success(request, "Your inquiry has been sent!")
            return redirect('home')  # Redirect to home or another page
    else:
        form = InquiryForm()
    
    return render(request, "main/send_inquiry.html", {"form": form})

# view to respond to an inquiry
@login_required
def respond_inquiry(request, inquiry_id):
    user_role = request.user.role.lower()
    if user_role not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to respond to inquiries.")
        return redirect('home')

    inquiry = get_object_or_404(Inquiry, id=inquiry_id)

    if request.method == "POST":
        form = ResponseForm(request.POST, instance=inquiry)  # ✅ Use instance to update inquiry directly
        if form.is_valid():
            form.save()
            messages.success(request, f"Inquiry from {inquiry.user.username} has been responded to.")
            return redirect('reception_dashboard')  # ✅ Redirect to admin dashboard

    else:
        form = ResponseForm(instance=inquiry)  # ✅ Pre-fill form with existing inquiry data

    return render(request, 'main/respond_inquiry.html', {'inquiry': inquiry, 'form': form})

# view to toggle user status
@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active  # Toggle status
    user.save()
    messages.success(request, f"User {'unbanned' if user.is_active else 'banned'} successfully.")
    return redirect('reception_dashboard')



# view to send a notification
@login_required
def send_notification(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        message = request.POST.get("message")
        
        
        if user_id and message:
            user = get_object_or_404(CustomUser, id=user_id)
            
            # Save notification in the database
            try:
                Notification.objects.create(user=user, message=message)
            except Exception as e:
                messages.error(request, "Failed to save notification in database.")
                return redirect('reception_dashboard')

            # Send real-time notification via WebSockets
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{user.id}",  # Send to specific user group
                    {"type": "send_notification", "message": message},
                )
            except Exception as e:
                messages.error(request, "Failed to send notification via WebSockets.")
                return redirect('reception_dashboard')

            messages.success(request, "Notification sent successfully.")
    
    return redirect('reception_dashboard')

# view to delete a booking by manager
@login_required
def staff_delete(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        if request.user.role.lower() != 'manager':
            return HttpResponseForbidden("You do not have permission to delete a booking.")
        booking.delete()
        messages.success(request, "Booking deleted successfully.")
        return redirect('reception_dashboard')
    else:
        return HttpResponseForbidden("Invalid request method.")

# view to respond to an inquiry
@login_required
def respond_inquiry(request, inquiry_id):
    user_role = request.user.role.lower()
    if user_role not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to respond to inquiries.")
        return redirect('home')

    inquiry = get_object_or_404(Inquiry, id=inquiry_id)

    if request.method == "POST":
        form = ResponseForm(request.POST)
        if form.is_valid():
            inquiry.response = form.cleaned_data['response']
            inquiry.is_resolved = True
            inquiry.save()
            messages.success(request, "Inquiry responded successfully!")
            return redirect('reception_dashboard')

    else:
        form = ResponseForm()

    return render(request, 'main/respond_inquiry.html', {'inquiry': inquiry, 'form': form})


# view to archive an inquiry
@login_required
def archive_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this inquiry.")
        return redirect('reception_dashboard')
    inquiry.is_archived = True
    inquiry.save()
    messages.success(request, "Inquiry archived!")
    return redirect('reception_dashboard')

# view to unarchive an inquiry
@login_required
def unarchive_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this inquiry.")
        return redirect('reception_dashboard')
    inquiry.is_archived = False
    inquiry.save()
    messages.success(request, "Inquiry unarchived!")
    return redirect('reception_dashboard')

# view to delete an inquiry
@login_required
def delete_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this inquiry.")
        return redirect('reception_dashboard')
    inquiry.delete()
    messages.success(request, "Inquiry deleted successfully!")
    return redirect('reception_dashboard')

# view to archive a notification
@login_required
def archive_notification(request, notification_id):
    notifications = get_object_or_404(Notification, id=notification_id) 
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this notification.")
        return redirect('reception_dashboard')
    notifications.is_archived = True
    notifications.save()
    messages.success(request, "Notification archived!")
    return redirect('reception_dashboard')

# view to create a notification
@login_required
def new_notifications(request):
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to view archived notifications.")
        return redirect('reception_dashboard')

    archived_notifications = Notification.objects.filter(is_archived=True)
    return render(request, 'main/archived_notifications.html', {'archived_notifications': archived_notifications})

# view to unarchive a notification
@login_required
def unarchive_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to unarchive notifications.")
        return redirect('reception_dashboard')

    notification.is_archived = False
    notification.save()
    messages.success(request, "Notification unarchived!")
    return redirect('reception_dashboard')

# view to list notifications
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()  # Count unread notifications
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if it's an AJAX request
        return JsonResponse({'unread_count': unread_count})
    return render(request, 'main/notifications_list.html', {'notifications': notifications, 'unread_count': unread_count})

# view to mark a notification as read
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('notifications_list')


# view to delete a notification
@login_required
def delete_notification(request, notification_id):
    notifications = get_object_or_404(Notification, id=notification_id) 
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this notification.")
        return redirect('reception_dashboard')
    notifications.delete()
    messages.success(request, "Notification deleted!")
    return redirect('reception_dashboard')

# view to delete a guest inquiry
@login_required
def delete_guest_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id, user=request.user)
    inquiry.delete()
    messages.success(request, "Inquiry deleted successfully!")
    return redirect('inquiry_list')

# view to update profile
@login_required
def update_profile(request):
    user = request.user
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=user)
    return render(request, "main/profile_update.html", {"form": form})

# view to change password
@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents logout
            messages.success(request, "Password updated successfully!")
            return redirect("profile")
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "main/change_password.html", {"form": form})


@login_required
def manage_email_preferences(request):
    user = request.user
    form = EmailPreferenceForm(request.POST or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'main/preferences_updated.html')  # optional success page

    return render(request, 'main/manage_email_preferences.html', {'form': form})



@login_required
def checkout_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room
    category = room.types if room else None

    if not booking.is_checked_out:
        booking.is_checked_out = True
        booking.save()

        if category:
            category.available_rooms += 1
            category.save()
            messages.success(request, f"{room.name} successfully checked out.")
        else:
            messages.warning(request, "Checkout recorded, but no room category found to update availability.")
    else:
        messages.info(request, "This booking has already been checked out.")

    return redirect('booking_list')



@login_required
def leave_review(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Check if user has booked the room
    has_booked = Booking.objects.filter(user=request.user, room=room).exists()

    if not has_booked:
        messages.error(request, "You can only review rooms you've booked.")
        return redirect('rooms')

    if Review.objects.filter(user=request.user, room=room).exists():
        messages.warning(request, "You've already reviewed this room.")
        return redirect('room_detail', room_id=room.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.room = room
            review.save()
            messages.success(request, "Review submitted.")
            return redirect('room_detail', room_id=room.id)
    else:
        form = ReviewForm()

    return render(request, 'main/leave_review.html', {'form': form, 'room': room})


def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    reviews = room.review_set.all()  # or use related_name='reviews' if set
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    return render(request, 'main/room_detail.html', {
        'room': room,
        'reviews': reviews,
        'average_rating': average_rating or 0,
    })





def delete_review(request, room_id, review_id):
    review = get_object_or_404(Review, id=review_id, room__id=room_id)

    if request.user == review.user:
        review.delete()
        messages.success(request, "Review deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this review.")
    
    return redirect('room_detail', room_id=room_id)



@login_required
def update_review(request, room_id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user, room_id=room_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully.")
            return redirect('room_detail', room_id=room_id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'main/update_review.html', {'form': form, 'review': review})
