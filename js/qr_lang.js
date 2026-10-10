/**
 * Virasat Museum - Language Preference Manager & Global Visitor Tracking
 * Remembers language selection and counts every website use & QR code scan.
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

// Global visitor tracking ping (counts every page view & QR code scan)
(function trackVisitorUsage() {
    try {
        var path = (window.location.pathname || '').toLowerCase();
        var isIndexBadgePage = (
            path === '/' ||
            path === '' ||
            path.endsWith('/index.html') ||
            path.endsWith('/index_en.html') ||
            path.endsWith('/index_hi.html') ||
            path.endsWith('/index_pa.html')
        );

        // Subpages and scanned QR code pages ping hits.sh to increment visitor count
        if (!isIndexBadgePage) {
            var ping = new Image();
            ping.src = "https://hits.sh/virasatsrc.netlify.app/visits.svg?label=No%20of%20Visitors&color=f59e0b&labelColor=0f172a&t=" + Date.now();
        }
    } catch (e) {}
})();

// Ensure Copyright tag is present on each page
(function ensureCopyrightTag() {
    function injectTag() {
        if (!document.querySelector('.praval-copyright-tag')) {
            var tag = document.createElement('div');
            tag.className = 'praval-copyright-tag';
            tag.style.cssText = 'position:fixed;right:12px;bottom:8px;z-index:999999;padding:4px 10px;background:rgba(15,23,42,0.88);color:#cbd5e1;border:1px solid rgba(245,158,11,0.35);border-radius:6px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:11px;font-weight:500;letter-spacing:0.3px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-shadow:0 2px 10px rgba(0,0,0,0.4);pointer-events:none;user-select:none;';
            tag.innerHTML = 'Copyright &copy; 2026 Praval Dheer';
            document.body.appendChild(tag);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectTag);
    } else {
        injectTag();
    }
})();

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
