import os
import sys
import re
import glob
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import translators as ts
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

def translate(text, lang):
    text_str = str(text).strip()
    if not text_str or text_str.isdigit() or len(text_str) <= 1:
        return text_str

    with CACHE_LOCK:
        if text_str in CACHE[lang]:
            return CACHE[lang][text_str]

    # Pre-built glossary
    if lang == "hi":
        if text_str == "Back to Home": return "मुख्य पृष्ठ"
        if text_str == "Listen to Narration": return "वर्णन सुनें"
        if text_str == "Pause Audio": return "ऑडियो रोकें"
        if text_str == "Previous Piece": return "पिछली कलाकृति"
        if text_str == "Next Piece": return "अगली कलाकृति"
        if text_str == "Open on Mobile": return "मोबाइल पर खोलें"
        if text_str == "Religious Corner": return "धार्मिक कोना"
        if text_str == "COR Gallery": return "सी.ओ.आर. गैलरी"
        if text_str == "Comdts' Gallery": return "कमांडेंट्स गैलरी"
        if text_str == "Unknown Artist": return "अज्ञात कलाकार"
        if text_str == "Historical Figure": return "ऐतिहासिक व्यक्तित्व"
        if text_str == "Historical": return "ऐतिहासिक"
    elif lang == "pa":
        if text_str == "Back to Home": return "ਮੁੱਖ ਪੰਨਾ"
        if text_str == "Listen to Narration": return "ਵੇਰਵਾ ਸੁਣੋ"
        if text_str == "Pause Audio": return "ਆਡੀਓ ਰੋਕੋ"
        if text_str == "Previous Piece": return "ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ"
        if text_str == "Next Piece": return "ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ"
        if text_str == "Open on Mobile": return "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
        if text_str == "Religious Corner": return "ਧਾਰਮਿਕ ਕੋਨਾ"
        if text_str == "COR Gallery": return "ਸੀ.ਓ.ਆਰ. ਗੈਲਰੀ"
        if text_str == "Comdts' Gallery": return "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ"
        if text_str == "Unknown Artist": return "ਅਣਜਾਣ ਕਲਾਕਾਰ"
        if text_str == "Historical Figure": return "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ"
        if text_str == "Historical": return "ਇਤਿਹਾਸਕ"

    providers = ['bing', 'google', 'alibaba', 'yandex']
    res = None
    for p in providers:
        try:
            res = ts.translate_text(
                text_str,
                from_language='en',
                to_language=lang,
                translator=p,
                timeout=6
            )
            if res and len(res.strip()) > 0:
                break
        except Exception:
            continue

    if not res:
        res = text_str

    with CACHE_LOCK:
        CACHE[lang][text_str] = res
    return res

def get_language_switcher_html(current_page, current_lang):
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

def process_art_page(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    h1 = soup.find("h1")
    title_en = h1.text.strip() if h1 else ""

    audio_tag = soup.find("audio")
    audio_src = audio_tag.get("src", "") if audio_tag else ""
    audio_num_match = re.search(r'audio_(\d+)\.mp3', audio_src)
    art_num = audio_num_match.group(1) if audio_num_match else ""

    boxes = soup.find_all("div", class_="description-box")
    meta_box = boxes[0] if len(boxes) > 0 else None
    narration_box = boxes[1] if len(boxes) > 1 else (boxes[0] if len(boxes) > 0 else None)
    narration_en = narration_box.get_text(separator=' ') if narration_box else ""

    # 1. Update English Page
    soup_en = BeautifulSoup(html, "html.parser")
    gallery_container_en = soup_en.find("div", class_="gallery-container")
    if gallery_container_en:
        ex = soup_en.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html(filename, 'en'), "html.parser")
        gallery_container_en.insert(0, lang_bar_soup)
    
    back_btn_en = soup_en.find("a", href="index.html")
    if back_btn_en:
        back_btn_en["href"] = "index_en.html"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # 2. Generate Hindi Page
    title_hi = translate(title_en, "hi")
    soup_hi = BeautifulSoup(html, "html.parser")
    
    if soup_hi.find("title"):
        soup_hi.find("title").string = f"{title_hi} - विरासत संग्रहालय"
    if soup_hi.find("h1"):
        soup_hi.find("h1").string = title_hi

    gallery_container_hi = soup_hi.find("div", class_="gallery-container")
    if gallery_container_hi:
        ex = soup_hi.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html(f"{os.path.splitext(filename)[0]}_hi.html", 'hi'), "html.parser")
        gallery_container_hi.insert(0, lang_bar_soup)

    home_link_hi = soup_hi.find("a", href="index.html") or soup_hi.find("a", href="index_en.html")
    if home_link_hi:
        home_link_hi["href"] = "index_hi.html"
        for txt_node in list(home_link_hi.find_all(string=True)):
            if "Back to Home" in txt_node:
                txt_node.replace_with(" मुख्य पृष्ठ")

    audio_hi_tag = soup_hi.find("audio")
    if audio_hi_tag and art_num:
        audio_hi_tag["src"] = f"assets/audio_hi/audio_{art_num}.mp3"

    play_btn_hi = soup_hi.find("button", class_="play-btn")
    if play_btn_hi:
        play_btn_hi.clear()
        play_btn_hi.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> वर्णन सुनें', 'html.parser'))

    script_tag_hi = soup_hi.find("script")
    if script_tag_hi and script_tag_hi.string:
        js_str = script_tag_hi.string
        js_str = js_str.replace("Pause Audio", "ऑडियो रोकें").replace("Listen to Narration", "वर्णन सुनें")
        script_tag_hi.string = js_str

    boxes_hi = soup_hi.find_all("div", class_="description-box")
    if len(boxes_hi) > 0:
        m_html = boxes_hi[0].decode_contents()
        m_html = m_html.replace("Title:", "<strong>शीर्षक:</strong>")
        m_html = m_html.replace("Category:", "<strong>श्रेणी:</strong>")
        m_html = m_html.replace("Artist:", "<strong>कलाकार:</strong>")
        m_html = m_html.replace("Year:", "<strong>वर्ष:</strong>")
        m_html = m_html.replace("Religious Corner", "धार्मिक कोना")
        m_html = m_html.replace("COR Gallery", "सी.ओ.आर. गैलरी")
        m_html = m_html.replace("Comdts' Gallery", "कमांडेंट्स गैलरी")
        m_html = m_html.replace("Unknown Artist", "अज्ञात कलाकार")
        m_html = m_html.replace("Historical Figure", "ऐतिहासिक व्यक्तित्व")
        m_html = m_html.replace("Historical", "ऐतिहासिक")
        boxes_hi[0].clear()
        boxes_hi[0].append(BeautifulSoup(m_html, "html.parser"))

    translated_narration_hi = ""
    if len(boxes_hi) > 1:
        n_text = boxes_hi[1].get_text(separator=' ')
        translated_narration_hi = translate(n_text, "hi")
        boxes_hi[1].clear()
        boxes_hi[1].append(BeautifulSoup(f"<strong>{title_hi}</strong><br><br>{translated_narration_hi}", "html.parser"))

    nav_hi = soup_hi.find("div", class_="navigation")
    if nav_hi:
        links = nav_hi.find_all("a", class_="nav-link")
        if len(links) >= 2:
            prev_a, next_a = links[0], links[1]
            if prev_a.get("href") and prev_a["href"].startswith("art"):
                prev_a["href"] = prev_a["href"].replace(".html", "_hi.html")
            if next_a.get("href") and next_a["href"].startswith("art"):
                next_a["href"] = next_a["href"].replace(".html", "_hi.html")
            
            for t in list(prev_a.find_all(string=True)):
                if "Previous Piece" in t: t.replace_with(" पिछली कलाकृति")
            for t in list(next_a.find_all(string=True)):
                if "Next Piece" in t: t.replace_with("अगली कलाकृति ")

        span = nav_hi.find("span")
        if span and span.string:
            span.string = span.string.replace("Piece", "कलाकृति")

    qr_info_hi = soup_hi.find("div", class_="qr-info")
    if qr_info_hi:
        h3 = qr_info_hi.find("h3")
        p = qr_info_hi.find("p")
        if h3: h3.string = "मोबाइल पर खोलें"
        if p: p.string = "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।"

    hi_filepath = os.path.join(os.path.dirname(filepath), f"{os.path.splitext(filename)[0]}_hi.html")
    with open(hi_filepath, "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # 3. Generate Punjabi Page
    title_pa = translate(title_en, "pa")
    soup_pa = BeautifulSoup(html, "html.parser")
    
    if soup_pa.find("title"):
        soup_pa.find("title").string = f"{title_pa} - ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ"
    if soup_pa.find("h1"):
        soup_pa.find("h1").string = title_pa

    gallery_container_pa = soup_pa.find("div", class_="gallery-container")
    if gallery_container_pa:
        ex = soup_pa.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html(f"{os.path.splitext(filename)[0]}_pa.html", 'pa'), "html.parser")
        gallery_container_pa.insert(0, lang_bar_soup)

    home_link_pa = soup_pa.find("a", href="index.html") or soup_pa.find("a", href="index_en.html")
    if home_link_pa:
        home_link_pa["href"] = "index_pa.html"
        for txt_node in list(home_link_pa.find_all(string=True)):
            if "Back to Home" in txt_node:
                txt_node.replace_with(" ਮੁੱਖ ਪੰਨਾ")

    audio_pa_tag = soup_pa.find("audio")
    if audio_pa_tag and art_num:
        audio_pa_tag["src"] = f"assets/audio_pa/audio_{art_num}.mp3"

    play_btn_pa = soup_pa.find("button", class_="play-btn")
    if play_btn_pa:
        play_btn_pa.clear()
        play_btn_pa.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> ਵੇਰਵਾ ਸੁਣੋ', 'html.parser'))

    script_tag_pa = soup_pa.find("script")
    if script_tag_pa and script_tag_pa.string:
        js_str = script_tag_pa.string
        js_str = js_str.replace("Pause Audio", "ਆਡੀਓ ਰੋਕੋ").replace("Listen to Narration", "ਵੇਰਵਾ ਸੁਣੋ")
        script_tag_pa.string = js_str

    boxes_pa = soup_pa.find_all("div", class_="description-box")
    if len(boxes_pa) > 0:
        m_html = boxes_pa[0].decode_contents()
        m_html = m_html.replace("Title:", "<strong>ਸਿਰਲੇਖ:</strong>")
        m_html = m_html.replace("Category:", "<strong>ਸ਼੍ਰੇਣੀ:</strong>")
        m_html = m_html.replace("Artist:", "<strong>ਕਲਾਕਾਰ:</strong>")
        m_html = m_html.replace("Year:", "<strong>ਸਾਲ:</strong>")
        m_html = m_html.replace("Religious Corner", "ਧਾਰਮਿਕ ਕੋਨਾ")
        m_html = m_html.replace("COR Gallery", "ਸੀ.ਓ.ਆਰ. ਗੈਲਰੀ")
        m_html = m_html.replace("Comdts' Gallery", "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ")
        m_html = m_html.replace("Unknown Artist", "ਅਣਜਾਣ ਕਲਾਕਾਰ")
        m_html = m_html.replace("Historical Figure", "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ")
        m_html = m_html.replace("Historical", "ਇਤਿਹਾਸਕ")
        boxes_pa[0].clear()
        boxes_pa[0].append(BeautifulSoup(m_html, "html.parser"))

    translated_narration_pa = ""
    if len(boxes_pa) > 1:
        n_text = boxes_pa[1].get_text(separator=' ')
        translated_narration_pa = translate(n_text, "pa")
        boxes_pa[1].clear()
        boxes_pa[1].append(BeautifulSoup(f"<strong>{title_pa}</strong><br><br>{translated_narration_pa}", "html.parser"))

    nav_pa = soup_pa.find("div", class_="navigation")
    if nav_pa:
        links = nav_pa.find_all("a", class_="nav-link")
        if len(links) >= 2:
            prev_a, next_a = links[0], links[1]
            if prev_a.get("href") and prev_a["href"].startswith("art"):
                prev_a["href"] = prev_a["href"].replace(".html", "_pa.html")
            if next_a.get("href") and next_a["href"].startswith("art"):
                next_a["href"] = next_a["href"].replace(".html", "_pa.html")
            
            for t in list(prev_a.find_all(string=True)):
                if "Previous Piece" in t: t.replace_with(" ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ")
            for t in list(next_a.find_all(string=True)):
                if "Next Piece" in t: t.replace_with("ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ ")

        span = nav_pa.find("span")
        if span and span.string:
            span.string = span.string.replace("Piece", "ਕਲਾਕ੍ਰਿਤੀ")

    qr_info_pa = soup_pa.find("div", class_="qr-info")
    if qr_info_pa:
        h3 = qr_info_pa.find("h3")
        p = qr_info_pa.find("p")
        if h3: h3.string = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
        if p: p.string = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"

    pa_filepath = os.path.join(os.path.dirname(filepath), f"{os.path.splitext(filename)[0]}_pa.html")
    with open(pa_filepath, "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

    return {
        "art_num": art_num,
        "title_hi": title_hi,
        "title_pa": title_pa,
        "narration_hi": translated_narration_hi if translated_narration_hi else title_hi,
        "narration_pa": translated_narration_pa if translated_narration_pa else title_pa,
    }

def process_special_page(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update English special page
    soup_en = BeautifulSoup(html, "html.parser")
    container_en = soup_en.find("div", class_="gallery-container") or soup_en.find("body")
    if container_en:
        ex = soup_en.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html(filename, 'en'), "html.parser")
        container_en.insert(0, lang_bar_soup)
    back_en = soup_en.find("a", href="index.html")
    if back_en: back_en["href"] = "index_en.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # 2. Generate Hindi special page
    soup_hi = BeautifulSoup(html, "html.parser")
    container_hi = soup_hi.find("div", class_="gallery-container") or soup_hi.find("body")
    if container_hi:
        ex = soup_hi.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html(f"{os.path.splitext(filename)[0]}_hi.html", 'hi'), "html.parser")
        container_hi.insert(0, lang_bar_soup)

    back_hi = soup_hi.find("a", href="index.html") or soup_hi.find("a", href="index_en.html")
    if back_hi:
        back_hi["href"] = "index_hi.html"
        for t in list(back_hi.find_all(string=True)):
            if "Back to Home" in t: t.replace_with(" मुख्य पृष्ठ")

    for a in soup_hi.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and not href.endswith("_hi.html") and href != "index.html" and href != "index_hi.html":
            a["href"] = href.replace(".html", "_hi.html")

    hi_path = f"{os.path.splitext(filename)[0]}_hi.html"
    with open(hi_path, "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # 3. Generate Punjabi special page
    soup_pa = BeautifulSoup(html, "html.parser")
    container_pa = soup_pa.find("div", class_="gallery-container") or soup_pa.find("body")
    if container_pa:
        ex = soup_pa.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html(f"{os.path.splitext(filename)[0]}_pa.html", 'pa'), "html.parser")
        container_pa.insert(0, lang_bar_soup)

    back_pa = soup_pa.find("a", href="index.html") or soup_pa.find("a", href="index_en.html")
    if back_pa:
        back_pa["href"] = "index_pa.html"
        for t in list(back_pa.find_all(string=True)):
            if "Back to Home" in t: t.replace_with(" ਮੁੱਖ ਪੰਨਾ")

    for a in soup_pa.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and not href.endswith("_pa.html") and href != "index.html" and href != "index_pa.html":
            a["href"] = href.replace(".html", "_pa.html")

    pa_path = f"{os.path.splitext(filename)[0]}_pa.html"
    with open(pa_path, "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

def generate_index_galleries():
    with open("index_en.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update index_en.html with Language Switcher
    soup_en = BeautifulSoup(html, "html.parser")
    container_en = soup_en.find("div", class_="gallery-container")
    if container_en:
        ex = soup_en.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html("index_en.html", 'en'), "html.parser")
        container_en.insert(0, lang_bar_soup)
    with open("index_en.html", "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # 2. Generate index_hi.html
    soup_hi = BeautifulSoup(html, "html.parser")
    if soup_hi.find("title"):
        soup_hi.find("title").string = "विरासत संग्रहालय - मुख्य गैलरी"
    
    container_hi = soup_hi.find("div", class_="gallery-container")
    if container_hi:
        ex = soup_hi.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html("index_hi.html", 'hi'), "html.parser")
        container_hi.insert(0, lang_bar_soup)

    for btn in soup_hi.find_all("button", class_="nav-btn"):
        txt = btn.text.strip()
        btn.string = translate(txt.replace("▼", "").strip(), "hi") + " ▼"

    for a in soup_hi.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and href != "index.html":
            a["href"] = href.replace(".html", "_hi.html")
        a_txt = a.text.strip()
        if a_txt:
            a.string = translate(a_txt, "hi")

    with open("index_hi.html", "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # 3. Generate index_pa.html
    soup_pa = BeautifulSoup(html, "html.parser")
    if soup_pa.find("title"):
        soup_pa.find("title").string = "ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ - ਮੁੱਖ ਗੈਲਰੀ"
    
    container_pa = soup_pa.find("div", class_="gallery-container")
    if container_pa:
        ex = soup_pa.find("div", class_="lang-switch-bar")
        if ex: ex.decompose()
        lang_bar_soup = BeautifulSoup(get_language_switcher_html("index_pa.html", 'pa'), "html.parser")
        container_pa.insert(0, lang_bar_soup)

    for btn in soup_pa.find_all("button", class_="nav-btn"):
        txt = btn.text.strip()
        btn.string = translate(txt.replace("▼", "").strip(), "pa") + " ▼"

    for a in soup_pa.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and href != "index.html":
            a["href"] = href.replace(".html", "_pa.html")
        a_txt = a.text.strip()
        if a_txt:
            a.string = translate(a_txt, "pa")

    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

    print("index_en.html, index_hi.html, index_pa.html generated successfully!", flush=True)

async def synth_all_hi_audio(items):
    print("Starting Async Edge-TTS for Hindi Audio...", flush=True)
    semaphore = asyncio.Semaphore(6)
    
    async def synth_one(r):
        num = r.get("art_num")
        if not num: return
        path = os.path.join(AUDIO_HI_DIR, f"audio_{num}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return
        clean_text = re.sub(r'<[^>]+>', ' ', r["narration_hi"]).strip()
        if not clean_text: return
        async with semaphore:
            try:
                comm = edge_tts.Communicate(clean_text, 'hi-IN-MadhurNeural')
                await comm.save(path)
            except Exception:
                try:
                    tts = gTTS(text=clean_text, lang='hi')
                    tts.save(path)
                except Exception:
                    pass

    tasks = [synth_one(r) for r in items]
    for i in range(0, len(tasks), 20):
        batch = tasks[i:i+20]
        await asyncio.gather(*batch)
        print(f"Hindi audio batch {min(i+20, len(tasks))}/{len(tasks)} complete...", flush=True)
    print("All Hindi Audio generated!", flush=True)

def synth_all_pa_audio(items):
    print("Starting Parallel gTTS for Punjabi Audio...", flush=True)
    def synth_one(r):
        num = r.get("art_num")
        if not num: return
        path = os.path.join(AUDIO_PA_DIR, f"audio_{num}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return
        clean_text = re.sub(r'<[^>]+>', ' ', r["narration_pa"]).strip()
        if not clean_text: return
        try:
            tts = gTTS(text=clean_text, lang='pa')
            tts.save(path)
        except Exception as e:
            pass

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(synth_one, r) for r in items]
        cnt = 0
        for f in as_completed(futures):
            cnt += 1
            if cnt % 20 == 0 or cnt == len(items):
                print(f"Punjabi audio {cnt}/{len(items)} complete...", flush=True)
    print("All Punjabi Audio generated!", flush=True)

def main():
    special_pages = ["coas_citations.html", "kirti_chakra.html", "mahavir_chakra.html", "weapons_ammunition.html"]
    for sp in special_pages:
        if os.path.exists(sp):
            process_special_page(sp)
    print("Special exhibition pages processed!", flush=True)

    art_files = sorted(glob.glob("art*.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    art_files = [f for f in art_files if not f.endswith("_hi.html") and not f.endswith("_pa.html") and f != "art_template.html"]
    print(f"Processing {len(art_files)} art pieces in parallel (12 workers)...", flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_file = {executor.submit(process_art_page, f): f for f in art_files}
        count = 0
        for future in as_completed(future_to_file):
            f = future_to_file[future]
            try:
                res = future.result()
                results.append(res)
                count += 1
                if count % 20 == 0 or count == len(art_files):
                    print(f"Processed {count}/{len(art_files)} pages...", flush=True)
                    save_cache()
            except Exception as e:
                print(f"Error on {f}: {e}", flush=True)

    save_cache()
    print("All art pages processed!", flush=True)

    generate_index_galleries()
    save_cache()

    # Synthesize Audio files
    asyncio.run(synth_all_hi_audio(results))
    synth_all_pa_audio(results)

    print("ALL MULTILINGUAL TASKS COMPLETED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    main()
