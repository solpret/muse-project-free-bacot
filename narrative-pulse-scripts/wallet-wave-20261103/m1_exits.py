#!/usr/bin/env python3
"""Wallet wave 2026-11-03 — bounded real-exit check (v2 of sell check).

Lesson from 9999: the first Transfer-out is often the SAME tx as the buy
(atomic routed swap leg) — not a sell. So for each survivor x coin:
  query Transfer(from=survivor) in [buy_block, buy_block+2000] (~15 min)
  first_real_out  = earliest log with tx != buy_tx (any destination)
  first_real_pool = earliest log with tx != buy_tx AND to == pool
If none in window -> held >=15 min (no exit observed in window).
One Ankr call per (survivor, coin): fast and bounded.
Output: m1_exits.json + printed summary.
"""
import json, sys, importlib.util
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

spec = importlib.util.spec_from_file_location('m1', f'{WAVE}/m1_pull.py')
m1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m1)
POOLS = {c[0]: c[2].lower() for c in m1.COINS}
TOKENS = {c[0]: c[1].lower() for c in m1.COINS}

def main():
    coins = json.load(open(f'{WAVE}/m1_coins.json'))
    inter = json.load(open(f'{WAVE}/m1_intersection.json'))
    code = json.load(open(f'{WAVE}/m1_code_class.json'))
    survivors = [w for w in inter if code[w]['kind'] in ('EOA', 'EOA-DELEGATED')]
    buy_map = {}
    for r in coins:
        for b in r.get('early_buyers', []):
            buy_map[(r['name'], b['buyer'].lower())] = b
    out = {}
    for w in survivors:
        out[w] = {}
        for coin in inter[w]['coins']:
            token, pool = TOKENS[coin], POOLS[coin]
            buy = buy_map.get((coin, w.lower()))
            if not buy:
                out[w][coin] = {'error': 'buy row not found'}
                continue
            pad = '0x' + '0' * 24 + w[2:].lower()
            try:
                res = ankr.get_logs(token, buy['block'], buy['block'] + 2000,
                                    topics=[[TRANSFER], [pad]])
                logs = res.get('result', {}).get('logs', [])
            except Exception as e:
                out[w][coin] = {'error': f'query_fail:{e}'[:120]}
                continue
            logs.sort(key=lambda l: (int(l['blockNumber'], 16), int(l.get('logIndex', '0x0'), 16)))
            real = [l for l in logs if l.get('transactionHash', '') != buy['tx']]
            row = {'buy_block': buy['block'], 'buy_tx': buy['tx'],
                   'n_outs_15min': len(logs), 'n_real_outs_15min': len(real)}
            if real:
                f = real[0]
                to0 = '0x' + f['topics'][2][-40:]
                row['first_real_out'] = {'block': int(f['blockNumber'], 16),
                                         'tx': f.get('transactionHash', ''),
                                         'to': to0,
                                         'value_raw': f.get('data', '0x0'),
                                         'hold_min': round((int(f['blockNumber'], 16) - buy['block']) * 0.45 / 60, 1),
                                         'to_pool': to0 == pool}
                rp = [l for l in real if '0x' + l['topics'][2][-40:] == pool]
                if rp:
                    p = rp[0]
                    row['first_real_pool'] = {'block': int(p['blockNumber'], 16),
                                              'tx': p.get('transactionHash', ''),
                                              'value_raw': p.get('data', '0x0'),
                                              'hold_min': round((int(p['blockNumber'], 16) - buy['block']) * 0.45 / 60, 1)}
            out[w][coin] = row
            fr = row.get('first_real_out')
            fp = row.get('first_real_pool')
            print(f"{w[:10]} {coin}: buy@{buy['block']} "
                  f"real_out={fr['block'] if fr else None}({fr['hold_min'] if fr else '-'}m to_pool={fr['to_pool'] if fr else '-'}) "
                  f"real_pool={fp['block'] if fp else None}({fp['hold_min'] if fp else '-'}m) "
                  f"n15={len(logs)}/{len(real)}", flush=True)
    json.dump(out, open(f'{WAVE}/m1_exits.json', 'w'), indent=1)
    print('DONE', flush=True)

if __name__ == '__main__':
    main()
