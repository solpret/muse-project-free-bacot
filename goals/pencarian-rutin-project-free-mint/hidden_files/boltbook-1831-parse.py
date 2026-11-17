#!/usr/bin/env python3
"""Parse Boltbook front page HTML (run 1831) into posts.json + .txt, like run 1631."""
import re, json, html, sys

def parse(fn):
    s = open(fn, encoding='utf-8').read()
    arts = re.findall(r'<article class="card post" data-id="([^"]+)">(.*?)</article>', s, re.S)
    posts = []
    for pid, body in arts:
        m = re.search(r'<a class="author"[^>]*>([^<]+)</a>', body)
        author = m.group(1) if m else ''
        m = re.search(r'<time datetime="([^"]+)">([^<]+)</time>', body)
        dt, ago = (m.group(1), m.group(2)) if m else ('', '')
        m = re.search(r'<h3><a[^>]*>(.*?)</a></h3>', body, re.S)
        title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        title = re.sub(r'\s+', ' ', title)
        m = re.search(r'<p class="preview">(.*?)</p>', body, re.S)
        preview = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        preview = re.sub(r'\s+', ' ', preview)
        addrs = sorted(set(re.findall(r'0x[a-fA-F0-9]{40}', body)))
        posts.append({'id': pid, 'author': author, 'dt': dt, 'ago': ago,
                      'title': title, 'preview': preview, 'addresses': addrs})
    return posts, s

def to_text(s):
    t = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t)
    t = html.unescape(t)
    lines = [ln.strip() for ln in t.split('\n')]
    return '\n'.join(ln for ln in lines if ln)

if __name__ == '__main__':
    for lang in ('en', 'zh'):
        fn = f'boltbook-2026-11-07-1831-{lang}.html'
        posts, s = parse(fn)
        with open(f'boltbook-2026-11-07-1831-{lang}.txt', 'w', encoding='utf-8') as f:
            f.write(to_text(s))
        if lang == 'en':
            with open('boltbook-2026-11-07-1831-posts.json', 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=1)
        print(lang, 'posts:', len(posts))
        for p in posts:
            print(' ', p['id'], p['author'], p['ago'], '|', p['title'][:90], '| addrs:', p['addresses'])
        # unique addresses
        all_a = sorted({a for p in posts for a in p['addresses']})
        print(' unique addrs:', all_a)
