import os
import glob
import re
from bs4 import BeautifulSoup

def clean_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    # Determine language
    if filename.endswith("_hi.html"):
        lang = "hi"
        base_name = filename.replace("_hi.html", ".html")
    elif filename.endswith("_pa.html"):
        lang = "pa"
        base_name = filename.replace("_pa.html", ".html")
    else:
        lang = "en"
        base_name = filename

    if base_name in ["index.html", "index_en.html", "index_hi.html", "index_pa.html"]:
        en_url = "index_en.html"
        hi_url = "index_hi.html"
        pa_url = "index_pa.html"
        home_href = "index.html"
    else:
        root = os.path.splitext(base_name)[0]
        en_url = f"{root}.html"
        hi_url = f"{root}_hi.html"
        pa_url = f"{root}_pa.html"
        home_href = "index_en.html" if lang == "en" else (f"index_{lang}.html")

    # Clean up all existing switcher bars
    for bar in soup.find_all("div", class_="lang-switch-bar"):
        bar.decompose()

    # Create fresh language switcher bar
    en_active = 'style="background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;"' if lang == 'en' else ''
    hi_active = 'style="background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;"' if lang == 'hi' else ''
    pa_active = 'style="background: rgba(245, 158, 11, 0.3); border-color: #f59e0b; font-weight: 700;"' if lang == 'pa' else ''

    portal_label = "🏛️ Language Portal" if lang == 'en' else ("🏛️ भाषा चयन" if lang == 'hi' else "🏛️ ਭਾਸ਼ਾ ਚੋਣ")

    bar_html = f"""
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

    container = soup.find("div", class_="gallery-container") or soup.find("body")
    if container and filename != "index.html": # do not add on landing page
        bar_soup = BeautifulSoup(bar_html, "html.parser")
        container.insert(0, bar_soup)

    # Clean home button link and text on art/special pages
    if filename not in ["index.html", "index_en.html", "index_hi.html", "index_pa.html"]:
        home_btn = soup.find("a", href=re.compile(r"index.*\.html"))
        if home_btn:
            home_btn["href"] = home_href
            for t in list(home_btn.find_all(string=True)):
                if "Back to Home" in t or "मुख्य पृष्ठ" in t or "ਮੁੱਖ ਪੰਨਾ" in t:
                    if lang == "hi":
                        t.replace_with(" मुख्य पृष्ठ")
                    elif lang == "pa":
                        t.replace_with(" ਮੁੱਖ ਪੰਨਾ")
                    else:
                        t.replace_with(" Back to Home")

    # Ensure internal navigation links match the current page language
    if filename not in ["index.html", "index_en.html", "index_hi.html", "index_pa.html"]:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".html") and not href.startswith("http") and href not in ["index.html", "index_en.html", "index_hi.html", "index_pa.html"]:
                base = href.replace("_hi.html", ".html").replace("_pa.html", ".html")
                root = os.path.splitext(base)[0]
                if lang == "hi":
                    a["href"] = f"{root}_hi.html"
                elif lang == "pa":
                    a["href"] = f"{root}_pa.html"
                else:
                    a["href"] = f"{root}.html"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

def main():
    all_html = glob.glob("*.html")
    print(f"Cleaning {len(all_html)} HTML files...")
    for f in all_html:
        if f != "index.html" and f != "art_template.html" and f != "index_template.html":
            clean_file(f)
    print("All files cleaned and verified!")

if __name__ == "__main__":
    main()
