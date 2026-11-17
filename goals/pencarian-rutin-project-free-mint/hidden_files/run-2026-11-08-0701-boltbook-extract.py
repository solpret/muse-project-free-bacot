import re, json, html

def parse(fn):
    raw = open(fn, encoding='utf-8', errors='ignore').read()
    text = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
    text = re.sub(r'\s+', ' ', text)
    addrs = sorted(set(a for a in re.findall(r'0x[0-9a-fA-F]{40}', raw)))
    # post titles: look for h-tags / link text near 'free'
    # extract link texts
    links = re.findall(r'<a[^>]*>(.*?)</a>', raw, re.S)
    clean_links = []
    for l in links:
        t = html.unescape(re.sub(r'<[^>]+>', ' ', l)).strip()
        t = re.sub(r'\s+', ' ', t)
        if t and len(t) < 200:
            clean_links.append(t)
    return text, addrs, clean_links

for fn in ['run-2026-11-08-0701-boltbook-en.html','run-2026-11-08-0701-boltbook-zh.html']:
    text, addrs, links = parse(fn)
    print('====', fn, 'bytes', len(open(fn,'rb').read()))
    print('addrs (%d):' % len(addrs))
    for a in addrs: print('  ', a)
    print('links (%d):' % len(links))
    for l in links: print('  |', l)
    print('--- text snippet around free ---')
    for m in re.finditer(r'.{0,80}free.{0,120}', text, re.I):
        print('  *', m.group(0)[:220])
        if m.start() > 20000: break
