/**
 * Virasat Museum - Multilingual QR Code Engine
 * Ensures any physical QR code scanned works seamlessly in English, Hindi, or Punjabi.
 */

// Save language preference in localStorage and cookie
function setMuseumLang(lang) {
    if (!lang) return;
    try {
        localStorage.setItem('museum_lang', lang);
        document.cookie = "museum_lang=" + encodeURIComponent(lang) + "; path=/; max-age=31536000; SameSite=Lax";
    } catch (e) {
        console.warn("Storage access restricted:", e);
    }
}

// Retrieve current saved language
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
        // Cookie check fallback
        var match = document.cookie.match(/(?:^|;\s*)museum_lang=([^;]+)/);
        if (match) return decodeURIComponent(match[1]);
    } catch (e) {}
    return null;
}

// Compute language variant target URL for a given language
function getLangTargetUrl(targetLang) {
    var loc = window.location;
    var path = loc.pathname;
    // Strip existing _hi or _pa and .html
    var cleanBase = path.replace(/(_hi|_pa)?(\.html|\/)?$/, '');
    var filename = cleanBase.substring(cleanBase.lastIndexOf('/') + 1);

    // If on landing or index pages
    if (filename === 'index' || filename === 'index_en' || filename === 'index_hi' || filename === 'index_pa') {
        return targetLang === 'en' ? 'index_en.html' : ('index_' + targetLang + '.html');
    }

    var ext = targetLang === 'en' ? '.html' : ('_' + targetLang + '.html');
    var basePath = cleanBase.substring(0, cleanBase.lastIndexOf('/') + 1);
    return basePath + filename + ext + (targetLang ? ('?lang=' + targetLang) : '');
}

// Redirect if on a page not matching saved language
function checkAndRedirect() {
    var savedLang = getMuseumLang();
    if (!savedLang) return; // Wait for selection if not set

    var path = window.location.pathname;
    var isHi = path.endsWith('_hi.html');
    var isPa = path.endsWith('_pa.html');
    var isEn = !isHi && !isPa;

    // Do not auto-redirect the language selection portal (index.html)
    var filename = path.substring(path.lastIndexOf('/') + 1).replace(/\.html$/, '');
    if (filename === 'index' || filename === '') return;

    if (savedLang === 'hi' && !isHi) {
        window.location.replace(getLangTargetUrl('hi'));
    } else if (savedLang === 'pa' && !isPa) {
        window.location.replace(getLangTargetUrl('pa'));
    } else if (savedLang === 'en' && !isEn) {
        window.location.replace(getLangTargetUrl('en'));
    }
}

// Show the First-Time Language Choice Modal (on base/English pages if no preference set)
function showFirstTimeLangModal() {
    var savedLang = getMuseumLang();
    if (savedLang) return; // Already chosen!

    var path = window.location.pathname;
    var filename = path.substring(path.lastIndexOf('/') + 1).replace(/\.html$/, '');
    // Only show modal on exhibit / gallery pages, not on index.html (which already has language cards)
    if (filename === 'index' || filename === '') return;

    // Pause audio while user is making their first-time choice
    var audio = document.getElementById('artAudio');
    if (audio) {
        try { audio.pause(); } catch (e) {}
    }

    // Check if modal already in DOM
    if (document.getElementById('langModalOverlay')) return;

    var overlay = document.createElement('div');
    overlay.id = 'langModalOverlay';
    overlay.className = 'lang-modal-overlay';
    overlay.innerHTML = `
        <div class="lang-modal-card">
            <button class="lang-modal-close" onclick="selectFirstTimeLang('en')" title="Continue in English">&times;</button>
            <div class="lang-modal-crest">⚔️ VIRASAT HERITAGE MUSEUM ⚔️</div>
            <h2 class="lang-modal-title">Select Your Language</h2>
            <div class="lang-modal-sub">
                अपनी ऑडियो भाषा चुनें &bull; ਆਪਣੀ ਆਡੀਓ ਭਾਸ਼ਾ ਚੁਣੋ<br>
                <span style="font-size: 0.85em; color: #cbd5e1;">Choose your audio guide &amp; reading language for all exhibits:</span>
            </div>

            <div class="lang-modal-btn-group">
                <!-- 1. ENGLISH -->
                <div class="lang-modal-choice-btn" onclick="selectFirstTimeLang('en')">
                    <div class="lang-modal-flag">🇬🇧</div>
                    <div class="lang-modal-btn-text">
                        <h4>ENGLISH</h4>
                        <p>Listen to audio &amp; read in English</p>
                    </div>
                </div>

                <!-- 2. HINDI -->
                <div class="lang-modal-choice-btn" onclick="selectFirstTimeLang('hi')">
                    <div class="lang-modal-flag">🇮🇳</div>
                    <div class="lang-modal-btn-text">
                        <h4>हिन्दी (Hindi)</h4>
                        <p>शुद्ध हिंदी में ऑडियो सुनें और विवरण पढ़ें</p>
                    </div>
                </div>

                <!-- 3. PUNJABI -->
                <div class="lang-modal-choice-btn" onclick="selectFirstTimeLang('pa')">
                    <div class="lang-modal-flag">ੴ</div>
                    <div class="lang-modal-btn-text">
                        <h4>ਪੰਜਾਬੀ (Punjabi)</h4>
                        <p>ਪੰਜਾਬੀ ਵਿੱਚ ਆਡੀਓ ਸੁਣੋ ਅਤੇ ਇਤਿਹਾਸ ਪੜ੍ਹੋ</p>
                    </div>
                </div>
            </div>

            <div class="lang-modal-note">
                ✓ Your choice is automatically remembered for all QR codes you scan.
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
}

function selectFirstTimeLang(lang) {
    setMuseumLang(lang);
    var overlay = document.getElementById('langModalOverlay');
    if (overlay) overlay.remove();

    var path = window.location.pathname;
    var isHi = path.endsWith('_hi.html');
    var isPa = path.endsWith('_pa.html');
    var isEn = !isHi && !isPa;

    if (lang === 'hi' && !isHi) {
        window.location.replace(getLangTargetUrl('hi'));
    } else if (lang === 'pa' && !isPa) {
        window.location.replace(getLangTargetUrl('pa'));
    } else {
        // Stays on English
        var audio = document.getElementById('artAudio');
        if (audio) {
            try { audio.play(); } catch (e) {}
        }
    }
}

// Auto-run on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    var path = window.location.pathname;
    if (path.endsWith('_hi.html')) {
        setMuseumLang('hi');
    } else if (path.endsWith('_pa.html')) {
        setMuseumLang('pa');
    } else if (path.endsWith('index_en.html')) {
        setMuseumLang('en');
    } else if (path.endsWith('index_hi.html')) {
        setMuseumLang('hi');
    } else if (path.endsWith('index_pa.html')) {
        setMuseumLang('pa');
    } else {
        // Base / English page: check if first time
        showFirstTimeLangModal();
    }
});
