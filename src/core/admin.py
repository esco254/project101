from django.contrib import admin
from .models import HotelRoom  
from .models import HotelRoom, GuestProfile
from .models import HotelRoom, Booking

@admin.register(HotelRoom)  
class HotelRoomAdmin(admin.ModelAdmin):
    # THINGS UNDER ROOM FILTER
    list_display = ('room_number', 'room_type', 'price', 'is_cleaned')
    list_filter = ('room_type', 'is_cleaned')

    # Find rooms instantly
    search_fields = ('room_number',)

@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number',)
    search_fields = ('user__username', 'user__email', 'phone_number') 

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'room_number', 'days_booked', 'is_payment_verified','is_refunded')   
    readonly_fields = ['verification_code', 'digital_access_token', 'is_refunded', 'refund_amount']    