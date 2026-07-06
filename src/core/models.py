import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('receptionist', 'Receptionist'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone_number = models.CharField(max_length=10, blank=True)
    department = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'


class GuestProfile(models.Model):
    user_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, default="")
    phone = models.CharField(max_length=15, default="")

    def __str__(self):
        return self.user_name


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single Room'),
        ('standard', 'Standard Room'),
        ('family', 'Family Room'),
        ('suite', 'Presidential Suite'),
        ('deluxe', 'Deluxe Room'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"


class Booking(models.Model):
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)

    check_in = models.DateField()
    check_out = models.DateField()
    days_spent = models.IntegerField(default=0)

    is_payment_verified = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    verification_code = models.CharField(max_length=12, blank=True, null=True)
    digital_access_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        guest_display = self.guest.user_name if self.guest else "Unassigned"
        return f"{guest_display} ({self.check_in})"

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            self.days_spent = (self.check_out - self.check_in).days

        if self.is_payment_verified and not self.verification_code:
            self.verification_code = str(uuid.uuid4().hex[:12]).upper()
            self.send_confirmation_email_with_qr()

        if self.is_refunded and self.refund_amount == 0.00 and self.room:
            self.refund_amount = self.room.price_per_night * self.days_spent
            self.send_refund_email()

        super().save(*args, **kwargs)

    def send_confirmation_email_with_qr(self):
        if self.guest and self.guest.email:
            qr_url = f"http://127.0.0.1:8000/verify/{self.verification_code}/"
            subject = "Booking Confirmed!"
            message = f"Hi {self.guest.user_name},\n\nYour booking is verified!\nUse this link to access your digital QR Key: {qr_url}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.guest.email], fail_silently=True)

    def send_refund_email(self):
        if self.guest and self.guest.email:
            subject = "Refund Processed"
            message = f"Hi {self.guest.user_name},\n\nYour booking cancellation is processed. A refund of {self.refund_amount} has been issued."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.guest.email], fail_silently=True)


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='mpesa')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KES {self.amount} - {self.booking}"


class AccessLog(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attempted_token = models.CharField(max_length=255)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Room {self.room.room_number} - {self.timestamp}"