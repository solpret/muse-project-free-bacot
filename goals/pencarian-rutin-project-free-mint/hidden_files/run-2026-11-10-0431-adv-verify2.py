#!/usr/bin/env python3
"""Post-state reads for Adventure Agent #554 (run 0431, part 2).
Receipt already verified (status 1, block 132664145). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
ADV_TOKEN = "0x95ad3b9b02c424af94bc3ed417467e174d93f08f"
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

def view_str(addr, sig, args=""):
    res = raw_call(addr, sel(sig) + args)
    if not res or res == "0x":
        return None
    try:
        b = bytes.fromhex(res[2:])
        if len(b) >= 96:
            off = int.from_bytes(b[0:32], "big")
            ln = int.from_bytes(b[off:off+32], "big")
            return b[off+32:off+32+ln].decode("utf-8", "ignore")[:600]
    except Exception:
        return None
    return None

TOKEN_HEX = "0" * 62 + "22a"
out = {
    "tx": "0x0bdb0e16ee7e5ed45af8e7e21b050c4aa25d4998358518013bc2c98168dab991",
    "receipt_status": 1,
    "receipt_block": 132664145,
    "receipt_gasUsed": 223234,
    "ownerOf_554": view_addr(ADV, "ownerOf(uint256)", TOKEN_HEX),
    "rarityOf_554": view(ADV, "rarityOf(uint256)", TOKEN_HEX),
    "jobOf_554": view(ADV, "jobOf(uint256)", TOKEN_HEX),
    "tokenURI_554": view_str(ADV, "tokenURI(uint256)", TOKEN_HEX),
    "freeClaimed_user": view(ADV, "freeClaimed(address)", enc(USER)),
    "balanceOf_user": view(ADV, "balanceOf(address)", enc(USER)),
    "freeMinted": view(ADV, "freeMinted()"),
    "freeLeft": view(ADV, "freeLeft()"),
    "totalMinted": view(ADV, "totalMinted()"),
    "ADV_balance_user": view(ADV_TOKEN, "balanceOf(address)", enc(USER)),
}
blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
        blk = int(r["result"], 16)
        break
    except Exception:
        continue
out["block"] = blk
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-10-0431-adv-verify.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s", flush=True)
