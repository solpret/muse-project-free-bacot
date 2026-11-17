#!/usr/bin/env python3
"""Follow-up for the 11 contracts truncated at Ankr pageSize 1000 in the
inbound-gap sweep (blocks 131352466-131366223). Re-queries each truncated
contract in recursively split sub-ranges until every chunk returns <1000
logs, then filters for Transfer/TransferSingle FROM zero TO a tracked
wallet. Read-only."""
import json, sys, time
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr as ankr_mod
from Crypto.Hash import keccak

FROM, TO = 131352466, 131366223
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
_k = keccak.new(digest_bits=256)
_k.update(b'TransferSingle(address,address,address,uint256,uint256)')
SINGLE = '0x' + _k.hexdigest()
ZERO = '0x' + '0' * 64

tier = json.load(open('/home/hatch/workspace/narrative-pulse/tier-ab-watch-state.json'))
wallets = list(tier['wallets'].keys())
feed = ['0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6',
        '0x2325f175975abdbcde555c79cc8e63381d28551b',
        '0xbf004bff64725914ee36d03b87d6965b0ced4903']
uniq = []
for w in wallets + feed:
    if w.lower() not in uniq:
        uniq.append(w.lower())
user = {'0xeb237f6f9fb4e826739f0954e9768914f28b2c2e',
        '0xcf3c6fc1bf670a8d3f03436395286f86dbee7418'}
uniq = [w for w in uniq if w not in user]
wallet_topics = {'0x' + '0' * 24 + w[2:] for w in uniq}

prev = json.load(open('/home/hatch/workspace/narrative-pulse/inbound-gap-sweep-2026-11-03.json'))
truncated = prev['contracts_truncated_1000']
state = json.load(open('/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json'))
known_tx = set()
for f in state.get('reported_findings', []):
    for m in f.get('mints', []):
        if m.get('tx'):
            known_tx.add(m['tx'].lower())
for m in prev['mint_to_tracked']:
    known_tx.add(m['tx'].lower())
print(f'truncated contracts to re-check: {len(truncated)}', flush=True)

found, failed = [], []
calls = [0]

def fetch(ca, fb, tb, depth=0):
    calls[0] += 1
    for attempt in range(2):
        try:
            res = ankr_mod.get_logs(ca, fb, tb)
            if isinstance(res, dict) and 'error' in res:
                raise RuntimeError(str(res['error'])[:200])
            logs = (res.get('result') or {}).get('logs') or []
            break
        except Exception as e:
            if attempt == 0:
                time.sleep(10)
            else:
                failed.append({'contract': ca, 'from': fb, 'to': tb, 'error': str(e)[:200]})
                return
    if len(logs) >= 1000 and tb - fb > 50 and depth < 6:
        mid = (fb + tb) // 2
        fetch(ca, fb, mid, depth + 1)
        fetch(ca, mid + 1, tb, depth + 1)
        return
    for lg in logs:
        topics = lg.get('topics') or []
        if not topics:
            continue
        to_w = kind = token_id = None
        if topics[0].lower() == TRANSFER and len(topics) >= 3 and topics[1].lower() == ZERO and topics[2].lower() in wallet_topics:
            to_w, kind = topics[2][-40:], 'Transfer'
            token_id = int(topics[3], 16) if len(topics) >= 4 else None
        elif topics[0].lower() == SINGLE and len(topics) >= 4 and topics[2].lower() == ZERO and topics[3].lower() in wallet_topics:
            to_w, kind = topics[3][-40:], 'TransferSingle'
            token_id = int(topics[4], 16) if len(topics) >= 5 else None
        if to_w:
            tx = (lg.get('transactionHash') or '').lower()
            found.append({'contract': ca, 'kind': kind, 'to': '0x' + to_w,
                          'token_id': token_id, 'tx': tx,
                          'block': int(lg['blockNumber'], 16) if lg.get('blockNumber') else None,
                          'already_reported': tx in known_tx})
    time.sleep(0.3)

for ca in truncated:
    fetch(ca, FROM, TO)
    print(f'  {ca[:14]} done, total mint-to-tracked so far: {len(found)}', flush=True)

seen, dedup = set(), []
for f in found:
    k = (f['tx'], f['contract'], f['to'], f['token_id'])
    if k not in seen:
        seen.add(k)
        dedup.append(f)
new = [f for f in dedup if not f['already_reported']]
out = {'contracts_rechecked': truncated, 'ankr_calls': calls[0], 'failed_chunks': failed,
       'mint_to_tracked': dedup, 'new_inbound_only': new}
json.dump(out, open('/home/hatch/workspace/narrative-pulse/inbound-gap-sweep-truncated-followup.json', 'w'), indent=1)
print(f'DONE calls={calls[0]} failed_chunks={len(failed)} mint_to_tracked={len(dedup)} NEW={len(new)}')
for f in new:
    print(' NEW:', f)
