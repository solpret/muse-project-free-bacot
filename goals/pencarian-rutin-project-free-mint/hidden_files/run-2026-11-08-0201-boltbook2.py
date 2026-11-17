import re, json, html

def load(p): return open(p, encoding='utf-8', errors='ignore').read()
def text_of(h):
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<[^>]+>', '\n', h)
    return html.unescape(h)

en_t = text_of(load('boltbook-2026-11-08-0201-en.html'))
raca_t = text_of(load('boltbook-2026-11-08-0201-raca.html'))

# post titles: extract from raw html <a ...> link texts? Try h1/h2/h3 and title-ish lines
raw = load('boltbook-2026-11-08-0201-en.html')
titles = re.findall(r'<h[123][^>]*>(.*?)</h[123]>', raw, flags=re.S|re.I)
print('--- H-titles EN ---')
for t in titles:
    t2 = re.sub(r'<[^>]+>','',t).strip()
    if t2: print(' *', t2[:160])

# context around each address in EN text
pat = re.compile(r'0x[0-9a-fA-F]{40}')
seen=set()
print('--- EN address contexts ---')
for m in pat.finditer(en_t):
    a=m.group(0).lower()
    if a in seen: continue
    seen.add(a)
    s=max(0,m.start()-350); e=min(len(en_t), m.end()+350)
    ctx=' '.join(en_t[s:e].split())
    print(f'\n### {a}\n{ctx[:700]}')

print('\n--- RACA address contexts (new vs EN only) ---')
en_set=set(x.lower() for x in pat.findall(en_t))
seen=set()
for m in pat.finditer(raca_t):
    a=m.group(0).lower()
    if a in seen or a in en_set: continue
    seen.add(a)
    s=max(0,m.start()-350); e=min(len(raca_t), m.end()+350)
    ctx=' '.join(raca_t[s:e].split())
    print(f'\n### {a}\n{ctx[:700]}')
