from django.urls import path
from . import views
from .views import update_profile, change_password
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
    path('reception-dashboard/', views.reception_dashboard, name='reception_dashboard'),
    path('staff-delete/<int:booking_id>/', views.staff_delete, name='staff_delete'),
    path('toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('inquiry/<int:inquiry_id>/respond/', views.respond_inquiry, name='respond_inquiry'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path("send-inquiry/", views.send_inquiry, name="send_inquiry"),
    path("respond-inquiry/<int:inquiry_id>/", views.respond_inquiry, name="respond_inquiry"),
    path("inquiry-list/", views.inquiry_list, name="inquiry_list"),
    # path("delete-inquiry/<int:inquiry_id>/", views.delete_inquiry, name="delete_inquiry"),
    path("archive-inquiry/<int:inquiry_id>/", views.archive_inquiry, name="archive_inquiry"),
    path("unarchive-inquiry/<int:inquiry_id>/", views.unarchive_inquiry, name="unarchive_inquiry"),
    path("admin-inquiry-delete/<int:inquiry_id>/", views.delete_inquiry, name="delete_inquiry"),
    path("delete-guest-inquiry/<int:inquiry_id>/", views.delete_guest_inquiry, name="delete_guest_inquiry"),
    # path("update-profile", views.update_profile, name="update_profile"),
    path("profile/", update_profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("archive-notification/<int:notification_id>/", views.archive_notification, name="archive_notification"),
    path("unarchive-notification/<int:notification_id>/", views.unarchive_notification, name="unarchive_notification"),
    path("delete-notification/<int:notification_id>/", views.delete_notification, name="delete_notification"),
    path('notifications/archived/', views.new_notifications, name='new_notifications'),
    path("notifcation-list/", views.notifications_list, name="notifications_list"),
    path('notifications/read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),

]
