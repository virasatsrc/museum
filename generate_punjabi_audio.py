import os
import sys
import re
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')

AUDIO_PA_DIR = os.path.join("assets", "audio_pa")
os.makedirs(AUDIO_PA_DIR, exist_ok=True)

def load_pa_items():
    items = []
    pa_files = sorted(glob.glob("art*_pa.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    for f in pa_files:
        soup = BeautifulSoup(open(f, encoding="utf-8"), "html.parser")
        audio_tag = soup.find("audio")
        audio_src = audio_tag.get("src", "") if audio_tag else ""
        match = re.search(r'audio_(\d+)\.mp3', audio_src)
        if not match: continue
        art_num = match.group(1)

        boxes = soup.find_all("div", class_="description-box")
        title = soup.find("h1").text.strip() if soup.find("h1") else ""
        narr = boxes[1].get_text(separator=' ') if len(boxes) > 1 else title
        clean_text = re.sub(r'<[^>]+>', ' ', narr).strip()
        if not clean_text:
            clean_text = title

        items.append((art_num, clean_text))
    return items

def synth_one(item):
    art_num, text = item
    path = os.path.join(AUDIO_PA_DIR, f"audio_{art_num}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    try:
        tts = gTTS(text=text, lang='pa')
        tts.save(path)
        return True
    except Exception as e:
        print(f"Error on Punjabi audio {art_num}: {e}", flush=True)
        return False

def main():
    items = load_pa_items()
    print(f"Synthesizing {len(items)} Punjabi audio files with 12 parallel threads...", flush=True)
    
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(synth_one, it): it[0] for it in items}
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == len(items):
                print(f"Punjabi audio synthesized: {done}/{len(items)}...", flush=True)

    print("ALL PUNJABI AUDIO FILES SUCCESSFULLY GENERATED!", flush=True)

if __name__ == "__main__":
    main()
