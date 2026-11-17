#!/usr/bin/env python3
"""Run 2026-11-09 04:01 WIB — AGENT DOSSIER age close-out.
Retry the 8 error chunks (132430111-132438110) + step probes below 132428111
(132408111, 132388111, 132368111) to localize the first mint. Bounded: max 15 probes.
Then timestamp the earliest mint block via dataseed eth_getBlockByNumber (curl).
"""
import sys, time, json, subprocess, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000"
ADDR = "0xac3f9a33c653fb3ca49056cfa5edf19101debf97"

def probe(frm, to, tries=2):
    for t in range(tries):
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
                "fromBlock": hex(frm), "toBlock": hex(to),
                "address": ADDR, "pageSize": 1000, "decodeLogs": False,
                "topics": [TRANSFER, "0x" + "0" * 24 + ZERO[2:].lower()]}, timeout=30)
            logs = body.get("result", {}).get("logs", [])
            return logs
        except Exception as e:
            print(f"probe {frm}-{to} try{t+1} ERROR {type(e).__name__}", flush=True)
            time.sleep(2)
    return None

earliest = 132439162
# retry error chunks, low to high
for frm in [132430111, 132431111, 132432111, 132433111, 132434111, 132435111, 132436111, 132437111, 132446111, 132447111]:
    logs = probe(frm, frm + 999)
    if logs is None:
        print(f"RETRY {frm}-{frm+999}: STILL ERROR (unprobed)", flush=True)
    elif logs:
        first = min(int(l["blockNumber"], 16) for l in logs)
        print(f"RETRY {frm}-{frm+999}: {len(logs)} mints earliest {first}", flush=True)
        earliest = min(earliest, first)
    else:
        print(f"RETRY {frm}-{frm+999}: 0 mints (empty)", flush=True)
    time.sleep(1)

# step probes below 132428111 (20k steps ~2.5h each)
for frm in [132408111, 132388111, 132368111]:
    logs = probe(frm, frm + 999)
    if logs is None:
        print(f"STEP {frm}-{frm+999}: ERROR (unprobed)", flush=True)
    elif logs:
        first = min(int(l["blockNumber"], 16) for l in logs)
        print(f"STEP {frm}-{frm+999}: {len(logs)} mints earliest {first}", flush=True)
        earliest = min(earliest, first)
    else:
        print(f"STEP {frm}-{frm+999}: 0 mints (empty)", flush=True)
    time.sleep(1)

print(f"RESULT2 AGENT DOSSIER earliest_mint_block={earliest}", flush=True)
for ep in ["https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed1.bnbchain.org/"]:
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                              "params": [hex(earliest), False], "id": 1})],
            capture_output=True, text=True, timeout=30).stdout
        ts = int(json.loads(out)["result"]["timestamp"], 16)
        print(f"FIRST_MINT_TS {earliest} = {ts} = {datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M:%S WIB')}", flush=True)
        break
    except Exception as e:
        print("ts fail", ep, type(e).__name__, flush=True)
print("CLOSEOUT DONE", flush=True)
