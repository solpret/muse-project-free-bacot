#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-18 21:34 WIB. Legs 1-4 + bridge, fast, skip-on-stall."""
import json, re, subprocess, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from eth_hash.auto import keccak

HF = '/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/'
RUN = '2026-11-18-2134'
USER = '0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
REGISTRY = '0x60b9262456de011f7d15a54cdd8c48baaa8b022f'
EXCLUDED = {'0x827e83e49bd7e15b67efa0e90fc25f17b8d96124', '0x8b47354e7b76b1970a0d06365c8244a810d37493'}
t0 = time.time()

def wib_now():
    return time.strftime('%Y-%m-%d %H:%M WIB', time.gmtime(time.time() + 7 * 3600))

def curl(url, timeout=10):
    try:
        r = subprocess.run(['curl', '-sS', '-m', str(timeout), '-w', '\n%{http_code}', url],
                           capture_output=True, text=True, timeout=timeout + 5)
        body, _, code = r.stdout.rpartition('\n')
        return int(code.strip() or 0), body, r.stderr
    except Exception as e:
        return 0, '', str(e)

log = {'run': 'free-mint-hot-leg 2026-11-18 21:34 WIB', 'started_wib': wib_now(),
       'transport': 'Sourcify feed + Boltbook EN/ZH via curl (10s); leg3 Sourcify ABI via curl threaded (10w, 10s); leg4 bsc-dataseed eth_call batches of 5 (15s, 1 retry)'}

seen = json.load(open(HF + 'hot-leg-seen.json'))
seen_keys = {k.lower() for k in seen.keys()}
snap = json.load(open(HF + 'onchain-snapshot.json'))
snap_addrs = set()
for sec in ('contracts', 'track_c', 'pending_claims'):
    v = snap.get(sec, {})
    if isinstance(v, dict):
        for item in v.values():
            if isinstance(item, dict) and item.get('address'):
                snap_addrs.add(item['address'].lower())
reported = json.load(open(HF + 'hot-leg-reported.json'))

# ---------- LEG 1: Sourcify feed ----------
code, body, err = curl('https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc', 10)
feed_addrs, verified = [], []
if code == 200:
    try:
        j = json.loads(body)
        res = j.get('results', j if isinstance(j, list) else [])
        for r in res:
            a = r.get('address') if isinstance(r, dict) else None
            if a:
                feed_addrs.append(a)
                verified.append(r.get('verifiedAt'))
    except Exception:
        feed_addrs = list(dict.fromkeys(re.findall(r'0x[0-9a-fA-F]{40}', body)))
feed_new = [a for a in feed_addrs if a.lower() not in seen_keys and a.lower() != REGISTRY.lower()
            and a.lower() not in EXCLUDED]
log['leg1_sourcify'] = {'http': code, 'total': len(feed_addrs), 'new': len(feed_new),
                        'new_contracts': feed_new,
                        'verified_window': [verified[0], verified[-1]] if verified else [],
                        'error': err[:200] if code != 200 else ''}

# ---------- LEG 2: Boltbook EN + ZH ----------
EN_KW = ['free share', 'first share free', '1 free share', 'free mint share']
ZH_KW = ['免费份额', '首个免费', '免费铸造', '免费mint']
leg2 = {}
for tag, url in (('leg2_boltbook_en', 'https://boltbook.fun/'),
                 ('leg2_boltbook_zh', 'https://boltbook.fun/?lang=zh')):
    code, body, err = curl(url, 10)
    addrs = list(dict.fromkeys(re.findall(r'0x[0-9a-fA-F]{40}', body))) if code == 200 else []
    low = body.lower()
    leg2[tag] = {'bytes': len(body), 'http_code': code,
                 'addresses': len(addrs),
                 'new': len([a for a in addrs if a.lower() not in seen_keys]),
                 'new_contracts': [a for a in addrs if a.lower() not in seen_keys],
                 'free_kw': sum(low.count(k) for k in EN_KW),
                 'zh_free_kw': sum(body.count(k) for k in ZH_KW),
                 'error': err[:200] if code != 200 else ''}
log.update(leg2)

# ---------- LEG 3: shape-check new contracts ----------
FREE_VIEWS = ['freeSharesRemaining', 'freeClaimed', 'freeFor', 'freeLeft', 'freeUsed',
              'freeAvailable', 'freeSharePoolExhausted', 'freeSharesClaimed', 'freeMinted']
def shape_check(addr):
    abi = None
    for url in (f'https://sourcify.dev/server/v2/contract/56/{addr}',
                f'https://repo.sourcify.dev/contracts/full_match/56/{addr}/metadata.json'):
        code, body, err = curl(url, 10)
        if code == 200:
            try:
                j = json.loads(body)
                abi = j.get('abi') or (j.get('output', {}).get('abi') if isinstance(j.get('output'), dict) else None)
                if abi:
                    break
            except Exception:
                pass
    if not abi:
        return {'address': addr, 'status': 'shape-check-failed', 'error': 'no ABI from Sourcify (v2+repo)'}
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

to_check = [a for a in feed_new if a.lower() not in EXCLUDED]
# Boltbook-new addresses that are not in feed: shape-check too (bounded, max 5)
bb_new = [a for a in leg2['leg2_boltbook_en']['new_contracts'] + leg2['leg2_boltbook_zh']['new_contracts']
          if a not in to_check][:5]
to_check = list(dict.fromkeys(to_check + bb_new))
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(shape_check, to_check))
log['leg3_shape_check'] = results
log['leg3_sale_shape'] = [r['address'] for r in results if r.get('S1') or r.get('S2')]
log['leg3_failed'] = [r['address'] for r in results if r.get('status') == 'shape-check-failed']
checked = [r['address'] for r in results if r.get('status') == 'checked']
for a in checked:
    seen[a] = {'first_seen_wib': wib_now(), 'source': 'hot-leg-2134', 'shape': 'checked-not-sale-shape'}
log['seen_added'] = checked
log['seen_n'] = len(seen)

# ---------- LEG 4: re-read active snapshot items ----------
def sel(sig):
    return '0x' + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return '0x' + a.lower().replace('0x', '').rjust(64, '0')

def enc_uint(n):
    return '0x' + format(n, '064x')

def enc_call(sig, args):
    data = sel(sig)
    for kind, val in args:
        data += (enc_addr(val) if kind == 'address' else enc_uint(val))[2:]
    return data

ITEMS = [
    ('DGF CARD', '0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72',
     [('totalMinted', 'totalMinted()', []), ('balanceOf_user', 'balanceOf(address)', [('address', USER)])]),
    ('BinanceAI', '0x46cb1D3efd4307506Cda7EbBa5a51be64746739E',
     [('launched', 'launched()', []), ('failed', 'failed()', []),
      ('tokenClaimed_user', 'tokenClaimed(address)', [('address', USER)])]),
    ('AlphaPulse V1', '0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711',
     [('totalSupply', 'totalSupply()', []), ('mintOpen', 'mintOpen()', []),
      ('balanceOf_user', 'balanceOf(address)', [('address', USER)])]),
    ('FABE', '0xFabE022a5943462fee1Bd221791945DA57510BE8',
     [('freeSharesRemaining', 'freeSharesRemaining()', []), ('launched', 'launched()', []),
      ('freeSharesClaimed_user', 'freeSharesClaimed(address)', [('address', USER)]),
      ('totalShares', 'totalShares()', [])]),
    ('PUNNY', '0xaFAE0Bf373ad87E88555afe1605111F66C99062C',
     [('freeMinted', 'freeMinted()', []), ('FREE_SUPPLY', 'FREE_SUPPLY()', []),
      ('totalMinted', 'totalMinted()', []),
      ('hasClaimedFree_user', 'hasClaimedFree(address)', [('address', USER)])]),
    ('STOCK AGENT', '0xba7068233da805bdebcc167be361c219002e6b7f',
     [('totalSupply', 'totalSupply()', []), ('freeLeft', 'freeLeft()', []),
      ('quote_user_1', 'quote(address,uint256)', [('address', USER), ('uint', 1)]),
      ('freeMintedByWallet_user', 'freeMintedByWallet(address)', [('address', USER)]),
      ('balanceOf_user', 'balanceOf(address)', [('address', USER)])]),
    ('AGENTONE', '0x84D82E933D7781fe11245e7bbd3Eb23dbb963666',
     [('freeMinted', 'freeMinted()', [])]),
]
calls = []
meta = []
for name, addr, views in ITEMS:
    for vname, sig, args in views:
        calls.append({'to': addr, 'data': enc_call(sig, args)})
        meta.append((name, vname))

def rpc_batch(batch, bid_off):
    payload = json.dumps([{'jsonrpc': '2.0', 'id': bid_off + i, 'method': 'eth_call',
                           'params': [{'to': c['to'], 'data': c['data']}, 'latest']}
                          for i, c in enumerate(batch)]).encode()
    req = urllib.request.Request('https://bsc-dataseed.binance.org', data=payload,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def decode(h):
    if not isinstance(h, str) or len(h) < 4:
        return None
    try:
        v = int(h, 16)
        return v
    except Exception:
        return None

reads, errors, failures = {}, [], []
block = None
try:
    req = urllib.request.Request('https://bsc-dataseed.binance.org',
                                 data=json.dumps({'jsonrpc': '2.0', 'id': 0, 'method': 'eth_blockNumber',
                                                  'params': []}).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        block = int(json.loads(r.read())['result'], 16)
except Exception as e:
    errors.append('eth_blockNumber: ' + str(e)[:150])

for off in range(0, len(calls), 5):
    batch = calls[off:off + 5]
    res = None
    for attempt in range(2):
        try:
            res = rpc_batch(batch, off)
            break
        except Exception as e:
            if attempt == 1:
                errors.append(f'calls {off}-{off + len(batch) - 1}: {type(e).__name__}: {str(e)[:150]}')
            time.sleep(1)
    if res is None:
        for i, (name, vname) in enumerate(meta[off:off + len(batch)]):
            reads.setdefault(name, {})[vname] = None
            failures.append(f'{name} {vname}')
        continue
    by_id = {r.get('id'): r for r in res} if isinstance(res, list) else {}
    for i, (name, vname) in enumerate(meta[off:off + len(batch)]):
        r = by_id.get(off + i, {})
        val = decode(r.get('result')) if 'result' in r else None
        reads.setdefault(name, {})[vname] = val
        if val is None:
            failures.append(f'{name} {vname}')

log['leg4_reread'] = {'block': block, 'reads': reads, 'errors': errors}
log['leg4_read_failures'] = failures

# ---------- promotion / change check vs previous values ----------
prev = {
    'DGF CARD': {'totalMinted': 1671},
    'BinanceAI': {'launched': 0, 'failed': 1},
    'AlphaPulse V1': {'totalSupply': 34, 'mintOpen': 1, 'balanceOf_user': 0},
    'FABE': {'freeSharesRemaining': 2821, 'launched': 0, 'freeSharesClaimed_user': 1, 'totalShares': 512},
    'PUNNY': {'freeMinted': 379, 'FREE_SUPPLY': 999, 'totalMinted': 379},
    'STOCK AGENT': {},
    'AGENTONE': {},
}
changes = {}
for name, pv in prev.items():
    for k, old in pv.items():
        new = reads.get(name, {}).get(k)
        if new is not None and new != old:
            changes.setdefault(name, {})[k] = {'old': old, 'new': new}
log['leg4_changes'] = changes
punny = reads.get('PUNNY', {})
punny_pct = (round(100 * punny['freeMinted'] / punny['FREE_SUPPLY'], 2)
             if punny.get('freeMinted') is not None and punny.get('FREE_SUPPLY') else None)
stock = reads.get('STOCK AGENT', {})
stock_pct = (round(100 * stock['totalSupply'] / 1111, 1)
             if stock.get('totalSupply') is not None else None)
log['leg4_promotion_check'] = {
    'PUNNY_free_pct': punny_pct,
    'PUNNY_note': 'mintStart 2026-11-17 20:32 WIB; age-exclusion ALREADY REPORTED once at the 20:34 run - not re-reported; website gate UNVERIFIED -> no promotion either way.',
    'STOCK_totalSupply': stock.get('totalSupply'), 'STOCK_free_pct_inferred': stock_pct,
    'STOCK_note': 'crossed 70% already REPORTED at 18:44 run - no re-report; age UNVERIFIED + website gate UNVERIFIED -> still no strong-lead promotion.',
    'AGENTONE_note': 'minted by user 17:59 run (2 hero cards, quota used); pool tracking only - no promotion possible (user slot already used). FREE_TOTAL 10000.',
    'DGF_note': 'age + free% still unverified (no promotion); website verified but that alone is not a tier.',
    'BinanceAI_note': 'refund/failed phase already in main-run 21:01 note (launched=0, failed=1, isRefundPhase=1); check reported.json before any re-report.',
}
log['reported_status_binanceai'] = {k: v for k, v in reported.items()
                                    if 'binance' in k.lower() or '46cb1d' in k.lower()}

# ---------- scan bridge (read-only) ----------
try:
    bridge = json.load(open(HF + 'scan-bridge.json'))
    baddrs = []
    if isinstance(bridge, dict):
        for v in bridge.values():
            if isinstance(v, dict) and v.get('address'):
                baddrs.append(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, dict) and it.get('address'):
                        baddrs.append(it)
    elif isinstance(bridge, list):
        baddrs = [it for it in bridge if isinstance(it, dict) and it.get('address')]
    not_in = [b for b in baddrs if b['address'].lower() not in snap_addrs]
    discarded = [b for b in baddrs if b.get('same_owner_discarded')]
    log['bridge'] = {'total': len(baddrs), 'not_in_snapshot': len(not_in),
                     'not_in_snapshot_list': [b.get('address') for b in not_in],
                     'same_owner_discarded': len(discarded),
                     'note': 'bridge contracts not in snapshot are not reported as new; no bridge promotion/change unless leg4 shows one.'}
except Exception as e:
    log['bridge'] = {'error': str(e)[:200], 'note': 'bridge unreadable - skipped, run continues'}

log['elapsed_s'] = round(time.time() - t0, 1)
log['executions'] = 'none - no preview, no mint, no claim (read-only run)'
sale = log['leg3_sale_shape']
if sale or changes:
    log['result'] = 'REVIEW - sale shape or state change found, see leg3_sale_shape / leg4_changes'
else:
    log['result'] = 'SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim.'

json.dump(log, open(HF + f'hot-leg-run-{RUN}.json', 'w'), indent=1)
json.dump({'reads': reads, 'errors': errors, 'n_calls': len(calls), 'elapsed_s': log['elapsed_s'],
           'block': block, 'started_wib': log['started_wib']},
          open(HF + f'hot-leg-run-{RUN}-reread.json', 'w'), indent=1)
json.dump(seen, open(HF + 'hot-leg-seen.json', 'w'))
print(json.dumps({k: log[k] for k in ('leg1_sourcify', 'leg2_boltbook_en', 'leg2_boltbook_zh',
                                       'leg3_sale_shape', 'leg3_failed', 'seen_added',
                                       'leg4_changes', 'leg4_promotion_check', 'bridge',
                                       'reported_status_binanceai', 'elapsed_s', 'result')}, indent=1))
print('LEG4_READS:', json.dumps(reads))
print('LEG4_ERRORS:', json.dumps(errors))
print('LEG4_FAILURES:', json.dumps(failures))
