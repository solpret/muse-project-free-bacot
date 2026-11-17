#!/usr/bin/env python3
"""AGCE post-mint verification run 1901. Read-only."""
import json, urllib.request, time
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE = "0x5AD10026B4233aC004043DBB9291CFad19b1B3C3"
TOKEN = "0x942c19A87a77b062D94C452ED8FaC6162aff45aD"
TX = "0x587c6189253122c1f0aec3eb7840f4b3f24d4d121a546408e5e491cb87b54401"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def rpc(method, params):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r: out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return None
def call(to, sig, args=""):
    v = rpc("eth_call", [{"to": to, "data": sel(sig) + args}, "latest"])
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v
receipt = None
for i in range(20):
    receipt = rpc("eth_getTransactionReceipt", [TX])
    if receipt: break
    time.sleep(6)
print("RECEIPT:", json.dumps(receipt, indent=1) if receipt else None)
out = {"txHash": TX, "receipt": receipt}
if receipt:
    out["status"] = int(receipt["status"], 16)
    out["blockNumber"] = int(receipt["blockNumber"], 16)
    out["gasUsed"] = int(receipt["gasUsed"], 16)
    out["effectiveGasPrice"] = int(receipt.get("effectiveGasPrice", "0x0"), 16)
    out["gasCostBNB"] = out["gasUsed"] * out["effectiveGasPrice"] / 1e18
out["balanceOf_user_after"] = call(TOKEN, "balanceOf(address)", enc(USER))
out["freeClaimed_user_after"] = call(SALE, "freeClaimed(address)", enc(USER))
out["freeRemaining_after"] = call(SALE, "freeRemaining()")
out["freeSharesClaimed_after"] = call(SALE, "freeSharesClaimed()")
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1901-agce-receipt.json", "w"), indent=1)
