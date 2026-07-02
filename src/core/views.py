import random
import json
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
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

        # Generate random room number
        room_ranges = {
            'Single Room': (101, 115),
            'Standard Room': (201, 220),
            'Deluxe Room': (301, 315),
            'Family Room': (401, 410),
            'Presidential Suite': (501, 505),
        }
        low, high = room_ranges.get(room, (100, 200))
        room_number = random.randint(low, high)

        guest_message = f"""
Dear {full_name},

Thank you for choosing StayEase! Your booking is confirmed.

Booking Details:
----------------
Room Number: {room_number}
Room Type: {room}
Stay Type: {stay_type}
Check-in: {checkin}
Check-out: {checkout}
Guests: {guests}

Warm regards,
StayEase Team
Moyne Drive, Nyali, Mombasa
info@stayease.co.ke
+254 700 123 456
        """

        hotel_message = f"""
New Booking Request:

Name: {full_name}
Email: {email}
Phone: {phone}
Room Number: {room_number}
Room Type: {room}
Stay Type: {stay_type}
Check-in: {checkin}
Check-out: {checkout}
Guests: {guests}
        """

        try:
            send_mail(
                subject='Booking Confirmation - StayEase',
                message=guest_message,
                from_email=None,
                recipient_list=[email],
            )
            send_mail(
                subject=f'New Booking Request - {room} (Room {room_number})',
                message=hotel_message,
                from_email=None,
                recipient_list=['njeriregina213@gmail.com'],
            )
            return JsonResponse({'success': True, 'room_number': room_number})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'core/book.html', {'room_name': room_name})