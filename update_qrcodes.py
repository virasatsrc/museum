import os
import qrcode

# GitHub Pages base URL
BASE_URL = "https://virasatsrc.github.io/museum"
TOTAL_ART = 160
QR_DIR = os.path.join("assets", "qrcodes")

os.makedirs(QR_DIR, exist_ok=True)

print(f"Regenerating {TOTAL_ART} QR codes pointing to GitHub Pages URLs...")

for art_num in range(1, TOTAL_ART + 1):
    qr_file_path = os.path.join(QR_DIR, f"qr_art_{art_num}.png")
    url = f"{BASE_URL}/art{art_num}.html"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_file_path)

    if art_num % 20 == 0:
        print(f"  Done {art_num}/{TOTAL_ART}...")

print(f"\nAll {TOTAL_ART} QR codes updated!")
print(f"Example URL: {BASE_URL}/art1.html")
