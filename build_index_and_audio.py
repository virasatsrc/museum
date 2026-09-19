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

with open(CACHE_FILE, "r", encoding="utf-8") as f:
    CACHE = json.load(f)

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
            if cached_val and cached_val != text_str:
                return cached_val

    # If text is long, chunk by paragraphs
    if len(text_str) > 1000:
        paragraphs = text_str.split('\n')
        translated_paras = []
        for p in paragraphs:
            p_strip = p.strip()
            if not p_strip:
                translated_paras.append('')
                continue
            translated_paras.append(translate_text(p_strip, lang))
        result = "\n".join(translated_paras)
        with CACHE_LOCK:
            CACHE[lang][text_str] = result
        return result

    # Perform GoogleTranslator via deep_translator
    res = None
    try:
        translator = GoogleTranslator(source='en', target=lang)
        res = translator.translate(text_str)
    except Exception:
        pass

    if not res:
        res = text_str

    with CACHE_LOCK:
        CACHE[lang][text_str] = res
    return res

def batch_translate(texts, lang):
    with ThreadPoolExecutor(max_workers=12) as ex:
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

def load_all_art_metadata():
    art_dict = {}
    base_art_files = sorted(glob.glob("art*.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    base_art_files = [f for f in base_art_files if not f.endswith("_hi.html") and not f.endswith("_pa.html") and f != "art_template.html"]
    
    for f in base_art_files:
        hi_f = f.replace(".html", "_hi.html")
        pa_f = f.replace(".html", "_pa.html")
        
        soup_en = BeautifulSoup(open(f, encoding="utf-8"), "html.parser")
        title_en = soup_en.find("h1").text.strip() if soup_en.find("h1") else ""
        
        title_hi = ""
        narr_hi = ""
        if os.path.exists(hi_f):
            soup_hi = BeautifulSoup(open(hi_f, encoding="utf-8"), "html.parser")
            title_hi = soup_hi.find("h1").text.strip() if soup_hi.find("h1") else ""
            boxes_hi = soup_hi.find_all("div", class_="description-box")
            narr_hi = boxes_hi[1].get_text(separator=' ') if len(boxes_hi) > 1 else title_hi

        title_pa = ""
        narr_pa = ""
        if os.path.exists(pa_f):
            soup_pa = BeautifulSoup(open(pa_f, encoding="utf-8"), "html.parser")
            title_pa = soup_pa.find("h1").text.strip() if soup_pa.find("h1") else ""
            boxes_pa = soup_pa.find_all("div", class_="description-box")
            narr_pa = boxes_pa[1].get_text(separator=' ') if len(boxes_pa) > 1 else title_pa

        audio_tag = soup_en.find("audio")
        audio_src = audio_tag.get("src", "") if audio_tag else ""
        m = re.search(r'audio_(\d+)\.mp3', audio_src)
        art_num = m.group(1) if m else os.path.splitext(f)[0].replace("art", "")

        art_dict[f] = {
            "art_num": art_num,
            "title_en": title_en,
            "title_hi": title_hi if title_hi else translate_text(title_en, "hi"),
            "title_pa": title_pa if title_pa else translate_text(title_en, "pa"),
            "narration_hi": narr_hi,
            "narration_pa": narr_pa
        }
    return art_dict

def generate_index_pages(art_dict):
    print("Generating index_en.html, index_hi.html, index_pa.html...", flush=True)
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

    # --- 2. Build index_hi.html ---
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

    # Links in nav & photo nav
    links_hi = soup_hi.find_all("a", href=True)
    for a in links_hi:
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

    # Scroller Captions (batch translate)
    all_caps_nodes_hi = soup_hi.find_all("div", class_="ramgarh-caption")
    all_caps_text_hi = [c.text.strip() for c in all_caps_nodes_hi]
    translated_caps_hi = batch_translate(all_caps_text_hi, "hi")
    for idx, c in enumerate(all_caps_nodes_hi):
        c.string = translated_caps_hi[idx]

    # Description boxes
    all_dboxes_hi = soup_hi.find_all("div", class_="description-box")
    all_dboxes_text_hi = [d.get_text(separator='\n').strip() for d in all_dboxes_hi]
    translated_dboxes_hi = batch_translate(all_dboxes_text_hi, "hi")
    for idx, dbox in enumerate(all_dboxes_hi):
        lines = [l.strip() for l in translated_dboxes_hi[idx].split('\n') if l.strip()]
        if lines:
            header = lines[0]
            body = "<br><br>".join(lines[1:])
            dbox.clear()
            dbox.append(BeautifulSoup(f"<strong>{header}</strong><br><br>{body}", "html.parser"))

    # Ishar Singh box
    ishar_box_hi = soup_hi.find("div", class_="ishar-singh-box")
    if ishar_box_hi:
        p_nodes = ishar_box_hi.find_all("p")
        p_texts = [p.get_text().strip() for p in p_nodes]
        trans_ps = batch_translate(p_texts, "hi")
        for idx, p in enumerate(p_nodes):
            p.string = trans_ps[idx]
        
        bquote = ishar_box_hi.find("blockquote")
        if bquote:
            b_txt = bquote.get_text().strip().replace('“','').replace('”','')
            bquote.string = f"“{translate_text(b_txt, 'hi')}”"

    h3_ctb_hi = soup_hi.find("h3")
    if h3_ctb_hi and "A Legacy of Valour" in h3_ctb_hi.text:
        h3_ctb_hi.string = "वीरता की विरासत"

    p_ctb_hi = soup_hi.find("p", style=re.compile(r"font-style:\s*italic"))
    if p_ctb_hi and "An Illustrated History" in p_ctb_hi.text:
        p_ctb_hi.string = "सिख रेजिमेंट का एक सचित्र इतिहास (1846 से 2010)"

    qr_hi = soup_hi.find("div", class_="qr-info")
    if qr_hi:
        h3 = qr_hi.find("h3")
        p = qr_hi.find("p")
        if h3: h3.string = "मोबाइल पर खोलें"
        if p: p.string = "अपने फोन पर इस गैलरी को देखने के लिए स्कैन करें।"

    with open("index_hi.html", "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # --- 3. Build index_pa.html ---
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

    # Links in nav & photo nav
    links_pa = soup_pa.find_all("a", href=True)
    for a in links_pa:
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

    # Scroller Captions (batch translate)
    all_caps_nodes_pa = soup_pa.find_all("div", class_="ramgarh-caption")
    all_caps_text_pa = [c.text.strip() for c in all_caps_nodes_pa]
    translated_caps_pa = batch_translate(all_caps_text_pa, "pa")
    for idx, c in enumerate(all_caps_nodes_pa):
        c.string = translated_caps_pa[idx]

    # Description boxes
    all_dboxes_pa = soup_pa.find_all("div", class_="description-box")
    all_dboxes_text_pa = [d.get_text(separator='\n').strip() for d in all_dboxes_pa]
    translated_dboxes_pa = batch_translate(all_dboxes_text_pa, "pa")
    for idx, dbox in enumerate(all_dboxes_pa):
        lines = [l.strip() for l in translated_dboxes_pa[idx].split('\n') if l.strip()]
        if lines:
            header = lines[0]
            body = "<br><br>".join(lines[1:])
            dbox.clear()
            dbox.append(BeautifulSoup(f"<strong>{header}</strong><br><br>{body}", "html.parser"))

    # Ishar Singh box
    ishar_box_pa = soup_pa.find("div", class_="ishar-singh-box")
    if ishar_box_pa:
        p_nodes = ishar_box_pa.find_all("p")
        p_texts = [p.get_text().strip() for p in p_nodes]
        trans_ps = batch_translate(p_texts, "pa")
        for idx, p in enumerate(p_nodes):
            p.string = trans_ps[idx]
        
        bquote = ishar_box_pa.find("blockquote")
        if bquote:
            b_txt = bquote.get_text().strip().replace('“','').replace('”','')
            bquote.string = f"“{translate_text(b_txt, 'pa')}”"

    h3_ctb_pa = soup_pa.find("h3")
    if h3_ctb_pa and "A Legacy of Valour" in h3_ctb_pa.text:
        h3_ctb_pa.string = "ਬਹਾਦਰੀ ਦੀ ਵਿਰਾਸਤ"

    p_ctb_pa = soup_pa.find("p", style=re.compile(r"font-style:\s*italic"))
    if p_ctb_pa and "An Illustrated History" in p_ctb_pa.text:
        p_ctb_pa.string = "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਇੱਕ ਚਿੱਤਰਿਤ ਇਤਿਹਾਸ (1846 ਤੋਂ 2010)"

    qr_pa = soup_pa.find("div", class_="qr-info")
    if qr_pa:
        h3 = qr_pa.find("h3")
        p = qr_pa.find("p")
        if h3: h3.string = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
        if p: p.string = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਗੈਲਰੀ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"

    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

    print("Index galleries generated successfully!", flush=True)

async def synthesize_all_audio(art_dict):
    print("Checking and generating audio narrations...", flush=True)
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
    art_dict = load_all_art_metadata()
    print(f"Loaded metadata for {len(art_dict)} art pieces.", flush=True)
    generate_index_pages(art_dict)
    save_cache()
    asyncio.run(synthesize_all_audio(art_dict))
    print("--- COMPLETE INDEX AND AUDIO REBUILD FINISHED! ---", flush=True)

if __name__ == "__main__":
    main()
