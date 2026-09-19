/**
 * Virasat Museum - Language Preference Manager
 * Remembers language selection and highlights active language on artifact pages.
 */

function setMuseumLang(lang) {
    if (!lang) return;
    try {
        localStorage.setItem('museum_lang', lang);
        document.cookie = "museum_lang=" + encodeURIComponent(lang) + "; path=/; max-age=31536000; SameSite=Lax";
    } catch (e) {}
}

function getMuseumLang() {
    try {
        var urlParams = new URLSearchParams(window.location.search);
        var explicit = urlParams.get('lang');
        if (explicit) {
            setMuseumLang(explicit);
            return explicit;
        }
        var saved = localStorage.getItem('museum_lang');
        if (saved) return saved;
        var match = document.cookie.match(/(?:^|;\s*)museum_lang=([^;]+)/);
        if (match) return decodeURIComponent(match[1]);
    } catch (e) {}
    return null;
}

// Auto-record active language on load
document.addEventListener('DOMContentLoaded', function() {
    var path = window.location.pathname;
    if (path.endsWith('_hi.html')) {
        setMuseumLang('hi');
    } else if (path.endsWith('_pa.html')) {
        setMuseumLang('pa');
    } else if (path.endsWith('.html') && !path.endsWith('index.html')) {
        setMuseumLang('en');
    }
});
