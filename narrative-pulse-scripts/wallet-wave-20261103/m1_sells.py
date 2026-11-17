#!/usr/bin/env python3
"""Wallet wave 2026-11-03 — sell-timing check for method-1 EOA survivors.

For each survivor x each of its early coins:
  buy  = m1 early_buyers row (block/tx) + early_values value_raw
  outs = earliest Transfer(from=survivor) on the token (Ankr, bisection
         because getLogs is newest-first capped at 1000)
  first_out      = earliest transfer-out (any destination)
  first_to_pool  = earliest transfer-out whose destination == pool
Hold duration in minutes = (out_block - buy_block) * 0.45 / 60.
Dumper flag: first to-pool within 10 minutes of buy.
Output: m1_sells.json + printed summary.
"""
import json, sys, time, importlib.util
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

spec = importlib.util.spec_from_file_location('m1', f'{WAVE}/m1_pull.py')
m1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m1)
POOLS = {c[0]: c[2].lower() for c in m1.COINS}
TOKENS = {c[0]: c[1].lower() for c in m1.COINS}

def q(token, frm, to, topics):
    res = ankr.get_logs(token, frm, to, topics=topics)
    return res.get('result', {}).get('logs', [])

def first_outs(token, wallet, buy_block, latest):
    """Earliest Transfer(from=wallet) logs on token, via bisection."""
    pad = '0x' + '0' * 24 + wallet[2:].lower()
    topics = [[TRANSFER], [pad]]
    fails = 0
    start, end = buy_block, latest
    # phase 1: if [buy_block, latest] uncapped -> done; if capped -> bisect
    try:
        logs = q(token, start, end, topics)
    except Exception as e:
        return [], f'query_fail:{e}'[:120]
    if len(logs) < 1000:
        logs.sort(key=lambda l: (int(l['blockNumber'], 16), int(l.get('logIndex', '0x0'), 16)))
        return logs, None
    lo, hi = start, end
    for _ in range(30):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        try:
            logs = q(token, start, mid, topics)
        except Exception:
            fails += 1
            if fails >= 5:
                return [], 'ankr_fail'
            time.sleep(3)
            continue
        if not logs:
            lo = mid
        elif len(logs) >= 1000:
            hi = mid
        else:
            logs.sort(key=lambda l: (int(l['blockNumber'], 16), int(l.get('logIndex', '0x0'), 16)))
            return logs, None
    try:
        logs = q(token, start, hi, topics)
    except Exception as e:
        return [], f'query_fail:{e}'[:120]
    logs.sort(key=lambda l: (int(l['blockNumber'], 16), int(l.get('logIndex', '0x0'), 16)))
    return logs, 'capped_window'

def main():
    coins = json.load(open(f'{WAVE}/m1_coins.json'))
    inter = json.load(open(f'{WAVE}/m1_intersection.json'))
    code = json.load(open(f'{WAVE}/m1_code_class.json'))
    survivors = [w for w in inter if code[w]['kind'] in ('EOA', 'EOA-DELEGATED')]
    latest = int(m1.rpc_retry('eth_blockNumber', []), 16)
    print(f'latest block: {latest}, survivors: {len(survivors)}', flush=True)
    buy_map = {}
    for r in coins:
        for b, v in zip(r.get('early_buyers', []), r.get('early_values', [])):
            buy_map[(r['name'], b['buyer'].lower())] = {
                'block': b['block'], 'tx': b['tx'], 'value_raw': v['value_raw']}
    out = {}
    for w in survivors:
        out[w] = {}
        for coin in inter[w]['coins']:
            token = TOKENS[coin]
            pool = POOLS[coin]
            buy = buy_map.get((coin, w.lower()))
            if not buy:
                out[w][coin] = {'error': 'buy row not found'}
                continue
            logs, flag = first_outs(token, w, buy['block'], latest)
            row = {'buy_block': buy['block'], 'buy_tx': buy['tx'],
                   'buy_value_raw': buy['value_raw'], 'n_outs_window': len(logs),
                   'flag': flag}
            if logs:
                f = logs[0]
                to0 = '0x' + f['topics'][2][-40:]
                row['first_out'] = {'block': int(f['blockNumber'], 16),
                                    'tx': f.get('transactionHash', ''),
                                    'to': to0,
                                    'value_raw': f.get('data', '0x0'),
                                    'hold_min': round((int(f['blockNumber'], 16) - buy['block']) * 0.45 / 60, 1)}
                to_pool = [l for l in logs if '0x' + l['topics'][2][-40:] == pool]
                if to_pool:
                    p = to_pool[0]
                    row['first_to_pool'] = {'block': int(p['blockNumber'], 16),
                                            'tx': p.get('transactionHash', ''),
                                            'value_raw': p.get('data', '0x0'),
                                            'hold_min': round((int(p['blockNumber'], 16) - buy['block']) * 0.45 / 60, 1)}
                    row['dumper_10min'] = row['first_to_pool']['hold_min'] <= 10
                else:
                    row['first_to_pool'] = None
            out[w][coin] = row
            fo = row.get('first_out')
            fp = row.get('first_to_pool')
            print(f"{w[:10]} {coin}: buy@{buy['block']} "
                  f"first_out={fo['block'] if fo else None}({fo['hold_min'] if fo else '-'}m to {fo['to'][:10] if fo else '-'}) "
                  f"to_pool={fp['block'] if fp else None}({fp['hold_min'] if fp else '-'}m) "
                  f"flag={flag}", flush=True)
    json.dump(out, open(f'{WAVE}/m1_sells.json', 'w'), indent=1)
    print('DONE', flush=True)

if __name__ == '__main__':
    main()
