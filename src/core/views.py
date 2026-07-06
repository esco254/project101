import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import JsonResponse


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

    from datetime import datetime

    if checkin and checkout:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        nights = (checkout_date - checkin_date).days
    else:
        nights = 1

    per_night = prices.get(room, {}).get(stay_type, 0)
    amount = per_night * nights

    # Room allocation
    room_info = {
        "Single Room": {
            "floor": "1st Floor",
            "rooms": list(range(101, 121))
        },
        "Standard Room": {
            "floor": "2nd Floor",
            "rooms": list(range(201, 221))
        },
        "Deluxe Room": {
            "floor": "3rd Floor",
            "rooms": list(range(301, 321))
        },
        "Family Room": {
            "floor": "4th Floor",
            "rooms": list(range(401, 421))
        },
        "Presidential Suite": {
            "floor": "5th Floor",
            "rooms": list(range(501, 521))
        },
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