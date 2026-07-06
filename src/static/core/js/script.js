document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-btn');
    const prices = document.querySelectorAll('.price');
    const guestSelect = document.getElementById('guests');
    const roomCards = document.querySelectorAll('.room-card');

    // Pricing tab filter
    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const stay = this.dataset.stay;

            prices.forEach(price => {
                price.style.display = (stay === 'all' || price.dataset.type === stay) ? 'block' : 'none';
            });
        });
    });

    // Guest count filter
    guestSelect.addEventListener('change', function () {
        const guests = this.value;

        roomCards.forEach(card => {
            const occupancy = parseInt(card.dataset.occupancy);

            if (guests === 'all') {
                card.style.display = 'block';
            } else {
                const guestNum = parseInt(guests);
                // 3 and 4+ both match rooms with occupancy 4
                const matches = guestNum <= 2 ? occupancy === guestNum : occupancy >= 4;
                card.style.display = matches ? 'block' : 'none';
            }
        });
    });
});
// Pricing table
const pricing = {
    'Single Room': { 'Room Only': 5000, 'Bed & Breakfast': 6800, 'All-Inclusive': 9500 },
    'Standard Room': { 'Room Only': 8000, 'Bed & Breakfast': 10500, 'All-Inclusive': 14000 },
    'Deluxe Room': { 'Room Only': 18000, 'Bed & Breakfast': 22000, 'All-Inclusive': 28000 },
    'Family Room': { 'Room Only': 38000, 'Bed & Breakfast': 45000, 'All-Inclusive': 55000 },
    'Presidential Suite': { 'Room Only': 70000, 'Bed & Breakfast': 82000, 'All-Inclusive': 98000 },
};

function calculateTotal() {
    const room = document.getElementById('room')?.value;
    const stayType = document.getElementById('stay_type')?.value;
    const checkin = document.getElementById('checkin')?.value;
    const checkout = document.getElementById('checkout')?.value;
    const display = document.getElementById('total-display');

    if (!room || !stayType || !checkin || !checkout) {
        display.textContent = 'Fill in room, stay type, and dates to see your total.';
        return;
    }

    const checkinDate = new Date(checkin);
    const checkoutDate = new Date(checkout);
    const nights = Math.ceil((checkoutDate - checkinDate) / (1000 * 60 * 60 * 24));

    if (nights <= 0) {
        display.textContent = 'Check-out date must be after check-in date.';
        display.style.color = 'red';
        return;
    }

    const pricePerNight = pricing[room]?.[stayType];

    if (!pricePerNight) {
        display.textContent = 'Unable to calculate total.';
        return;
    }

    const total = pricePerNight * nights;
    display.style.color = '';
    display.innerHTML = `
        <strong>${room}</strong> &mdash; ${stayType}<br>
        KSh ${pricePerNight.toLocaleString()} &times; ${nights} night${nights > 1 ? 's' : ''}<br>
        <span class="total-amount">Total: KSh ${total.toLocaleString()}</span>
    `;
}

// Attach listeners
['room', 'stay_type', 'checkin', 'checkout'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', calculateTotal);
    document.getElementById(id)?.addEventListener('input', calculateTotal);
});
// Payment tab switching
const payTabs = document.querySelectorAll('.pay-tab');
const payPanels = document.querySelectorAll('.pay-panel');

if (payTabs.length) {
    payTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            payTabs.forEach(t => t.classList.remove('active'));
            payPanels.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.dataset.tab).classList.add('active');
        });
    });
}
   

   
    // Show payment section
    function showPayment() {
        const form = document.getElementById('booking-form');
        const required = form.querySelectorAll('[required]');
        let valid = true;

        required.forEach(field => {
            if (!field.value) {
                field.style.border = '2px solid red';
                valid = false;
            } else {
                field.style.border = '';
            }
        });

        if (!valid) {
            alert('Please fill in all required fields before proceeding.');
            return;
        }

        document.getElementById('payment-section').classList.remove('hidden');
        document.getElementById('payment-section').scrollIntoView({ behavior: 'smooth' });
        document.getElementById('proceed-btn').disabled = true;
        document.getElementById('proceed-btn').textContent = 'Details Saved ✓';

        // Submit booking form via fetch and get room number back
        fetch("{% url 'book' %}", {
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.bookingRoomNumber = data.room_number;
            }
        });
    }

    // Payment tabs
    document.querySelectorAll('.pay-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.pay-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.pay-form').forEach(f => f.classList.add('hidden'));
            this.classList.add('active');
            document.getElementById(this.dataset.method + '-form').classList.remove('hidden');
        });
    });

    // Simulate payment
    function simulatePayment() {
        document.querySelectorAll('.pay-form').forEach(f => f.classList.add('hidden'));
        document.getElementById('processing').classList.remove('hidden');

        setTimeout(() => {
            document.getElementById('processing').classList.add('hidden');
            const successDiv = document.getElementById('success-message');

            const room = document.getElementById('room').value;
            const checkin = document.getElementById('checkin').value;
            const checkout = document.getElementById('checkout').value;
            const roomNumber = window.bookingRoomNumber || '---';

            successDiv.innerHTML = `
                <div class="success-icon">✓</div>
                <h2>Payment Successful!</h2>
                <p>Your booking is confirmed!</p>
                <div class="success-details">
                    <p><strong>Room:</strong> ${room} &mdash; Room ${roomNumber}</p>
                    <p><strong>Check-in:</strong> ${checkin}</p>
                    <p><strong>Check-out:</strong> ${checkout}</p>
                </div>
                <p class="success-note">A confirmation email with your room details has been sent to you.</p>
                <a href="/" class="btn">Back to Home</a>
            `;

            successDiv.classList.remove('hidden');
            successDiv.scrollIntoView({ behavior: 'smooth' });
        }, 3000);
    }
 