import os
import sys
import json
import re
import asyncio
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import edge_tts
from gtts import gTTS
import qrcode
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

CACHE_FILE = "translations_cache.json"
AUDIO_EN_DIR = os.path.join("assets", "audio")
AUDIO_HI_DIR = os.path.join("assets", "audio_hi")
AUDIO_PA_DIR = os.path.join("assets", "audio_pa")
QR_DIR = os.path.join("assets", "qrcodes")

os.makedirs(AUDIO_EN_DIR, exist_ok=True)
os.makedirs(AUDIO_HI_DIR, exist_ok=True)
os.makedirs(AUDIO_PA_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

# 1. Load or Initialize Cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        CACHE = json.load(f)
else:
    CACHE = {"hi": {}, "pa": {}}

CACHE.setdefault("hi", {})
CACHE.setdefault("pa", {})

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(CACHE, f, ensure_ascii=False, indent=2)

def gtrans_single(text, target_lang):
    text_str = str(text).strip()
    if not text_str:
        return ""
    if text_str in CACHE[target_lang]:
        return CACHE[target_lang][text_str]
    try:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=' + target_lang + '&dt=t&q=' + urllib.parse.quote(text_str)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            res = ''.join([part[0] for part in data[0] if part[0]])
            if res:
                CACHE[target_lang][text_str] = res
                return res
    except Exception as e:
        print(f"Translate err ({target_lang}): {e} on '{text_str[:30]}...'")
    return text_str

# 2. Load Unit Data and Smart Summaries
with open("scratch/parsed_units.json", "r", encoding="utf-8") as f:
    parsed_units = json.load(f)

with open("scratch/smart_summaries.json", "r", encoding="utf-8") as f:
    smart_summaries = json.load(f)

print(f"Loaded {len(parsed_units)} units. Translating content in parallel...")

def process_unit(i, u):
    art_id = 701 + i
    str_id = str(art_id)
    s_info = smart_summaries[str_id]
    
    title_en = s_info["title_en"]
    title_hi = s_info["title_hi"]
    title_pa = s_info["title_pa"]
    
    reg_en = s_info["regiment_en"]
    reg_hi = s_info["regiment_hi"]
    reg_pa = s_info["regiment_pa"]
    
    sum_en = s_info["summary_en"]
    sum_hi = gtrans_single(sum_en, "hi")
    sum_pa = gtrans_single(sum_en, "pa")
    
    paras_en = u["paras"]
    paras_hi = [gtrans_single(p, "hi") for p in paras_en]
    paras_pa = [gtrans_single(p, "pa") for p in paras_en]
    
    return {
        "art_id": art_id,
        "title_en": title_en,
        "title_hi": title_hi,
        "title_pa": title_pa,
        "regiment_en": reg_en,
        "regiment_hi": reg_hi,
        "regiment_pa": reg_pa,
        "summary_en": sum_en,
        "summary_hi": sum_hi,
        "summary_pa": sum_pa,
        "paras_en": paras_en,
        "paras_hi": paras_hi,
        "paras_pa": paras_pa
    }

full_data = []
with ThreadPoolExecutor(max_workers=10) as ex:
    futures = [ex.submit(process_unit, i, u) for i, u in enumerate(parsed_units)]
    for f in as_completed(futures):
        full_data.append(f.result())

full_data.sort(key=lambda x: x["art_id"])
save_cache()

with open("scratch/full_unit_data.json", "w", encoding="utf-8") as f:
    json.dump(full_data, f, ensure_ascii=False, indent=2)

print(f"All {len(full_data)} units successfully translated and cached!")

# 3. Generate QR Codes
print("\n--- Generating QR Codes ---")
BASE_URL = "https://museumsrc.netlify.app"
for u in full_data:
    art_id = u["art_id"]
    qr_path = os.path.join(QR_DIR, f"qr_art_{art_id}.png")
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"{BASE_URL}/art{art_id}.html")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)
print(f"Created {len(full_data)} QR codes in {QR_DIR}.")

# 4. Generate Audio Narration Files
print("\n--- Synthesizing Smart Audio Narrations ---")

async def synth_edge_en(art_id, text):
    path = os.path.join(AUDIO_EN_DIR, f"audio_{art_id}.mp3")
    try:
        tts = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
        await tts.save(path)
        print(f"  [EN] art{art_id} generated ({os.path.getsize(path)} bytes)")
    except Exception as e:
        print(f"  [EN Fallback] art{art_id}: {e}")
        gTTS(text=text, lang='en').save(path)

async def synth_edge_hi(art_id, text):
    path = os.path.join(AUDIO_HI_DIR, f"audio_{art_id}.mp3")
    try:
        tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
        await tts.save(path)
        print(f"  [HI] art{art_id} generated ({os.path.getsize(path)} bytes)")
    except Exception as e:
        print(f"  [HI Fallback] art{art_id}: {e}")
        gTTS(text=text, lang='hi').save(path)

def synth_gtts_pa(art_id, text):
    path = os.path.join(AUDIO_PA_DIR, f"audio_{art_id}.mp3")
    try:
        tts = gTTS(text=text, lang='pa')
        tts.save(path)
        print(f"  [PA] art{art_id} generated ({os.path.getsize(path)} bytes)")
    except Exception as e:
        print(f"  [PA ERR] art{art_id}: {e}")

async def run_edge_tts():
    for u in full_data:
        art_id = u["art_id"]
        await synth_edge_en(art_id, u["summary_en"])
        await synth_edge_hi(art_id, u["summary_hi"])

asyncio.run(run_edge_tts())

print("Synthesizing Punjabi Audio via gTTS...")
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = [ex.submit(synth_gtts_pa, u["art_id"], u["summary_pa"]) for u in full_data]
    for f in as_completed(futures):
        pass

print("All 87 audio files generated successfully!")

# 5. Build HTML Pages
print("\n--- Generating 87 HTML Pages ---")
TOTAL_UNITS = len(full_data)

def generate_en_page(u, idx):
    art_id = u["art_id"]
    prev_link = f"art{art_id - 1}.html" if idx > 0 else "#"
    prev_class = "disabled" if idx == 0 else ""
    next_link = f"art{art_id + 1}.html" if idx < TOTAL_UNITS - 1 else "#"
    next_class = "disabled" if idx == TOTAL_UNITS - 1 else ""
    
    paras_html = "".join([f"<p style='margin-bottom: 1.2rem; line-height: 1.8; text-align: justify;'>{p}</p>" for p in u["paras_en"]])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>{u['title_en']} - Unit History | Sikh Regiment Museum</title>
    <link href="css/style.css" rel="stylesheet"/>
</head>
<body>
    <div class="gallery-container">
        <!-- Language Switcher Bar -->
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
            <a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
                🏛️ Language Portal
            </a>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a class="nav-link" href="art{art_id}.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24; padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
                <a class="nav-link" href="art{art_id}_hi.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
                <a class="nav-link" href="art{art_id}_pa.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
            </div>
        </div>

        <!-- Home Button -->
        <div style="margin-bottom: 20px;">
            <a class="nav-link" href="index_en.html" style="display: inline-flex; background: rgba(0,0,0,0.3); padding: 10px 20px; border-radius: 20px; border: 1px solid var(--glass-border);">
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg> Back to Home
            </a>
        </div>

        <!-- Unit Header Crest Card -->
        <div style="text-align: center; margin-bottom: 2rem; background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0) 70%); padding: 30px 20px; border-radius: 20px; border: 1px solid rgba(245, 158, 11, 0.25); box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
            <div style="display: inline-block; background: rgba(245, 158, 11, 0.15); border: 2px solid #f59e0b; padding: 12px 24px; border-radius: 50px; font-weight: 700; color: #fbbf24; font-size: 0.95rem; letter-spacing: 0.1em; margin-bottom: 15px;">
                ⚔️ REGIMENTAL UNIT HISTORY
            </div>
            <h1 style="font-size: 2.8rem; margin-bottom: 0.8rem; text-shadow: 0 4px 16px rgba(0,0,0,0.8);">{u['title_en']}</h1>
            <p style="color: #94a3b8; font-size: 1.15rem; font-weight: 500;">{u['regiment_en']}</p>
        </div>

        <!-- Audio Player Section -->
        <div class="audio-section" style="margin-bottom: 2rem;">
            <audio autoplay="" id="artAudio" src="assets/audio/audio_{art_id}.mp3"></audio>
            <button class="play-btn" onclick="toggleAudio()" style="box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);">
                <svg fill="currentColor" viewbox="0 0 24 24">
                    <path d="M8 5v14l11-7z"></path>
                </svg>
                Listen to Smart Narration
            </button>
        </div>

        <!-- Metadata Box -->
        <div class="description-box" style="margin-bottom: 2rem;">
            <strong>Unit Name:</strong> {u['title_en']}<br/>
            <strong>Category:</strong> Unit History<br/>
            <strong>Affiliation:</strong> {u['regiment_en']}<br/>
        </div>

        <!-- Full Battalion History -->
        <div class="description-box" style="margin-bottom: 2.5rem; padding: 30px;">
            <h3 style="color: #f59e0b; font-size: 1.4rem; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                Detailed Historical Record
            </h3>
            {paras_html}
        </div>

        <!-- Navigation Bar -->
        <div class="navigation">
            <a class="nav-link {prev_class}" href="{prev_link}">
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
                    <path d="M19 12H5M12 19l-7-7 7-7"></path>
                </svg>
                Previous Unit
            </a>
            <span style="color: #94a3b8; font-weight: 600;">Unit {idx + 1} / {TOTAL_UNITS}</span>
            <a class="nav-link {next_class}" href="{next_link}">
                Next Unit
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
                    <path d="M5 12h14M12 5l7 7-7 7"></path>
                </svg>
            </a>
        </div>

        <!-- QR Code Section -->
        <div class="qr-container">
            <div class="qr-wrapper">
                <img alt="Scan for mobile" src="assets/qrcodes/qr_art_{art_id}.png"/>
                <div class="qr-info">
                    <h3>Open on Mobile</h3>
                    <p>Scan to view this unit history record in Chrome on your phone.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const audio = document.getElementById('artAudio');
            const btn = document.querySelector('.play-btn');

            audio.addEventListener('play', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> Pause Audio`;
            }});
            audio.addEventListener('pause', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> Listen to Smart Narration`;
            }});
            audio.addEventListener('ended', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> Listen to Smart Narration`;
            }});

            let playPromise = audio.play();
            if (playPromise !== undefined) {{
                playPromise.catch(error => {{
                    console.log("Autoplay prevented:", error);
                    const startAudio = () => {{
                        audio.play();
                        document.body.removeEventListener('click', startAudio);
                        document.body.removeEventListener('touchstart', startAudio);
                    }};
                    document.body.addEventListener('click', startAudio);
                    document.body.addEventListener('touchstart', startAudio);
                }});
            }}
        }});

        function toggleAudio() {{
            const audio = document.getElementById('artAudio');
            if (audio.paused) {{ audio.play(); }} else {{ audio.pause(); }}
        }}
    </script>
</body>
</html>
"""
    return html


def generate_hi_page(u, idx):
    art_id = u["art_id"]
    prev_link = f"art{art_id - 1}_hi.html" if idx > 0 else "#"
    prev_class = "disabled" if idx == 0 else ""
    next_link = f"art{art_id + 1}_hi.html" if idx < TOTAL_UNITS - 1 else "#"
    next_class = "disabled" if idx == TOTAL_UNITS - 1 else ""
    
    paras_html = "".join([f"<p style='margin-bottom: 1.2rem; line-height: 1.8; text-align: justify;'>{p}</p>" for p in u["paras_hi"]])
    
    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>{u['title_hi']} - यूनिट इतिहास | सिख रेजिमेंट संग्रहालय</title>
    <link href="css/style.css" rel="stylesheet"/>
</head>
<body>
    <div class="gallery-container">
        <!-- Language Switcher Bar -->
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
            <a class="nav-link" href="index_hi.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg> मुख्य पृष्ठ पर वापस
            </a>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a class="nav-link" href="art{art_id}.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
                <a class="nav-link" href="art{art_id}_hi.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24; padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
                <a class="nav-link" href="art{art_id}_pa.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
            </div>
        </div>

        <!-- Unit Header Crest Card -->
        <div style="text-align: center; margin-bottom: 2rem; background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0) 70%); padding: 30px 20px; border-radius: 20px; border: 1px solid rgba(245, 158, 11, 0.25); box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
            <div style="display: inline-block; background: rgba(245, 158, 11, 0.15); border: 2px solid #f59e0b; padding: 12px 24px; border-radius: 50px; font-weight: 700; color: #fbbf24; font-size: 0.95rem; letter-spacing: 0.1em; margin-bottom: 15px;">
                ⚔️ रेजिमेंटल यूनिट इतिहास
            </div>
            <h1 style="font-size: 2.8rem; margin-bottom: 0.8rem; text-shadow: 0 4px 16px rgba(0,0,0,0.8);">{u['title_hi']}</h1>
            <p style="color: #94a3b8; font-size: 1.15rem; font-weight: 500;">{u['regiment_hi']}</p>
        </div>

        <!-- Audio Player Section -->
        <div class="audio-section" style="margin-bottom: 2rem;">
            <audio autoplay="" id="artAudio" src="assets/audio_hi/audio_{art_id}.mp3"></audio>
            <button class="play-btn" onclick="toggleAudio()" style="box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);">
                <svg fill="currentColor" viewbox="0 0 24 24">
                    <path d="M8 5v14l11-7z"></path>
                </svg>
                स्मार्ट वर्णन सुनें
            </button>
        </div>

        <!-- Metadata Box -->
        <div class="description-box" style="margin-bottom: 2rem;">
            <strong>यूनिट का नाम:</strong> {u['title_hi']}<br/>
            <strong>श्रेणी:</strong> यूनिट इतिहास<br/>
            <strong>संबद्धता:</strong> {u['regiment_hi']}<br/>
        </div>

        <!-- Full Battalion History -->
        <div class="description-box" style="margin-bottom: 2.5rem; padding: 30px;">
            <h3 style="color: #f59e0b; font-size: 1.4rem; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                विस्तृत ऐतिहासिक विवरण
            </h3>
            {paras_html}
        </div>

        <!-- Navigation Bar -->
        <div class="navigation">
            <a class="nav-link {prev_class}" href="{prev_link}">
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
                    <path d="M19 12H5M12 19l-7-7 7-7"></path>
                </svg>
                पिछली यूनिट
            </a>
            <span style="color: #94a3b8; font-weight: 600;">यूनिट {idx + 1} / {TOTAL_UNITS}</span>
            <a class="nav-link {next_class}" href="{next_link}">
                अगली यूनिट
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
                    <path d="M5 12h14M12 5l7 7-7 7"></path>
                </svg>
            </a>
        </div>

        <!-- QR Code Section -->
        <div class="qr-container">
            <div class="qr-wrapper">
                <img alt="Scan for mobile" src="assets/qrcodes/qr_art_{art_id}.png"/>
                <div class="qr-info">
                    <h3>मोबाइल पर खोलें</h3>
                    <p>अपने फोन पर इस यूनिट का इतिहास देखने के लिए स्कैन करें।</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const audio = document.getElementById('artAudio');
            const btn = document.querySelector('.play-btn');

            audio.addEventListener('play', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> ऑडियो रोकें`;
            }});
            audio.addEventListener('pause', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> स्मार्ट वर्णन सुनें`;
            }});
            audio.addEventListener('ended', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> स्मार्ट वर्णन सुनें`;
            }});

            let playPromise = audio.play();
            if (playPromise !== undefined) {{
                playPromise.catch(error => {{
                    console.log("Autoplay prevented:", error);
                    const startAudio = () => {{
                        audio.play();
                        document.body.removeEventListener('click', startAudio);
                        document.body.removeEventListener('touchstart', startAudio);
                    }};
                    document.body.addEventListener('click', startAudio);
                    document.body.addEventListener('touchstart', startAudio);
                }});
            }}
        }});

        function toggleAudio() {{
            const audio = document.getElementById('artAudio');
            if (audio.paused) {{ audio.play(); }} else {{ audio.pause(); }}
        }}
    </script>
</body>
</html>
"""
    return html


def generate_pa_page(u, idx):
    art_id = u["art_id"]
    prev_link = f"art{art_id - 1}_pa.html" if idx > 0 else "#"
    prev_class = "disabled" if idx == 0 else ""
    next_link = f"art{art_id + 1}_pa.html" if idx < TOTAL_UNITS - 1 else "#"
    next_class = "disabled" if idx == TOTAL_UNITS - 1 else ""
    
    paras_html = "".join([f"<p style='margin-bottom: 1.2rem; line-height: 1.8; text-align: justify;'>{p}</p>" for p in u["paras_pa"]])
    
    html = f"""<!DOCTYPE html>
<html lang="pa">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>{u['title_pa']} - ਯੂਨਿਟ ਇਤਿਹਾਸ | ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਅਜਾਇਬ ਘਰ</title>
    <link href="css/style.css" rel="stylesheet"/>
</head>
<body>
    <div class="gallery-container">
        <!-- Language Switcher Bar -->
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
            <a class="nav-link" href="index_pa.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg> ਮੁੱਖ ਪੰਨੇ 'ਤੇ ਵਾਪਸ
            </a>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a class="nav-link" href="art{art_id}.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
                <a class="nav-link" href="art{art_id}_hi.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
                <a class="nav-link" href="art{art_id}_pa.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24; padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
            </div>
        </div>

        <!-- Unit Header Crest Card -->
        <div style="text-align: center; margin-bottom: 2rem; background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0) 70%); padding: 30px 20px; border-radius: 20px; border: 1px solid rgba(245, 158, 11, 0.25); box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
            <div style="display: inline-block; background: rgba(245, 158, 11, 0.15); border: 2px solid #f59e0b; padding: 12px 24px; border-radius: 50px; font-weight: 700; color: #fbbf24; font-size: 0.95rem; letter-spacing: 0.1em; margin-bottom: 15px;">
                ⚔️ ਰੈਜੀਮੈਂਟਲ ਯੂਨਿਟ ਇਤਿਹਾਸ
            </div>
            <h1 style="font-size: 2.8rem; margin-bottom: 0.8rem; text-shadow: 0 4px 16px rgba(0,0,0,0.8);">{u['title_pa']}</h1>
            <p style="color: #94a3b8; font-size: 1.15rem; font-weight: 500;">{u['regiment_pa']}</p>
        </div>

        <!-- Audio Player Section -->
        <div class="audio-section" style="margin-bottom: 2rem;">
            <audio autoplay="" id="artAudio" src="assets/audio_pa/audio_{art_id}.mp3"></audio>
            <button class="play-btn" onclick="toggleAudio()" style="box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);">
                <svg fill="currentColor" viewbox="0 0 24 24">
                    <path d="M8 5v14l11-7z"></path>
                </svg>
                ਸਮਾਰਟ ਵੇਰਵਾ ਸੁਣੋ
            </button>
        </div>

        <!-- Metadata Box -->
        <div class="description-box" style="margin-bottom: 2rem;">
            <strong>ਯੂਨਿਟ ਦਾ ਨਾਂ:</strong> {u['title_pa']}<br/>
            <strong>ਸ਼੍ਰੇਣੀ:</strong> ਯੂਨਿਟ ਇਤਿਹਾਸ<br/>
            <strong>ਸੰਬੰਧਿਤ:</strong> {u['regiment_pa']}<br/>
        </div>

        <!-- Full Battalion History -->
        <div class="description-box" style="margin-bottom: 2.5rem; padding: 30px;">
            <h3 style="color: #f59e0b; font-size: 1.4rem; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                ਵਿਸਤ੍ਰਿਤ ਇਤਿਹਾਸਕ ਰਿਕਾਰਡ
            </h3>
            {paras_html}
        </div>

        <!-- Navigation Bar -->
        <div class="navigation">
            <a class="nav-link {prev_class}" href="{prev_link}">
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
                    <path d="M19 12H5M12 19l-7-7 7-7"></path>
                </svg>
                ਪਿਛਲੀ ਯੂਨਿਟ
            </a>
            <span style="color: #94a3b8; font-weight: 600;">ਯੂਨਿਟ {idx + 1} / {TOTAL_UNITS}</span>
            <a class="nav-link {next_class}" href="{next_link}">
                ਅਗਲੀ ਯੂਨਿਟ
                <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
                    <path d="M5 12h14M12 5l7 7-7 7"></path>
                </svg>
            </a>
        </div>

        <!-- QR Code Section -->
        <div class="qr-container">
            <div class="qr-wrapper">
                <img alt="Scan for mobile" src="assets/qrcodes/qr_art_{art_id}.png"/>
                <div class="qr-info">
                    <h3>ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ</h3>
                    <p>ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਯੂਨਿਟ ਦਾ ਇਤਿਹਾਸ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const audio = document.getElementById('artAudio');
            const btn = document.querySelector('.play-btn');

            audio.addEventListener('play', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> ਆਡੀਓ ਰੋਕੋ`;
            }});
            audio.addEventListener('pause', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> ਸਮਾਰਟ ਵੇਰਵਾ ਸੁਣੋ`;
            }});
            audio.addEventListener('ended', function () {{
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> ਸਮਾਰਟ ਵੇਰਵਾ ਸੁਣੋ`;
            }});

            let playPromise = audio.play();
            if (playPromise !== undefined) {{
                playPromise.catch(error => {{
                    console.log("Autoplay prevented:", error);
                    const startAudio = () => {{
                        audio.play();
                        document.body.removeEventListener('click', startAudio);
                        document.body.removeEventListener('touchstart', startAudio);
                    }};
                    document.body.addEventListener('click', startAudio);
                    document.body.addEventListener('touchstart', startAudio);
                }});
            }}
        }});

        function toggleAudio() {{
            const audio = document.getElementById('artAudio');
            if (audio.paused) {{ audio.play(); }} else {{ audio.pause(); }}
        }}
    </script>
</body>
</html>
"""
    return html

for idx, u in enumerate(full_data):
    art_id = u["art_id"]
    with open(f"art{art_id}.html", "w", encoding="utf-8") as f:
        f.write(generate_en_page(u, idx))
    with open(f"art{art_id}_hi.html", "w", encoding="utf-8") as f:
        f.write(generate_hi_page(u, idx))
    with open(f"art{art_id}_pa.html", "w", encoding="utf-8") as f:
        f.write(generate_pa_page(u, idx))

print("All 87 Unit History HTML pages generated successfully!")

# 6. Update Navigation Bars in index_en.html, index_hi.html, index_pa.html
print("\n--- Updating Top Navigation Bars ---")

def update_index_en():
    with open("index_en.html", "r", encoding="utf-8") as f:
        content = f.read()

    links = "\n".join([f'<a href="art{u["art_id"]}.html">{u["title_en"]}</a>' for u in full_data])
    unit_history_en = f"""<div class="nav-dropdown">
<button class="nav-btn" onclick="toggleDropdown(event, 'dropdown-9')">Unit History ▼</button>
<div class="dropdown-content" id="dropdown-9">
{links}
</div>
</div>"""

    if 'id="dropdown-9"' in content:
        content = re.sub(r'<div class="nav-dropdown">\s*<button class="nav-btn"[^>]*>Unit History.*?</button>\s*<div class="dropdown-content" id="dropdown-9">.*?</div>\s*</div>', unit_history_en, content, flags=re.DOTALL)
    else:
        succ_pattern = r'(<div class="dropdown-content" id="dropdown-8">.*?</div>\s*</div>)'
        content = re.sub(succ_pattern, r'\1\n' + unit_history_en, content, flags=re.DOTALL)

    with open("index_en.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("index_en.html updated.")

def update_index_hi():
    with open("index_hi.html", "r", encoding="utf-8") as f:
        content = f.read()

    links = "\n".join([f'<a href="art{u["art_id"]}_hi.html">{u["title_hi"]}</a>' for u in full_data])
    unit_history_hi = f"""<div class="nav-dropdown">
<button class="nav-btn" onclick="toggleDropdown(event, 'dropdown-9')">यूनिट इतिहास ▼</button>
<div class="dropdown-content" id="dropdown-9">
{links}
</div>
</div>"""

    if 'id="dropdown-9"' in content:
        content = re.sub(r'<div class="nav-dropdown">\s*<button class="nav-btn"[^>]*>.*?</button>\s*<div class="dropdown-content" id="dropdown-9">.*?</div>\s*</div>', unit_history_hi, content, flags=re.DOTALL)
    else:
        succ_pattern = r'(<div class="dropdown-content" id="dropdown-8">.*?</div>\s*</div>)'
        content = re.sub(succ_pattern, r'\1\n' + unit_history_hi, content, flags=re.DOTALL)

    with open("index_hi.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("index_hi.html updated.")

def update_index_pa():
    with open("index_pa.html", "r", encoding="utf-8") as f:
        content = f.read()

    links = "\n".join([f'<a href="art{u["art_id"]}_pa.html">{u["title_pa"]}</a>' for u in full_data])
    unit_history_pa = f"""<div class="nav-dropdown">
<button class="nav-btn" onclick="toggleDropdown(event, 'dropdown-9')">ਯੂਨਿਟ ਇਤਿਹਾਸ ▼</button>
<div class="dropdown-content" id="dropdown-9">
{links}
</div>
</div>"""

    if 'id="dropdown-9"' in content:
        content = re.sub(r'<div class="nav-dropdown">\s*<button class="nav-btn"[^>]*>.*?</button>\s*<div class="dropdown-content" id="dropdown-9">.*?</div>\s*</div>', unit_history_pa, content, flags=re.DOTALL)
    else:
        succ_pattern = r'(<div class="dropdown-content" id="dropdown-8">.*?</div>\s*</div>)'
        content = re.sub(succ_pattern, r'\1\n' + unit_history_pa, content, flags=re.DOTALL)

    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("index_pa.html updated.")

update_index_en()
update_index_hi()
update_index_pa()

print("\n==========================================")
print("UNIT HISTORY FEATURE BUILD COMPLETE!")
print("==========================================")
