from django.shortcuts import render, redirect
from . models import Room, Amenity, Booking, Inquiry, Notification, CustomUser, Inquiry
from django.contrib.auth.decorators import login_required, permission_required
from . forms import BookingForm, CustomUserCreationForm, CustomLoginForm, InquiryForm, ResponseForm, UserUpdateForm, ChangePasswordForm
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


# Create your views here.
def home(request):
    user_role = None
    room = Room.objects.first()
    if request.user.is_authenticated:
        user_role = request.user.role
    messages.info(request, "Check-in time: 12:00 PM | Check-out time: 12:00 PM(The folowing day) Please note that regardless of your check-in time, check-out time is required by 12:00 Noon.")
    return render(request, 'main/home.html', {'user_role': user_role , 'room': room})

def privacy_policy(request):
    return render(request, 'main/privacy.html')


def rooms(request):
    all_rooms = Room.objects.all().order_by('price')
    messages.info(request, "Check-in time: 12:00 PM | Check-out time: 12:00 PM(The folowing day) Please note that regardless of your check-in time, check-out time is required by 12:00 Noon.")
    return render(request, 'main/rooms.html' , {'rooms': all_rooms})

def amenity(request):
    all_amenities = Amenity.objects.all()

    return render(request, 'main/amenities.html' , {'amenities': all_amenities})



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
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found or you do not have permission to delete this booking")
        return redirect('booking_list')

    if request.method == 'POST':
        try:
            booking.delete()
            messages.success(request, "Booking deleted successfully")
            print(list(messages.get_messages(request)))
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
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')
            if room.name in ['King-Size', 'Double-Room'] and quantity > 8:
                messages.error(request, "You cannot book more than 8 King-size or Double rooms.")
            elif room.name == 'Single-Room' and quantity > 20:
                messages.error(request, "You cannot book more than 20 Single rooms.")            
            elif quantity > 0:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.room = room
                booking.save()
                messages.success(request, f'Booking successful for {quantity} {room.name}')
                return redirect('booking_list')
            else:
                messages.error(request, "Quantity must be greater than 0.")
    else:
        form = BookingForm()
    messages.info(request, "Check-in time: 12:00 PM | Check-out time: 12:00 PM(The folowing day) Please note that regardless of your check-in time, check-out time is required by 12:00 Noon.")
    return render(request, 'main/booking.html', {'room': room, 'form': form})


@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    room = booking.room  # Get the associated room

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')

            # Check quantity limits based on room type
            if room.name in ['King-Size', 'Double-Room'] and quantity > 8:
                messages.error(request, "You cannot book more than 8 King-size or Double rooms.")
            elif room.name == 'Single-Room' and quantity > 20:
                messages.error(request, "You cannot book more than 20 Single rooms.")
            elif quantity > 0:
                form.save()
                messages.success(request, "Your booking has been updated successfully.")
                return redirect('booking_list')  # Redirect to the booking list page
            else:
                messages.error(request, "Quantity must be greater than 0.")
    else:
        form = BookingForm(instance=booking)

    return render(request, 'main/update_booking.html', {'form': form, 'booking': booking})


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
        print("Notifications:", notifications)
    return render(request, 'main/receptionist_dashboard.html', {
        'user_role': user_role, 
        'inquiries': inquiries, 
        'users': users, 
        'notifications': notifications, 
        'bookings': booking})

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


@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active  # Toggle status
    user.save()
    messages.success(request, f"User {'unbanned' if user.is_active else 'banned'} successfully.")
    return redirect('reception_dashboard')




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

@login_required
def delete_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this inquiry.")
        return redirect('reception_dashboard')
    inquiry.delete()
    messages.success(request, "Inquiry deleted successfully!")
    return redirect('reception_dashboard')


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

@login_required
def new_notifications(request):
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to view archived notifications.")
        return redirect('reception_dashboard')

    archived_notifications = Notification.objects.filter(is_archived=True)
    return render(request, 'main/archived_notifications.html', {'archived_notifications': archived_notifications})

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


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()  # Count unread notifications
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if it's an AJAX request
        return JsonResponse({'unread_count': unread_count})
    return render(request, 'main/notifications_list.html', {'notifications': notifications, 'unread_count': unread_count})


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('notifications_list')



@login_required
def delete_notification(request, notification_id):
    notifications = get_object_or_404(Notification, id=notification_id) 
    if request.user.role.lower() not in ['manager', 'receptionist']:
        messages.error(request, "You do not have permission to delete this notification.")
        return redirect('reception_dashboard')
    notifications.delete()
    messages.success(request, "Notification deleted!")
    return redirect('reception_dashboard')


@login_required
def delete_guest_inquiry(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id, user=request.user)
    inquiry.delete()
    messages.success(request, "Inquiry deleted successfully!")
    return redirect('inquiry_list')


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



   

