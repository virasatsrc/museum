import os
import sys
import re
import glob
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import edge_tts
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')

AUDIO_HI_DIR = os.path.join("assets", "audio_hi")
AUDIO_PA_DIR = os.path.join("assets", "audio_pa")

os.makedirs(AUDIO_HI_DIR, exist_ok=True)
os.makedirs(AUDIO_PA_DIR, exist_ok=True)

# Build a dictionary of art titles and narrations from generated files
def load_art_metadata():
    art_meta = {}
    hi_files = sorted(glob.glob("art*_hi.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    for f in hi_files:
        base_name = f.replace("_hi.html", ".html")
        pa_file = f.replace("_hi.html", "_pa.html")
        
        soup_hi = BeautifulSoup(open(f, encoding="utf-8"), "html.parser")
        title_hi = soup_hi.find("h1").text.strip() if soup_hi.find("h1") else ""
        
        # Narration text
        boxes_hi = soup_hi.find_all("div", class_="description-box")
        narr_hi = boxes_hi[1].get_text(separator=' ') if len(boxes_hi) > 1 else title_hi

        title_pa = ""
        narr_pa = ""
        if os.path.exists(pa_file):
            soup_pa = BeautifulSoup(open(pa_file, encoding="utf-8"), "html.parser")
            title_pa = soup_pa.find("h1").text.strip() if soup_pa.find("h1") else ""
            boxes_pa = soup_pa.find_all("div", class_="description-box")
            narr_pa = boxes_pa[1].get_text(separator=' ') if len(boxes_pa) > 1 else title_pa

        audio_tag = soup_hi.find("audio")
        audio_src = audio_tag.get("src", "") if audio_tag else ""
        match = re.search(r'audio_(\d+)\.mp3', audio_src)
        art_num = match.group(1) if match else ""

        art_meta[base_name] = {
            "art_num": art_num,
            "title_hi": title_hi,
            "title_pa": title_pa,
            "narr_hi": narr_hi,
            "narr_pa": narr_pa
        }
    return art_meta

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

def generate_index_galleries(art_meta):
    print("Generating Index Galleries (English, Hindi, Punjabi)...")
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

    # Menu translations map
    nav_hi_map = {
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
        "Historic Photos & Archives": "ऐतिहासिक तस्वीरें एवं अभिलेखागार"
    }

    nav_pa_map = {
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
        "Historic Photos & Archives": "ਇਤਿਹਾਸਕ ਤਸਵੀਰਾਂ ਅਤੇ ਪੁਰਾਲੇਖ"
    }

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
        txt = btn.text.strip().replace("▼", "").strip()
        trans = nav_hi_map.get(txt, txt)
        btn.string = f"{trans} ▼"

    for a in soup_hi.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and href != "index.html":
            a["href"] = href.replace(".html", "_hi.html")
            if href in art_meta and art_meta[href]["title_hi"]:
                a.string = art_meta[href]["title_hi"]

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
        txt = btn.text.strip().replace("▼", "").strip()
        trans = nav_pa_map.get(txt, txt)
        btn.string = f"{trans} ▼"

    for a in soup_pa.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http") and href != "index.html":
            a["href"] = href.replace(".html", "_pa.html")
            if href in art_meta and art_meta[href]["title_pa"]:
                a.string = art_meta[href]["title_pa"]

    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

    print("Index Galleries generated successfully!")

async def synth_hi_batch(items):
    print("Generating Hindi Audio via Edge-TTS (Madhur Neural voice)...", flush=True)
    semaphore = asyncio.Semaphore(8)

    async def synth_one(art_num, text):
        if not art_num: return
        path = os.path.join(AUDIO_HI_DIR, f"audio_{art_num}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return
        clean_text = re.sub(r'<[^>]+>', ' ', text).strip()
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

    tasks = [synth_one(meta["art_num"], meta["narr_hi"]) for meta in items.values() if meta.get("art_num")]
    for i in range(0, len(tasks), 25):
        batch = tasks[i:i+25]
        await asyncio.gather(*batch)
        print(f"Hindi audio batch {min(i+25, len(tasks))}/{len(tasks)} complete...", flush=True)
    print("All Hindi Audio files created successfully!", flush=True)

def synth_pa_batch(items):
    print("Generating Punjabi Audio via gTTS (Punjabi voice)...", flush=True)
    def synth_one(meta):
        art_num = meta.get("art_num")
        if not art_num: return
        path = os.path.join(AUDIO_PA_DIR, f"audio_{art_num}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return
        clean_text = re.sub(r'<[^>]+>', ' ', meta.get("narr_pa", "")).strip()
        if not clean_text: return
        try:
            tts = gTTS(text=clean_text, lang='pa')
            tts.save(path)
        except Exception:
            pass

    items_list = [v for v in items.values() if v.get("art_num")]
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(synth_one, m) for m in items_list]
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 25 == 0 or done == len(items_list):
                print(f"Punjabi audio {done}/{len(items_list)} complete...", flush=True)
    print("All Punjabi Audio files created successfully!", flush=True)

def main():
    art_meta = load_art_metadata()
    print(f"Loaded metadata for {len(art_meta)} art pieces.")

    generate_index_galleries(art_meta)

    asyncio.run(synth_hi_batch(art_meta))
    synth_pa_batch(art_meta)

    print("ALL MULTILINGUAL GENERATION & SYNTHESIS COMPLETE!", flush=True)

if __name__ == "__main__":
    main()
