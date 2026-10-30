#!/usr/bin/env python3
"""
Generate a Google-compliant sitemap.xml for Virasat - The Sikh Regimental Centre Heritage Museum.
Includes:
- Full URL index (loc, lastmod, changefreq, priority)
- Multilingual alternates (hreflang) across English, Hindi & Punjabi versions
- Image sitemap extension for Google Image search indexing
"""

import glob
import os
import re
import html
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date

def generate():
    today = date.today().isoformat()
    base_url = "https://virasatsrc.github.io/museum/"

    excluded = {"googlec6765fedd1f53eb0.html", "art_template.html", "index_template.html"}
    all_files = sorted(list(set(glob.glob("*.html")) - excluded))

    def get_stem_and_lang(f):
        if f == "index.html":
            return "index_root", "x-default"
        m = re.match(r"^(.*?)(?:_(hi|pa))?\.html$", f)
        if not m:
            return f, "en"
        stem = m.group(1)
        lang = m.group(2) if m.group(2) else "en"
        return stem, lang

    groups = {}
    for f in all_files:
        stem, lang = get_stem_and_lang(f)
        groups.setdefault(stem, {})[lang] = f

    def get_priority_and_freq(f):
        if f == "index.html":
            return "1.0", "daily"
        if f in ["index_en.html", "index_hi.html", "index_pa.html"]:
            return "0.95", "weekly"
        if any(k in f for k in ["mahavir_chakra", "kirti_chakra", "coas_citations", "weapons_ammunition"]):
            return "0.90", "monthly"
        if any(k in f for k in ["art201", "art104", "art205", "art206", "art410", "art405", "art406", "art417", "art12"]):
            return "0.85", "monthly"
        return "0.80", "monthly"

    def get_file_metadata(f):
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
        except:
            content = ""
        title_m = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        title = title_m.group(1).strip() if title_m else f
        
        raw_imgs = re.findall(r'<img[^>]+src=[\"\'](assets/[^\"\'<>]+)[\"\']', content)
        clean_imgs = []
        seen = set()
        for img in raw_imgs:
            if img not in seen:
                seen.add(img)
                clean_imgs.append(img)
        return title, clean_imgs[:3]

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
    ]

    def sort_key(f):
        if f == "index.html":
            return (0, f)
        if f.startswith("index_"):
            return (1, f)
        if any(k in f for k in ["mahavir_chakra", "kirti_chakra", "coas_citations", "weapons_ammunition"]):
            return (2, f)
        return (3, f)

    sorted_files = sorted(all_files, key=sort_key)

    for f in sorted_files:
        stem, lang = get_stem_and_lang(f)
        priority, freq = get_priority_and_freq(f)
        title, imgs = get_file_metadata(f)
        
        loc = base_url + f
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{html.escape(loc)}</loc>")
        xml_lines.append(f"    <lastmod>{today}</lastmod>")
        xml_lines.append(f"    <changefreq>{freq}</changefreq>")
        xml_lines.append(f"    <priority>{priority}</priority>")
        
        if stem in ("index_root", "index"):
            xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base_url}"/>')
            xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{base_url}index_en.html"/>')
            xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="hi" href="{base_url}index_hi.html"/>')
            xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="pa" href="{base_url}index_pa.html"/>')
        elif stem in groups:
            g = groups[stem]
            if "en" in g:
                xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{base_url}{g["en"]}"/>')
            if "hi" in g:
                xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="hi" href="{base_url}{g["hi"]}"/>')
            if "pa" in g:
                xml_lines.append(f'    <xhtml:link rel="alternate" hreflang="pa" href="{base_url}{g["pa"]}"/>')
                
        if f == "index.html":
            imgs = ["assets/virasat/DSC_0438.webp"]
        for img_path in imgs:
            encoded_img_path = urllib.parse.quote(img_path, safe="/:")
            img_url = base_url + encoded_img_path
            xml_lines.append("    <image:image>")
            xml_lines.append(f"      <image:loc>{html.escape(img_url)}</image:loc>")
            xml_lines.append(f"      <image:title>{html.escape(title)}</image:title>")
            xml_lines.append("    </image:image>")
            
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    sitemap_content = "\n".join(xml_lines)
    with open("sitemap.xml", "w", encoding="utf-8") as sf:
        sf.write(sitemap_content)

    ET.fromstring(sitemap_content)
    print(f"Successfully generated and validated sitemap.xml with {len(sorted_files)} URLs.")

if __name__ == "__main__":
    generate()
