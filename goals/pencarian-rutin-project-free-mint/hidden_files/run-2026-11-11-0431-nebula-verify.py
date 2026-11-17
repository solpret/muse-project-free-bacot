#!/usr/bin/env python3
"""Run 0431: verify NEBULA mint tx + post-state. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TX = "0x65b5844f22c5bff06b6c84b1e8a3369f8772c8b4b67cfe9f0eaa3d1bf8ab4ea2"
ADDR = "0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return int(v, 16) if v not in (None, "0x") else None
    except Exception:
        return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

receipt = None
for attempt in range(12):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionReceipt",
                          "params": [TX]}, timeout=25)
            if isinstance(r, dict) and r.get("result"):
                receipt = r["result"]
                break
        except Exception:
            pass
    if receipt:
        break
    print(f"receipt poll {attempt+1}/12: not yet", flush=True)
    time.sleep(10)

out = {"tx": TX, "receipt": None}
if receipt:
    out["receipt"] = {
        "status": to_int(receipt.get("status")),
        "blockNumber": to_int(receipt.get("blockNumber")),
        "gasUsed": to_int(receipt.get("gasUsed")),
        "from": receipt.get("from"),
        "to": receipt.get("to"),
    }
    print("RECEIPT", json.dumps(out["receipt"]), flush=True)
else:
    print("RECEIPT NOT FOUND after polls", flush=True)

# post-state reads
calls = []
views = ["totalShares()", "totalFreeShares()", "totalPaidShares()", "totalSupply()"]
for sig in views:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]})
for sig in ["freeUsed(address)", "sharesOf(address)", "balanceOf(address)"]:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig) + enc(USER)}, "latest"]})
calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_getBalance",
              "params": [USER, "latest"]})
calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_blockNumber", "params": []})
keys = views + ["freeUsed_user", "sharesOf_user", "balanceOf_user", "bnb_balance_wei", "block"]
for ep in EPS:
    try:
        r = post(ep, calls, timeout=25)
        if isinstance(r, list) and len(r) == len(calls):
            for k, item in zip(keys, r):
                res = item.get("result") if isinstance(item, dict) else None
                out[k] = to_int(res)
            print("POST-STATE EP OK", ep, flush=True)
            break
    except Exception as e:
        print("POST-STATE ERR", ep, e, flush=True)
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "run-2026-11-11-0431-nebula-verify.json", "w"), indent=1)
