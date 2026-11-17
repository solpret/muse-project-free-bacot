#!/usr/bin/env python3
"""Re-check run 0431: 0x38491597 sale views + Adventure Agent tokenURI(1)/contractURI.
Read-only. Writes run-2026-11-10-0431-38491597.log + .json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

blk = get_block()
SALE = "0x3849159784aa47Fe76117103904204D9f5D153E7"
s = {"block": blk}
for sig in ["FREE_SHARES()", "TOTAL_SHARES()", "totalShares()", "totalPaidShares()",
            "freeSharesRemaining()", "publicFreeRemaining()", "launched()",
            "launchPending()", "saleClockStart()"]:
    s[sig.split("(")[0]] = view(SALE, sig)
s["freeSharesClaimed_user"] = view(SALE, "freeSharesClaimed(address)", enc(USER))
s["balanceOf_user"] = view(SALE, "balanceOf(address)", enc(USER))
print("0x38491597 sale re-check (run 0431):", json.dumps(s), flush=True)
print("block:", blk, flush=True)

ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
adv = {"tokenURI_1": view_str(ADV, "tokenURI(uint256)", "0" * 63 + "1"),
       "contractURI": view_str(ADV, "contractURI()")}
print("ADV tokenURI(1):", adv["tokenURI_1"], flush=True)
print("ADV contractURI:", adv["contractURI"], flush=True)
json.dump({"sale_0x38491597": s, "adv_method_I": adv},
          open(f"{BASE}/run-2026-11-10-0431-38491597.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s", flush=True)
