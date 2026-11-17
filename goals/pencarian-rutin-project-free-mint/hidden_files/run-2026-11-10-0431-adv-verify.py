#!/usr/bin/env python3
"""Post-mint verification for Adventure Agent #554 (run 0431).
Polls receipt, then reads ownerOf(554), rarityOf(554), jobOf(554),
freeClaimed(user), freeMinted, ADV balance. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
ADV_TOKEN = "0x95ad3b9b02c424af94bc3ed417467e174d93f08f"
TX = "0x0bdb0e16ee7e5ed45af8e7e21b050c4aa25d4998358518013bc2c98168dab991"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

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

def rpc(method, params):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=25)
            if isinstance(r, dict) and "error" not in r:
                return r.get("result")
        except Exception:
            continue
    return None

receipt = None
for attempt in range(12):
    receipt = rpc("eth_getTransactionReceipt", [TX])
    if receipt:
        break
    print(f"receipt attempt {attempt+1}: pending...", flush=True)
    time.sleep(10)
print("RECEIPT:", json.dumps(receipt, indent=1) if receipt else None, flush=True)

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

def view(addr, sig, args=""):
    return to_int(raw_call(addr, sel(sig) + args))

def view_addr(addr, sig, args=""):
    res = raw_call(addr, sel(sig) + args)
    if res and len(res) >= 66:
        return "0x" + res[26:66]
    return None

TOKEN_ID = 554
out = {
    "tx": TX,
    "receipt_status": int(receipt["status"], 16) if receipt and receipt.get("status") else None,
    "receipt_block": int(receipt["blockNumber"], 16) if receipt and receipt.get("blockNumber") else None,
    "receipt_gasUsed": int(receipt["gasUsed"], 16) if receipt and receipt.get("gasUsed") else None,
    "receipt_from": receipt.get("from") if receipt else None,
    "receipt_to": receipt.get("to") if receipt else None,
    "ownerOf_554": view_addr(ADV, "ownerOf(uint256)", "0" * 62 + "22a"),
    "rarityOf_554": view(ADV, "rarityOf(uint256)", "0" * 62 + "22a"),
    "jobOf_554": view(ADV, "jobOf(uint256)", "0" * 62 + "22a"),
    "freeClaimed_user": view(ADV, "freeClaimed(address)", enc(USER)),
    "balanceOf_user": view(ADV, "balanceOf(address)", enc(USER)),
    "freeMinted": view(ADV, "freeMinted()"),
    "freeLeft": view(ADV, "freeLeft()"),
    "totalMinted": view(ADV, "totalMinted()"),
    "ADV_balance_user": view(ADV_TOKEN, "balanceOf(address)", enc(USER)),
    "block": None,
}
blk = rpc("eth_blockNumber", [])
out["block"] = int(blk, 16) if blk else None
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-10-0431-adv-verify.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s", flush=True)
