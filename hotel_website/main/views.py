from django.shortcuts import render, redirect
from . models import Room, Amenity, Booking
from django.contrib.auth.decorators import login_required, permission_required
from . forms import BookingForm, CustomUserCreationForm, CustomLoginForm
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
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

# Create your views here.
def home(request):
    return render(request, 'main/home.html')

def privacy_policy(request):
    return render(request, 'main/privacy.html')


def rooms(request):
    all_rooms = Room.objects.all().order_by('price')
    return render(request, 'main/rooms.html' , {'rooms': all_rooms})

def amenity(request):
    all_amenities = Amenity.objects.all()

    return render(request, 'main/amenities.html' , {'amenities': all_amenities})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'main/register.html', {'form': form, "hide_nav": True})
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form , "hide_nav": True})

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



@login_required
def booking_list(request):
    user = request.user
    name = user.username
    phone_number = user.phone_number
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for booking in bookings:
        booking.num_of_day = (booking.check_out - booking.check_in).days
        booking.total_price = booking.room.price * booking.num_of_day
        booking.grand_total = booking.total_price * booking.quantity
    return render(request, 'main/my_booking.html', {'bookings': bookings, 'name': name, 'phone_number': phone_number, 'page_obj': page_obj}) 


@login_required
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    available_rooms = Room.objects.all()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')
            if room.name in ['King-Size', 'Double-Room'] and quantity > 8:
                messages.error(request, "You cannot book more than 8 King-size or Double rooms.")
            elif room.name == 'Single-Room' and quantity > 20:
                messages.error(request, "You cannot book more than 20 Single rooms.")    
            elif quantity and quantity > 0:
                booking = form.save(commit=False)
                booking.user = request.user
                selected_room = request.POST.get('selected_room')
                booking.room = Room.objects.get(id=selected_room)
                booking.save()
                messages.success(request, f'Booking successful for {quantity} {room.name}')
                return redirect('booking_list')
            else:
                messages.error(request, "Quantity must be greater than 0.")
    else:
        form = BookingForm()
    return render(request, 'main/booking.html', {'room': room, 'form': form, 'available_rooms': available_rooms})

@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Your booking has been updated successfully.")
            return redirect('booking_list')  # Redirect to the booking list page
    else:
        form = BookingForm(instance=booking)

    return render(request, 'main/update_booking.html', {'form': form, 'booking': booking})

