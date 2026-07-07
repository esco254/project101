import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from decimal import Decimal
from .models import Booking, GuestProfile, Room, Payment, AccessLog
import qrcode


ROOM_TYPE_MAP = {
    'Single Room': 'single',
    'Standard Room': 'standard',
    'Deluxe Room': 'deluxe',
    'Family Room': 'family',
    'Presidential Suite': 'suite',
}


def home(request):
    return render(request, 'core/home.html')

def rooms(request):
    return render(request, 'core/rooms.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        hotel_message = f"""
New Contact Message

Name: {name}
Email: {email}

Message:
{message}
"""

        try:
            send_mail(
                subject=f"Contact Form Message from {name}",
                message=hotel_message,
                from_email=None,
                recipient_list=['njeriregina213@gmail.com'],
            )

            guest_message = f"""
Dear {name},

Thank you for contacting StayEase Hotel.

We have successfully received your message and a member of our team will get back to you as soon as possible.

Below is a copy of your message:


{message}


If your enquiry is urgent, please call us on:

Phone: +254 700 123 456
Email: info@stayease.co.ke

Kind regards,

StayEase Team
"""

            send_mail(
                subject="We've Received Your Message - StayEase",
                message=guest_message,
                from_email=None,
                recipient_list=[email],
            )

            return redirect('contact')

        except Exception as e:
            print(f"CONTACT EMAIL ERROR: {e}")

    return render(request, 'core/contact.html')


def book(request):
    room_name = request.GET.get('room', '')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        id_type = request.POST.get("id_type")
        id_number = request.POST.get("id_number")
        room = request.POST.get('room')
        stay_type = request.POST.get('stay_type')
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        guests = request.POST.get('guests')

        print("Guest email:", email)
        print(f'Booking received: {full_name}, {email}, {room}')

        request.session['booking'] = {
            'full_name': full_name,
            'email': email,
            'id_type': id_type,
            'id_number': id_number,
            'room': room,
            'stay_type': stay_type,
            'checkin': checkin,
            'checkout': checkout,
            'guests': guests,
        }
        request.session.modified = True
        return redirect('payment')

    return render(request, 'core/book.html', {'room_name': room_name})


def payment(request):
    booking = request.session.get('booking', {})

    prices = {
        'Single Room': {'Room Only': 5000, 'Bed & Breakfast': 6800, 'All-Inclusive': 9500},
        'Standard Room': {'Room Only': 8000, 'Bed & Breakfast': 10500, 'All-Inclusive': 14000},
        'Deluxe Room': {'Room Only': 18000, 'Bed & Breakfast': 22000, 'All-Inclusive': 28000},
        'Family Room': {'Room Only': 38000, 'Bed & Breakfast': 45000, 'All-Inclusive': 55000},
        'Presidential Suite': {'Room Only': 70000, 'Bed & Breakfast': 82000, 'All-Inclusive': 98000},
    }

    room = booking.get('room', '')
    stay_type = booking.get('stay_type', '')
    checkin = booking.get('checkin', '')
    checkout = booking.get('checkout', '')

    if checkin and checkout:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        nights = (checkout_date - checkin_date).days
    else:
        nights = 1

    per_night = prices.get(room, {}).get(stay_type, 0)
    amount = per_night * nights

    # Room allocation (display only)
    room_info = {
        "Single Room": {"floor": "1st Floor", "rooms": list(range(101, 121))},
        "Standard Room": {"floor": "2nd Floor", "rooms": list(range(201, 221))},
        "Deluxe Room": {"floor": "3rd Floor", "rooms": list(range(301, 321))},
        "Family Room": {"floor": "4th Floor", "rooms": list(range(401, 421))},
        "Presidential Suite": {"floor": "5th Floor", "rooms": list(range(501, 521))},
    }

    selected_room = room_info.get(room)

    if selected_room:
        room_number = random.choice(selected_room["rooms"])
        floor = selected_room["floor"]
    else:
        room_number = "N/A"
        floor = "N/A"

    if request.method == 'POST':
        guest_name = booking.get('full_name')
        guest_email = booking.get('email')

        print("Sending confirmation email to:", guest_email)

        booking_reference = f"BK-{random.randint(100000,999999)}"
        payment_reference = f"PAY-{random.randint(100000,999999)}"

       # --- Create the actual booking record ---
        guest, created = GuestProfile.objects.get_or_create(
            email=guest_email,
            defaults={'user_name': guest_name}
        )
        if not created:
            guest.user_name = guest_name
            guest.save()

        room_key = ROOM_TYPE_MAP.get(room)
        room_obj = Room.objects.filter(room_type=room_key, availability=True).first()

        try:
            checkin_date_obj = datetime.strptime(booking.get('checkin'), '%Y-%m-%d').date()
            checkout_date_obj = datetime.strptime(booking.get('checkout'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            checkin_date_obj = timezone.now().date()
            checkout_date_obj = timezone.now().date()

        new_booking = Booking.objects.create(
            guest=guest,
            room=room_obj,
            check_in=checkin_date_obj,
            check_out=checkout_date_obj,
            is_payment_verified=True,
        )

        Payment.objects.create(
            booking=new_booking,
            amount=amount,
            payment_method='mpesa',
            status='completed',
        )

        if room_obj:
            room_obj.availability = False
            room_obj.save()
        # --- end booking creation ---

        guest_message = f"""
Dear {guest_name},

Thank you for choosing StayEase!

Your payment has been received successfully and your booking has been confirmed.

=======================================================
                 BOOKING DETAILS
=======================================================

Booking Reference: {booking_reference}
Payment Reference: {payment_reference}

Room Type: {room}
Floor: {floor}
Room Number: {room_number}

{booking.get('id_type')}: {booking.get('id_number')}

Stay Type: {stay_type}
Check-in Date: {booking.get('checkin')}
Check-out Date: {booking.get('checkout')}
Guests: {booking.get('guests')}

Amount Paid: Ksh {amount:,}
Payment Status: Successful

-------------------------------------------------------

Check-in Time: From 12:00 PM
Check-out Time: Before 11:00 AM

Please present this confirmation email together with a valid identification document during check-in.

If you have any questions before your arrival:

Phone: +254 700 123 456
Email: info@stayease.co.ke

We look forward to welcoming you to StayEase!

Warm regards,

StayEase Team
Moyne Drive, Nyali, Mombasa
"""

        hotel_message = f"""
A new booking has been confirmed.

Guest Name: {guest_name}
Guest Email: {guest_email}

Room Type: {room}
Floor: {floor}
Room Number: {room_number}

Stay Type: {stay_type}
Check-in: {booking.get('checkin')}
Check-out: {booking.get('checkout')}
Guests: {booking.get('guests')}

Booking Reference: {booking_reference}
Payment Reference: {payment_reference}

Amount Paid: Ksh {amount:,}
Payment Status: Successful (Simulated)
"""

        try:
            send_mail(
                subject='Booking Confirmed - StayEase',
                message=guest_message,
                from_email=None,
                recipient_list=[guest_email],
            )

            send_mail(
                subject=f'New Booking - {room}',
                message=hotel_message,
                from_email=None,
                recipient_list=['njeriregina213@gmail.com'],
            )

            return redirect('success')

        except Exception as e:
            print(f'EMAIL ERROR: {e}')
            return redirect('success')

    return render(request, 'core/payment.html', {
        'room': room,
        'stay_type': stay_type,
        'amount': f'KSh {amount:,}',
        'guest_email': booking.get('email'),
        'guest_name': booking.get('full_name'),
    })


def success(request):
    booking = request.session.get('booking', {})
    return render(request, 'core/success.html', {
        'guest_name': booking.get('full_name'),
        'room': booking.get('room'),
        'guest_email': booking.get('email'),
    })


# --- Access / verification views ---

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


def verify_payment_code(request, booking_id):
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
    else:
        return JsonResponse({"status": "Allowed"})


def process_refund(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    if booking.is_refunded:
        return HttpResponse("Already refunded.")

    now_date = timezone.now().date()

    if now_date >= booking.check_in:
        return HttpResponse("Refund Denied: Stay has already started or passed.")

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
        <h3>Cancellation & Refund</h3>
        <hr style="border-color: #313244;">
        <p style="color: #a6adc8; font-size: 0.9rem;"><b>Policy applied:</b> {status_msg}</p>
        <p style="color: #cdd6f4;">Amount Returned: <b>Ksh {refund_cash:,.2f}</b></p>
        <p style="color: #6c7086; font-size: 0.8rem;">Room {booking.room.room_number} has been released back to availability.</p>
    </div>
    """
    return HttpResponse(html_refund)


def check_door_access(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    user_pin = request.GET.get('pin')

    current_time = timezone.now()
    checkout_limit = timezone.datetime.combine(
        booking.check_out, timezone.datetime.min.time()
    ) + timezone.timedelta(hours=11, minutes=30)

    if user_pin == booking.verification_code and current_time.timestamp() <= checkout_limit.timestamp():
        AccessLog.objects.create(room=booking.room, attempted_token=user_pin, is_successful=True)
        return HttpResponse("Access has been Granted.")
    else:
        AccessLog.objects.create(room=booking.room, attempted_token=user_pin, is_successful=False)
        return HttpResponse("Access has been Denied.", status=403)
