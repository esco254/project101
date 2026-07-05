from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import Staff, Room, Guest, Booking, Payment

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
    list_display = ['room_number', 'room_type', 'price_per_night', 'is_available']
    list_filter = ['room type', 'description']
    search_fields = ['room_number', 'description']
    list_editable = ['is_available']
    ordering = ['room_number']

# Guest
@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_number', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'national_id']
    readonly_fields = ['created_at']
    ordering = ['last_name', 'first_name']

# Inside Booking admin page
class PaymentInLine(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_date']
    fields = ['amount', 'payment_method', 'status', 'transaction_id', 'payment_date']

# Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['ref_short_display', 'guest', 'room',
                    'check_in', 'check_out', 'status_badge', 'created_by']
    list_filter = ['status', 'room_room_type', 'check_in']
    search_fields = ['guest__first_name', 'guest__last_name', 'room__room_number', 'reference']
    readonly_fields = ['reference', 'created_at', 'created_by']
    date_hierarchy = ['check_in']
    ordering = ['-created_at']
    inlines = [PaymentInLine]
    fieldsets = [
        ('Booking Reference', {'fields': ['reference', 'status', 'created_by', 'created_at']}),
        ('Room & Guest', {'fields'['room', 'guest']}),
        ('Dates', {'fields': ['check_in', 'check_out']}),
    ]

def ref_short_display(self, obj):
    return obj.ref_short
ref_short_display.short_description = 'Reference'

def status_badge(self, obj):
    colors = {
        'pending': '#ffc107', 'confirmed':'#198754',
        'checked_in': '#0d6efd', 'checked_out': '#6c757d', 'cancelled': '#dc3545'
    }
    colors = colors.get(obj.status, '#aaa')
    text = '#000' if obj.status == 'pending' else '#fff'
    return format_html(
        '<span style= "background: {}; color: {}; padding:2px 10px;'
        'border-radius: 12px; font-size: 12px;">{}</span>',
        color, text, obj.get_status_display()
    )
status_badge.short_description = 'Status'

def save_model(self, request, obj, form, change):
    if not obj.pk:
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['booking__reference', 'transaction_id']
    readonly_fields = ['payment_date']
    ordering = ['-payment_date']

# Admin site branding
admin.site.site_header = 'StayEase Hotel - Admin'
admin.site.site_title = 'StayEase Grand Hotel'
admin.site.index_title = 'Hotel Management'