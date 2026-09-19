import os
import sys
import re
import glob
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

AUDIO_PA_DIR = os.path.join("assets", "audio_pa")
os.makedirs(AUDIO_PA_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. AUDIO SYNTHESIS FOR PUNJABI
# -------------------------------------------------------------

def synth_punjabi_audio(text, out_path, max_retries=3):
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    if not clean_text:
        return False

    # Split text into chunks of <= 180 chars at word boundaries
    words = clean_text.split(' ')
    chunks = []
    curr = ''
    for w in words:
        if len(curr) + len(w) + 1 <= 180:
            curr = curr + (' ' if curr else '') + w
        else:
            if curr: chunks.append(curr)
            curr = w
    if curr: chunks.append(curr)

    url = 'https://translate.google.com/translate_tts'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    all_audio = bytearray()
    for idx, chunk in enumerate(chunks):
        chunk_success = False
        for attempt in range(max_retries):
            try:
                params = {'ie': 'UTF-8', 'q': chunk, 'tl': 'pa', 'client': 'tw-ob'}
                r = requests.get(url, params=params, headers=headers, timeout=12)
                if r.status_code == 200 and len(r.content) > 500:
                    all_audio.extend(r.content)
                    chunk_success = True
                    break
                else:
                    time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        if not chunk_success:
            print(f"Warning: Failed chunk {idx+1}/{len(chunks)} for {os.path.basename(out_path)}")

    if len(all_audio) > 1000:
        with open(out_path, 'wb') as f:
            f.write(all_audio)
        return True
    return False

def generate_all_punjabi_audios():
    print("=== Generating Authentic Punjabi Audio for All Exhibits ===", flush=True)
    pa_files = sorted(glob.glob("art*_pa.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    
    tasks = []
    for f in pa_files:
        soup = BeautifulSoup(open(f, encoding='utf-8'), 'html.parser')
        
        # Get art number
        audio_tag = soup.find("audio")
        audio_src = audio_tag.get("src", "") if audio_tag else ""
        m = re.search(r'audio_(\d+)\.mp3', audio_src)
        if m:
            art_num = m.group(1)
        else:
            base = os.path.basename(f).replace("_pa.html", "").replace("art", "")
            art_num = base

        boxes = soup.find_all("div", class_="description-box")
        title = soup.find("h1").text.strip() if soup.find("h1") else ""
        if len(boxes) > 1:
            narr = boxes[1].get_text(separator=' ')
        elif len(boxes) == 1:
            narr = boxes[0].get_text(separator=' ')
        else:
            narr = title

        # Combine title and narration for rich narration experience
        full_text = f"{title}. {narr}"
        out_path = os.path.join(AUDIO_PA_DIR, f"audio_{art_num}.mp3")
        tasks.append((art_num, full_text, out_path))

    print(f"Synthesizing {len(tasks)} Punjabi audio files with 8 threads...", flush=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_art = {executor.submit(synth_punjabi_audio, text, out_p): num for (num, text, out_p) in tasks}
        completed = 0
        for future in as_completed(future_to_art):
            completed += 1
            num = future_to_art[future]
            try:
                res = future.result()
                if completed % 20 == 0 or completed == len(tasks):
                    print(f"Punjabi audio generation: {completed}/{len(tasks)} completed...", flush=True)
            except Exception as e:
                print(f"Error synthesizing art {num}: {e}", flush=True)

    print("All Punjabi Audio Files Generated Successfully!", flush=True)

# -------------------------------------------------------------
# 2. FIX LANGUAGE SWITCHER BARS ACROSS ALL HTML PAGES
# -------------------------------------------------------------

def build_lang_bar(page_type, root_name, lang):
    """
    Constructs the standard language switcher bar HTML.
    root_name: e.g. 'art1', 'coas_citations', 'index'
    lang: 'en', 'hi', or 'pa'
    """
    if root_name in ["index", "index_en", "index_hi", "index_pa"]:
        en_url = "index_en.html"
        hi_url = "index_hi.html"
        pa_url = "index_pa.html"
        portal_url = "index.html"
    else:
        en_url = f"{root_name}.html"
        hi_url = f"{root_name}_hi.html"
        pa_url = f"{root_name}_pa.html"
        portal_url = "index.html"

    en_style = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;"' if lang == 'en' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'
    hi_style = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;"' if lang == 'hi' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'
    pa_style = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;"' if lang == 'pa' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'

    portal_label = "🏛️ Language Portal" if lang == 'en' else ("🏛️ भाषा चयन" if lang == 'hi' else "🏛️ ਭਾਸ਼ਾ ਚੋਣ")

    return f"""<div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
<a class="nav-link" href="{portal_url}" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
    {portal_label}
</a>
<div style="display: flex; gap: 8px; align-items: center;">
<a class="nav-link" href="{en_url}" {en_style}>🇬🇧 English</a>
<a class="nav-link" href="{hi_url}" {hi_style}>🇮🇳 हिन्दी</a>
<a class="nav-link" href="{pa_url}" {pa_style}>ੴ ਪੰਜਾਬੀ</a>
</div>
</div>"""

def process_html_file(filepath):
    filename = os.path.basename(filepath)
    if filename in ["index.html", "art_template.html", "index_template.html"]:
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # Determine language and root
    if filename.endswith("_hi.html"):
        lang = "hi"
        root = filename.replace("_hi.html", "")
        home_href = "index_hi.html"
        home_text = " मुख्य पृष्ठ"
    elif filename.endswith("_pa.html"):
        lang = "pa"
        root = filename.replace("_pa.html", "")
        home_href = "index_pa.html"
        home_text = " ਮੁੱਖ ਪੰਨਾ"
    else:
        lang = "en"
        root = filename.replace(".html", "")
        home_href = "index_en.html"
        home_text = " Back to Home"

    if root in ["index", "index_en"]:
        root = "index"

    # 1. Update internal links (Previous/Next/Nav/Dropdowns) EXCLUDING the lang-switch-bar
    # Remove existing lang-switch-bars first
    for bar in soup.find_all("div", class_="lang-switch-bar"):
        bar.decompose()

    # Update all <a> links currently in document to match language
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".html") and not href.startswith("http"):
            # Check if it's an index/home link
            if href in ["index.html", "index_en.html", "index_hi.html", "index_pa.html"]:
                # If this is a Back to Home button or in gallery
                if "Back to Home" in a.text or "मुख्य पृष्ठ" in a.text or "ਮੁੱਖ ਪੰਨਾ" in a.text or "home" in a.get("class", []):
                    a["href"] = home_href
                    for t in list(a.find_all(string=True)):
                        if "Back to Home" in t or "मुख्य पृष्ठ" in t or "ਮੁੱਖ ਪੰਨਾ" in t:
                            t.replace_with(home_text)
            else:
                # Content page link (e.g. art2.html, mahavir_chakra.html)
                base = href.replace("_hi.html", ".html").replace("_pa.html", ".html")
                target_root = os.path.splitext(base)[0]
                if lang == "hi":
                    a["href"] = f"{target_root}_hi.html"
                elif lang == "pa":
                    a["href"] = f"{target_root}_pa.html"
                else:
                    a["href"] = f"{target_root}.html"

    # 2. Insert pristine Language Switcher Bar at the top of container or body
    bar_html = build_lang_bar("gallery" if root == "index" else "art", root, lang)
    bar_soup = BeautifulSoup(bar_html, "html.parser")
    container = soup.find("div", class_="gallery-container") or soup.find("body")
    if container:
        container.insert(0, bar_soup)

    # 3. Ensure audio tag is correct
    if root != "index":
        audio_tag = soup.find("audio")
        if audio_tag:
            audio_src = audio_tag.get("src", "")
            m = re.search(r'audio_(\d+)\.mp3', audio_src)
            num = m.group(1) if m else root.replace("art", "")
            if lang == "pa":
                audio_tag["src"] = f"assets/audio_pa/audio_{num}.mp3"
            elif lang == "hi":
                audio_tag["src"] = f"assets/audio_hi/audio_{num}.mp3"
            else:
                audio_tag["src"] = f"assets/audio/audio_{num}.mp3"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

def update_all_html_files():
    print("=== Updating Language Switcher Bars Across All HTML Files ===", flush=True)
    all_html = sorted(glob.glob("*.html"))
    count = 0
    for f in all_html:
        if f not in ["index.html", "art_template.html", "index_template.html"]:
            process_html_file(f)
            count += 1
    print(f"Successfully processed and updated {count} HTML files!", flush=True)

def main():
    # Step 1: Synthesize all Punjabi audio
    generate_all_punjabi_audios()

    # Step 2: Update all HTML files with functional language switchers
    update_all_html_files()

    print("=== ALL TASKS COMPLETED SUCCESSFULLY! ===", flush=True)

if __name__ == "__main__":
    main()
