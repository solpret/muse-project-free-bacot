#!/usr/bin/env python3
"""Fresh read Agent Harvest Land + codelen checks for Boltbook-new null addresses.
Run free-mint-search 2026-11-20 09:01 WIB. Read-only. Writes harvest-0901.json."""
import json, subprocess, time
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
LAND = "0xacf150d9eC909E3d339Bf4c6D090b18495674E66"

def sel(sig):
    return keccak(sig.encode())[:4].hex()
def enc_addr(a):
    return "0" * 24 + a[2:].lower()

calls, labels = [], []
def add(addr, sig, args, lab):
    calls.append((addr, "0x" + sel(sig) + args))
    labels.append(lab)

for sig, lab in [("freeMinted()", "freeMinted"), ("totalMinted()", "totalMinted"),
                 ("currentPhase()", "currentPhase"), ("phaseMinted()", "phaseMinted"),
                 ("freeOpen()", "freeOpen"), ("phasePauseEnd()", "phasePauseEnd"),
                 ("FREE_SUPPLY()", "FREE_SUPPLY"), ("balanceOf(address)", "balanceOf_user"),
                 ("freeClaimed(address)", "freeClaimed_user")]:
    args = enc_addr(USER) if "(address)" in sig else ""
    add(LAND, sig, args, lab)

# codelen checks
codes = {}
for a in ["0x48afa54a08ef30e1af87e12c929cf7700ccde983",
          "0xd301d472f2e469a1aafa1af6f214e312f1858873",
          "0x79F55DAa8a3CF2Eb76EE40e26ff6E244a4cC1eD4"]:
    payload = [{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                "params": [a, "latest"]}]
    try:
        o = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", RPC,
                            "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                           capture_output=True, text=True)
        r = json.loads(o.stdout)[0].get("result", "")
        codes[a] = {"codelen": len(r) - 2 if r.startswith("0x") else None, "raw_len": len(r)}
    except Exception as e:
        codes[a] = {"error": f"{type(e).__name__}: {e}"}

results = [None] * len(calls)
t0 = time.time()
for i in range(0, len(calls), 5):
    chunk = calls[i:i + 5]
    payload = [{"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                "params": [{"to": a, "data": d}, "latest"]} for j, (a, d) in enumerate(chunk)]
    try:
        o = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST", RPC,
                            "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                           capture_output=True, text=True)
        resp = json.loads(o.stdout)
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by_id.get(j + 1, {})
            results[i + j] = it.get("result") if it.get("result") not in (None, "0x") else {"error": str(it.get("error", "null"))[:160]}
    except Exception as e:
        for j in range(len(chunk)):
            results[i + j] = {"error": f"transport {type(e).__name__}: {str(e)[:100]}"}
    time.sleep(1)

try:
    blk = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", RPC,
                          "-H", "Content-Type: application/json",
                          "-d", json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])],
                         capture_output=True, text=True)
    block = int(json.loads(blk.stdout)[0]["result"], 16)
except Exception:
    block = "ERR"

views = {}
for lab, v in zip(labels, results):
    if isinstance(v, dict):
        views[lab] = v
    else:
        try:
            views[lab] = int(v, 16)
        except Exception:
            views[lab] = v

out = {"block": block, "read_wib": "2026-11-20 ~09:1x WIB",
       "elapsed_s": round(time.time() - t0, 1), "harvest_land": views, "codelen": codes}
json.dump(out, open(BASE + "harvest-0901.json", "w"), indent=1)
print(json.dumps(out, indent=1))
