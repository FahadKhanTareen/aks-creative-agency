"""Check blog discovery before opening a publication PR. Run from any directory."""
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import sys

ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=set(); self.canonical=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a': self.links.add(attrs.get('href',''))
        if tag=='link' and attrs.get('rel')=='canonical': self.canonical=attrs.get('href')
index=Links(); index.feed((ROOT/'blog/index.html').read_text(encoding='utf-8'))
urls={el.text for el in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')}
errors=[]
for page in sorted((ROOT/'blog').glob('*.html')):
    if page.name=='index.html': continue
    parsed=Links(); parsed.feed(page.read_text(encoding='utf-8'))
    if not parsed.canonical:
        errors.append(f'{page.name}: missing canonical'); continue
    if parsed.canonical not in urls: errors.append(f'{page.name}: canonical missing from sitemap.xml')
    path='/blog/'+page.stem
    if not {path,path+'.html',parsed.canonical}&index.links:
        errors.append(f'{page.name}: missing link in blog/index.html')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('PASS: every blog article has a canonical URL, sitemap entry and blog-index link.')
