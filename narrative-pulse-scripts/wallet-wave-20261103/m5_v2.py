#!/usr/bin/env python3
"""Method 5 step 1b: V2 pairs (JAGENT, SAFU-B13B) via LP-token Transfer mints.
V2 Pair Mint event has NO `to` field (Mint(address,uint256,uint256)), so the
provider is read from the LP-token Transfer(from=0x0, to=provider) on the pair
contract itself. First provider per pair = presumed creator, excluded.
READ-ONLY. Topics via keccak. Saves m5_v2.json."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
import ankr
import fast_rpc
from Crypto.Hash import keccak

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'

def k(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()

TRANSFER = k('Transfer(address,address,uint256)')
ZERO_PAD = '0x' + '0' * 64

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
    coins = json.load(open(f'{WAVE}/m1_coins.json'))
    out = {'pairs': []}
    for c in coins:
        if c['name'] not in ('JAGENT', 'SAFU-B13B'):
            continue
        pool, fb = c['pool'], c['verify']['first_buy_block']
        rec = {'coin': c['name'], 'pool': pool, 'first_buy_block': fb, 'type': 'V2'}
        lo = max(0, fb - 2000000)
        ls = logs(pool, lo, fb, [TRANSFER, ZERO_PAD])
        # earliest LP mint to a non-zero recipient
        cand = [l for l in ls if len(l.get('topics', [])) > 2 and l['topics'][2][-40:] != '0' * 40]
        if not cand:
            rec['note'] = f'no LP mint found in [{lo},{fb}] ({len(ls)} from-zero logs)'
            out['pairs'].append(rec)
            print(f"{c['name']}: {rec['note']}", flush=True)
            continue
        f = min(blk(l['blockNumber']) for l in cand)
        first_to = None
        for l in cand:
            if blk(l['blockNumber']) == f:
                first_to = '0x' + l['topics'][2][-40:].lower()
                break
        rec['first_lp_block'] = f
        rec['first_provider'] = first_to
        rec['pre_window_lp_logs'] = len(ls)
        # 4h window by timestamp sampling
        samples = [f + i * 2000 for i in range(21)]
        try:
            blks = fast_rpc.batch([('eth_getBlockByNumber', [hex(b), False]) for b in samples])
            ts = [int(b['timestamp'], 16) for b in blks]
        except Exception as e:
            ts = [None] * 21
            rec['timestamp_error'] = str(e)[:200]
        if ts[0] is None:
            end = f + 20000
            rec['window'] = [f, end]
            rec['window_hours'] = None
        else:
            target = ts[0] + 4 * 3600
            end, end_ts = samples[-1], ts[-1]
            for b, t in zip(samples, ts):
                if t >= target:
                    end, end_ts = b, t
                    break
            rec['window'] = [f, end]
            rec['window_hours'] = round((end_ts - ts[0]) / 3600, 2)
        wlogs = logs(pool, f, end, [TRANSFER, ZERO_PAD])
        prov = {}
        for l in wlogs:
            t = l.get('topics', [])
            if len(t) <= 2:
                continue
            to = '0x' + t[2][-40:].lower()
            if to == '0x' + '0' * 40:
                continue
            b = blk(l['blockNumber'])
            e = prov.setdefault(to, {'first_block': b, 'mint_logs': 0, 'sample_tx': None})
            e['first_block'] = min(e['first_block'], b)
            e['mint_logs'] += 1
            if not e['sample_tx']:
                e['sample_tx'] = l.get('transactionHash')
        rec['window_lp_logs'] = len(wlogs)
        rec['window_capped'] = len(wlogs) >= 1000
        rec['providers'] = {p: v for p, v in sorted(prov.items(), key=lambda kv: kv[1]['first_block'])}
        rec['provider_count'] = len(prov)
        out['pairs'].append(rec)
        print(f"{c['name']}: V2 first_lp={f} window={rec['window']} hours={rec.get('window_hours')} "
              f"providers={len(prov)} first_provider={first_to}", flush=True)
        for p, v in rec['providers'].items():
            print(f"   {p} first_block={v['first_block']} mints={v['mint_logs']}", flush=True)
    json.dump(out, open(f'{WAVE}/m5_v2.json', 'w'), indent=1)
    print('SAVED m5_v2.json')

if __name__ == '__main__':
    main()
