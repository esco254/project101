from django.contrib import admin
from .models import GuestProfile, HotelRoom, Booking

@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'phone')
    search_fields = ('user_name', 'email')

@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'price_per_night', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'check_in', 'check_out', 'is_payment_verified', 'is_refunded')
    list_filter = ('is_payment_verified', 'is_refunded')
    autocomplete_fields = ('guest', 'room')