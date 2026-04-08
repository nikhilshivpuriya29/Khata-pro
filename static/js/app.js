// Khata Pro — Dynamic Mobile-First JS

document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss alerts after 3.5s
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 3500);
    });

    // Auto-submit search on typing (debounced)
    const searchInput = document.querySelector('.search-bar input[name="q"]');
    if (searchInput) {
        let timer;
        searchInput.addEventListener('input', function () {
            clearTimeout(timer);
            timer = setTimeout(() => {
                if (this.value.length >= 2 || this.value.length === 0) {
                    this.closest('form').submit();
                }
            }, 500);
        });
    }

    // Select all text in number inputs on focus
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('focus', function () { this.select(); });
    });

    // Haptic feedback on button tap (mobile)
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('touchstart', function () {
            if (navigator.vibrate) navigator.vibrate(10);
        }, { passive: true });
    });

    // Stagger animation for dynamically loaded content
    document.querySelectorAll('.stagger > *').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.05}s`;
    });

    // Active state for bottom nav
    const bottomLinks = document.querySelectorAll('.bottom-nav .nav-link:not(.add-btn)');
    const currentPath = window.location.pathname;
    bottomLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Swipe to go back (mobile gesture)
    let touchStartX = 0;
    document.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    document.addEventListener('touchend', e => {
        const diff = e.changedTouches[0].screenX - touchStartX;
        if (diff > 100 && touchStartX < 30) {
            window.history.back();
        }
    }, { passive: true });
});
