from django.contrib import admin
from .models import Room, Amenity, Booking, CustomUser, RoomCategory, Inquiry, Notification
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'phone_number', 'address', 'first_name', 'last_name', 'role', 'wants_emails')
    list_filter = ('is_staff', 'is_active','wants_emails')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'role', 'wants_emails')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'phone_number', 'address', 'first_name', 'last_name', 'role', 'wants_emails'),
        }),
    )

from django.utils.html import format_html
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'room_image')

    def room_image(self, obj):
        if obj.room and obj.room.image:
            return format_html('<img src="{}" style="height:50px;">', obj.room.image.url)
        return "No Image"
    room_image.short_description = "Room Image"


   

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Room)
admin.site.register(Amenity)
admin.site.register(RoomCategory)
admin.site.register(Inquiry)
admin.site.register(Notification)


