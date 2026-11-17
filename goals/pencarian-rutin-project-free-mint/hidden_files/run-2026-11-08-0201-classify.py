import re, json

def load(p): return open(p, encoding='utf-8', errors='ignore').read()
def text_of(h):
    import html
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<[^>]+>', '\n', h)
    return html.unescape(h)

snap = json.load(open('onchain-snapshot.json'))
bridge = json.load(open('scan-bridge.json'))['contracts']
seen = json.load(open('onchain-scan-seen.json'))['contracts']
hot = json.load(open('hot-leg-seen.json'))
excl = snap.get('excluded', {})
trackc = snap.get('track_c', {})

# build address -> snapshot key map (search all string values)
def addr_map(d):
    m = {}
    for k, v in d.items():
        s = json.dumps(v).lower()
        for a in set(re.findall(r'0x[0-9a-f]{40}', s)):
            m[a] = k
    return m
snap_map = addr_map(snap.get('contracts', {}))
excl_map = addr_map(excl)
tc_map = addr_map(trackc)
bridge_l = {k.lower(): v for k, v in bridge.items()}
seen_l = {k.lower(): v for k, v in seen.items()}
hot_l = {k.lower(): v for k, v in hot.items()}

en = set(a.lower() for a in re.findall(r'0x[0-9a-fA-F]{40}', load('boltbook-2026-11-08-0201-en.html')))
raca = set(a.lower() for a in re.findall(r'0x[0-9a-fA-F]{40}', load('boltbook-2026-11-08-0201-raca.html')))
all_a = sorted(en | raca)
print('total unique addrs EN+RACA:', len(all_a))
for a in all_a:
    parts = []
    if a in snap_map: parts.append(f"SNAPSHOT[{snap_map[a]}]")
    if a in excl_map: parts.append(f"EXCLUDED[{excl_map[a]}]")
    if a in tc_map: parts.append(f"TRACK_C[{tc_map[a]}]")
    if a in bridge_l:
        b = bridge_l[a]
        parts.append(f"BRIDGE[discarded={b.get('same_owner_discarded')}]")
    if a in seen_l:
        v = seen_l[a]
        fs = v.get('first_seen_block') if isinstance(v, dict) else v
        parts.append(f"SCAN-SEEN[first_seen_block={fs}]")
    if a in hot_l:
        v = hot_l[a]
        fs = v.get('first_seen') if isinstance(v, dict) else v
        note = (v.get('note') if isinstance(v, dict) else '') or ''
        parts.append(f"HOTLEG[first_seen={fs} note={str(note)[:120]}]")
    print(f"{a} :: {'; '.join(parts) if parts else 'NOWHERE (never-seen-anywhere)'}")
