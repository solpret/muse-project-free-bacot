#!/usr/bin/env python3
"""Fresh pre-mint verification for Adventure Agent (run 0431).
Read-only. Prints free views + user slot + block."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_call(addr, data):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "error" not in r and r.get("result"):
                return r["result"]
        except Exception:
            continue
    return None

def view(sig, args=""):
    return to_int(raw_call(ADV, sel(sig) + args))

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

out = {"block": get_block()}
for sig in ["freeMinted()", "freeLeft()", "FREE_SUPPLY()", "totalMinted()",
            "paidMinted()", "FREE_ADV_BONUS()", "MAX_FREE_PER_WALLET()"]:
    out[sig.split("(")[0]] = view(sig)
out["freeClaimed_user"] = view("freeClaimed(address)", enc(USER))
out["balanceOf_user"] = view("balanceOf(address)", enc(USER))
# ADV token balance of user (advToken 0x95ad3b9b02c424af94bc3ed417467e174d93f08f)
adv_token = "0x95ad3b9b02c424af94bc3ed417467e174d93f08f"
out["ADV_balance_user"] = to_int(raw_call(adv_token, sel("balanceOf(address)") + enc(USER)))
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-2026-11-10-0431-adv-premint.json", "w"), indent=1)
