#!/usr/bin/env python3
"""Tracked-wallet mint scan run17: sent pass (Ankr) + receipts (fast_rpc) + inbound leg (Ankr getLogs).
Read-only. Outputs under workspace/narrative-pulse/scan-runs/ (persistent)."""
import sys, json, time, datetime
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
from ankr import ankr_post, get_logs
from fast_rpc import race, batch

FROM = 131471151
OUT = '/home/hatch/workspace/narrative-pulse/scan-runs/'
WIB = datetime.timezone(datetime.timedelta(hours=7))
def wib(ts):
    return datetime.datetime.fromtimestamp(ts, WIB).strftime('%Y-%m-%d %H:%M:%S WIB')

tier = json.load(open('/home/hatch/workspace/narrative-pulse/tier-ab-watch-state.json'))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
wallets = sorted(set(k.lower() for k in tier['wallets']) | set(w.lower() for w in feed))
assert '0xeb237f6f9fb4e826739f0954e9768914f28b2c2e' not in wallets
assert '0xcf3c6fc1bf670a8d3f03436395286f86dbee7418' not in wallets
cur = race('eth_blockNumber', ['latest'])
TO = int(cur, 16)
print(f'WALLETS {len(wallets)} WINDOW {FROM}-{TO}', flush=True)

sent = {}
for w in wallets:
    token = None; inw = []; ok = True; err = ''
    try:
        for _ in range(25):
            params = {"blockchain": "bsc", "address": w, "pageSize": 100}
            if token: params["pageToken"] = token
            res = ankr_post('ankr_getTransactionsByAddress', params)
            txs = res['result']['transactions']
            for t in txs:
                b = int(t['blockNumber'], 16)
                if FROM <= b <= TO:
                    inw.append({'hash': t['hash'], 'block': b, 'to': (t.get('to') or '').lower(),
                                'value': t.get('value'), 'status': t.get('status'),
                                'ts': int(t['timestamp'], 16) if t.get('timestamp') else None,
                                'time_wib': wib(int(t['timestamp'], 16)) if t.get('timestamp') else None,
                                'input_prefix': (t.get('input') or '')[:10]})
            token = res['result'].get('nextPageToken')
            if not txs or not token: break
    except Exception as e:
        ok = False; err = str(e)[:200]
    sent[w] = {'ok': ok, 'err': err, 'in_window': inw}
    print(f'SENT {w[:8]} ok={ok} n={len(inw)}', flush=True)
json.dump({'from_block': FROM, 'max_block': TO, 'results': sent},
          open(OUT + 'run17-sent.json', 'w'), indent=1)
total = sum(len(v['in_window']) for v in sent.values())
failed = [w for w, v in sent.items() if not v['ok']]
print(f'SENT DONE wallets_ok={len(wallets)-len(failed)}/{len(wallets)} total={total} failed={failed}', flush=True)

APPROVE = '0x095ea7b3'
cands = []
for w, v in sent.items():
    for t in v['in_window']:
        if t['input_prefix'] != APPROVE: cands.append((w, t))
print(f'RECEIPT CANDIDATES {len(cands)}', flush=True)
tracked_padded = set('0x' + '0'*24 + w[2:] for w in wallets)
ZERO = '0x' + '0'*64
TSIG = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
TSIG_SINGLE = '0xc3d58168c5ae7397731d9e3f1f0e6f497e7b40291dcb9a5b066a02f255a6d8e8f'
detail = {}
for i in range(0, len(cands), 6):
    chunk = cands[i:i+6]
    try:
        res = batch([('eth_getTransactionReceipt', [t['hash']]) for _, t in chunk])
    except Exception:
        res = []
        for _, t in chunk:
            try: res.append(race('eth_getTransactionReceipt', [t['hash']]))
            except Exception: res.append(None)
            time.sleep(1)
    for (w, t), r in zip(chunk, res):
        if not r or r.get('status') != '0x1': continue
        events = []
        for lg in r.get('logs', []):
            topics = lg.get('topics', [])
            if len(topics) >= 3 and topics[0].lower() == TSIG and topics[1].lower() == ZERO and topics[2].lower() in tracked_padded:
                events.append({'kind': 'ERC721/20 Transfer', 'contract': lg['address'].lower(),
                               'to': '0x' + topics[2][-40:], 'token_id': int(topics[3], 16) if len(topics) > 3 else None})
            elif len(topics) >= 4 and topics[0].lower() == TSIG_SINGLE and topics[2].lower() == ZERO and topics[3].lower() in tracked_padded:
                data = lg.get('data', '0x')
                tid = int(data[2:66], 16) if len(data) >= 66 else None
                events.append({'kind': 'ERC1155 TransferSingle', 'contract': lg['address'].lower(),
                               'to': '0x' + topics[3][-40:], 'token_id': tid})
        if events:
            detail[t['hash']] = {'wallet': w, 'to': t['to'], 'selector': t['input_prefix'],
                                 'value': t['value'], 'time_wib': t['time_wib'],
                                 'receipt_status': '0x1', 'block': hex(t['block']), 'events': events}
            print(f"MINT {t['hash']} wallet={w[:8]} to={t['to'][:8]} time={t['time_wib']} events={events}", flush=True)
    time.sleep(4)
json.dump({'detail': detail}, open(OUT + 'run17-detail.json', 'w'), indent=1)
print(f'RECEIPTS DONE mint_txs={len(detail)}', flush=True)

def walk(o, addrs):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) == 42 and v.startswith('0x'): addrs.add(v.lower())
            walk(v, addrs)
    elif isinstance(o, list):
        for v in o: walk(v, addrs)
snap = json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
addrs = set(); walk(snap, addrs)
bridge = json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-bridge.json'))['contracts']
addrs |= set(bridge.keys())
st = json.load(open('/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json'))
for f in st['reported_findings']:
    for m in f.get('mints', []):
        addrs.add(m['mint_contract'].lower())
d16 = json.load(open(OUT + 'run16-detail.json'))['detail']
for v in d16.values():
    for e in v['events']: addrs.add(e['contract'].lower())
for v in detail.values():
    for e in v['events']: addrs.add(e['contract'].lower())
addrs = sorted(addrs)
print(f'INBOUND contracts={len(addrs)} window={FROM}-{TO}', flush=True)
hits = []; failed_c = []; truncated = []; total_logs = 0
for idx, c in enumerate(addrs):
    try:
        res = get_logs(c, FROM, TO)
        logs = res['result']['logs'] if isinstance(res, dict) else res.get('logs', [])
        total_logs += len(logs)
        if len(logs) >= 1000:
            truncated.append(c); continue
        for lg in logs:
            topics = lg.get('topics', [])
            if len(topics) >= 3 and topics[0].lower() == TSIG and topics[1].lower() == ZERO and topics[2].lower() in tracked_padded:
                hits.append({'contract': c, 'kind': 'ERC721/20 Transfer', 'to': '0x' + topics[2][-40:],
                             'token_id': int(topics[3], 16) if len(topics) > 3 else None,
                             'block': lg.get('blockNumber'), 'tx': lg.get('transactionHash')})
            elif len(topics) >= 4 and topics[0].lower() == TSIG_SINGLE and topics[2].lower() == ZERO and topics[3].lower() in tracked_padded:
                hits.append({'contract': c, 'kind': 'ERC1155 TransferSingle', 'to': '0x' + topics[3][-40:],
                             'token_id': None, 'block': lg.get('blockNumber'), 'tx': lg.get('transactionHash')})
    except Exception as e:
        failed_c.append((c, str(e)[:150]))
    if (idx+1) % 50 == 0:
        print(f'[{idx+1}/{len(addrs)}] logs={total_logs} hits={len(hits)} failed={len(failed_c)} truncated={len(truncated)}', flush=True)
for c in truncated[:]:
    try:
        res = get_logs(c, FROM, TO, topics=[TSIG, ZERO])
        logs = res['result']['logs'] if isinstance(res, dict) else []
        n = 0
        for lg in logs:
            topics = lg.get('topics', [])
            if len(topics) >= 3 and topics[2].lower() in tracked_padded:
                hits.append({'contract': c, 'kind': 'ERC721/20 Transfer(topic-filtered)', 'to': '0x' + topics[2][-40:],
                             'token_id': int(topics[3], 16) if len(topics) > 3 else None,
                             'block': lg.get('blockNumber'), 'tx': lg.get('transactionHash')}); n += 1
        print(f'truncated topic-filtered {c}: logs={len(logs)} tracked_hits={n}', flush=True)
    except Exception as e:
        print(f'truncated topic-filtered {c} FAILED: {str(e)[:200]}', flush=True)
json.dump({'from': FROM, 'to': TO, 'contracts_checked': len(addrs), 'total_logs': total_logs,
           'hits': hits, 'failed': failed_c, 'truncated': truncated},
          open(OUT + 'run17-inbound.json', 'w'), indent=1)
print(f"INBOUND DONE contracts={len(addrs)} logs={total_logs} hits={len(hits)} failed={len(failed_c)} truncated={truncated}", flush=True)
