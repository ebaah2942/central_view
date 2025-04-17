from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Receptionist', 'Receptionist'),
        ('Guest', 'Guest')
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Guest')
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    wants_emails = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class RoomCategory(models.Model):
    CATEGORY_CHOICES = [
        ('King-size Room', 'King-size Room'),
        ('Double Room', 'Double Room'),
        ('Single Room', 'Single Room'),
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    total_rooms = models.PositiveIntegerField(default=0)
    available_rooms = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.get_category_display()}"


class Room(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    capacity = models.IntegerField(default=1)
    types = models.ForeignKey(RoomCategory, on_delete=models.CASCADE)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.types}"   



class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, null=True, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    quantity = models.PositiveIntegerField(default=1)
    is_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    receipt_sent = models.BooleanField(default=False)
    is_checked_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.room.price * self.quantity


    def __str__(self):
        return f"{self.user.username} - {self.check_in} to {self.check_out} ({self.category.category})" 

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name       


class Inquiry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    is_unarchived = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Inquiry from {self.user.username} - {'Resolved' if self.is_resolved else 'Pending'}"
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_unarchived = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    

    def __str__(self):
        return self.message[:50]