import os
import re
import glob
import json
import time
import asyncio
from bs4 import BeautifulSoup, NavigableString
import translators as ts
from gtts import gTTS
import edge_tts

TRANSLATION_CACHE_FILE = "translations_cache.json"
AUDIO_HI_DIR = os.path.join("assets", "audio_hi")
AUDIO_PA_DIR = os.path.join("assets", "audio_pa")

os.makedirs(AUDIO_HI_DIR, exist_ok=True)
os.makedirs(AUDIO_PA_DIR, exist_ok=True)

# Load existing cache
if os.path.exists(TRANSLATION_CACHE_FILE):
    try:
        with open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as f:
            trans_cache = json.load(f)
    except Exception:
        trans_cache = {"hi": {}, "pa": {}}
else:
    trans_cache = {"hi": {}, "pa": {}}

def save_cache():
    with open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(trans_cache, f, ensure_ascii=False, indent=2)

def translate_text_single(text, target_lang):
    text_clean = text.strip()
    if not text_clean:
        return text
    
    # Check cache
    if text_clean in trans_cache.get(target_lang, {}):
        return trans_cache[target_lang][text_clean]

    # Translation providers to try
    providers = ['bing', 'google', 'alibaba', 'yandex']
    translated = None
    for provider in providers:
        try:
            translated = ts.translate_text(
                text_clean,
                from_language='en',
                to_language=target_lang,
                translator=provider,
                timeout=10
            )
            if translated and len(translated.strip()) > 0:
                break
        except Exception as e:
            continue

    if not translated:
        translated = text_clean

    if target_lang not in trans_cache:
        trans_cache[target_lang] = {}
    trans_cache[target_lang][text_clean] = translated
    return translated

# Common UI Glossary for consistent translations
GLOSSARY_HI = {
    "Back to Home": "मुख्य पृष्ठ",
    "Choose Language": "भाषा चुनें",
    "Listen to Narration": "वर्णन सुनें",
    "Pause Audio": "ऑडियो रोकें",
    "Previous Piece": "पिछली कलाकृति",
    "Next Piece": "अगली कलाकृति",
    "Piece": "कलाकृति",
    "Open on Mobile": "मोबाइल पर खोलें",
    "Scan to view this art record in Chrome on your phone.": "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।",
    "Religious Corner": "धार्मिक कोना",
    "COR Gallery": "सी.ओ.आर. गैलरी",
    "Comdts' Gallery": "कमांडेंट्स गैलरी",
    "Post Independence Battles": "स्वतंत्रता पश्चात युद्ध",
    "Pre-Independence Battles": "स्वतंत्रता पूर्व युद्ध",
    "Sikh Regiment Citations & Honors": "सिख रेजिमेंट प्रशस्ति पत्र एवं सम्मान",
    "Mahavir Chakra Recipients": "महावीर चक्र प्राप्तकर्ता",
    "Kirti Chakra Recipients": "कीर्ति चक्र प्राप्तकर्ता",
    "COAS Citations": "सेना प्रमुख प्रशस्ति पत्र",
    "Weapons & Ammunition": "हथियार एवं गोला-बारूद",
    "Historic Photos & Archives": "ऐतिहासिक तस्वीरें एवं अभिलेखागार",
    "Title:": "शीर्षक:",
    "Category:": "श्रेणी:",
    "Artist:": "कलाकार:",
    "Year:": "वर्ष:",
    "Unknown Artist": "अज्ञात कलाकार",
    "Historical": "ऐतिहासिक",
    "Historical Figure": "ऐतिहासिक व्यक्तित्व",
    "English": "English",
    "Hindi": "हिन्दी",
    "Punjabi": "ਪੰਜਾਬੀ"
}

GLOSSARY_PA = {
    "Back to Home": "ਮੁੱਖ ਪੰਨਾ",
    "Choose Language": "ਭਾਸ਼ਾ ਚੁਣੋ",
    "Listen to Narration": "ਵੇਰਵਾ ਸੁਣੋ",
    "Pause Audio": "ਆਡੀਓ ਰੋਕੋ",
    "Previous Piece": "ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ",
    "Next Piece": "ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ",
    "Piece": "ਕਲਾਕ੍ਰਿਤੀ",
    "Open on Mobile": "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ",
    "Scan to view this art record in Chrome on your phone.": "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।",
    "Religious Corner": "ਧਾਰਮਿਕ ਕੋਨਾ",
    "COR Gallery": "ਸੀ.ਓ.ਆਰ. ਗੈਲਰੀ",
    "Comdts' Gallery": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
    "Post Independence Battles": "ਆਜ਼ਾਦੀ ਤੋਂ ਬਾਅਦ ਦੀਆਂ ਲੜਾਈਆਂ",
    "Pre-Independence Battles": "ਆਜ਼ਾਦੀ ਤੋਂ ਪਹਿਲਾਂ ਦੀਆਂ ਲੜਾਈਆਂ",
    "Sikh Regiment Citations & Honors": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਪ੍ਰਸ਼ੰਸਾ ਪੱਤਰ ਅਤੇ ਸਨਮਾਨ",
    "Mahavir Chakra Recipients": "ਮਹਾਂਵੀਰ ਚੱਕਰ ਪ੍ਰਾਪਤਕਰਤਾ",
    "Kirti Chakra Recipients": "ਕੀਰਤੀ ਚੱਕਰ ਪ੍ਰਾਪਤਕਰਤਾ",
    "COAS Citations": "ਫੌਜ ਮੁਖੀ ਪ੍ਰਸ਼ੰਸਾ ਪੱਤਰ",
    "Weapons & Ammunition": "ਹਥਿਆਰ ਅਤੇ ਗੋਲਾ-ਬਾਰੂਦ",
    "Historic Photos & Archives": "ਇਤਿਹਾਸਕ ਤਸਵੀਰਾਂ ਅਤੇ ਪੁਰਾਲੇਖ",
    "Title:": "ਸਿਰਲੇਖ:",
    "Category:": "ਸ਼੍ਰੇਣੀ:",
    "Artist:": "ਕਲਾਕਾਰ:",
    "Year:": "ਸਾਲ:",
    "Unknown Artist": "ਅਣਜਾਣ ਕਲਾਕਾਰ",
    "Historical": "ਇਤਿਹਾਸਕ",
    "Historical Figure": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
    "English": "English",
    "Hindi": "हिन्दी",
    "Punjabi": "ਪੰਜਾਬੀ"
}

# Pre-populate glossary in cache
for k, v in GLOSSARY_HI.items():
    trans_cache.setdefault("hi", {})[k] = v
for k, v in GLOSSARY_PA.items():
    trans_cache.setdefault("pa", {})[k] = v
save_cache()

def get_language_switcher_html(current_page, current_lang):
    """Generates the top language switch navbar for any page"""
    base_name = current_page.replace('_hi.html', '.html').replace('_pa.html', '.html')
    if base_name == "index.html" or base_name == "index_en.html":
        en_url = "index_en.html"
        hi_url = "index_hi.html"
        pa_url = "index_pa.html"
    else:
        name_root = os.path.splitext(base_name)[0]
        en_url = f"{name_root}.html"
        hi_url = f"{name_root}_hi.html"
        pa_url = f"{name_root}_pa.html"

    en_active = "style=\"background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;\"" if current_lang == 'en' else ""
    hi_active = "style=\"background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;\"" if current_lang == 'hi' else ""
    pa_active = "style=\"background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;\"" if current_lang == 'pa' else ""

    home_label = "🌐 Language Portal" if current_lang == 'en' else ("🌐 भाषा चुनें" if current_lang == 'hi' else "🌐 ਭਾਸ਼ਾ ਚੁਣੋ")

    return f"""
    <!-- Language Switcher Bar -->
    <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
        <a href="index.html" class="nav-link" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
            {home_label}
        </a>
        <div style="display: flex; gap: 8px; align-items: center;">
            <a href="{en_url}" class="nav-link" {en_active} style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
            <a href="{hi_url}" class="nav-link" {hi_active} style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
            <a href="{pa_url}" class="nav-link" {pa_active} style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
        </div>
    </div>
    """

print("Multilingual generator loaded successfully.")
