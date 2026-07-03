from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('receptionist', 'Receptionist')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default ='receptionist')

    phone_number = models.CharField(max_length=10, blank=True)

    department = models.CharField(max_length=100, blank=True)

    date_joined = models.DateField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
class Room(models, Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single')
        ('family', 'Family')
        ('suite', 'Presidential Suite')
        ('Deluxe', 'Deluxe')
    ]

    room_number = models.CharsField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices= ROOM_TYPE_CHOICES)
    price_per_night = model.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)

    def _str_(self):
        return f"Room {self.room_number} ({self.room_type()})"
    
class Guest(models. Model):
first_name = models.CharField(max_length=50)
last_name = models.CharField(max_length=50)
email = models.EmailField(unique=True)
phone_number = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending')
        ('confirmed', 'Confirmed')
        ('checked_in', 'Checked In')
        ('checked_out', 'Checked Out')
        ('cancelled', 'Cancelled')
    ]

reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
room = models.ForeignKey(Room, on_delete= models.CASCADE, related_name= 'bookings')
guest = models.ForeignKey(Guest, on_delete= models.CASCADE, related_name= 'bookings')
check_in = models.DateField()
check_out = models.DateField()
status = models.CharField(max_length= 20, choices=STATUS_CHOICES, default= 'pending')

class Meta:
    constraints = [
        models.CheckConstraint (
        check = Q(check_out_gt=F('check_in'))
         name= 'check_out_after_check_in')
    ]

def clean(self):

    #Date Logic check
    if self.check_in and self.check_out:
        if self.check_out <= self.check_in:
            raise ValidationError("Check out must be after check in date")
        
    #Double booking overlap check
    if self.room_id:
        overlapping = Booking.objects.filter(
            room = self.room,
            status_in = ['pending', 'confirmed', 'checked_in']
        ).exclude(pk=self.pk).filter(
            check_in_lt=self.check_out
            check_out_gt=self.check_in,
            )
    
    if overlapping.exists():
        clash = overlapping.first()
        raise ValidationError(
            f"Room {self.room} is already booked"
            f"from {clash.check_in} to {clash.check_out}"
        )
    
def save(self, *args, **kwargs):
    #run before saving
    self.full_clean()
    super().save(*args, **kwargs)

@property
def ref_short(self):
    """First 8 chars of UUID in uppercase - use in templates as {{booking.ref_short}}"""
    return str(self.reference)[:8].upper()

def _str_(self):
    return f"Booking #{self.ref_short} - {self.room}"


class Payment (models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending')
        ('completed', 'Completed')
        ('failed', 'Failed')
        ('refunded', 'Refunded')
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash')
        ('mpesa', 'M-Pesa')
        ('card', 'Card')
    ]

booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name= 'payments')
amount = models.DecimalField(max_digits=10, decimal_places=2)
payment_method = models.CharField(
    max_length=20, choices=PAYMENT_CHOICES, default= 'mpesa')
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
payment_date = models.DateTimeField(auto_now_add=True)

def _str_(self):
    return f"KES {self.amount} - {self.booking}"