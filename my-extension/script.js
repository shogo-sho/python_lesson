document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    updateGreeting();
    setBackground();

    // Update every second
    setInterval(updateClock, 1000);
});

function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    // Optional: Add seconds? keeping it clean with HH:MM
    const timeString = `${hours}:${minutes}`;

    document.getElementById('clock').textContent = timeString;

    // Check greeting every minute (in case hour changes)
    if (now.getSeconds() === 0) {
        updateGreeting();
    }
}

function updateGreeting() {
    const hour = new Date().getHours();
    const greetingElement = document.getElementById('greeting');

    let greetingText = '';

    if (hour >= 5 && hour < 12) {
        greetingText = 'Good Morning';
    } else if (hour >= 12 && hour < 18) {
        greetingText = 'Good Afternoon';
    } else {
        greetingText = 'Good Evening';
    }

    greetingElement.textContent = greetingText;
}

function setBackground() {
    const bgElement = document.getElementById('bg-image');
    // Using Picsum for reliable beautiful nature images
    // Adding a query param to cache-bust if needed, or stick to one per load
    // 1920x1080 resolution, keyword 'nature'
    const imageUrl = 'https://picsum.photos/1920/1080?nature';

    // Create a new image object to preload
    const img = new Image();
    img.src = imageUrl;

    img.onload = () => {
        bgElement.style.backgroundImage = `url('${imageUrl}')`;
    };

    // Fallback in case of load error (though picsum is reliable)
    img.onerror = () => {
        bgElement.style.backgroundColor = '#2b2b2b';
    };
}
