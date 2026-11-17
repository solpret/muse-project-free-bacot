#!/usr/bin/env python3
"""Run 2026-11-09 04:01 WIB — AGENT DOSSIER first-mint search.
Stepped probes (20k blocks ~2.5h) back from the known mint block 132448111,
then 1k-block walkback from the last non-empty step. Bounded: max 45 probes.
Prints RESULT first_mint_block + block timestamp (via dataseed eth_getBlockByNumber).
"""
import sys, time, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000"
ADDR = "0xac3f9a33c653fb3ca49056cfa5edf19101debf97"
KNOWN = 132448111  # block of mint #343 per Boltbook post
STEP = 20000
CHUNK = 1000
MAX_PROBES = 45
probes = [0]

def has_mint(frm, to):
    probes[0] += 1
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
            "fromBlock": hex(frm), "toBlock": hex(to),
            "address": ADDR, "pageSize": 1000, "decodeLogs": False,
            "topics": [TRANSFER, "0x" + "0" * 24 + ZERO[2:].lower()]}, timeout=30)
        logs = body.get("result", {}).get("logs", [])
        return logs
    except Exception as e:
        print(f"probe {frm}-{to} ERROR {type(e).__name__}: {e}", flush=True)
        return None

# Phase 1: step back 20k at a time
last_nonempty = KNOWN
empty_at = None
b = KNOWN - STEP
while b > KNOWN - 400000 and probes[0] < MAX_PROBES:
    logs = has_mint(b, b + CHUNK - 1)
    if logs is None:
        print(f"step probe {b}: ERROR, retry once", flush=True)
        time.sleep(2)
        logs = has_mint(b, b + CHUNK - 1)
    n = len(logs) if logs is not None else -1
    print(f"step probe {b}-{b+CHUNK-1}: {n} mints", flush=True)
    if logs:
        last_nonempty = b
        b -= STEP
    else:
        empty_at = b
        break
    time.sleep(1)

print(f"PHASE1 done probes={probes[0]} last_nonempty_step={last_nonempty} empty_at={empty_at}", flush=True)

# Phase 2: fine walkback 1k chunks from last_nonempty down toward empty_at
found = None
if empty_at is not None:
    to_b = last_nonempty + CHUNK - 1
    empty_run = 0
    while to_b >= empty_at and probes[0] < MAX_PROBES:
        frm = to_b - CHUNK + 1
        logs = has_mint(frm, to_b)
        if logs is None:
            print(f"fine {frm}-{to_b}: ERROR, skip", flush=True)
            to_b -= CHUNK
            continue
        if logs:
            first = min(int(l["blockNumber"], 16) for l in logs)
            print(f"fine {frm}-{to_b}: {len(logs)} mints earliest {first}", flush=True)
            if found is None or first < found:
                found = first
            empty_run = 0
        else:
            empty_run += 1
            print(f"fine {frm}-{to_b}: 0 mints (empty {empty_run}/3)", flush=True)
            if empty_run >= 3 and found is not None:
                break
        to_b -= CHUNK
        time.sleep(1)
    print(f"RESULT AGENT DOSSIER first_mint_block={found} probes={probes[0]}", flush=True)
else:
    print("RESULT AGENT DOSSIER first_mint_block=NOT_BOUNDED (no empty step found in range)", flush=True)

# timestamp of first mint block (fast_rpc is 8s-capped; use curl)
if found:
    for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                                  "params": [hex(found), False], "id": 1})],
                capture_output=True, text=True, timeout=30).stdout
            ts = int(json.loads(out)["result"]["timestamp"], 16)
            import datetime
            print(f"FIRST_MINT_TS {found} = {ts} = {datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M:%S WIB')}", flush=True)
            break
        except Exception as e:
            print("ts fail", ep, type(e).__name__, flush=True)
print("WALKBACK DONE", flush=True)
