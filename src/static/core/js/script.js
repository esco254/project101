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