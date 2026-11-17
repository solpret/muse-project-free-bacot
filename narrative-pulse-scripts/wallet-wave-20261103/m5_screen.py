#!/usr/bin/env python3
"""Method 5 step 2: screen early-LP providers with the 7 trusted filters.
READ-ONLY. Topics computed via keccak. Candidates = providers (excluding each
pair's first minter) in >=2 pairs; (c) needs >=3 pairs (early LP counts, and
m1 early-buyer membership is reported separately). (d) realized profit is
UNVERIFIED for all (archive price reads fail on free RPC, same as m1-2/m4).
Saves m5_screen.json."""
import json, re, sys, time
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
import ankr
import fast_rpc
from Crypto.Hash import keccak

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'

def k(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()

BURN_V2 = k('Burn(address,address,uint256,uint256)')
BURN_V3 = k('Burn(address,int24,int24,uint128,uint256,uint256)')

FEED = ['0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6',
        '0x2325f175975abdbcde555c79cc8e63381d28551b',
        '0xbf004bff64725914ee36d03b87d6965b0ced4903',
        '0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7',
        '0x892200223bdfb11d2506c5ab1cae9222ce253acc',
        '0xda91cefe240175e6fab56271110427a4195ab71f']
TIERC = ['0x341bed5b412968755f3dd6e9946636ac6f97457a',
         '0xd124dd5825ecaad959acdea6336926eb40aa0c9b',
         '0x5cf3f945620ba1a3cc9065bfc728b172a0f',
         '0x355ea9e542b36c645a2dee63b9df079ccb9df3db']
HUB = '0x4982085c9e2f89f2ecb8131eca71afad896e89cb'
PROV = '0x9b79cc64cd3e5ec86d951acb27ddbd9ed660cd07'
PAIR1 = '0x2fc2a32f16d683038187b87e0409d122da6f17d4'  # corrected, 40 hex

def blk(x):
    return int(x, 16) if isinstance(x, str) else int(x)

def tx_page(wallet, frm, to, page_size=1000, token=None):
    params = {'blockchain': 'bsc', 'address': [wallet], 'pageSize': page_size,
              'fromBlock': hex(frm), 'toBlock': hex(to)}
    if token:
        params['pageToken'] = token
    r = ankr.ankr_post('ankr_getTransactionsByAddress', params)
    res = r.get('result', {}) if isinstance(r, dict) else {}
    return res.get('transactions', []), res.get('nextPageToken')

def has_tx(wallet, frm, to):
    txs, _ = tx_page(wallet, frm, to, page_size=1)
    return len(txs) > 0

def first_tx_block(wallet, latest):
    if not has_tx(wallet, 0, latest):
        return None
    lo, hi = 0, latest
    while lo < hi:
        mid = (lo + hi) // 2
        if has_tx(wallet, 0, mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

def native_summary(wallet, frm, to, cap_pages=3):
    funders, funded, total, capped, token = {}, {}, 0, False, None
    for _ in range(cap_pages):
        txs, token = tx_page(wallet, frm, to, token=token)
        total += len(txs)
        for t in txs:
            if t.get('input', '') not in ('0x', ''):
                continue
            try:
                val = int(t.get('value', '0x0'), 16) / 1e18
            except Exception:
                continue
            if val <= 0 or t.get('from', '').lower() == wallet.lower():
                continue
            if t.get('to', '').lower() == wallet.lower():
                funders[t['from'].lower()] = funders.get(t['from'].lower(), 0) + val
            else:
                funded[t.get('to', '').lower()] = funded.get(t.get('to', '').lower(), 0) + val
        if not token:
            break
    else:
        capped = True
    return {'funders': funders, 'funded': funded, 'txs_scanned': total, 'capped': capped}

def logs(pool, frm, to, topics):
    r = ankr.get_logs(pool, frm, to, topics=topics)
    if isinstance(r, dict):
        res = r.get('result', {})
        if isinstance(res, dict) and 'logs' in res:
            return res['logs']
    return []

def main():
    mints = json.load(open(f'{WAVE}/m5_mints.json'))
    coins = json.load(open(f'{WAVE}/m1_coins.json'))
    m4 = json.load(open(f'{WAVE}/m4_screen.json'))
    m1code = json.load(open(f'{WAVE}/m1_code_class.json'))
    # provider -> pairs (exclude first minter per pair)
    prov_pairs = {}
    pair_info = {}
    for p in mints['pairs']:
        if p.get('type') not in ('V2', 'V3'):
            continue
        pair_info[p['coin']] = p
        fm = (p.get('first_minter') or '').lower()
        for prov, v in p.get('providers', {}).items():
            if prov.lower() == fm:
                continue
            prov_pairs.setdefault(prov.lower(), []).append(
                {'coin': p['coin'], 'pool': p['pool'], 'type': p['type'],
                 'first_block': v['first_block'], 'mint_logs': v['mint_logs'],
                 'sample_tx': v.get('sample_tx')})
    cands = {w: ps for w, ps in prov_pairs.items() if len(ps) >= 2}
    print(f'providers total={len(prov_pairs)} candidates(>=2 pairs)={len(cands)}')
    for w, ps in sorted(cands.items(), key=lambda kv: -len(kv[1])):
        print(f'  {w}: {[p["coin"] for p in ps]}')
    # latest block + code batch
    latest = int(fast_rpc.race('eth_blockNumber', []), 16)
    now = int(time.time())
    print('latest block:', latest, 'now:', now)
    codes = {}
    if cands:
        try:
            res = fast_rpc.batch([('eth_getCode', [w, 'latest']) for w in cands])
            codes = dict(zip(cands, res))
        except Exception as e:
            print('code batch failed:', str(e)[:200])
            for w in cands:
                try:
                    codes[w] = fast_rpc.race('eth_getCode', [w, 'latest'])
                except Exception:
                    codes[w] = None
    # m1 early-buyer membership
    m1buy = {}
    for c in coins:
        for b in c.get('early_buyers', []):
            m1buy.setdefault(b['buyer'].lower(), []).append(c['name'])
    # m4 candidate set
    m4set = set()
    for r in m4.get('results', []):
        a = (r.get('address') or r.get('wallet')) if isinstance(r, dict) else None
        if a:
            m4set.add(a.lower())
    # T7 set
    t7 = set()
    for fn in ('t7_exact_window.json', 't7_window_wallets.json'):
        try:
            d = json.load(open(f'{WAVE}/{fn}'))
            s = json.dumps(d)
            t7 |= set(x.lower() for x in re.findall(r'0x[0-9a-fA-F]{40}', s))
        except Exception:
            pass
    # TRIO/PAIR from rescreen file (Peringkat 1 + correction block)
    trio_pair = set()
    try:
        txt = open('/home/hatch/workspace/narrative-pulse/wallet-rescreen-2026-11-02.md').read()
        seg = txt[txt.find('### Peringkat 1'):txt.find('### Peringkat 1') + 6000]
        trio_pair |= set(x.lower() for x in re.findall(r'0x[0-9a-fA-F]{40}', seg))
    except Exception as e:
        print('trio extract failed:', e)
    trio_pair.add(PAIR1)
    m1_eoas = [a.lower() for a, v in m1code.items() if v.get('kind', '').startswith('EOA')]
    m1_contracts = [a.lower() for a, v in m1code.items() if v.get('kind') == 'CONTRACT']
    results = []
    for w, ps in sorted(cands.items(), key=lambda kv: -len(kv[1])):
        r = {'wallet': w, 'lp_pairs': ps, 'lp_pair_count': len(ps),
             'collect_only_third': len(ps) == 3 and sorted(p['coin'] for p in ps)[2] == 'COLLECT'}
        code = codes.get(w)
        r['code'] = (code or '')[:30]
        r['is_eoa'] = code in ('0x', '0X', '', None) or (isinstance(code, str) and code.startswith('0xef01'))
        r['delegated_ef01'] = isinstance(code, str) and code.startswith('0xef01')
        # (b) active 30d: max tx timestamp in window
        win_from = latest - 5760000
        txs, nxt = tx_page(w, win_from, latest, page_size=1000)
        ts_list = [int(t.get('timestamp', 0)) for t in txs if str(t.get('timestamp', '')).isdigit()]
        r['txs_30d_window'] = len(txs)
        r['tx_page_capped'] = bool(nxt)
        r['latest_tx_ts'] = max(ts_list) if ts_list else None
        r['active30d'] = bool(ts_list) and max(ts_list) >= now - 30 * 86400
        # (a) funder: first tx + early window
        ft = first_tx_block(w, latest)
        r['first_tx_block'] = ft
        if ft is not None:
            ns = native_summary(w, ft, ft + 200000)
            top = sorted(ns['funders'].items(), key=lambda kv: -kv[1])[:4]
            r['funders_top'] = top
            r['funder_capped'] = ns['capped']
            r['distinct_funders_early'] = len(ns['funders'])
        else:
            r['funders_top'] = []
        # (c) m1 buyer membership
        r['m1_buyer_coins'] = m1buy.get(w, [])
        r['early_total'] = sorted(set([p['coin'] for p in ps]) | set(r['m1_buyer_coins']))
        # (e) burn timing per pair: first Burn with tx != mint tx, within +2000 blocks
        burns = {}
        for p in ps:
            v2 = p['type'] == 'V2'
            topic = BURN_V2 if v2 else BURN_V3
            pad = '0x' + w[2:].lower().rjust(64, '0')
            topics = [topic, None, pad] if v2 else [topic, pad]
            bl = logs(p['pool'], p['first_block'], p['first_block'] + 2000, topics)
            mint_tx = p.get('sample_tx')
            real = [l for l in bl if l.get('transactionHash') != mint_tx]
            if real:
                burns[p['coin']] = {'burn_block': blk(real[0]['blockNumber']),
                                    'delta_blocks': blk(real[0]['blockNumber']) - p['first_block'],
                                    'burn_tx': real[0].get('transactionHash')}
        r['burns_15m'] = burns
        # overlaps
        ov = []
        if w in [x.lower() for x in FEED]:
            ov.append('feed')
        if w in TIERC:
            ov.append('tierC')
        if w in m1_eoas:
            ov.append('m1_eoa')
        if w in m1_contracts:
            ov.append('m1_contract')
        if w in m4set:
            ov.append('m4')
        if w == HUB:
            ov.append('m1_hub')
        if w == PROV:
            ov.append('m1_provisioner')
        if w in t7:
            ov.append('t7')
        if w in trio_pair:
            ov.append('trio_or_pair_file')
        r['overlaps'] = ov
        results.append(r)
        print(f"{w}: pairs={len(ps)} eoa={r['is_eoa']} active30d={r['active30d']} "
              f"m1buy={r['m1_buyer_coins']} burns={list(burns)} overlaps={ov}", flush=True)
    json.dump({'latest': latest, 'now': now, 'candidates': results,
               'providers_total': len(prov_pairs)},
              open(f'{WAVE}/m5_screen.json', 'w'), indent=1)
    print('SAVED m5_screen.json')

if __name__ == '__main__':
    main()
