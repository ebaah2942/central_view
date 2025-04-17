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

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'is_paid', 'amount_paid')
    list_filter = ('is_paid',)
    search_fields = ('user__username', 'room__name')
    fields = ('user', 'room', 'check_in', 'check_out', 'is_paid', 'amount_paid')

# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'room', 'check_in', 'check_out')
#     search_fields = ('user__username', 'room__name')
#     list_filter = ['check_in']    

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Room)
admin.site.register(Amenity)
admin.site.register(RoomCategory)
admin.site.register(Inquiry)
admin.site.register(Notification)


