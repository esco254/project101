from django.core.mail import send_mail
from django.conf import settings

def send_booking_confirmation_email(booking):
    subject = f"Booking Confirmed — StayEase Grand Hotel (Ref: {booking.ref_short})"
    message = (
        f"Dear {booking.guest},\n\n"
        f"Your booking at StayEase Grand Hotel has been confirmed.\n\n"
        f" Room : {booking.room}\n"
        f" Check-in : {booking.check_in.strftime('%d %B %Y')}\n"
        f" Check-out : {booking.check_out.strftime('%d %B %Y')}\n"
        f" Reference : {booking.ref_short}\n\n"
        f"Please present this reference at reception on arrival.\n\n"
        f"Warm regards,\n"
        f"StayEase Grand Hotel\n"
        )
    send_mail(
    subject=subject,
    message=message,
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[booking.guest.email],
    fail_silently=False,
    )
def send_payment_confirmation_email(payment):
    booking = payment.booking
    subject = f"Payment Received — StayEase Grand Hotel (Receipt #{payment.pk})"
    message = (
        f"Dear {booking.guest},\n\n"
        f"We have received your payment. Here are the details:\n\n"
        f" Amount : KES {payment.amount}\n"
        f" Payment Method : {payment.get_payment_method_display()}\n"
        f" Booking Ref : {booking.ref_short}\n"
        f" Room : {booking.room}\n"
        f" Check-in : {booking.check_in.strftime('%d %B %Y')}\n"
        f" Check-out : {booking.check_out.strftime('%d %B %Y')}\n"
        f" Payment Date : {payment.payment_date.strftime('%d %B %Y, %I:%M %p')}\n\n"
        f"Thank you for choosing StayEase Grand Hotel.\n\n"
        f"Warm regards,\n"
        f"StayEase Grand Hotel\n"
    )
    send_mail(
    subject=subject,
    message=message,
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[booking.guest.email],
    fail_silently=False,
    )