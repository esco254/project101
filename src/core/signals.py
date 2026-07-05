from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Booking, Payment
from .utils import send_booking_confirmation_email, send_payment_confirmation_email


@receiver(post_save, sender=Booking)
def on_booking_created(sender, instance, created, **kwargs):
    if created:
        try:
            send_booking_confirmation_email(instance)
        except Exception as e:
            print(f"[EMAIL ERROR] Booking confirmation failed: {e}")

@receiver(post_save, sender=Payment)
def on_payment_completed(sender, instance, created, **kwargs):
    if created and instance.status == 'completed':
        try:
            send_payment_confirmation_email(instance)
        except Exception as e:
            print(f"[EMAIL ERROR] Payment confirmation failed: {e}")