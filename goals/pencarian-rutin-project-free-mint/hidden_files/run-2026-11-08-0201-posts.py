import re, html
def load(p): return open(p, encoding='utf-8', errors='ignore').read()
def text_of(h):
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<[^>]+>', '\n', h)
    return html.unescape(h)
t = text_of(load('boltbook-2026-11-08-0201-en.html'))
# find positions of key titles and print following 1500 chars
keys = ['SPACE ROT', 'Luma Agent', 'Night Shift Agents 9.397', 'How to Mint AlphaPulse', 'Meow & Bark', '盯盘笔记', 'ORBITA pace check', 'Shadow Blade', 'Horus 2,000/2,000', 'Horus closed', 'Agent Wilds']
for k in keys:
    i = t.find(k)
    if i < 0:
        print(f'### {k}: NOT FOUND'); continue
    print(f'\n===== {k} =====')
    print(' '.join(t[i:i+1800].split())[:1800])
