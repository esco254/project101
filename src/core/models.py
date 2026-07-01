import uuid
from django.db import models
from django.contrib.auth.models import User

class HotelRoom(models.Model):
    ROOM_CATEGORIES = [
        ('STANDARD', 'Standard'),
        ('DELUXE', 'Deluxe'),
        ('FAMILY', 'Family'),
        ('SINGLE', 'Single'),
        ('PRESIDENTIAL', 'Presidential'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_CATEGORIES, default='STANDARD')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_cleaned = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"


class GuestProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"


class Booking(models.Model):
    guest_profile = models.ForeignKey(GuestProfile, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)
    
    checkin_date = models.DateTimeField()
    days_booked = models.IntegerField(default=1)
    days_spent = models.IntegerField(default=0)
    
    is_payment_verified = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    verification_code = models.CharField(max_length=12, blank=True, null=True)
    digital_access_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Booking for {self.guest_name} - Room {self.room_number}"