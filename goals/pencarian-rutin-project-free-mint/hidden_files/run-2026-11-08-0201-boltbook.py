import re, json, html

def load(p):
    return open(p, encoding='utf-8', errors='ignore').read()

def text_of(h):
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<[^>]+>', '\n', h)
    return html.unescape(h)

en = load('boltbook-2026-11-08-0201-en.html')
zh = load('boltbook-2026-11-08-0201-zh.html')
raca = load('boltbook-2026-11-08-0201-raca.html')
en_t, zh_t, raca_t = text_of(en), text_of(zh), text_of(raca)

pat = re.compile(r'0x[0-9a-fA-F]{40}')
def addrs(t): return sorted(set(a.lower() for a in pat.findall(t)))
en_a, zh_a, raca_a = addrs(en), addrs(zh), addrs(raca)
print('EN addrs:', len(en_a), en_a)
print('ZH addrs:', len(zh_a), zh_a)
print('EN==ZH:', en_a == zh_a)
print('RACA addrs:', len(raca_a), raca_a)
print('RACA extra vs EN:', sorted(set(raca_a)-set(en_a)))
for kw in ['free mint','free share','first share free','免费份额','首个免费','免费铸造','免费mint','free shares']:
    print(f"kw {kw!r}: EN={en_t.lower().count(kw.lower())} ZH={zh_t.lower().count(kw.lower())} RACA={raca_t.lower().count(kw.lower())}")

# post titles: pull <h...> or link texts? print lines containing 'free' or project-ish
lines = [l.strip() for l in en_t.split('\n') if l.strip()]
print('--- EN lines mentioning mint/free/claim (first 120) ---')
n=0
for l in lines:
    if re.search(r'free|mint|claim|refund|phase', l, re.I):
        print(' ', l[:220]); n+=1
        if n>=120: break
