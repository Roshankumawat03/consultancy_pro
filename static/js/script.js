// Initialize AOS
document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });
});

// Mobile Menu Toggle
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close menu when clicking nav link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Mobile dropdown toggle
document.querySelectorAll('.dropdown > a').forEach(link => {
    link.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            e.preventDefault();
            link.parentElement.classList.toggle('active');
        }
    });
});

// Header scroll effect
const header = document.querySelector('.header');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.style.boxShadow = '0 5px 20px rgba(0,0,0,0.1)';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.05)';
    }
});

// Scroll to top button
const scrollTop = document.getElementById('scrollTop');
window.addEventListener('scroll', () => {
    if (window.scrollY > 500) {
        scrollTop.classList.add('show');
    } else {
        scrollTop.classList.remove('show');
    }
});

scrollTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Flash message close
document.querySelectorAll('.flash-close').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.parentElement.style.display = 'none';
    });
});

// Auto hide flash messages
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(flash => {
        flash.style.opacity = '0';
        setTimeout(() => flash.style.display = 'none', 300);
    });
}, 5000);