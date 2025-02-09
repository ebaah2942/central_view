from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('amenities/', views.amenity, name='amenities'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('update_booking/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]
