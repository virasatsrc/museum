import os
import sys
import re
import glob
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from gtts import gTTS
import edge_tts
import asyncio

sys.stdout.reconfigure(encoding='utf-8')

CACHE_FILE = "translations_cache.json"
AUDIO_HI_DIR = os.path.join("assets", "audio_hi")
AUDIO_PA_DIR = os.path.join("assets", "audio_pa")

os.makedirs(AUDIO_HI_DIR, exist_ok=True)
os.makedirs(AUDIO_PA_DIR, exist_ok=True)

CACHE_LOCK = threading.Lock()

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            CACHE = json.load(f)
    except Exception:
        CACHE = {"hi": {}, "pa": {}}
else:
    CACHE = {"hi": {}, "pa": {}}

CACHE.setdefault("hi", {})
CACHE.setdefault("pa", {})

def save_cache():
    with CACHE_LOCK:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(CACHE, f, ensure_ascii=False, indent=2)

GLOSSARY_HI = {
    # Nav tabs
    "Religious Corner": "धार्मिक कोना",
    "COR Gallery": "सी.ओ.आर. गैलरी",
    "Comdts' Gallery": "कमांडेंट्स गैलरी",
    "Battle Gallery": "बैटल गैलरी",
    "Beyond Battle Fd": "युद्ध क्षेत्र से परे",
    "Beyond Battle Fd▼": "युद्ध क्षेत्र से परे ▼",
    "Regimental Icons": "रेजिमेंटल प्रतीक",
    "Hall of Fame": "हॉल ऑफ फेम",
    "Victoria Cross": "विक्टोरिया क्रॉस",
    "Paramvir Chakra": "परमवीर चक्र",
    "Mahavir Chakra": "महावीर चक्र",
    "Ashok Chakra": "अशोक चक्र",
    "Kirti Chakra": "कीर्ति चक्र",
    "COAS Citations": "सेना प्रमुख प्रशस्ति पत्र",
    "Weapons & Ammunition": "हथियार एवं गोला-बारूद",
    "Successors": "उत्तराधिकारी बटालियनें",
    "WALL ATRIUM": "वॉल एट्रियम",
    
    # Common UI
    "Back to Home": "मुख्य पृष्ठ",
    "Listen to Narration": "वर्णन सुनें",
    "Pause Audio": "ऑडियो रोकें",
    "Previous Piece": "पिछली कलाकृति",
    "Next Piece": "अगली कलाकृति",
    "Piece": "कलाकृति",
    "Open on Mobile": "मोबाइल पर खोलें",
    "Scan to view this art record in Chrome on your phone.": "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।",
    "Scan to view this gallery in Chrome on your phone.": "अपने फोन पर इस गैलरी को देखने के लिए स्कैन करें।",
    "BATTLE GALLERY PICTURES": "बैटल गैलरी चित्र",
    "WELCOME TO VIRASAT": "विरासत में आपका स्वागत है",
    "HISTORY OF RAMGARH": "रामगढ़ का इतिहास",
    "History of Ramgarh": "रामगढ़ का इतिहास",
    "HISTORY OF SIKH REGIMENT": "सिख रेजिमेंट का इतिहास",
    "History of Sikh Regiment": "सिख रेजिमेंट का इतिहास",
    "HAVALDAR ISHAR SINGH, IOM, IDSM": "हवलदार ईशर सिंह, आईओएम, आईडीएसएम",
    "BATTLE OF SARAGARHI": "सारागढ़ी का युद्ध",
    "Battle of Saragarhi": "सारागढ़ी का युद्ध",
    "Coffee Table Book": "कॉफी टेबल बुक",
    "A Legacy of Valour": "वीरता की विरासत",
    "An Illustrated History of The Sikh Regiment (1846 to 2010)": "सिख रेजिमेंट का एक सचित्र इतिहास (1846 से 2010)",
    "Unknown Artist": "अज्ञात कलाकार",
    "Historical Figure": "ऐतिहासिक व्यक्तित्व",
    "Historical": "ऐतिहासिक",
    "Sikh Regiment": "सिख रेजिमेंट",
}

GLOSSARY_PA = {
    # Nav tabs
    "Religious Corner": "ਧਾਰਮਿਕ ਕੋਨਾ",
    "COR Gallery": "ਸੀ.ਓ.ਆਰ. ਗੈਲਰੀ",
    "Comdts' Gallery": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
    "Battle Gallery": "ਬੈਟਲ ਗੈਲਰੀ",
    "Beyond Battle Fd": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ",
    "Beyond Battle Fd▼": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ ▼",
    "Regimental Icons": "ਰੈਜੀਮੈਂਟਲ ਪ੍ਰਤੀਕ",
    "Hall of Fame": "ਹਾਲ ਆਫ਼ ਫ਼ੇਮ",
    "Victoria Cross": "ਵਿਕਟੋਰੀਆ ਕਰਾਸ",
    "Paramvir Chakra": "ਪਰਮਵੀਰ ਚੱਕਰ",
    "Mahavir Chakra": "ਮਹਾਂਵੀਰ ਚੱਕਰ",
    "Ashok Chakra": "ਅਸ਼ੋਕ ਚੱਕਰ",
    "Kirti Chakra": "ਕੀਰਤੀ ਚੱਕਰ",
    "COAS Citations": "ਫੌਜ ਮੁਖੀ ਪ੍ਰਸ਼ੰਸਾ ਪੱਤਰ",
    "Weapons & Ammunition": "ਹਥਿਆਰ ਅਤੇ ਗੋਲਾ-ਬਾਰੂਦ",
    "Successors": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
    "WALL ATRIUM": "ਵਾਲ ਐਟ੍ਰੀਅਮ",
    
    # Common UI
    "Back to Home": "ਮੁੱਖ ਪੰਨਾ",
    "Listen to Narration": "ਵੇਰਵਾ ਸੁਣੋ",
    "Pause Audio": "ਆਡੀਓ ਰੋਕੋ",
    "Previous Piece": "ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ",
    "Next Piece": "ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ",
    "Piece": "ਕਲਾਕ੍ਰਿਤੀ",
    "Open on Mobile": "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ",
    "Scan to view this art record in Chrome on your phone.": "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।",
    "Scan to view this gallery in Chrome on your phone.": "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਗੈਲਰੀ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।",
    "BATTLE GALLERY PICTURES": "ਬੈਟਲ ਗੈਲਰੀ ਤਸਵੀਰਾਂ",
    "WELCOME TO VIRASAT": "ਵਿਰਾਸਤ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ",
    "HISTORY OF RAMGARH": "ਰਾਮਗੜ੍ਹ ਦਾ ਇਤਿਹਾਸ",
    "History of Ramgarh": "ਰਾਮਗੜ੍ਹ ਦਾ ਇਤਿਹਾਸ",
    "HISTORY OF SIKH REGIMENT": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਇਤਿਹਾਸ",
    "History of Sikh Regiment": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਇਤਿਹਾਸ",
    "HAVALDAR ISHAR SINGH, IOM, IDSM": "ਹਵਾਲਦਾਰ ਈਸ਼ਰ ਸਿੰਘ, ਆਈਓਐਮ, ਆਈਡੀਐਸਐਮ",
    "BATTLE OF SARAGARHI": "ਸਾਰਾਗੜ੍ਹੀ ਦੀ ਲੜਾਈ",
    "Battle of Saragarhi": "ਸਾਰਾਗੜ੍ਹੀ ਦੀ ਲੜਾਈ",
    "Coffee Table Book": "ਕੌਫੀ ਟੇਬਲ ਬੁੱਕ",
    "A Legacy of Valour": "ਬਹਾਦਰੀ ਦੀ ਵਿਰਾਸਤ",
    "An Illustrated History of The Sikh Regiment (1846 to 2010)": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਇੱਕ ਚਿੱਤਰਿਤ ਇਤਿਹਾਸ (1846 ਤੋਂ 2010)",
    "Unknown Artist": "ਅਣਜਾਣ ਕਲਾਕਾਰ",
    "Historical Figure": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
    "Historical": "ਇਤਿਹਾਸਕ",
    "Sikh Regiment": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
}

def translate_text(text, lang):
    text_str = str(text).strip()
    if not text_str or text_str.isdigit() or len(text_str) <= 1:
        return text_str

    if lang == "hi" and text_str in GLOSSARY_HI:
        return GLOSSARY_HI[text_str]
    if lang == "pa" and text_str in GLOSSARY_PA:
        return GLOSSARY_PA[text_str]

    with CACHE_LOCK:
        if text_str in CACHE[lang]:
            cached_val = CACHE[lang][text_str]
            # Ensure cached value is valid and not empty fallback
            if cached_val and cached_val != text_str:
                return cached_val

    # If text is long, chunk by paragraphs or sentences
    if len(text_str) > 1200:
        paragraphs = text_str.split('\n')
        translated_paras = []
        for p in paragraphs:
            p_strip = p.strip()
            if not p_strip:
                translated_paras.append('')
                continue
            if len(p_strip) > 1200:
                sentences = re.split(r'(?<=[.!?])\s+', p_strip)
                chunk = ""
                trans_sentences = []
                for s in sentences:
                    if len(chunk) + len(s) < 1000:
                        chunk += (" " if chunk else "") + s
                    else:
                        trans_chunk = translate_text(chunk, lang)
                        trans_sentences.append(trans_chunk)
                        chunk = s
                if chunk:
                    trans_sentences.append(translate_text(chunk, lang))
                translated_paras.append(" ".join(trans_sentences))
            else:
                translated_paras.append(translate_text(p_strip, lang))
        result = "\n".join(translated_paras)
        with CACHE_LOCK:
            CACHE[lang][text_str] = result
        return result

    # Perform GoogleTranslator via deep_translator
    res = None
    for attempt in range(3):
        try:
            translator = GoogleTranslator(source='en', target=lang)
            res = translator.translate(text_str)
            if res and len(res.strip()) > 0:
                break
        except Exception:
            time.sleep(0.3 * (attempt + 1))

    if not res:
        res = text_str

    with CACHE_LOCK:
        CACHE[lang][text_str] = res
    return res

def batch_translate_list(texts, lang):
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(lambda t: translate_text(t, lang), texts))
    return results

def get_language_switcher_html(current_page, current_lang):
    base_name = current_page.replace('_hi.html', '.html').replace('_pa.html', '.html')
    if base_name in ["index.html", "index_en.html", "index_hi.html", "index_pa.html"]:
        en_url = "index_en.html"
        hi_url = "index_hi.html"
        pa_url = "index_pa.html"
    else:
        root = os.path.splitext(base_name)[0]
        en_url = f"{root}.html"
        hi_url = f"{root}_hi.html"
        pa_url = f"{root}_pa.html"

    en_active = 'style="background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;"' if current_lang == 'en' else ''
    hi_active = 'style="background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;"' if current_lang == 'hi' else ''
    pa_active = 'style="background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;"' if current_lang == 'pa' else ''

    portal_label = "🏛️ Language Portal" if current_lang == 'en' else ("🏛️ भाषा चयन" if current_lang == 'hi' else "🏛️ ਭਾਸ਼ਾ ਚੋਣ")

    return f"""
        <!-- Language Switcher Bar -->
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
            <a href="index.html" class="nav-link" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
                {portal_label}
            </a>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a href="{en_url}" class="nav-link" {en_active} style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
                <a href="{hi_url}" class="nav-link" {hi_active} style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
                <a href="{pa_url}" class="nav-link" {pa_active} style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
            </div>
        </div>
    """

def process_special_exhibit(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. English special page
    soup_en = BeautifulSoup(html, "html.parser")
    for b in soup_en.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_en = soup_en.find("div", class_="gallery-container") or soup_en.find("body")
    if c_en:
        c_en.insert(0, BeautifulSoup(get_language_switcher_html(filename, 'en'), "html.parser"))
    h_a_en = soup_en.find("a", href=re.compile(r"index.*\.html"))
    if h_a_en: h_a_en["href"] = "index_en.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # Extract all caption texts for batch translation
    captions = [c.text.strip() for c in soup_en.find_all("div", class_="caption-text")]
    captions_hi = batch_translate_list(captions, "hi") if captions else []
    captions_pa = batch_translate_list(captions, "pa") if captions else []

    # 2. Hindi special page
    soup_hi = BeautifulSoup(html, "html.parser")
    for b in soup_hi.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_hi = soup_hi.find("div", class_="gallery-container") or soup_hi.find("body")
    if c_hi:
        c_hi.insert(0, BeautifulSoup(get_language_switcher_html(filename, 'hi'), "html.parser"))
    
    h_a_hi = soup_hi.find("a", href=re.compile(r"index.*\.html"))
    if h_a_hi:
        h_a_hi["href"] = "index_hi.html"
        for t in list(h_a_hi.find_all(string=True)):
            if "Back to Home" in t: t.replace_with(" मुख्य पृष्ठ")

    span_badge_hi = soup_hi.find("span", style=re.compile(r"color:\s*var\(--accent-color\)"))
    if span_badge_hi:
        b_txt = span_badge_hi.text.strip()
        span_badge_hi.string = GLOSSARY_HI.get(b_txt, translate_text(b_txt, "hi"))

    h1_hi = soup_hi.find("h1")
    if h1_hi:
        h1_txt = h1_hi.text.strip()
        h1_hi.string = GLOSSARY_HI.get(h1_txt, translate_text(h1_txt, "hi"))
        if soup_hi.find("title"):
            soup_hi.find("title").string = f"{h1_hi.string} - विरासत संग्रहालय"

    sub_p_hi = soup_hi.find("p", style=re.compile(r"color:\s*#94a3b8"))
    if sub_p_hi:
        sub_p_hi.string = translate_text(sub_p_hi.text.strip(), "hi")

    for idx, cap in enumerate(soup_hi.find_all("div", class_="caption-text")):
        if idx < len(captions_hi):
            cap.string = captions_hi[idx]

    # Special handling for weapons script in Hindi
    if filename == "weapons_ammunition.html":
        s_tag = soup_hi.find("script")
        if s_tag and s_tag.string:
            s_code = s_tag.string
            s_code = s_code.replace("Weapons & Ammunition - Exhibit", "हथियार एवं गोला-बारूद - प्रदर्शनी")
            s_code = s_code.replace("Bren Light Machine Gun (BREN MK II)", "ब्रेन लाइट मशीन गन (BREN MK II)")
            s_code = s_code.replace("Machine Gun Receiver & Barrel", "मशीन गन रिसीवर एवं बैरल")
            s_code = s_code.replace("Light Mortar", "लाइट मोर्टार")
            s_code = s_code.replace("Grenade Launcher / Spigot Mortar", "ग्रेनेड लांचर / स्पिगोट मोर्टार")
            s_code = s_code.replace("German Rifle (RIF GERMAN)", "जर्मन राइफल (RIF GERMAN)")
            s_code = s_code.replace("Rifle No. 5 Mk I", "राइफल नंबर 5 एमके I")
            s_code = s_code.replace("Loading exhibit...", "प्रदर्शनी लोड हो रही है...")
            s_code = s_code.replace("Slide", "स्लाइड")
            s_code = s_code.replace("of", "का")
            s_tag.string = s_code

    hi_special_path = filepath.replace(".html", "_hi.html")
    with open(hi_special_path, "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # 3. Punjabi special page
    soup_pa = BeautifulSoup(html, "html.parser")
    for b in soup_pa.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_pa = soup_pa.find("div", class_="gallery-container") or soup_pa.find("body")
    if c_pa:
        c_pa.insert(0, BeautifulSoup(get_language_switcher_html(filename, 'pa'), "html.parser"))
    
    h_a_pa = soup_pa.find("a", href=re.compile(r"index.*\.html"))
    if h_a_pa:
        h_a_pa["href"] = "index_pa.html"
        for t in list(h_a_pa.find_all(string=True)):
            if "Back to Home" in t: t.replace_with(" ਮੁੱਖ ਪੰਨਾ")

    span_badge_pa = soup_pa.find("span", style=re.compile(r"color:\s*var\(--accent-color\)"))
    if span_badge_pa:
        b_txt = span_badge_pa.text.strip()
        span_badge_pa.string = GLOSSARY_PA.get(b_txt, translate_text(b_txt, "pa"))

    h1_pa = soup_pa.find("h1")
    if h1_pa:
        h1_txt = h1_pa.text.strip()
        h1_pa.string = GLOSSARY_PA.get(h1_txt, translate_text(h1_txt, "pa"))
        if soup_pa.find("title"):
            soup_pa.find("title").string = f"{h1_pa.string} - ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ"

    sub_p_pa = soup_pa.find("p", style=re.compile(r"color:\s*#94a3b8"))
    if sub_p_pa:
        sub_p_pa.string = translate_text(sub_p_pa.text.strip(), "pa")

    for idx, cap in enumerate(soup_pa.find_all("div", class_="caption-text")):
        if idx < len(captions_pa):
            cap.string = captions_pa[idx]

    # Special handling for weapons script in Punjabi
    if filename == "weapons_ammunition.html":
        s_tag = soup_pa.find("script")
        if s_tag and s_tag.string:
            s_code = s_tag.string
            s_code = s_code.replace("Weapons & Ammunition - Exhibit", "ਹਥਿਆਰ ਅਤੇ ਗੋਲਾ-ਬਾਰੂਦ - ਪ੍ਰਦਰਸ਼ਨੀ")
            s_code = s_code.replace("Bren Light Machine Gun (BREN MK II)", "ਬ੍ਰੇਨ ਲਾਈਟ ਮਸ਼ੀਨ ਗਨ (BREN MK II)")
            s_code = s_code.replace("Machine Gun Receiver & Barrel", "ਮਸ਼ੀਨ ਗਨ ਰਿਸੀਵਰ ਅਤੇ ਬੈਰਲ")
            s_code = s_code.replace("Light Mortar", "ਲਾਈਟ ਮੋਰਟਾਰ")
            s_code = s_code.replace("Grenade Launcher / Spigot Mortar", "ਗ੍ਰੇਨੇਡ ਲਾਂਚਰ / ਸਪਿਗੋਟ ਮੋਰਟਾਰ")
            s_code = s_code.replace("German Rifle (RIF GERMAN)", "ਜਰਮਨ ਰਾਈਫਲ (RIF GERMAN)")
            s_code = s_code.replace("Rifle No. 5 Mk I", "ਰਾਈਫਲ ਨੰਬਰ 5 ਐਮਕੇ I")
            s_code = s_code.replace("Loading exhibit...", "ਪ੍ਰਦਰਸ਼ਨੀ ਲੋਡ ਹੋ ਰਹੀ ਹੈ...")
            s_code = s_code.replace("Slide", "ਸਲਾਈਡ")
            s_code = s_code.replace("of", "ਦਾ")
            s_tag.string = s_code

    pa_special_path = filepath.replace(".html", "_pa.html")
    with open(pa_special_path, "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

def process_single_art_page(filepath, art_dict):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup_base = BeautifulSoup(html, "html.parser")
    h1 = soup_base.find("h1")
    title_en = h1.text.strip() if h1 else ""

    audio_tag = soup_base.find("audio")
    audio_src = audio_tag.get("src", "") if audio_tag else ""
    m = re.search(r'audio_(\d+)\.mp3', audio_src)
    art_num = m.group(1) if m else os.path.splitext(filename)[0].replace("art", "")

    # Extract all text elements
    boxes = soup_base.find_all("div", class_="description-box")

    # Scroller nomenclatures
    scroller_track = soup_base.find("div", class_="scroller-track")
    noms_en = [nom.text.strip() for nom in scroller_track.find_all("div", class_="nomenclature")] if scroller_track else []
    noms_hi = batch_translate_list(noms_en, "hi") if noms_en else []
    noms_pa = batch_translate_list(noms_en, "pa") if noms_en else []

    # --- 1. Clean English Page ---
    soup_en = BeautifulSoup(html, "html.parser")
    for b in soup_en.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_en = soup_en.find("div", class_="gallery-container") or soup_en.find("body")
    if c_en:
        c_en.insert(0, BeautifulSoup(get_language_switcher_html(filename, 'en'), "html.parser"))
    
    home_a_en = soup_en.find("a", href=re.compile(r"index.*\.html"))
    if home_a_en:
        home_a_en["href"] = "index_en.html"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # --- 2. Build Hindi Page ---
    soup_hi = BeautifulSoup(html, "html.parser")
    for b in soup_hi.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_hi = soup_hi.find("div", class_="gallery-container") or soup_hi.find("body")
    if c_hi:
        c_hi.insert(0, BeautifulSoup(get_language_switcher_html(filename, 'hi'), "html.parser"))

    title_hi = translate_text(title_en, "hi")
    if soup_hi.find("title"):
        soup_hi.find("title").string = f"{title_hi} - विरासत संग्रहालय"
    if soup_hi.find("h1"):
        soup_hi.find("h1").string = title_hi

    home_a_hi = soup_hi.find("a", href=re.compile(r"index.*\.html"))
    if home_a_hi:
        home_a_hi["href"] = "index_hi.html"
        for t in list(home_a_hi.find_all(string=True)):
            if "Back to Home" in t: t.replace_with(" मुख्य पृष्ठ")

    aud_hi = soup_hi.find("audio")
    if aud_hi:
        aud_hi["src"] = f"assets/audio_hi/audio_{art_num}.mp3"
    play_btn_hi = soup_hi.find("button", class_="play-btn")
    if play_btn_hi:
        play_btn_hi.clear()
        play_btn_hi.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> वर्णन सुनें', 'html.parser'))
    
    script_tag_hi = soup_hi.find("script")
    if script_tag_hi and script_tag_hi.string:
        s_str = script_tag_hi.string
        s_str = s_str.replace("Pause Audio", "ऑडियो रोकें").replace("Listen to Narration", "वर्णन सुनें")
        script_tag_hi.string = s_str

    h2_battle_hi = soup_hi.find("h2")
    if h2_battle_hi and "BATTLE GALLERY PICTURES" in h2_battle_hi.text:
        h2_battle_hi.string = "बैटल गैलरी चित्र"

    scroller_hi = soup_hi.find("div", class_="scroller-track")
    if scroller_hi:
        for idx, nom in enumerate(scroller_hi.find_all("div", class_="nomenclature")):
            if idx < len(noms_hi):
                nom.string = noms_hi[idx]

    boxes_hi = soup_hi.find_all("div", class_="description-box")
    if len(boxes_hi) > 0:
        m_txt = boxes_hi[0].decode_contents()
        m_txt = m_txt.replace("Title:", "<strong>शीर्षक:</strong>")
        m_txt = m_txt.replace("Category:", "<strong>श्रेणी:</strong>")
        m_txt = m_txt.replace("Artist:", "<strong>कलाकार:</strong>")
        m_txt = m_txt.replace("Year:", "<strong>वर्ष:</strong>")
        m_txt = m_txt.replace("Regiment:", "<strong>रेजिमेंट:</strong>")
        for k, v in GLOSSARY_HI.items():
            m_txt = m_txt.replace(k, v)
        boxes_hi[0].clear()
        boxes_hi[0].append(BeautifulSoup(m_txt, "html.parser"))

    narration_hi_plain = ""
    if len(boxes_hi) > 1:
        raw_n = boxes[1].get_text(separator=' ').strip()
        raw_n_clean = re.sub(re.escape(title_en), '', raw_n, count=1, flags=re.IGNORECASE).strip()
        trans_n_hi = translate_text(raw_n_clean, "hi")
        narration_hi_plain = f"{title_hi}. {trans_n_hi}"
        boxes_hi[1].clear()
        boxes_hi[1].append(BeautifulSoup(f"<strong>{title_hi}</strong><br><br>{trans_n_hi}", "html.parser"))
    elif len(boxes_hi) == 1:
        narration_hi_plain = title_hi

    nav_hi = soup_hi.find("div", class_="navigation")
    if nav_hi:
        for a in nav_hi.find_all("a", href=True):
            h = a["href"]
            if h.startswith("art") and h.endswith(".html") and not h.endswith("_hi.html"):
                a["href"] = h.replace(".html", "_hi.html")
            for t in list(a.find_all(string=True)):
                if "Previous Piece" in t: t.replace_with(" पिछली कलाकृति")
                elif "Next Piece" in t: t.replace_with("अगली कलाकृति ")
        span = nav_hi.find("span")
        if span and span.string:
            span.string = span.string.replace("Piece", "कलाकृति")

    qr_hi = soup_hi.find("div", class_="qr-info")
    if qr_hi:
        h3 = qr_hi.find("h3")
        p = qr_hi.find("p")
        if h3: h3.string = "मोबाइल पर खोलें"
        if p: p.string = "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।"

    hi_path = filepath.replace(".html", "_hi.html")
    with open(hi_path, "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # --- 3. Build Punjabi Page ---
    soup_pa = BeautifulSoup(html, "html.parser")
    for b in soup_pa.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_pa = soup_pa.find("div", class_="gallery-container") or soup_pa.find("body")
    if c_pa:
        c_pa.insert(0, BeautifulSoup(get_language_switcher_html(filename, 'pa'), "html.parser"))

    title_pa = translate_text(title_en, "pa")
    if soup_pa.find("title"):
        soup_pa.find("title").string = f"{title_pa} - ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ"
    if soup_pa.find("h1"):
        soup_pa.find("h1").string = title_pa

    home_a_pa = soup_pa.find("a", href=re.compile(r"index.*\.html"))
    if home_a_pa:
        home_a_pa["href"] = "index_pa.html"
        for t in list(home_a_pa.find_all(string=True)):
            if "Back to Home" in t: t.replace_with(" ਮੁੱਖ ਪੰਨਾ")

    aud_pa = soup_pa.find("audio")
    if aud_pa:
        aud_pa["src"] = f"assets/audio_pa/audio_{art_num}.mp3"
    play_btn_pa = soup_pa.find("button", class_="play-btn")
    if play_btn_pa:
        play_btn_pa.clear()
        play_btn_pa.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> ਵੇਰਵਾ ਸੁਣੋ', 'html.parser'))
    
    script_tag_pa = soup_pa.find("script")
    if script_tag_pa and script_tag_pa.string:
        s_str = script_tag_pa.string
        s_str = s_str.replace("Pause Audio", "ਆਡੀਓ ਰੋਕੋ").replace("Listen to Narration", "ਵੇਰਵਾ ਸੁਣੋ")
        script_tag_pa.string = s_str

    h2_battle_pa = soup_pa.find("h2")
    if h2_battle_pa and "BATTLE GALLERY PICTURES" in h2_battle_pa.text:
        h2_battle_pa.string = "ਬੈਟਲ ਗੈਲਰੀ ਤਸਵੀਰਾਂ"

    scroller_pa = soup_pa.find("div", class_="scroller-track")
    if scroller_pa:
        for idx, nom in enumerate(scroller_pa.find_all("div", class_="nomenclature")):
            if idx < len(noms_pa):
                nom.string = noms_pa[idx]

    boxes_pa = soup_pa.find_all("div", class_="description-box")
    if len(boxes_pa) > 0:
        m_txt = boxes_pa[0].decode_contents()
        m_txt = m_txt.replace("Title:", "<strong>ਸਿਰਲੇਖ:</strong>")
        m_txt = m_txt.replace("Category:", "<strong>ਸ਼੍ਰੇਣੀ:</strong>")
        m_txt = m_txt.replace("Artist:", "<strong>ਕਲਾਕਾਰ:</strong>")
        m_txt = m_txt.replace("Year:", "<strong>ਸਾਲ:</strong>")
        m_txt = m_txt.replace("Regiment:", "<strong>ਰੈਜੀਮੈਂਟ:</strong>")
        for k, v in GLOSSARY_PA.items():
            m_txt = m_txt.replace(k, v)
        boxes_pa[0].clear()
        boxes_pa[0].append(BeautifulSoup(m_txt, "html.parser"))

    narration_pa_plain = ""
    if len(boxes_pa) > 1:
        raw_n = boxes[1].get_text(separator=' ').strip()
        raw_n_clean = re.sub(re.escape(title_en), '', raw_n, count=1, flags=re.IGNORECASE).strip()
        trans_n_pa = translate_text(raw_n_clean, "pa")
        narration_pa_plain = f"{title_pa}. {trans_n_pa}"
        boxes_pa[1].clear()
        boxes_pa[1].append(BeautifulSoup(f"<strong>{title_pa}</strong><br><br>{trans_n_pa}", "html.parser"))
    elif len(boxes_pa) == 1:
        narration_pa_plain = title_pa

    nav_pa = soup_pa.find("div", class_="navigation")
    if nav_pa:
        for a in nav_pa.find_all("a", href=True):
            h = a["href"]
            if h.startswith("art") and h.endswith(".html") and not h.endswith("_pa.html"):
                a["href"] = h.replace(".html", "_pa.html")
            for t in list(a.find_all(string=True)):
                if "Previous Piece" in t: t.replace_with(" ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ")
                elif "Next Piece" in t: t.replace_with("ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ ")
        span = nav_pa.find("span")
        if span and span.string:
            span.string = span.string.replace("Piece", "ਕਲਾਕ੍ਰਿਤੀ")

    qr_pa = soup_pa.find("div", class_="qr-info")
    if qr_pa:
        h3 = qr_pa.find("h3")
        p = qr_pa.find("p")
        if h3: h3.string = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
        if p: p.string = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"

    pa_path = filepath.replace(".html", "_pa.html")
    with open(pa_path, "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

    art_dict[filename] = {
        "art_num": art_num,
        "title_en": title_en,
        "title_hi": title_hi,
        "title_pa": title_pa,
        "narration_hi": narration_hi_plain,
        "narration_pa": narration_pa_plain
    }

def rebuild_index_pages(art_dict):
    print("Rebuilding index_en.html, index_hi.html, index_pa.html with full translations...", flush=True)
    with open("index_en.html", "r", encoding="utf-8") as f:
        html_en = f.read()

    # 1. Polish index_en.html
    soup_en = BeautifulSoup(html_en, "html.parser")
    for b in soup_en.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_en = soup_en.find("div", class_="gallery-container") or soup_en.find("body")
    if c_en:
        c_en.insert(0, BeautifulSoup(get_language_switcher_html("index_en.html", 'en'), "html.parser"))
    with open("index_en.html", "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # --- 2. Build complete index_hi.html ---
    soup_hi = BeautifulSoup(html_en, "html.parser")
    if soup_hi.find("title"):
        soup_hi.find("title").string = "विरासत संग्रहालय - मुख्य गैलरी"

    for b in soup_hi.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_hi = soup_hi.find("div", class_="gallery-container") or soup_hi.find("body")
    if c_hi:
        c_hi.insert(0, BeautifulSoup(get_language_switcher_html("index_hi.html", 'hi'), "html.parser"))

    # Top nav buttons
    for btn in soup_hi.find_all("button", class_="nav-btn"):
        txt = btn.text.strip().replace("▼", "").strip()
        trans = GLOSSARY_HI.get(txt, translate_text(txt, "hi"))
        btn.string = f"{trans} ▼"

    # Nested dropdown buttons
    for nbtn in soup_hi.find_all("button", class_="nested-btn"):
        svg = nbtn.find("svg")
        txt = nbtn.get_text().strip()
        trans = GLOSSARY_HI.get(txt, translate_text(txt, "hi"))
        nbtn.clear()
        nbtn.append(trans + " ")
        if svg: nbtn.append(svg)

    # Convert all links in index_hi.html to _hi.html and translate link text
    for a in soup_hi.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and href not in ["index.html", "index_hi.html"]:
            a["href"] = href.replace(".html", "_hi.html")
            txt = a.text.strip()
            if href in art_dict and art_dict[href]["title_hi"]:
                a.string = art_dict[href]["title_hi"]
            elif txt:
                a.string = GLOSSARY_HI.get(txt, translate_text(txt, "hi"))

    # Headings
    h1_hi = soup_hi.find("h1")
    if h1_hi and "WELCOME TO VIRASAT" in h1_hi.text:
        h1_hi.string = "विरासत में आपका स्वागत है"

    for h2 in soup_hi.find_all("h2"):
        h2_txt = h2.text.strip()
        if "HISTORY OF RAMGARH" in h2_txt:
            h2.string = "रामगढ़ का इतिहास"
        elif "HISTORY OF SIKH REGIMENT" in h2_txt:
            h2.string = "सिख रेजिमेंट का इतिहास"
        elif "HAVALDAR ISHAR SINGH" in h2_txt:
            h2.string = "हवलदार ईशर सिंह, आईओएम, आईडीएसएम"
        elif "BATTLE OF SARAGARHI" in h2_txt:
            h2.string = "सारागढ़ी का युद्ध"
        elif "Coffee Table Book" in h2_txt:
            h2.string = "कॉफी टेबल बुक"

    # Scroller Captions
    ramgarh_caps = [cap.text.strip() for cap in soup_hi.find_all("div", class_="ramgarh-caption")]
    ramgarh_caps_hi = batch_translate_list(ramgarh_caps, "hi")
    for idx, cap in enumerate(soup_hi.find_all("div", class_="ramgarh-caption")):
        if idx < len(ramgarh_caps_hi):
            cap.string = ramgarh_caps_hi[idx]

    # Descriptions & Paragraphs
    for dbox in soup_hi.find_all("div", class_="description-box"):
        raw_text = dbox.get_text(separator='\n').strip()
        trans_box = translate_text(raw_text, "hi")
        lines = [l.strip() for l in trans_box.split('\n') if l.strip()]
        if lines:
            header_line = lines[0]
            rest = "<br><br>".join(lines[1:])
            dbox.clear()
            dbox.append(BeautifulSoup(f"<strong>{header_line}</strong><br><br>{rest}", "html.parser"))

    # Ishar Singh box paragraphs
    ishar_box = soup_hi.find("div", class_="ishar-singh-box")
    if ishar_box:
        for p in ishar_box.find_all("p"):
            p_txt = p.get_text().strip()
            p.string = translate_text(p_txt, "hi")
        bquote = ishar_box.find("blockquote")
        if bquote:
            b_txt = bquote.get_text().strip()
            bquote.string = f"“{translate_text(b_txt.replace('“','').replace('”',''), 'hi')}”"

    # Coffee Table Book subtitles
    h3_ctb = soup_hi.find("h3")
    if h3_ctb and "A Legacy of Valour" in h3_ctb.text:
        h3_ctb.string = "वीरता की विरासत"

    p_ctb = soup_hi.find("p", style=re.compile(r"font-style:\s*italic"))
    if p_ctb and "An Illustrated History" in p_ctb.text:
        p_ctb.string = "सिख रेजिमेंट का एक सचित्र इतिहास (1846 से 2010)"

    # QR container
    qr_hi = soup_hi.find("div", class_="qr-info")
    if qr_hi:
        h3 = qr_hi.find("h3")
        p = qr_hi.find("p")
        if h3: h3.string = "मोबाइल पर खोलें"
        if p: p.string = "अपने फोन पर इस गैलरी को देखने के लिए स्कैन करें।"

    with open("index_hi.html", "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # --- 3. Build complete index_pa.html ---
    soup_pa = BeautifulSoup(html_en, "html.parser")
    if soup_pa.find("title"):
        soup_pa.find("title").string = "ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ - ਮੁੱਖ ਗੈਲਰੀ"

    for b in soup_pa.find_all("div", class_="lang-switch-bar"): b.decompose()
    c_pa = soup_pa.find("div", class_="gallery-container") or soup_pa.find("body")
    if c_pa:
        c_pa.insert(0, BeautifulSoup(get_language_switcher_html("index_pa.html", 'pa'), "html.parser"))

    # Top nav buttons
    for btn in soup_pa.find_all("button", class_="nav-btn"):
        txt = btn.text.strip().replace("▼", "").strip()
        trans = GLOSSARY_PA.get(txt, translate_text(txt, "pa"))
        btn.string = f"{trans} ▼"

    # Nested dropdown buttons
    for nbtn in soup_pa.find_all("button", class_="nested-btn"):
        svg = nbtn.find("svg")
        txt = nbtn.get_text().strip()
        trans = GLOSSARY_PA.get(txt, translate_text(txt, "pa"))
        nbtn.clear()
        nbtn.append(trans + " ")
        if svg: nbtn.append(svg)

    # Convert all links in index_pa.html to _pa.html and translate link text
    for a in soup_pa.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and href not in ["index.html", "index_pa.html"]:
            a["href"] = href.replace(".html", "_pa.html")
            txt = a.text.strip()
            if href in art_dict and art_dict[href]["title_pa"]:
                a.string = art_dict[href]["title_pa"]
            elif txt:
                a.string = GLOSSARY_PA.get(txt, translate_text(txt, "pa"))

    # Headings
    h1_pa = soup_pa.find("h1")
    if h1_pa and "WELCOME TO VIRASAT" in h1_pa.text:
        h1_pa.string = "ਵਿਰਾਸਤ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ"

    for h2 in soup_pa.find_all("h2"):
        h2_txt = h2.text.strip()
        if "HISTORY OF RAMGARH" in h2_txt:
            h2.string = "ਰਾਮਗੜ੍ਹ ਦਾ ਇਤਿਹਾਸ"
        elif "HISTORY OF SIKH REGIMENT" in h2_txt:
            h2.string = "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਇਤਿਹਾਸ"
        elif "HAVALDAR ISHAR SINGH" in h2_txt:
            h2.string = "ਹਵਾਲਦਾਰ ਈਸ਼ਰ ਸਿੰਘ, ਆਈਓਐਮ, ਆਈਡੀਐਸਐਮ"
        elif "BATTLE OF SARAGARHI" in h2_txt:
            h2.string = "ਸਾਰਾਗੜ੍ਹੀ ਦੀ ਲੜਾਈ"
        elif "Coffee Table Book" in h2_txt:
            h2.string = "ਕੌਫੀ ਟੇਬਲ ਬੁੱਕ"

    # Scroller Captions
    ramgarh_caps_pa = batch_translate_list(ramgarh_caps, "pa")
    for idx, cap in enumerate(soup_pa.find_all("div", class_="ramgarh-caption")):
        if idx < len(ramgarh_caps_pa):
            cap.string = ramgarh_caps_pa[idx]

    # Descriptions & Paragraphs
    for dbox in soup_pa.find_all("div", class_="description-box"):
        raw_text = dbox.get_text(separator='\n').strip()
        trans_box = translate_text(raw_text, "pa")
        lines = [l.strip() for l in trans_box.split('\n') if l.strip()]
        if lines:
            header_line = lines[0]
            rest = "<br><br>".join(lines[1:])
            dbox.clear()
            dbox.append(BeautifulSoup(f"<strong>{header_line}</strong><br><br>{rest}", "html.parser"))

    # Ishar Singh box paragraphs
    ishar_box_pa = soup_pa.find("div", class_="ishar-singh-box")
    if ishar_box_pa:
        for p in ishar_box_pa.find_all("p"):
            p_txt = p.get_text().strip()
            p.string = translate_text(p_txt, "pa")
        bquote = ishar_box_pa.find("blockquote")
        if bquote:
            b_txt = bquote.get_text().strip()
            bquote.string = f"“{translate_text(b_txt.replace('“','').replace('”',''), 'pa')}”"

    # Coffee Table Book subtitles
    h3_ctb_pa = soup_pa.find("h3")
    if h3_ctb_pa and "A Legacy of Valour" in h3_ctb_pa.text:
        h3_ctb_pa.string = "ਬਹਾਦਰੀ ਦੀ ਵਿਰਾਸਤ"

    p_ctb_pa = soup_pa.find("p", style=re.compile(r"font-style:\s*italic"))
    if p_ctb_pa and "An Illustrated History" in p_ctb_pa.text:
        p_ctb_pa.string = "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਇੱਕ ਚਿੱਤਰਿਤ ਇਤਿਹਾਸ (1846 ਤੋਂ 2010)"

    # QR container
    qr_pa = soup_pa.find("div", class_="qr-info")
    if qr_pa:
        h3 = qr_pa.find("h3")
        p = qr_pa.find("p")
        if h3: h3.string = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
        if p: p.string = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਗੈਲਰੀ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"

    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

    print("Index galleries rebuild complete!", flush=True)

async def synthesize_all_audio(art_dict):
    print("Synthesizing missing or updated audio narrations...", flush=True)
    semaphore = asyncio.Semaphore(8)

    async def gen_hi_single(art_num, text):
        if not art_num or not text: return
        p = os.path.join(AUDIO_HI_DIR, f"audio_{art_num}.mp3")
        clean = re.sub(r'<[^>]+>', ' ', text).strip()
        if not clean: return
        async with semaphore:
            try:
                comm = edge_tts.Communicate(clean[:3000], 'hi-IN-MadhurNeural')
                await comm.save(p)
            except Exception:
                try:
                    tts = gTTS(text=clean[:3000], lang='hi')
                    tts.save(p)
                except Exception:
                    pass

    # Batch Hindi
    tasks_hi = []
    for meta in art_dict.values():
        num = meta.get("art_num")
        narr_hi = meta.get("narration_hi")
        if num and narr_hi:
            p = os.path.join(AUDIO_HI_DIR, f"audio_{num}.mp3")
            if not os.path.exists(p) or os.path.getsize(p) < 1500:
                tasks_hi.append(gen_hi_single(num, narr_hi))

    print(f"Generating {len(tasks_hi)} Hindi audio files...", flush=True)
    for i in range(0, len(tasks_hi), 25):
        batch = tasks_hi[i:i+25]
        await asyncio.gather(*batch)
        print(f"Hindi audio {min(i+25, len(tasks_hi))}/{len(tasks_hi)} generated...", flush=True)

    # Batch Punjabi
    def gen_pa_single(meta):
        num = meta.get("art_num")
        narr_pa = meta.get("narration_pa")
        if not num or not narr_pa: return
        p = os.path.join(AUDIO_PA_DIR, f"audio_{num}.mp3")
        if os.path.exists(p) and os.path.getsize(p) >= 1500:
            return
        clean = re.sub(r'<[^>]+>', ' ', narr_pa).strip()
        if not clean: return
        try:
            tts = gTTS(text=clean[:2500], lang='pa')
            tts.save(p)
        except Exception:
            pass

    items_pa = [m for m in art_dict.values() if m.get("art_num") and m.get("narration_pa")]
    items_to_generate = [m for m in items_pa if not os.path.exists(os.path.join(AUDIO_PA_DIR, f"audio_{m['art_num']}.mp3")) or os.path.getsize(os.path.join(AUDIO_PA_DIR, f"audio_{m['art_num']}.mp3")) < 1500]
    
    print(f"Generating {len(items_to_generate)} Punjabi audio files...", flush=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(gen_pa_single, m) for m in items_to_generate]
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 25 == 0 or done == len(items_to_generate):
                print(f"Punjabi audio {done}/{len(items_to_generate)} generated...", flush=True)

    print("All audio synthesis completed!", flush=True)

def main():
    print("--- Starting Complete Museum Multilingual Engine ---", flush=True)
    
    # 1. Process special pages
    special_pages = ["coas_citations.html", "kirti_chakra.html", "mahavir_chakra.html", "weapons_ammunition.html"]
    for sp in special_pages:
        if os.path.exists(sp):
            print(f"Processing special exhibit: {sp}", flush=True)
            process_special_exhibit(sp)

    # 2. Process all base art pages
    all_art_files = sorted(glob.glob("art*.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    base_art_files = [f for f in all_art_files if not f.endswith("_hi.html") and not f.endswith("_pa.html") and f != "art_template.html"]
    print(f"Found {len(base_art_files)} base art files to process...", flush=True)

    art_dict = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_map = {executor.submit(process_single_art_page, f, art_dict): f for f in base_art_files}
        done = 0
        for fut in as_completed(future_map):
            done += 1
            if done % 25 == 0 or done == len(base_art_files):
                print(f"Processed {done}/{len(base_art_files)} art pieces...", flush=True)
                save_cache()

    save_cache()

    # 3. Rebuild main gallery index pages
    rebuild_index_pages(art_dict)
    save_cache()

    # 4. Synthesize any missing audio
    asyncio.run(synthesize_all_audio(art_dict))

    print("--- ALL MULTILINGUAL PAGES AND AUDIO COMPLETED SUCCESSFULLY! ---", flush=True)

if __name__ == "__main__":
    main()
