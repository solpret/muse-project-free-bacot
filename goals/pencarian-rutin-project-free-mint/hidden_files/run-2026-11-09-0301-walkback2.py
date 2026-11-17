#!/usr/bin/env python3
"""Extension walkback: pin the TRUE first mint for ALL ACCESS + Hexrotta.
Walks back from the earliest-in-window block found by walkback1, in 1000-block
chunks, until 5 consecutive empty chunks (launch boundary) or 20 chunks."""
import sys, time
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
from ankr import ankr_post
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ZERO = '0x0000000000000000000000000000000000000000'
TARGETS = {
 'ALL ACCESS': ('0xc3ce00677dad113f5d466d46c8c7b3a227855a5b', 132443056),
 'Hexrotta': ('0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9', 132451927),
}
for name, (addr, start) in TARGETS.items():
    found = start
    empty = 0
    for i in range(20):
        to_b = start - 1 - i*1000
        from_b = to_b - 1000 + 1
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
            found = min(found, first); empty = 0
        else:
            empty += 1
            print(f"{name}: chunk {from_b}-{to_b}: 0 mints (empty {empty}/5)", flush=True)
            if empty >= 5:
                break
        time.sleep(1)
    print(f"RESULT2 {name} first_mint_block={found}", flush=True)
print("WALKBACK2 DONE", flush=True)
