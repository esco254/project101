from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import Staff, Room, GuestProfile, Booking, Payment

# Register your models here.
# When creating staff in /admin/,
# tick "Staff status" and then under Permissions
# only assign these permissions to a receptionist:
# core|booking|Can add booking
# core|booking|Can view booking
# core|guest|Can view guest
# core|room|Can view room


class StaffInLine(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name = 'Staff Profile'
    verbose_name_plural = 'Staff Profile'
    fields = ['role', 'phone_number', 'department', 'is_active']


class UserAdmin(BaseUserAdmin):
    inlines = [StaffInLine]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff']
    list_select_related = ['staff_profile']

    def get_role(self, obj):
        profile = getattr(obj, 'staff_profile', None)
        return profile.get_role_display() if profile else '-'
    get_role.short_description = 'Hotel Role'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Room
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'price_per_night', 'availability']
    list_filter = ['room_type', 'availability']
    search_fields = ['room_number']
    list_editable = ['availability']
    ordering = ['room_number']
    readonly_fields = ('price_per_night', 'room_type', 'availability', 'room_number')


# Guest
@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'email', ]
    search_fields = ['user_name', 'email']
    ordering = ['user_name']


# Inside Booking admin page
class PaymentInLine(admin.TabularInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = ['amount', 'payment_method', 'status', 'payment_date']
    fields = ['amount', 'payment_method', 'status', 'payment_date']

    def has_add_permission(self, request, obj=None):
        return False


# Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest', 'room', 'check_in', 'check_out',
                     'is_payment_verified']
    list_filter = ['is_payment_verified', 'check_in']
    search_fields = ['guest__user_name', 'room__room_number']
    readonly_fields = ['guest', 'room', 'check_in', 'check_out', 'days_spent','verification_code']
    date_hierarchy = 'check_in'
    ordering = ['-check_in']
    inlines = [PaymentInLine]
    fieldsets = [
        ('Room & Guest', {'fields': ['room', 'guest']}),
        ('Dates', {'fields': ['check_in', 'check_out', 'days_spent']}),
        ('Payment & Access', {'fields': ['is_payment_verified', 'verification_code']}),
    ]

    def has_delete_permission(self, request, obj=None):
        return False


# Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['booking__guest__user_name']
    readonly_fields = ['booking', 'amount', 'payment_method', 'payment_date']
    ordering = ['-payment_date']


    def has_delete_permission(self, request, obj=None):
        return False

# Admin site branding
admin.site.site_header = 'StayEase Hotel - Admin'
admin.site.site_title = 'StayEase Grand Hotel'
admin.site.index_title = 'Hotel Management'