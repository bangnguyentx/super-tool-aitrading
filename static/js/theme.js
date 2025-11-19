// Theme and Language Management

// Theme functionality
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon
    const icon = event.target.querySelector('i');
    if (icon) {
        icon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Language functionality  
function toggleLanguage() {
    const currentLang = localStorage.getItem('language') || 'vi';
    const newLang = currentLang === 'vi' ? 'en' : 'vi';
    
    localStorage.setItem('language', newLang);
    location.reload();
}

// Initialize theme and language
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const savedLang = localStorage.getItem('language') || 'vi';
    
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.documentElement.setAttribute('lang', savedLang);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initializeTheme);
