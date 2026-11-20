#!/usr/bin/env python3
"""free-mint-hot-leg 2134 follow-up: fix leg2-EN (follow redirect), retry leg3 with -L repo
metadata, confirm AGENTONE sellout + retry PUNNY/FABE failed views."""
import json, re, subprocess, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from eth_hash.auto import keccak

HF = '/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/'
RUN = '2026-11-18-2134'
USER = '0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
REGISTRY = '0x60b9262456de011f7d15a54cdd8c48baaa8b022f'
t0 = time.time()
log = json.load(open(HF + f'hot-leg-run-{RUN}.json'))
seen = json.load(open(HF + 'hot-leg-seen.json'))
seen_keys = {k.lower() for k in seen.keys()}

def wib_now():
    return time.strftime('%Y-%m-%d %H:%M WIB', time.gmtime(time.time() + 7 * 3600))

def curl(url, timeout=10, follow=False):
    cmd = ['curl', '-sS', '-m', str(timeout), '-w', '\n%{http_code}']
    if follow:
        cmd.append('-L')
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        body, _, code = r.stdout.rpartition('\n')
        return int(code.strip() or 0), body, r.stderr
    except Exception as e:
        return 0, '', str(e)

# ---------- leg2 EN redo (from already-downloaded followed page) ----------
body = open('/tmp/bb-en.html').read()
addrs = list(dict.fromkeys(re.findall(r'0x[0-9a-fA-F]{40}', body)))
low = body.lower()
en = {'bytes': len(body), 'http_code': 200, 'addresses': len(addrs),
      'new': len([a for a in addrs if a.lower() not in seen_keys]),
      'new_contracts': [a for a in addrs if a.lower() not in seen_keys],
      'free_kw': sum(low.count(k) for k in ['free share', 'first share free', '1 free share', 'free mint share']),
      'zh_free_kw': sum(body.count(k) for k in ['免费份额', '首个免费', '免费铸造', '免费mint']),
      'note': 'EN first fetch 302 -> https://boltbook.fun/?lang=en (curl without -L); refetched with -L, 200.'}
log['leg2_boltbook_en'] = en

# ---------- leg3 retry with fixed transport ----------
FREE_VIEWS = ['freeSharesRemaining', 'freeClaimed', 'freeFor', 'freeLeft', 'freeUsed',
              'freeAvailable', 'freeSharePoolExhausted', 'freeSharesClaimed', 'freeMinted']

def shape_check(addr):
    abi = None
    for url, fol in ((f'https://repo.sourcify.dev/contracts/full_match/56/{addr}/metadata.json', True),
                     (f'https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi', False)):
        code, b, err = curl(url, 10, follow=fol)
        if code == 200:
            try:
                j = json.loads(b)
                abi = j.get('abi')
                if abi:
                    break
            except Exception:
                pass
    if not abi:
        return {'address': addr, 'status': 'shape-check-failed', 'error': 'no ABI (repo -L + v2 ?fields=abi)'}
    fns = [f for f in abi if isinstance(f, dict) and f.get('type') == 'function']
    names = [f.get('name', '') for f in fns]
    has_mint = any('mint' in n.lower() for n in names)
    has_quote = any(n.lower() in ('quote', 'cost', 'getquote', 'price', 'getprice', 'mintprice', 'mintcost')
                    or 'quote' in n.lower() for n in names)
    free_views = [v for v in FREE_VIEWS if v in names]
    raw = json.dumps(abi)
    agent_ref = (any('agent' in n.lower() for n in names)
                 or REGISTRY.lower() in raw.lower() or 'agentgate' in raw.lower())
    is_token = all(x in names for x in ('name', 'symbol', 'decimals', 'totalSupply'))
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and 'mintFree' in names
              and ('freeClaimed' in names or 'freeMinted' in names)
              and any(x in names for x in ('FREE_SLOTS', 'FREE_SUPPLY')) and agent_ref)
    return {'address': addr, 'S1': s1, 'S2': s2, 'has_mint': has_mint, 'has_quote': has_quote,
            'free_views': free_views, 'agent_ref': agent_ref, 'is_token': is_token,
            'n_fns': len(fns), 'status': 'checked'}

to_check = log['leg3_failed']
# add boltbook-EN new addresses not already in the retry list (bounded 5)
extra = [a for a in en['new_contracts'] if a not in to_check][:5]
to_check = list(dict.fromkeys(to_check + extra))
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(shape_check, to_check))
log['leg3_shape_check_retry'] = results
log['leg3_sale_shape'] = [r['address'] for r in results if r.get('S1') or r.get('S2')]
log['leg3_failed'] = [r['address'] for r in results if r.get('status') == 'shape-check-failed']
checked = [r['address'] for r in results if r.get('status') == 'checked']
for a in checked:
    seen[a] = {'first_seen_wib': wib_now(), 'source': 'hot-leg-2134-retry', 'shape': 'checked-not-sale-shape'}
log['seen_added'] = checked
log['seen_n'] = len(seen)

# ---------- leg4 confirm: AGENTONE sellout + retry failed views ----------
def sel(sig):
    return '0x' + keccak(sig.encode()).hex()[:8]

def enc_call(sig, args):
    data = sel(sig)
    for kind, val in args:
        h = val.lower().replace('0x', '').rjust(64, '0') if kind == 'address' else format(val, '064x')
        data += h
    return data

CONFIRM = [
    ('AGENTONE', '0x84D82E933D7781fe11245e7bbd3Eb23dbb963666',
     [('freeMinted', 'freeMinted()', [])]),
    ('PUNNY', '0xaFAE0Bf373ad87E88555afe1605111F66C99062C',
     [('freeMinted', 'freeMinted()', []), ('FREE_SUPPLY', 'FREE_SUPPLY()', []),
      ('totalMinted', 'totalMinted()', [])]),
    ('FABE', '0xFabE022a5943462fee1Bd221791945DA57510BE8',
     [('freeSharesClaimed_user', 'freeSharesClaimed(address)', [('address', USER)]),
      ('totalShares', 'totalShares()', [])]),
]
calls, meta = [], []
for name, addr, views in CONFIRM:
    for vname, sig, args in views:
        calls.append({'to': addr, 'data': enc_call(sig, args)})
        meta.append((name, vname))

def rpc_batch(batch, off):
    payload = json.dumps([{'jsonrpc': '2.0', 'id': off + i, 'method': 'eth_call',
                           'params': [{'to': c['to'], 'data': c['data']}, 'latest']}
                          for i, c in enumerate(batch)]).encode()
    req = urllib.request.Request('https://bsc-dataseed.binance.org', data=payload,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

confirm, cerr = {}, []
for off in range(0, len(calls), 5):
    res = None
    for attempt in range(2):
        try:
            res = rpc_batch(calls[off:off + 5], off)
            break
        except Exception as e:
            if attempt == 1:
                cerr.append(f'calls {off}: {type(e).__name__}: {str(e)[:150]}')
            time.sleep(1)
    if res is None:
        continue
    by_id = {r.get('id'): r for r in res} if isinstance(res, list) else {}
    for i, (name, vname) in enumerate(meta[off:off + len(calls)]):
        r = by_id.get(off + i, {})
        h = r.get('result')
        try:
            confirm.setdefault(name, {})[vname] = int(h, 16) if isinstance(h, str) and len(h) > 2 else None
        except Exception:
            confirm.setdefault(name, {})[vname] = None
log['leg4_confirm'] = {'reads': confirm, 'errors': cerr}
aone = confirm.get('AGENTONE', {}).get('freeMinted')
log['agentone_sellout'] = {
    'freeMinted': aone, 'FREE_TOTAL': 10000,
    'sold_out': (aone == 10000),
    'note': 'first successful AGENTONE freeMinted read since 9959/10000 (21:01 main run retained value); '
            'user slot already used (minted 17:59 run) - sellout is a track-C change report, no action.',
}
# merge confirmed values into leg4 reads for the record
for name, views in confirm.items():
    for k, v in views.items():
        if v is not None:
            log['leg4_reread']['reads'].setdefault(name, {})[k] = v
log['leg4_read_failures'] = [f for f in log.get('leg4_read_failures', [])
                             if not (f.startswith('PUNNY') and confirm.get('PUNNY', {}).get(f.split()[-1]) is not None)
                             and not (f.startswith('FABE') and confirm.get('FABE', {}).get(f.split()[-1]) is not None)]
punny = log['leg4_reread']['reads'].get('PUNNY', {})
if punny.get('freeMinted') is not None and punny.get('FREE_SUPPLY'):
    log['leg4_promotion_check']['PUNNY_free_pct'] = round(100 * punny['freeMinted'] / punny['FREE_SUPPLY'], 2)
log['elapsed_s'] = round(time.time() - t0 + log.get('elapsed_s', 0), 1)
sale = log['leg3_sale_shape']
changes = log.get('leg4_changes', {})
if log['agentone_sellout']['sold_out']:
    log['result'] = 'REPORT-CHANGE - AGENTONE track-C sold out (freeMinted 10000/10000, confirmed); no other lead/candidate/change.'
elif sale or changes:
    log['result'] = 'REVIEW - sale shape or state change found, see leg3_sale_shape / leg4_changes'
else:
    log['result'] = 'SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim.'
json.dump(log, open(HF + f'hot-leg-run-{RUN}.json', 'w'), indent=1)
json.dump(seen, open(HF + 'hot-leg-seen.json', 'w'))
print(json.dumps({'leg2_en_redo': en, 'leg3_sale_shape': log['leg3_sale_shape'],
                  'leg3_failed': log['leg3_failed'], 'seen_added': log['seen_added'],
                  'leg4_confirm': confirm, 'agentone_sellout': log['agentone_sellout'],
                  'leg4_read_failures_left': log['leg4_read_failures'],
                  'punny_pct': log['leg4_promotion_check'].get('PUNNY_free_pct'),
                  'result': log['result']}, indent=1))
