#!/usr/bin/env python3
"""Method 5 step 1: earliest LP providers per m1 pair (first 4h after first Mint).
READ-ONLY. Topics computed via keccak, never hand-typed. Providers = Mint `to`
(V2) / `owner` (V3 topics[1]). First minter per pair excluded as presumed
creator/initial LP. Window = 4h by block timestamp (batched eth_getBlockByNumber).
Saves m5_mints.json. Run in background; Ankr calls are the slow part."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
import ankr
import fast_rpc
from Crypto.Hash import keccak

def k(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()

MINT_V2 = k('Mint(address,address,uint256,uint256)')
MINT_V3 = k('Mint(address,address,int24,int24,uint128,uint256,uint256)')

def blk(x):
    return int(x, 16) if isinstance(x, str) else int(x)

def logs(pool, frm, to, topic):
    r = ankr.get_logs(pool, frm, to, topics=[topic])
    if not isinstance(r, dict):
        return [], f'non-dict response: {str(r)[:200]}'
    res = r.get('result', {})
    if isinstance(res, dict) and 'logs' in res:
        return res['logs'], None
    return [], f'no logs key: {str(r)[:200]}'

def provider_of(lg, v2):
    t = lg.get('topics', [])
    idx = 2 if v2 else 1
    if len(t) <= idx:
        return None
    return '0x' + t[idx][-40:].lower()

def first_mint_bisect(pool, lo, hi, topic):
    """Find earliest Mint block in [lo,hi] by existence bisection. ~21 calls."""
    if lo >= hi:
        return lo
    while hi - lo > 1:
        mid = (lo + hi) // 2
        ls, _ = logs(pool, lo, mid, topic)
        if ls:
            hi = mid
        else:
            lo = mid
    return hi

def main():
    coins = json.load(open('/home/hatch/workspace/narrative-pulse/wallet-wave-20261103/m1_coins.json'))
    out = {'pairs': [], 'notes': []}
    for c in coins:
        name, pool, fb = c['name'], c['pool'], c['verify']['first_buy_block']
        rec = {'coin': name, 'pool': pool, 'first_buy_block': fb}
        lo = max(0, fb - 2000000)
        lv2, e2 = logs(pool, lo, fb, MINT_V2)
        lv3, e3 = logs(pool, lo, fb, MINT_V3)
        rec['v2_window_logs'] = len(lv2)
        rec['v3_window_logs'] = len(lv3)
        if e2: rec['v2_error'] = e2
        if e3: rec['v3_error'] = e3
        v2 = len(lv2) > 0 and len(lv3) == 0
        v3 = len(lv3) > 0 and len(lv2) == 0
        if len(lv2) > 0 and len(lv3) > 0:
            # both topics hit: earliest overall decides; keep both, flag it
            rec['both_topics_hit'] = True
            e2b = min(blk(l['blockNumber']) for l in lv2)
            e3b = min(blk(l['blockNumber']) for l in lv3)
            v2, v3 = e2b <= e3b, e3b < e2b
        if not v2 and not v3:
            rec['type'] = 'UNKNOWN'
            rec['note'] = 'no Mint logs of either type in window'
            out['pairs'].append(rec)
            print(f"{name}: UNKNOWN (v2={len(lv2)} v3={len(lv3)})", flush=True)
            continue
        topic = MINT_V2 if v2 else MINT_V3
        rec['type'] = 'V2' if v2 else 'V3'
        win = lv2 if v2 else lv3
        capped = len(win) >= 1000
        rec['window_capped'] = capped
        if capped:
            f = first_mint_bisect(pool, lo, fb, topic)
            rec['first_mint_block'] = f
            rec['first_mint_note'] = 'bisected (window capped)'
        else:
            f = min(blk(l['blockNumber']) for l in win)
            rec['first_mint_block'] = f
        # timestamps: sample F..F+40000 step 2000 in one batch
        samples = [f + i * 2000 for i in range(21)]
        try:
            blks = fast_rpc.batch([('eth_getBlockByNumber', [hex(b), False]) for b in samples])
            ts = [int(b['timestamp'], 16) for b in blks]
        except Exception as e:
            ts = [None] * 21
            rec['timestamp_error'] = str(e)[:200]
        rec['sample_blocks'] = samples
        rec['sample_timestamps'] = ts
        if ts[0] is None:
            end = f + 20000
            rec['window'] = [f, end]
            rec['window_hours'] = None
            rec['window_note'] = 'timestamps unavailable; 20000-block fallback'
        else:
            target = ts[0] + 4 * 3600
            end = samples[-1]
            end_ts = ts[-1]
            for b, t in zip(samples, ts):
                if t >= target:
                    end, end_ts = b, t
                    break
            rec['window'] = [f, end]
            rec['window_hours'] = round((end_ts - ts[0]) / 3600, 2)
        # Mint logs inside the window
        wlogs, werr = logs(pool, f, end, topic)
        if werr:
            rec['window_error'] = werr
            wlogs = []
        rec['window_mint_logs'] = len(wlogs)
        rec['window_capped'] = len(wlogs) >= 1000
        prov = {}
        for lg in wlogs:
            p = provider_of(lg, v2)
            if not p:
                continue
            b = blk(lg['blockNumber'])
            e = prov.setdefault(p, {'first_block': b, 'txs': 0, 'tx_set': []})
            e['first_block'] = min(e['first_block'], b)
            e['txs'] += 1
            if lg.get('transactionHash') not in e['tx_set']:
                e['tx_set'].append(lg.get('transactionHash'))
        first_provider = None
        for lg in wlogs:
            if blk(lg['blockNumber']) == f:
                first_provider = provider_of(lg, v2)
                break
        rec['first_minter'] = first_provider
        rec['providers'] = {p: {'first_block': v['first_block'], 'mint_logs': v['txs'],
                                 'sample_tx': v['tx_set'][0] if v['tx_set'] else None}
                            for p, v in sorted(prov.items(), key=lambda kv: kv[1]['first_block'])}
        rec['provider_count'] = len(prov)
        out['pairs'].append(rec)
        print(f"{name}: {rec['type']} first_mint={f} window={rec['window']} "
              f"hours={rec.get('window_hours')} providers={len(prov)} "
              f"first_minter={first_provider}", flush=True)
    json.dump(out, open('/home/hatch/workspace/narrative-pulse/wallet-wave-20261103/m5_mints.json', 'w'), indent=1)
    print('SAVED m5_mints.json')

if __name__ == '__main__':
    main()
