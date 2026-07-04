from django.utils import timezone
from decimal import Decimal
from .models import AccessLog
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
    
    qr = qrcode.QRCode(version=1, box_size=5, border=4)
    qr.add_data(str(booking.digital_access_token))
    qr.make(fit=True)
    img = qr.make_image(fill_color="#ffffff", back_color="#1e1e2e")
    
    from io import BytesIO
    import base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_png_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    html_layout = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121214; color: #e4e4e7; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .ticket-card {{ background-color: #1e1e2e; border: 1px solid #313244; border-radius: 16px; width: 400px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }}
            .header {{ font-size: 1.2rem; font-weight: 600; color: #cba6f7; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 20px; }}
            .welcome {{ font-size: 1.1rem; margin-bottom: 20px; color: #cdd6f4; }}
            .info-badge {{ background-color: #252538; border-radius: 8px; padding: 12px; margin: 10px 0; border-left: 4px solid #89b4fa; text-align: left; }}
            .label {{ font-size: 0.8rem; color: #a6adc8; text-transform: uppercase; letter-spacing: 0.5px; }}
            .value {{ font-size: 1rem; font-weight: 600; color: #f5e0dc; margin-top: 2px; font-family: monospace; }}
            .qr-section {{ margin-top: 25px; padding: 15px; background-color: #1e1e2e; border-radius: 12px; display: inline-block; }}
            .qr-image {{ border-radius: 8px; width: 180px; height: 180px; }}
            .footer-text {{ font-size: 0.75rem; color: #6c7086; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="ticket-card">
            <div class="header">Booking Confirmed</div>
            <div class="welcome">Welcome, {booking.guest.user_name}</div>
            
            <div class="info-badge">
                <div class="label">Verification Pin</div>
                <div class="value">{booking.verification_code}</div>
            </div>
            
            <div class="info-badge" style="border-left-color: #a6e3a1;">
                <div class="label">Digital Access Pass</div>
                <div class="value" style="font-size: 0.8rem; word-break: break-all;">{booking.digital_access_token}</div>
            </div>
            
            <div class="qr-section">
                <img class="qr-image" src="data:image/png;base64,{image_png_data}" alt="Access QR">
            </div>
            
            <div class="footer-text">Scan pass at terminal upon arrival</div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_layout)

def check_verification_code(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    user_typed_code = request.GET.get('code')
    
    
    if user_typed_code == booking.verification_code:
        booking.is_payment_verified = True  
        booking.save()
        return JsonResponse({"message": "Success! Payment verified and room unlocked."})
    else:
        return JsonResponse({"message": "Error! Wrong verification code."})
    


def scan_door(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    if booking.days_spent >= booking.days_booked:
        return JsonResponse({"status": "Denied", "message": "Your stay has expired!"})
        
        return JsonResponse({"status":"Allowed"})
    

def process_refund(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    if booking.is_refunded:
        return HttpResponse("Already refunded.")
        
    now_date = timezone.now().date()
    
    if now_date >= booking.check_in:
        return HttpResponse("🔒 Refund Denied: Stay has already started or passed.")
        
    time_remaining = booking.check_in - now_date
    days_remaining = time_remaining.days
    
    full_price = booking.days_spent * booking.room.price_per_night
    
    if days_remaining >= 3:
        refund_percentage = Decimal('1.00')
        status_msg = "Full Refund (Cancelled > 72h in advance)"
    elif days_remaining >= 1:
        refund_percentage = Decimal('0.50')
        status_msg = "Partial 50% Refund (Last-minute cancellation)"
    else:
        refund_percentage = Decimal('0.00')
        status_msg = "No Refund (Cancelled less than 24h before check-in)"
        
    refund_cash = full_price * refund_percentage
    
    booking.is_refunded = True
    booking.refund_amount = refund_cash
    booking.save()
    
    booking.room.is_available = True
    booking.room.save()
    
    html_refund = f"""
    <div style="font-family: sans-serif; background: #1e1e2e; color: #a6e3a1; padding: 20px; border-radius: 12px; max-width: 400px; margin: 40px auto; border: 1px solid #313244;">
        <h3>💸 Cancellation & Refund</h3>
        <hr style="border-color: #313244;">
        <p style="color: #a6adc8; font-size: 0.9rem;"><b>Policy applied:</b> {status_msg}</p>
        <p style="color: #cdd6f4;">Amount Returned: <b>Ksh {refund_cash:,.2f}</b></p>
        <p style="color: #6c7086; font-size: 0.8rem;">Room {booking.room.room_number} has been released back to availability.</p>
    </div>
    """
    return HttpResponse(html_refund)
def check_verification_code(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    user_pin = request.GET.get('pin')
    
    current_time = timezone.now()
    checkout_limit = timezone.datetime.combine(booking.check_out, timezone.datetime.min.time()) + timezone.timedelta(hours=11, minutes=30)
    
    if user_pin == booking.verification_code and current_time.timestamp() <= checkout_limit.timestamp():
        AccessLog.objects.create(room=booking.room, attempted_token=user_pin, is_successful=True)
        return HttpResponse("Access  has been Granted.")
    else:
        AccessLog.objects.create(room=booking.room, attempted_token=user_pin, is_successful=False)
        return HttpResponse("Access has been Denied.", status=403)