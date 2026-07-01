from django.utils import timezone

from django.shortcuts import render


from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Booking
import qrcode
from django.http import HttpResponse

# Create your views here.


def send_payment_email(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
   
    secret_code = get_random_string(length=8)
    booking.verification_code = secret_code
    booking.save()
    
    
    qr_link = f"http://127.0.0.1:8000/qr/{booking.id}/"
    verify_link = f"http://127.0.0.1:8000/verify/{booking.id}/?code={secret_code}"
    
    subject = "Your Hotel Booking Details"
    body = f"Hello {booking.guest_name},\n\nYour code is {secret_code}.\nQR Key: {qr_link}\nVerify: {verify_link}"
    
    send_mail(subject, body, "hmsdestek@gmail.com", ["guest@email.com"])
    
    return JsonResponse({"status": "Success", "message": "All items synced!"})


def check_verification_code(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    user_typed_code = request.GET.get('code')
    
    
    if user_typed_code == booking.verification_code:
        booking.is_payment_verified = True  # Flip the switch to True!
        booking.save()
        return JsonResponse({"message": "Success! Payment verified and room unlocked."})
    else:
        return JsonResponse({"message": "Error! Wrong verification code."})
    
def show_qr_code(request, booking_id):
    #find booking 
    booking = Booking.objects.get(id=booking_id) 
   
    token_data = str(booking.digital_access_token)
    qr_img = qrcode.make(token_data)
    #Prepare a blank HTTP response to hold an image instead of text
    response = HttpResponse(content_type="image/png")
    qr_img.save(response, "PNG")
    
    return response

def scan_door(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    if booking.days_spent >= booking.days_booked:
        return JsonResponse({"status": "Denied", "message": "Your stay has expired!"})
        
    return JsonResponse({"status": "Granted", "message": "Welcome to your room!"})


def process_refund(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    now = timezone.now()
    time_remaining = booking.checkin_date - now
    hours_remaining = time_remaining.total_seconds() / 3600
    
    base_price = 100.00 
    
    if hours_remaining >= 72:
        refund_percentage = 0.50  
    elif hours_remaining >= 48:
        refund_percentage = 0.25  
    else:
        refund_percentage = 0.00  
        

    booking.refund_amount = base_price * refund_percentage
    booking.is_refunded = True
    booking.verification_code = "" 
    booking.save()
    
    return JsonResponse({
        "status": "Processed",
        "hours_prior": round(hours_remaining, 1),
        "refund_percent": f"{refund_percentage * 100}%",
        "amount_returned": booking.refund_amount
    })