#!/usr/bin/env python3
"""Standalone first-mint walkback for ALL ACCESS / Hexrotta / APASS / AgentX.
Uses Ankr getLogs only (no OnFinality) so it does not compete with leads2 views.
Finds the earliest Transfer-from-zero (mint) per contract, walking back in
1000-block chunks from head. Prints first mint block + timestamp via Ankr's
block data is not available -> timestamp fetched separately if needed."""
import sys, time, json
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
from ankr import ankr_post
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ZERO = '0x0000000000000000000000000000000000000000'
HEAD = 132456769
TARGETS = {
 'ALL ACCESS': '0xc3ce00677dad113f5d466d46c8c7b3a227855a5b',
 'Hexrotta': '0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9',
 'APASS': '0x01c106835091c09d5c69737631af133530093c89',
 'AgentX': '0x59d96d8b4b82abb350868e897f25f8e021360823',
}
CHUNK = 1000
for name, addr in TARGETS.items():
    found = None
    # walk back: newest chunk first, keep going until a chunk has no mint; the
    # earliest mint is in the oldest chunk that still has one. We walk the full
    # 14 chunks (14000 blocks ~ 105 min) or until 3 consecutive empty chunks.
    empty = 0
    for i in range(14):
        to_b = HEAD - i*CHUNK
        from_b = to_b - CHUNK + 1
        try:
            body = ankr_post('ankr_getLogs', {'blockchain':'bsc',
                'fromBlock': hex(from_b), 'toBlock': hex(to_b),
                'address': addr, 'pageSize': 1000, 'decodeLogs': False,
                'topics': [TRANSFER, '0x'+'0'*24+ZERO[2:].lower()]}, timeout=30)
            logs = body.get('result', {}).get('logs', [])
        except Exception as e:
            print(f"{name}: chunk {from_b}-{to_b} ERROR {e}", flush=True)
            logs = []
        if logs:
            first = min(int(l['blockNumber'], 16) for l in logs)
            print(f"{name}: chunk {from_b}-{to_b}: {len(logs)} mints, earliest {first}", flush=True)
            if found is None or first < found:
                found = first
            empty = 0
        else:
            empty += 1
            print(f"{name}: chunk {from_b}-{to_b}: 0 mints", flush=True)
            if empty >= 3 and found is not None:
                break
        time.sleep(1)
    print(f"RESULT {name} first_mint_block={found}", flush=True)
print("WALKBACK DONE", flush=True)
