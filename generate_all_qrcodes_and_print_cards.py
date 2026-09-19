import os
import re
import glob
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "https://virasatsrc.netlify.app"

ASSETS_QR_DIR = os.path.join("assets", "qrcodes")
PRINT_QR_DIR = os.path.join("print QR", "qrcodes")
CARDS_PNG_DIR = os.path.join("print QR", "cards_png")

os.makedirs(ASSETS_QR_DIR, exist_ok=True)
os.makedirs(PRINT_QR_DIR, exist_ok=True)
os.makedirs(CARDS_PNG_DIR, exist_ok=True)

# 1. Collect all base art files and their titles
base_arts = sorted(glob.glob("art[0-9]*.html"), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
base_arts = [f for f in base_arts if not f.endswith("_hi.html") and not f.endswith("_pa.html")]

all_items = []

# Add Special Pages first
special_pages = [
    {
        "filename": "index.html",
        "card_name": "index.png",
        "title": "The Legacy of Sikh Regiment",
        "url": BASE_URL,
        "assets_qr": "qr_home.png",
        "print_qr": "qr_home.png"
    },
    {
        "filename": "coas_citations.html",
        "card_name": "coas_citations.png",
        "title": "COAS CITATIONS GALLERY",
        "url": f"{BASE_URL}/coas_citations",
        "assets_qr": "qr_coas_citations.png",
        "print_qr": "qr_coas_citations.png"
    },
    {
        "filename": "kirti_chakra.html",
        "card_name": "kirti_chakra.png",
        "title": "KIRTI CHAKRA GALLERY",
        "url": f"{BASE_URL}/kirti_chakra",
        "assets_qr": "qr_kirti_chakra.png",
        "print_qr": "qr_kirti_chakra.png"
    },
    {
        "filename": "mahavir_chakra.html",
        "card_name": "mahavir_chakra.png",
        "title": "MAHAVIR CHAKRA GALLERY",
        "url": f"{BASE_URL}/mahavir_chakra",
        "assets_qr": "qr_mahavir_chakra.png",
        "print_qr": "qr_mahavir_chakra.png"
    },
    {
        "filename": "weapons_ammunition.html",
        "card_name": "weapons_ammunition.png",
        "title": "WEAPONS & AMMUNITION",
        "url": f"{BASE_URL}/weapons_ammunition",
        "assets_qr": "qr_weapons_ammunition.png",
        "print_qr": "qr_weapons_ammunition.png"
    }
]

for sp in special_pages:
    all_items.append(sp)

for f in base_arts:
    num = re.search(r'\d+', f).group(0)
    with open(f, "r", encoding="utf-8") as fp:
        content = fp.read()
    m_h1 = re.search(r'<h1>(.*?)</h1>', content)
    m_title = re.search(r'<title>(.*?)</title>', content)
    if m_h1:
        title = m_h1.group(1).strip()
    elif m_title:
        title = m_title.group(1).split('-')[0].strip()
    else:
        title = f"Exhibit {num}"
    title = re.sub(r'<[^>]+>', '', title).strip()

    all_items.append({
        "num": num,
        "filename": f,
        "card_name": f"art{num}.png",
        "title": title,
        "url": f"{BASE_URL}/art{num}",
        "assets_qr": f"qr_art_{num}.png",
        "print_qr": f"qr_art{num}.png"
    })

print(f"Total catalog items to process: {len(all_items)}")

# 2. Generate QR Code Images
def make_qr(url, filepath):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)

print("Generating QR Codes in assets/qrcodes and print QR/qrcodes...")
for item in all_items:
    # Save in assets/qrcodes
    assets_path = os.path.join(ASSETS_QR_DIR, item["assets_qr"])
    make_qr(item["url"], assets_path)
    
    # Save in print QR/qrcodes
    print_path = os.path.join(PRINT_QR_DIR, item["print_qr"])
    make_qr(item["url"], print_path)

print("QR Code generation complete!")

# 3. Generate Printable Card PNGs (1200 x 1800)
def generate_card(title, qr_path, out_path):
    W, H = 1200, 1800
    img = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(img)
    
    # Outer black border: 40px margin, 8px width
    draw.rectangle([40, 40, W - 40, H - 40], outline='black', width=8)
    
    # Top title: VIRASAT
    try:
        font_top = ImageFont.truetype('arialbd.ttf', 72)
    except:
        font_top = ImageFont.load_default()
    
    top_text = "VIRASAT"
    top_spaced = "  ".join(list(top_text))
    bbox_top = draw.textbbox((0, 0), top_spaced, font=font_top)
    w_top = bbox_top[2] - bbox_top[0]
    draw.text(((W - w_top) / 2, 115), top_spaced, fill='black', font=font_top)
    
    # Horizontal line under VIRASAT: at y=250
    draw.line([(140, 250), (W - 140, 250)], fill='black', width=4)
    
    # Center QR Code: ~800x800 centered between y=320 and y=1300
    if os.path.exists(qr_path):
        qr_img = Image.open(qr_path).convert('RGB')
        QR_SIZE = 820
        qr_resized = qr_img.resize((QR_SIZE, QR_SIZE), Image.Resampling.NEAREST)
        qr_x = (W - QR_SIZE) // 2
        qr_y = 350
        img.paste(qr_resized, (qr_x, qr_y))
    
    # Bottom title: wrapped if too long
    try:
        font_bottom = ImageFont.truetype('arialbd.ttf', 52)
    except:
        font_bottom = ImageFont.load_default()
        
    words = title.split()
    lines = []
    curr = ""
    for w in words:
        test = (curr + " " + w).strip()
        bb = draw.textbbox((0, 0), test, font=font_bottom)
        if (bb[2] - bb[0]) <= 980:
            curr = test
        else:
            if curr: lines.append(curr)
            curr = w
    if curr: lines.append(curr)
    
    # Center text vertically in bottom zone (y=1240 to 1720)
    line_h = 65
    total_text_h = len(lines) * line_h
    start_y = 1260 + (440 - total_text_h) // 2
    for i, line in enumerate(lines):
        bb = draw.textbbox((0, 0), line, font=font_bottom)
        w_line = bb[2] - bb[0]
        draw.text(((W - w_line) / 2, start_y + i * line_h), line, fill='black', font=font_bottom)
        
    img.save(out_path, 'PNG')

print("Generating Printable Card PNGs in print QR/cards_png...")
for item in all_items:
    qr_p = os.path.join(PRINT_QR_DIR, item["print_qr"])
    card_p = os.path.join(CARDS_PNG_DIR, item["card_name"])
    generate_card(item["title"], qr_p, card_p)

print("All Card PNGs generated successfully!")

# 4. Update print QR/index.html with all 228 items
print_items_json = []
for item in all_items:
    print_items_json.append({
        "filename": item["filename"],
        "title": item["title"],
        "url": item["url"],
        "qr_image": f"qrcodes/{item['print_qr']}"
    })

with open(os.path.join("print QR", "index.html"), "r", encoding="utf-8") as fp:
    html_index = fp.read()

# Replace const items = [...];
new_items_code = "const items = " + json.dumps(print_items_json) + ";"
html_index = re.sub(r'const items = \[.*?\];', lambda m: new_items_code, html_index, count=1, flags=re.DOTALL)

with open(os.path.join("print QR", "index.html"), "w", encoding="utf-8") as fp:
    fp.write(html_index)

print("Updated print QR/index.html with full catalog!")

# 5. Update print QR/print_all.html with all 228 items
all_cards_html = []
for item in all_items:
    all_cards_html.append(f'''    <div class="card">
        <div class="card-title-top">VIRASAT</div>
        <div class="card-qr-container">
            <img class="card-qr" src="qrcodes/{item['print_qr']}" alt="QR Code">
        </div>
        <div class="card-title-bottom">{item['title']}</div>
    </div>''')

cards_block = "\n    \n".join(all_cards_html)

new_print_all = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Print All QR Cards - VIRASAT</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');
        
        body {{
            margin: 0;
            padding: 20px;
            background: #1e293b;
            font-family: 'Outfit', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }}
        
        .no-print-btn {{
            background: #f59e0b;
            color: #000;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
            transition: all 0.3s ease;
        }}
        
        .no-print-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6);
        }}
        
        .card {{
            border: 4px solid #000;
            background: white;
            color: black;
            width: 4.5in;
            height: 6.5in;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 0.3in 0.4in 0.25in 0.4in;
            box-sizing: border-box;
            text-align: center;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        }}
        
        .card-title-top {{
            font-size: 32px;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: #000;
            border-bottom: 2px solid #000;
            width: 100%;
            padding-bottom: 8px;
            margin-bottom: 10px;
        }}
        
        .card-qr-container {{
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 15px 0;
        }}
        
        .card-qr {{
            width: 3.6in;
            height: 3.6in;
        }}
        
        .card-title-bottom {{
            font-size: 22px;
            font-weight: 600;
            color: #000;
            margin-top: auto;
            margin-bottom: 0px;
            word-wrap: break-word;
            width: 100%;
            line-height: 1.3;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
                gap: 0;
            }}
            .no-print-btn {{
                display: none;
            }}
            .card {{
                box-shadow: none;
                page-break-after: always;
                margin: 0 auto;
                height: 100vh;
                border: none;
            }}
        }}
    </style>
</head>
<body>

    <button class="no-print-btn" onclick="window.print()">🖨️ Print All Cards</button>

{cards_block}

</body>
</html>
'''

with open(os.path.join("print QR", "print_all.html"), "w", encoding="utf-8") as fp:
    fp.write(new_print_all)

print("Updated print QR/print_all.html with all cards!")
