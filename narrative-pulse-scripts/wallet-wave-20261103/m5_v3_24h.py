#!/usr/bin/env python3
"""Method 5 sensitivity check: when does the SECOND distinct V3 LP provider
appear per pair (beyond the 4h primary window)? Window [F, F+115200] (~24h at
0.75s/block). Timestamps of F and of the second provider's first block are
read via batched eth_getBlockByNumber so hours are real, not estimated.
READ-ONLY. Saves m5_v3_24h.json."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
import ankr
import fast_rpc
from Crypto.Hash import keccak

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'

def k(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()

MINT_V3 = k('Mint(address,address,int24,int24,uint128,uint256,uint256)')

def blk(x):
    return int(x, 16) if isinstance(x, str) else int(x)

def logs(pool, frm, to, topics):
    r = ankr.get_logs(pool, frm, to, topics=topics)
    if isinstance(r, dict):
        res = r.get('result', {})
        if isinstance(res, dict) and 'logs' in res:
            return res['logs']
    return []

def main():
    mints = json.load(open(f'{WAVE}/m5_mints.json'))
    v3pairs = [p for p in mints['pairs'] if p.get('type') == 'V3']
    # batch timestamps for all F and F+115200 blocks
    queries = []
    for p in v3pairs:
        queries.append(p['first_mint_block'])
        queries.append(p['first_mint_block'] + 115200)
    try:
        blks = fast_rpc.batch([('eth_getBlockByNumber', [hex(b), False]) for b in queries])
        tsmap = {b: int(r['timestamp'], 16) for b, r in zip(queries, blks)}
    except Exception as e:
        tsmap = {}
        print('timestamp batch failed:', str(e)[:200])
    out = {'pairs': []}
    for p in v3pairs:
        f = p['first_mint_block']
        end = f + 115200
        ls = logs(p['pool'], f, end, [MINT_V3])
        prov = {}
        for l in ls:
            t = l.get('topics', [])
            if len(t) <= 1:
                continue
            o = '0x' + t[1][-40:].lower()
            b = blk(l['blockNumber'])
            e = prov.setdefault(o, {'first_block': b, 'mint_logs': 0})
            e['first_block'] = min(e['first_block'], b)
            e['mint_logs'] += 1
        ordered = sorted(prov.items(), key=lambda kv: kv[1]['first_block'])
        second = ordered[1] if len(ordered) > 1 else None
        rec = {'coin': p['coin'], 'pool': p['pool'], 'first_mint_block': f,
               'window_24h': [f, end], 'mint_logs_24h': len(ls),
               'capped_24h': len(ls) >= 1000,
               'distinct_providers_24h': len(prov),
               'first_provider': ordered[0][0] if ordered else None}
        if second and tsmap:
            b2 = second[1]['first_block']
            try:
                t2 = fast_rpc.race('eth_getBlockByNumber', [hex(b2), False])
                rec['second_provider'] = second[0]
                rec['second_provider_block'] = b2
                rec['second_provider_hours_after_first'] = round(
                    (int(t2['timestamp'], 16) - tsmap[f]) / 3600, 2)
                rec['second_provider_mints'] = second[1]['mint_logs']
            except Exception as e:
                rec['second_provider'] = second[0]
                rec['second_provider_block'] = b2
                rec['second_provider_ts_error'] = str(e)[:150]
        elif second:
            rec['second_provider'] = second[0]
            rec['second_provider_block'] = second[1]['first_block']
        rec['providers_24h'] = {o: v for o, v in ordered}
        out['pairs'].append(rec)
        print(f"{p['coin']}: 24h mints={len(ls)} distinct={len(prov)} "
              f"second={rec.get('second_provider', '-')[:12]} "
              f"at_block={rec.get('second_provider_block', '-')} "
              f"hours={rec.get('second_provider_hours_after_first', '-')}", flush=True)
    json.dump(out, open(f'{WAVE}/m5_v3_24h.json', 'w'), indent=1)
    print('SAVED m5_v3_24h.json')

if __name__ == '__main__':
    main()
