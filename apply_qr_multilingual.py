import os
import re
import glob

HEAD_REDIRECT_SCRIPT = """<script>
(function() {
    try {
        var p = new URLSearchParams(window.location.search).get('lang');
        if (p) localStorage.setItem('museum_lang', p);
        var l = p || localStorage.getItem('museum_lang');
        var path = window.location.pathname;
        if (l === 'hi' && !path.endsWith('_hi.html')) {
            window.location.replace(path.replace(/(_hi|_pa)?(\.html|\/)?$/, '') + '_hi.html' + window.location.search);
        } else if (l === 'pa' && !path.endsWith('_pa.html')) {
            window.location.replace(path.replace(/(_hi|_pa)?(\.html|\/)?$/, '') + '_pa.html' + window.location.search);
        }
    } catch(e) {}
})();
</script>"""

JS_TAG = '<script src="js/qr_lang.js"></script>'

def update_lang_bar(html, root_name, current_lang):
    en_active = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24; padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"' if current_lang == 'en' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'
    hi_active = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24; padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"' if current_lang == 'hi' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'
    pa_active = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24; padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"' if current_lang == 'pa' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'

    if root_name in ['index', 'index_en', 'index_hi', 'index_pa']:
        en_href = "index_en.html?lang=en"
        hi_href = "index_hi.html?lang=hi"
        pa_href = "index_pa.html?lang=pa"
    else:
        en_href = f"{root_name}.html?lang=en"
        hi_href = f"{root_name}_hi.html?lang=hi"
        pa_href = f"{root_name}_pa.html?lang=pa"

    portal_label = "🏛️ Language Portal" if current_lang == 'en' else ("🏛️ भाषा चयन" if current_lang == 'hi' else "🏛️ ਭਾਸ਼ਾ ਚੋਣ")

    new_bar = f'''<!-- Language Switcher Bar -->
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
            <a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
                {portal_label}
            </a>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a class="nav-link" href="{en_href}" onclick="setMuseumLang('en')" {en_active}>🇬🇧 English</a>
                <a class="nav-link" href="{hi_href}" onclick="setMuseumLang('hi')" {hi_active}>🇮🇳 हिन्दी</a>
                <a class="nav-link" href="{pa_href}" onclick="setMuseumLang('pa')" {pa_active}>ੴ ਪੰਜਾਬੀ</a>
            </div>
        </div>'''

    # Replace existing lang-switch-bar if present
    bar_regex = r'<!-- Language Switcher Bar -->\s*<div class="lang-switch-bar".*?</div>\s*</div>|<div class="lang-switch-bar".*?</div>\s*</div>'
    if re.search(bar_regex, html, flags=re.DOTALL):
        html = re.sub(bar_regex, new_bar, html, count=1, flags=re.DOTALL)
    return html

def process_file(filepath):
    filename = os.path.basename(filepath)
    if filename in ['art_template.html', 'index_template.html', 'index.html'] or filename.startswith('test_'):
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Determine language and root name
    if filename.endswith('_hi.html'):
        current_lang = 'hi'
        root_name = filename[:-8]
    elif filename.endswith('_pa.html'):
        current_lang = 'pa'
        root_name = filename[:-8]
    else:
        current_lang = 'en'
        root_name = filename[:-5]

    # 1. Update Language Switcher Bar
    html = update_lang_bar(html, root_name, current_lang)

    # 2. For English base pages: add HEAD redirect script if not present
    if current_lang == 'en' and filename not in ['index.html', 'index_en.html']:
        # Remove any previous redirect script if already there
        html = re.sub(r'<script>\s*\(function\(\)\s*\{\s*try\s*\{\s*var p = new URLSearchParams.*?</script>\s*', '', html, flags=re.DOTALL)
        # Insert right after <head> or <head ...>
        head_match = re.search(r'<head[^>]*>', html, flags=re.IGNORECASE)
        if head_match:
            pos = head_match.end()
            html = html[:pos] + '\n' + HEAD_REDIRECT_SCRIPT + html[pos:]

    # 3. Add js/qr_lang.js before </body> if not present
    if JS_TAG not in html:
        body_end_match = re.search(r'</body>', html, flags=re.IGNORECASE)
        if body_end_match:
            pos = body_end_match.start()
            html = html[:pos] + f'    {JS_TAG}\n' + html[pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

all_files = sorted(glob.glob('*.html'))
count = 0
for f in all_files:
    if process_file(f):
        count += 1

print(f"Successfully processed {count} HTML files with multilingual QR engine.")
