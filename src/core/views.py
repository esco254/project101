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
    return render(request, 'core/contact.html')

def book(request):
    room_name = request.GET.get('room', '')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        room = request.POST.get('room')
        stay_type = request.POST.get('stay_type')
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        guests = request.POST.get('guests')

        print(f'Booking received: {full_name}, {email}, {room}')

        request.session['booking'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
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
        'Single Room':        {'Room Only': 5000,  'Bed & Breakfast': 6800,  'All-Inclusive': 9500},
        'Standard Room':      {'Room Only': 8000,  'Bed & Breakfast': 10500, 'All-Inclusive': 14000},
        'Deluxe Room':        {'Room Only': 18000, 'Bed & Breakfast': 22000, 'All-Inclusive': 28000},
        'Family Room':        {'Room Only': 38000, 'Bed & Breakfast': 45000, 'All-Inclusive': 55000},
        'Presidential Suite': {'Room Only': 70000, 'Bed & Breakfast': 82000, 'All-Inclusive': 98000},
    }

    room = booking.get('room', '')
    stay_type = booking.get('stay_type', '')
    amount = prices.get(room, {}).get(stay_type, 0)

    if request.method == 'POST':
        guest_name = booking.get('full_name')
        guest_email = booking.get('email')

        guest_message = f"""
Dear {guest_name},

Your payment has been received and your booking is confirmed!

Booking Details:
----------------
Room: {room}
Stay Type: {stay_type}
Check-in: {booking.get('checkin')}
Check-out: {booking.get('checkout')}
Guests: {booking.get('guests')}
Amount Paid: KSh {amount:,}

We look forward to welcoming you!

Warm regards,
StayEase Team
Moyne Drive, Nyali, Mombasa
+254 700 123 456
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
                message=f'Guest: {guest_name}\nEmail: {guest_email}\nRoom: {room}\nStay: {stay_type}\nCheck-in: {booking.get("checkin")}\nCheck-out: {booking.get("checkout")}',
                from_email=None,
                recipient_list=['njeriregina213@gmail.com'],
            )
            return redirect ('success')
        
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