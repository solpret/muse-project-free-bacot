#!/usr/bin/env python3
"""Wallet wave 2026-11-03 — Method 2: funding graph (read-only).

For each target wallet (AFeng + method-1 strong candidates):
  1. first-tx binary search via Ankr tx-by-address block filter (pageSize=1)
  2. early window [first_tx, first_tx+200000] native BNB in/out (funders/funded)
     (~25 h at measured 0.45 s/block — the true earliest funders)
  3. recent 7d window [latest-1344000, latest] native in/out (capped note if 1000)
  4. 30d activity probe [latest-5760000, latest] + eth_getCode (EOA vs contract)
Native = input == '0x'. Timestamps from tx objects (unix seconds).
Output JSON to the wave folder.
"""
import json, sys, time, urllib.request
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr

WAVE = '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103'
DATASEEDS = ['https://bsc-dataseed.binance.org/',
             'https://bsc-dataseed1.binance.org/',
             'https://bsc-dataseed2.binance.org/']

def rpc(method, params, tries=4):
    """Via fast_rpc.race (proven path). Direct urllib to
    bsc-dataseed.binance.org currently dies RemoteDisconnected."""
    import os as _os
    sys.path.insert(0, _os.path.expanduser('~/workspace/fast_exec'))
    import fast_rpc
    last = None
    for i in range(tries):
        try:
            res = fast_rpc.race(method, params)
            if res is not None:
                return res
            last = 'None result'
        except Exception as e:
            last = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f'RPC {method} failed: {last!r}')

def tx_page(wallet, frm, to, page_size=1000, token=None):
    params = {'blockchain': 'bsc', 'address': [wallet], 'pageSize': page_size,
              'fromBlock': hex(frm), 'toBlock': hex(to)}
    if token:
        params['pageToken'] = token
    r = ankr.ankr_post('ankr_getTransactionsByAddress', params)
    res = r.get('result', {})
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
    """Collect native in/out in window. Returns dict + capped flag."""
    funders, funded = {}, {}
    pages, capped, total = 0, False, 0
    token = None
    while pages < cap_pages:
        txs, token = tx_page(wallet, frm, to, token=token)
        total += len(txs)
        for t in txs:
            if t.get('input', '') not in ('0x', ''):
                continue
            try:
                val = int(t.get('value', '0x0'), 16) / 1e18
            except Exception:
                continue
            if val <= 0:
                continue
            blk = int(t.get('blockNumber', '0x0'), 16)
            ts = t.get('timestamp')
            if t.get('to', '').lower() == wallet.lower():
                f = t.get('from', '').lower()
                e = funders.setdefault(f, {'total_bnb': 0.0, 'count': 0, 'first_block': blk, 'first_ts': ts})
                e['total_bnb'] += val
                e['count'] += 1
                e['first_block'] = min(e['first_block'], blk)
            elif t.get('from', '').lower() == wallet.lower():
                d = t.get('to', '').lower()
                e = funded.setdefault(d, {'total_bnb': 0.0, 'count': 0, 'first_block': blk, 'first_ts': ts})
                e['total_bnb'] += val
                e['count'] += 1
                e['first_block'] = min(e['first_block'], blk)
        pages += 1
        if not token:
            break
    else:
        capped = True
    return {'funders': funders, 'funded': funded, 'txs_scanned': total,
            'pages': pages, 'capped': capped}

def profile(wallet, latest):
    print(f'== {wallet} ==', flush=True)
    out = {'wallet': wallet}
    try:
        ft = first_tx_block(wallet, latest)
    except Exception as e:
        out['error'] = f'first-tx search fail: {e}'
        print(f'  first-tx FAIL: {e}', flush=True)
        return out
    out['first_tx_block'] = ft
    print(f'  first_tx_block: {ft}', flush=True)
    if ft is None:
        return out
    try:
        out['early_window'] = native_summary(wallet, ft, min(ft + 200000, latest))
        print(f'  early funders: {len(out["early_window"]["funders"])}, funded: {len(out["early_window"]["funded"])}', flush=True)
    except Exception as e:
        out['early_window_error'] = str(e)
        print(f'  early window FAIL: {e}', flush=True)
    try:
        out['recent_7d'] = native_summary(wallet, max(0, latest - 1344000), latest)
        print(f'  recent funders: {len(out["recent_7d"]["funders"])}, funded: {len(out["recent_7d"]["funded"])}', flush=True)
    except Exception as e:
        out['recent_7d_error'] = str(e)
        print(f'  recent window FAIL: {e}', flush=True)
    try:
        out['active_30d'] = has_tx(wallet, max(0, latest - 5760000), latest)
    except Exception as e:
        out['active_30d'] = None
        out['active_30d_error'] = str(e)
    try:
        code = rpc('eth_getCode', [wallet, 'latest'])
        if code in ('0x', '0x0', None):
            out['account_kind'] = 'EOA'
        elif isinstance(code, str) and code.startswith('0xef01'):
            # EIP-7702 delegation: an EOA with a delegation designation,
            # NOT a deployed contract (cf. AFeng main). Record delegate.
            out['account_kind'] = 'EOA-DELEGATED'
            out['delegate'] = '0x' + code[6:46]
        else:
            out['account_kind'] = 'CONTRACT'
        out['is_contract'] = out['account_kind'] == 'CONTRACT'
    except Exception as e:
        out['account_kind'] = None
        out['is_contract'] = None
        out['code_error'] = str(e)
    print(f'  active30d={out.get("active_30d")} is_contract={out.get("is_contract")}', flush=True)
    return out

def main():
    import os
    cands = []
    if os.path.exists(f'{WAVE}/m2_targets.json'):
        cands = json.load(open(f'{WAVE}/m2_targets.json'))
    else:
        cands = ['0xbf004bff64725914ee36d03b87d6965b0ced4903']
    latest = int(rpc('eth_blockNumber', []), 16)
    print(f'latest block: {latest}', flush=True)
    results = [profile(w, latest) for w in cands]
    json.dump(results, open(f'{WAVE}/m2_funding.json', 'w'), indent=1)
    print('DONE', len(results), flush=True)

if __name__ == '__main__':
    main()
