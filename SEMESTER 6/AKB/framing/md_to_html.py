"""
Convert walkthrough.md.resolved to a beautifully styled HTML file,
then it can be printed to PDF via browser.
"""
import markdown
import base64
import re
import os

RESOLVED_MD = r"c:\Users\user\.gemini\antigravity\brain\d4cbd9a0-c9e0-4cb6-b3ba-20c84df69146\walkthrough.md.resolved"
OUTPUT_HTML = r"d:\UNAIR\SEMESTER 6\AKB\dokumentasi_olist_business_framing.html"

# Read the markdown
with open(RESOLVED_MD, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Embed images as base64 so they appear in PDF
def embed_images(md_content):
    """Replace image paths with base64 data URIs."""
    def replace_img(match):
        alt = match.group(1)
        path = match.group(2)
        # Try multiple path formats
        candidates = [
            path,
            path.replace('/', '\\'),
            path.replace('\\', '/'),
        ]
        found = None
        for p in candidates:
            if os.path.exists(p):
                found = p
                break
        if not found:
            print(f"  [SKIP] Image not found: {path}")
            return match.group(0)
        try:
            with open(found, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            ext = os.path.splitext(found)[1].lower().strip('.')
            mime_map = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'svg': 'image/svg+xml'}
            mime = mime_map.get(ext, 'image/png')
            print(f"  [OK] Embedded: {os.path.basename(found)}")
            return f'![{alt}](data:{mime};base64,{img_data})'
        except Exception as e:
            print(f"  [ERR] {e}")
            return match.group(0)
    
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_img, md_content)

# Process GitHub-style alerts
def process_alerts(html_content):
    alert_map = {
        'NOTE': ('#e8f4fd', '#1976d2', 'Catatan'),
        'TIP': ('#e8f5e9', '#388e3c', 'Tip'),
        'IMPORTANT': ('#fff3e0', '#e65100', 'Penting'),
        'WARNING': ('#fff8e1', '#f57f17', 'Peringatan'),
        'CAUTION': ('#fce4ec', '#c62828', 'Perhatian'),
    }
    for alert_type, (bg, border, label) in alert_map.items():
        # Multi-line: > [!TYPE]\n> content
        pattern = rf'<blockquote>\s*<p>\[!{alert_type}\]</p>\s*<p>(.*?)</p>\s*</blockquote>'
        replacement = f'<div style="background:{bg};border-left:4px solid {border};padding:12px 16px;margin:16px 0;border-radius:4px;page-break-inside:avoid"><strong>{label}:</strong> \\1</div>'
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        # Single-line with <br>
        pattern2 = rf'<blockquote>\s*<p>\[!{alert_type}\]\s*<br\s*/?>\s*(.*?)</p>\s*</blockquote>'
        html_content = re.sub(pattern2, replacement, html_content, flags=re.DOTALL)
    return html_content

print("Embedding images...")
md_text = embed_images(md_text)

print("Converting markdown to HTML...")
html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
html_body = process_alerts(html_body)

# Remove file:// links (not useful in PDF)
html_body = re.sub(r'<a href="file:///[^"]*">([^<]*)</a>', r'\1', html_body)

html_full = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Dokumentasi Business Framing - Olist E-Commerce</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1a1a2e;
    max-width: 210mm;
    margin: 0 auto;
    padding: 20mm 18mm;
    background: #ffffff;
}

h1 {
    font-size: 20pt;
    font-weight: 700;
    color: #0f0f23;
    margin-bottom: 4px;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
}

h2 {
    font-size: 14pt;
    font-weight: 600;
    color: #1e3a5f;
    margin-top: 28px;
    margin-bottom: 10px;
    padding-bottom: 4px;
    border-bottom: 1.5px solid #e2e8f0;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: 600;
    color: #334155;
    margin-top: 16px;
    margin-bottom: 6px;
    page-break-after: avoid;
}

p { margin-bottom: 8px; }

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th {
    background: #1e3a5f;
    color: #ffffff;
    font-weight: 600;
    padding: 7px 8px;
    text-align: left;
    border: 1px solid #1e3a5f;
}

td {
    padding: 5px 8px;
    border: 1px solid #d1d5db;
}

tr:nth-child(even) { background: #f8fafc; }
tr:nth-child(odd) { background: #ffffff; }

code {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 9pt;
    background: #f1f5f9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #be185d;
}

pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8.5pt;
    margin: 10px 0;
    page-break-inside: avoid;
}

pre code {
    background: none;
    color: #e2e8f0;
    padding: 0;
}

blockquote {
    border-left: 3px solid #2563eb;
    padding: 8px 14px;
    margin: 10px 0;
    background: #eff6ff;
    border-radius: 0 4px 4px 0;
    font-style: italic;
    color: #1e3a5f;
}

blockquote strong { font-style: normal; }

img {
    max-width: 100%;
    height: auto;
    margin: 10px auto;
    display: block;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    page-break-inside: avoid;
}

strong { font-weight: 600; }

ul, ol {
    margin: 6px 0;
    padding-left: 22px;
}

li { margin-bottom: 3px; }

@media print {
    body {
        padding: 12mm 15mm;
        font-size: 10pt;
    }
    h2 { page-break-after: avoid; }
    table, pre, img { page-break-inside: avoid; }
    h1 { font-size: 17pt; }
    h2 { font-size: 13pt; }
    h3 { font-size: 10.5pt; }
}
</style>
</head>
<body>
""" + html_body + """
</body>
</html>"""

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_full)

print(f"\nHTML saved to: {OUTPUT_HTML}")
print(f"Size: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")
print("Open this file in browser and use Ctrl+P to save as PDF.")
