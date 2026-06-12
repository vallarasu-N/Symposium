// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// Close mobile menu when a link is clicked
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Simple client-side validation highlight
const regForm = document.getElementById('regForm');
if (regForm) {
    regForm.addEventListener('submit', function(e) {
        const email = document.getElementById('email');
        const phone = document.getElementById('phone');
        let valid = true;

        // Email pattern
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email.value)) {
            email.style.borderColor = 'red';
            valid = false;
        } else {
            email.style.borderColor = '#e0e0e0';
        }

        // Phone pattern (10 digits)
        const phonePattern = /^\d{10}$/;
        if (!phonePattern.test(phone.value)) {
            phone.style.borderColor = 'red';
            valid = false;
        } else {
            phone.style.borderColor = '#e0e0e0';
        }

        if (!valid) {
            e.preventDefault();
            alert('Please fix the highlighted errors.');
        }
    });
}