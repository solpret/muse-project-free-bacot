#!/usr/bin/env python3
"""Wallet wave 2026-11-03 — Method 1 (v2): early buyers of formed coins.

Fixes vs v1:
- v1 bug: the capped-page path (window halved below 200) broke WITHOUT
  processing the 1000 logs in hand -> 0 buyers for 3 coins. Fixed: the
  capped page is always processed; halving shrinks the window END only,
  the start stays fixed before launch, so earliest logs are preserved.
- v1 binary-search launch blocks died on sick RPC (12/15 coins failed).
  v2 estimates launch from GeckoTerminal pool_created_at + era block
  rates measured from verified anchors (no 27-call search), then
  VERIFIES with one block-timestamp read per coin.
- Block time is ~0.45 s (measured 2026-11-02/03 anchors), NOT 3 s.

Sources: GeckoTerminal trending pools BSC (2026-11-03), MC > $1M.
Early buyers = Transfer(from=pool) via Ankr getLogs address+topics.
Early set per coin = first 200 unique buyers, chronological.
READ-ONLY. Output JSON to the wave folder.
"""
import json, time, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
import ankr
import fast_rpc

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
COINS = [
    ('AKE', '0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db', '0x4d3bf29ba30f8bfe4624e7678709afa195689c5d', '2025-08-20T07:40:09Z', 107682169.75),
    ('ARIA', '0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238', '0xa5dbeaf16fc031eae92175974f8d0a439be4ad17', '2025-08-19T09:07:05Z', 20305812.88),
    ('IDOL', '0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07', '0xfff4857a955b2b460c27fd431aa5a85fabca5559', '2025-06-10T13:33:11Z', 38570671.62),
    ('Q', '0xc07e1300dc138601fa6b0b59f8d0fa477e690589', '0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f', '2025-08-31T08:07:27Z', 135019380.52),
    ('JAGENT', '0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15', '0xe6efcdef2b720d1eca2b69edb7ef357725680bea', '2026-10-28T13:16:40Z', 3283127.32),
    ('EVAA', '0xaa036928c9c0df07d525b55ea8ee690bb5a628c1', '0x26deb24a2623cf54452ab5183e2c34551831d54d', '2025-10-02T09:03:49Z', 10003154.51),
    ('ESPORTS', '0xf39e4b21c84e737df08e2c3b32541d856f508e48', '0x83738a0b95cbd7dfd6989569a99edaed3dd704d0', '2025-07-19T09:08:11Z', 2201170.61),
    ('LYN', '0x302dfaf2cdbe51a18d97186a7384e87cf599877d', '0x302642976506d247c7017b85ddc89e3956f96ba1', '2025-10-06T07:04:44Z', 4371446.74),
    ('BASED', '0x1d28d989f9e3ccb8b15d0cec601734514f958e4d', '0x07b7556Ede0f9a6a7d155A78Bc0573f531001A57', '2026-03-30T05:09:11Z', 11284340.07),
    ('JCT', '0xea37a8de1de2d9d10772eeb569e28bfa5cb17707', '0xceC354f641Fb46b977c3a1f18B5cAf3E2Ede4C2c', '2025-11-10T10:29:31Z', 56337675.20),
    ('SAFU-B13B', '0xdd806e436dda5588bf54061c11590c77ddc87777', '0x13b86fcf85c9c8f5c36593822d216b8893c25450', '2026-10-10T18:56:06Z', 1675877.99),
    ('AIN', '0x9558a9254890b2a8b057a789f413631b9084f4a3', '0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8', '2025-07-04T12:46:04Z', 46134185.90),
    ('UAI', '0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0', '0x82ED13117144344B39e5ec74d614D54465897a24', '2025-11-06T10:38:06Z', 36799987.26),
    ('COLLECT', '0x4b3d30992f003c8167699735f5ab2831b2a087d3', '0x1FFEad9A221992D16f3AA02455542D2B2DA92bcf', '2025-12-26T19:50:28Z', 12806843.21),
]
# verified anchors (ts, block) — block timestamps read via fast_rpc
ANCHORS = [
    (1751633164, 52847146),    # 2025-07-04T12:46:04Z AIN launch
    (1762235330, 66985587),    # 2025-11-04T07:08:50Z UAI launch
    (1793684911, 131208979),   # 2026-11-02T08:28:31Z T7 anchor
    (1793685800, 131384241),   # 2026-11-03T06:23:20Z latest anchor
]
RATES = [0.7516, 0.4884, 0.4501]  # s/block between consecutive anchors

def parse_ts(iso):
    return int(datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ'
                                 ).replace(tzinfo=timezone.utc).timestamp())

def est_launch(created_iso):
    t = parse_ts(created_iso)
    if t < ANCHORS[0][0]:
        return int(ANCHORS[0][1] - (ANCHORS[0][0] - t) / RATES[0])
    for i in range(len(ANCHORS) - 1):
        if ANCHORS[i][0] <= t < ANCHORS[i + 1][0]:
            return int(ANCHORS[i][1] + (t - ANCHORS[i][0]) / RATES[i])
    return int(ANCHORS[-2][1] + (t - ANCHORS[-2][0]) / RATES[-1])

def rpc_retry(method, params, tries=6):
    last = None
    for i in range(tries):
        try:
            res = fast_rpc.race(method, params)
            if res is not None:
                return res
            last = 'None'
        except Exception as e:
            last = e
        time.sleep(3 * (i + 1))
    raise RuntimeError(f'{method} failed after {tries}: {last!r}')

def _query(token, pool, start, end):
    # normalize: pool may arrive as a 64-hex V4 PoolId or a truncated
    # transcription; only the first 40 hex chars can be a pool address
    p = pool[2:].lower()[:40] if pool.startswith('0x') else pool.lower()[:40]
    pad = '0x' + '0' * 24 + p
    res = ankr.get_logs(token, start, end, topics=[[TRANSFER], [pad]])
    return res.get('result', {}).get('logs', [])

def _sorted_buyers(logs):
    logs.sort(key=lambda l: (int(l['blockNumber'], 16),
                             int(l.get('logIndex', '0x0'), 16)))
    seen, uniq = set(), []
    for l in logs:
        t = l.get('topics', [])
        if len(t) < 3:
            continue
        b = '0x' + t[2][-40:]
        if b not in seen:
            seen.add(b)
            uniq.append((int(l['blockNumber'], 16),
                         int(l.get('logIndex', '0x0'), 16), b,
                         l.get('transactionHash', ''), l.get('data', '0x0')))
    return uniq

def _window_buyers(token, pool, start, end, latest):
    """Buys in [start, end] under Ankr's NEWEST-first pagination.
    Phase 1: expand end while empty (launch later than estimated).
    Phase 2 (capped): BISECT lo/hi with invariant [start, lo] empty,
    [start, hi] capped. An uncapped non-empty [start, mid] then holds
    the earliest buys (nothing before lo). Converges in <=30 calls,
    unlike page-by-page walk-back (50+ calls on dense tokens, which
    hit the old iteration cap)."""
    span = end - start
    fails = 0
    expansions = 0
    while True:
        try:
            logs = _query(token, pool, start, end)
            fails = 0
        except Exception as e:
            fails += 1
            print(f'  ankr fail [{start},{end}] x{fails}: {e}', flush=True)
            if fails >= 5:
                return [], 'ankr_fail'
            time.sleep(3)
            continue
        if not logs:
            if end >= latest:
                return [], 'no_buys_found'
            expansions += 1
            if expansions > 40:
                return [], 'expansion_cap'
            span = max(span * 2, 100000)
            new_end = min(start + span, latest)
            if new_end <= end:
                # never loop forever on a non-advancing window
                return [], 'no_buys_in_range'
            end = new_end
            continue
        break
    if len(logs) < 1000:
        return _sorted_buyers(logs), None
    lo, hi = start, end
    for _ in range(30):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        try:
            logs = _query(token, pool, start, mid)
        except Exception as e:
            fails += 1
            print(f'  ankr fail [{start},{mid}] x{fails}: {e}', flush=True)
            if fails >= 5:
                return [], 'ankr_fail'
            time.sleep(3)
            continue
        if not logs:
            lo = mid
        elif len(logs) >= 1000:
            hi = mid
        else:
            return _sorted_buyers(logs), None
    try:
        logs = _query(token, pool, start, hi)
    except Exception as e:
        return [], 'ankr_fail'
    return _sorted_buyers(logs), 'hot_launch_capped'

def early_buyers(token, pool, est, latest):
    """Margin escalation + pre-window check (Ankr-only, no RPC):
    try start = est - margin for margin in 50k/500k/2M blocks. After a
    window yields buyers, probe the 200k blocks BEFORE start: if any
    buy exists there, this window started after launch -> escalate.
    Returns (buyers, flag, margin_used)."""
    last = ([], 'no_buys_found', None)
    for margin in (50000, 500000, 2000000, 10000000):
        start = max(0, est - margin)
        end = min(est + margin, latest)
        buyers, flag = _window_buyers(token, pool, start, end, latest)
        if not buyers:
            last = ([], flag, margin)
            continue
        last = (buyers, flag, margin)
        # pre-check: any buy in the 200k blocks before start?
        try:
            pre = _query(token, pool, max(0, start - 200000), start - 1) \
                if start > 0 else []
        except Exception as e:
            print(f'  pre-check fail: {e}', flush=True)
            pre = []
        if pre:
            print(f'  pre-check: earlier buys exist before start {start} '
                  f'-> escalate margin', flush=True)
            continue
        return buyers, flag, margin
    return last

def process(coin, latest):
    name, token, pool, created, mc = coin
    print(f'== {name} ==', flush=True)
    est = est_launch(created)
    print(f'  est launch ~{est}', flush=True)
    buyers, flag, margin = early_buyers(token, pool, est, latest)
    if not buyers:
        return {'name': name, 'token': token, 'pool': pool, 'mc_usd': mc,
                'created_at': created, 'est_launch': est,
                'error': f'early-buyers empty (flag={flag})'}
    # verify only (supply/decimals deferred to candidate evaluation):
    # one RPC call, bounded retries — the v2 run died mid-flight, so
    # per-coin cost must stay low and results must be saved incrementally.
    verify = None
    try:
        blk = rpc_retry('eth_getBlockByNumber', [hex(buyers[0][0]), False], tries=4)
        ts = int(blk['timestamp'], 16)
        ct = parse_ts(created)
        verify = {'first_buy_block': buyers[0][0],
                  'first_buy_ts_utc': datetime.fromtimestamp(ts, timezone.utc).isoformat(),
                  'created_at': created,
                  'delta_sec': ts - ct,
                  'ok': -3600 <= ts - ct <= 7 * 86400}
    except Exception as e:
        verify = {'error': str(e)[:150]}
    early = buyers[:200]
    rows = [{'buyer': b, 'block': blk, 'tx': tx, 'pct_supply': None}
            for blk, li, b, tx, val in early]
    # keep raw values for later pct computation (candidates only)
    raw = [{'buyer': b, 'block': blk, 'value_raw': val}
           for blk, li, b, tx, val in early]
    print(f'  buyers: {len(buyers)} total, early set {len(early)}, flag={flag}, verify={verify}', flush=True)
    return {'name': name, 'token': token, 'pool': pool, 'mc_usd': mc,
            'created_at': created, 'est_launch': est, 'margin_used': margin,
            'flag': flag, 'verify': verify,
            'total_supply_raw': None, 'decimals': None,
            'early_buyers': rows, 'early_values': raw}

def main():
    latest = int(rpc_retry('eth_blockNumber', []), 16)
    print(f'latest block: {latest}', flush=True)
    # resume support: per-coin results are saved incrementally, so a
    # killed run loses at most the in-flight coins.
    partial_path = f'{WAVE}/m1_v2_partial.jsonl'
    done = {}
    try:
        with open(partial_path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    # last occurrence wins; only successes count as done
                    # (failures stay in the file but are redone)
                    if 'error' not in r:
                        done[r['name']] = r
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    if done:
        print(f'resuming: {len(done)} coins already done, skipping', flush=True)
        # rewrite partial clean (drop stale failures) so future resumes
        # never resurrect them
        with open(partial_path, 'w') as pf:
            for c in COINS:
                if c[0] in done:
                    pf.write(json.dumps(done[c[0]]) + '\n')
    todo = [c for c in COINS if c[0] not in done]
    results = [done[c[0]] for c in COINS if c[0] in done]
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(process, c, latest): c[0] for c in todo}
        for f in futs:
            try:
                r = f.result()
            except Exception as e:
                r = {'name': futs[f], 'error': f'process fail: {e}'}
            results.append(r)
            with open(partial_path, 'a') as pf:
                pf.write(json.dumps(r) + '\n')
            print(f'  saved {r["name"]} ({len(results)}/{len(COINS)})', flush=True)
    # keep COINS order
    order = {c[0]: i for i, c in enumerate(COINS)}
    results.sort(key=lambda r: order.get(r['name'], 99))
    json.dump(results, open(f'{WAVE}/m1_coins.json', 'w'), indent=1)
    from collections import Counter, defaultdict
    cnt, where = Counter(), defaultdict(list)
    for r in results:
        for b in r.get('early_buyers', []):
            cnt[b['buyer']] += 1
            where[b['buyer']].append(r['name'])
    inter = {w: c for w, c in cnt.items() if c >= 3}
    print(f'COINS OK: {sum(1 for r in results if "error" not in r)}/{len(results)}')
    print(f'INTERSECTION >=3: {len(inter)}')
    for w, c in sorted(inter.items(), key=lambda kv: -kv[1]):
        print(f'  {w} x{c}: {where[w]}')
    json.dump({w: {'count': c, 'coins': where[w]} for w, c in inter.items()},
              open(f'{WAVE}/m1_intersection.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
