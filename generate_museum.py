import os
import qrcode
import socket
import glob

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = 'localhost'
    finally:
        s.close()
    return IP

# Configuration
TOTAL_ART = 160
CATEGORIES = 6
ART_PER_CAT = 10
PHOTO_CATEGORIES = 10
ART_PER_PHOTO_CAT = 10
PORT = 8001
SERVER_IP = get_ip()
OUTPUT_DIR = r"d:\antigravity\museum"
ART_TEMPLATE_PATH = os.path.join(OUTPUT_DIR, "art_template.html")
INDEX_TEMPLATE_PATH = os.path.join(OUTPUT_DIR, "index_template.html")
QR_DIR = os.path.join(OUTPUT_DIR, "assets", "qrcodes")

os.makedirs(QR_DIR, exist_ok=True)

# Generate Navigation HTML
nav_html = '<div class="top-nav">\n'
for cat in range(1, CATEGORIES + 1):
    nav_html += f'    <div class="nav-dropdown">\n'
    nav_html += f'''        <button class="nav-btn" onclick="toggleDropdown(event, 'dropdown-{cat}')">Category {cat} ▼</button>\n'''
    nav_html += f'        <div id="dropdown-{cat}" class="dropdown-content">\n'
    for i in range(1, ART_PER_CAT + 1):
        art_num = (cat - 1) * ART_PER_CAT + i
        nav_html += f'            <a href="art{art_num}.html">Art {art_num}</a>\n'
    nav_html += f'        </div>\n'
    nav_html += f'    </div>\n'
nav_html += '</div>\n'

# Generate Photo Navigation HTML
photo_nav_html = '<div class="photo-nav-grid">\n'
for p_cat in range(1, PHOTO_CATEGORIES + 1):
    photo_nav_html += f'    <div class="photo-nav-item">\n'
    photo_nav_html += f'''        <img src="https://placehold.co/200x200/1e293b/f59e0b?text=Photo+{p_cat}" class="photo-nav-btn" onclick="toggleDropdown(event, 'photo-dropdown-{p_cat}')" alt="Photo {p_cat}">\n'''
    photo_nav_html += f'        <div id="photo-dropdown-{p_cat}" class="dropdown-content photo-nav-dropdown">\n'
    for i in range(1, ART_PER_PHOTO_CAT + 1):
        art_num = 60 + (p_cat - 1) * ART_PER_PHOTO_CAT + i
        photo_nav_html += f'            <a href="art{art_num}.html">Art {art_num}</a>\n'
    photo_nav_html += f'        </div>\n'
    photo_nav_html += f'    </div>\n'
photo_nav_html += '</div>\n'

# Get scroller images
scroller_images_dir = os.path.join(OUTPUT_DIR, "assets", "scroller_images")
os.makedirs(scroller_images_dir, exist_ok=True)
scroller_images = glob.glob(os.path.join(scroller_images_dir, "*.*"))

scroller_html = ""
if not scroller_images:
    # Use placeholders if no images exist
    for i in range(1, 6):
        scroller_html += f'<img src="https://placehold.co/350x250/1e293b/f59e0b?text=Scroller+Image+{i}" alt="Scroller Placeholder">\n'
else:
    for img_path in scroller_images:
        img_name = os.path.basename(img_path)
        scroller_html += f'<img src="assets/scroller_images/{img_name}" alt="Scroller Image">\n'

# Read templates
with open(ART_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    art_template = f.read()
    
with open(INDEX_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    index_template = f.read()

print(f"Starting generation using IP {SERVER_IP}...")

# Generate art pages
for art_num in range(1, TOTAL_ART + 1):
    if art_num <= 60:
        category_name = f"Category {((art_num - 1) // ART_PER_CAT) + 1}"
    else:
        category_name = f"Photo Category {((art_num - 61) // ART_PER_PHOTO_CAT) + 1}"
    
    # Paths
    photo_path = f"assets/art/art_{art_num}.png" # placeholder path
    audio_path = f"assets/audio/audio_{art_num}.mp3" # placeholder path
    qr_file_name = f"qr_art_{art_num}.png"
    qr_file_path = os.path.join(QR_DIR, qr_file_name)
    qr_relative_path = f"assets/qrcodes/{qr_file_name}"
    
    # Generate QR Code
    mobile_url = f"http://{SERVER_IP}:{PORT}/art{art_num}.html"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(mobile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_file_path)
    
    # Navigation logic
    prev_link = f"art{art_num-1}.html" if art_num > 1 else "#"
    prev_disabled = "disabled" if art_num == 1 else ""
    
    next_link = f"art{art_num+1}.html" if art_num < TOTAL_ART else "#"
    next_disabled = "disabled" if art_num == TOTAL_ART else ""
    
    # Generate page content
    page_html = art_template
    page_html = page_html.replace("{{ nav_html }}", nav_html)
    page_html = page_html.replace("{{ art_title }}", f"Art Piece {art_num}")
    page_html = page_html.replace("{{ category }}", category_name)
    page_html = page_html.replace("{{ artist }}", "Unknown Artist")
    page_html = page_html.replace("{{ year }}", "Historical")
    page_html = page_html.replace("{{ art_description }}", f"This is the description for Art Piece {art_num}.")
    page_html = page_html.replace("{{ photo_path }}", photo_path)
    page_html = page_html.replace("{{ audio_path }}", audio_path)
    page_html = page_html.replace("{{ art_num }}", str(art_num))
    page_html = page_html.replace("{{ prev_link }}", prev_link)
    page_html = page_html.replace("{{ prev_disabled }}", prev_disabled)
    page_html = page_html.replace("{{ next_link }}", next_link)
    page_html = page_html.replace("{{ next_disabled }}", next_disabled)
    page_html = page_html.replace("{{ qr_code_path }}", qr_relative_path)
    
    # Write page
    with open(os.path.join(OUTPUT_DIR, f"art{art_num}.html"), 'w', encoding='utf-8') as f:
        f.write(page_html)

# Generate index.html
index_html = index_template
index_html = index_html.replace("{{ nav_html }}", nav_html)
index_html = index_html.replace("{{ scroller_images_html }}", scroller_html)
index_html = index_html.replace("{{ photo_nav_html }}", photo_nav_html)

with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
    f.write(index_html)

print(f"Successfully generated {TOTAL_ART} art pages, QR codes, and index.html in {OUTPUT_DIR}")
