#!/usr/bin/env python3
"""One-off read-only sweep to close the tracked-wallet inbound-log gap
blocks 131352466-131366223 (runs 2-3 of tracked-wallet-mint-scan-hourly).

Why: public BSC dataseed eth_getLogs rejects topic-filtered queries here
(-32005 even at 10 blocks), and the fast_rpc pool 429'd the broad query.
Ankr ankr_getLogs IS address-filtered and works over the full gap, so we
query every contract the system already knows (Free Bacot snapshot 185 +
track_c sale/token + reported-finding mint contracts) and filter locally
for Transfer/TransferSingle FROM zero address TO a tracked wallet.

Read-only. No preview/mint/sign. Inbound-only mints from a contract the
system has never seen remain theoretically possible and are stated as
the residual, not hidden.
"""
import json, sys, time
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr as ankr_mod

FROM, TO = 131352466, 131366223
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
SINGLE = '0xc3d58168c5ae7397731d9e3f6c5d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3'
# NOTE: SINGLE topic below is recomputed in main from keccak to avoid a typo.
from Crypto.Hash import keccak
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

snap = json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
contracts = {}
for name, v in snap['contracts'].items():
    if isinstance(v, dict) and v.get('address'):
        contracts[v['address'].lower()] = name
for name, v in snap.get('track_c', {}).items():
    if isinstance(v, dict):
        for k in ('sale', 'token'):
            if v.get(k):
                contracts.setdefault(v[k].lower(), f'track_c:{name}:{k}')
state = json.load(open('/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json'))
known_tx = set()
for f in state.get('reported_findings', []):
    for m in f.get('mints', []):
        if m.get('tx'):
            known_tx.add(m['tx'].lower())
        if m.get('mint_contract'):
            contracts.setdefault(m['mint_contract'].lower(), 'reported-finding')
print(f'wallets={len(uniq)} contracts={len(contracts)} known_reported_tx={len(known_tx)}', flush=True)

found, failed, truncated = [], [], []
total_logs = 0
for i, (ca, label) in enumerate(sorted(contracts.items())):
    logs = None
    for attempt in range(2):
        try:
            res = ankr_mod.get_logs(ca, FROM, TO)
            if isinstance(res, dict) and 'error' in res:
                raise RuntimeError(str(res['error'])[:200])
            logs = (res.get('result') or {}).get('logs') or []
            break
        except Exception as e:
            if attempt == 0:
                time.sleep(10)
            else:
                failed.append({'contract': ca, 'label': label, 'error': str(e)[:200]})
    if logs is None:
        continue
    total_logs += len(logs)
    if len(logs) >= 1000:
        truncated.append(ca)
    for lg in logs:
        topics = lg.get('topics') or []
        if not topics:
            continue
        to_w = None
        kind = None
        token_id = None
        if topics[0].lower() == TRANSFER and len(topics) >= 3 and topics[1].lower() == ZERO and topics[2].lower() in wallet_topics:
            to_w, kind = topics[2][-40:], 'Transfer'
            token_id = int(topics[3], 16) if len(topics) >= 4 else None
        elif topics[0].lower() == SINGLE and len(topics) >= 4 and topics[2].lower() == ZERO and topics[3].lower() in wallet_topics:
            to_w, kind = topics[3][-40:], 'TransferSingle'
            token_id = int(topics[4], 16) if len(topics) >= 5 else None
        if to_w:
            tx = (lg.get('transactionHash') or '').lower()
            found.append({'contract': ca, 'label': label, 'kind': kind,
                          'to': '0x' + to_w, 'token_id': token_id,
                          'tx': tx, 'block': int(lg['blockNumber'], 16) if lg.get('blockNumber') else None,
                          'already_reported': tx in known_tx})
    if (i + 1) % 50 == 0:
        print(f'... {i+1}/{len(contracts)} contracts, {len(found)} mint-to-tracked so far, {len(failed)} failed', flush=True)
    time.sleep(0.3)

# Dedupe identical (tx, contract, to, token_id)
seen, dedup = set(), []
for f in found:
    k = (f['tx'], f['contract'], f['to'], f['token_id'])
    if k not in seen:
        seen.add(k)
        dedup.append(f)
new = [f for f in dedup if not f['already_reported']]
out = {'from_block': FROM, 'to_block': TO, 'contracts_checked': len(contracts),
       'contracts_failed': failed, 'contracts_truncated_1000': truncated,
       'total_logs_scanned': total_logs, 'mint_to_tracked': dedup,
       'new_inbound_only': new}
json.dump(out, open('/home/hatch/workspace/narrative-pulse/inbound-gap-sweep-2026-11-03.json', 'w'), indent=1)
print(f'DONE contracts={len(contracts)} failed={len(failed)} truncated={len(truncated)} logs={total_logs} mint_to_tracked={len(dedup)} NEW_inbound_only={len(new)}')
for f in new:
    print(' NEW:', f)
