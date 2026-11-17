#!/usr/bin/env python3
"""Triage3 run 0301: 0x38491597 sale views with CORRECT signatures from the
Sourcify ABI (curl-fetched), + Adventure Agent tokenURI(1) method I.
Read-only. Writes run-2026-11-10-0301-triage3.json."""
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

def view_addr(addr, sig):
    res = raw_call(addr, sel(sig))
    if res and len(res) >= 66:
        return "0x" + res[26:66]
    return None

def view_tuple(addr, sig, args=""):
    res = raw_call(addr, sel(sig) + args)
    if not res:
        return None
    try:
        b = bytes.fromhex(res[2:])
        return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception:
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
            s = b[off+32:off+32+ln].decode("utf-8", "ignore")
            return s[:600]
    except Exception:
        return None
    return None

SALE = "0x3849159784aa47Fe76117103904204D9f5D153E7"
s = {}
s["AGENT_ID_REGISTRY"] = view_addr(SALE, "AGENT_ID_REGISTRY()")
s["FREE_SHARES"] = view(SALE, "FREE_SHARES()")
s["TOTAL_SHARES"] = view(SALE, "TOTAL_SHARES()")
s["totalShares"] = view(SALE, "totalShares()")
s["totalPaidShares"] = view(SALE, "totalPaidShares()")
s["freeSharesRemaining"] = view(SALE, "freeSharesRemaining()")
s["publicFreeRemaining"] = view(SALE, "publicFreeRemaining()")
s["TOKENS_PER_SHARE"] = view(SALE, "TOKENS_PER_SHARE()")
s["PRICE_PER_SHARE"] = view(SALE, "PRICE_PER_SHARE()")
s["PAID_SHARES"] = view(SALE, "PAID_SHARES()")
s["LP_TOKEN_RESERVE"] = view(SALE, "LP_TOKEN_RESERVE()")
s["launched"] = view(SALE, "launched()")
s["launchPending"] = view(SALE, "launchPending()")
s["saleClockStart"] = view(SALE, "saleClockStart()")
s["owner"] = view_addr(SALE, "owner()")
s["token"] = view_addr(SALE, "token()")
s["hasAgentId_user"] = view(SALE, "hasAgentId(address)", enc(USER))
s["freeSharesClaimed_user"] = view(SALE, "freeSharesClaimed(address)", enc(USER))
s["sharesMinted_user"] = view(SALE, "sharesMinted(address)", enc(USER))
s["paidSharesMinted_user"] = view(SALE, "paidSharesMinted(address)", enc(USER))
s["quote_user_1"] = view_tuple(SALE, "quote(address,uint256)", enc(USER) + "0" * 63 + "1")
s["totalPaidIn"] = view(SALE, "totalPaidIn()")
s["adminBurnMinted"] = view(SALE, "adminBurnMinted()")
print("SALE:", json.dumps(s), flush=True)

ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
adv = {}
adv["tokenURI_1"] = view_str(ADV, "tokenURI(uint256)", "0" * 63 + "1")
adv["contractURI"] = view_str(ADV, "contractURI()")
print("ADV tokenURI(1):", adv["tokenURI_1"], flush=True)
print("ADV contractURI:", adv["contractURI"], flush=True)

out = {"sale_0x38491597": s, "adv_method_I": adv}
json.dump(out, open(f"{BASE}/run-2026-11-10-0301-triage3.json", "w"), indent=1)
print(f"TRIAGE3 DONE in {time.time()-T0:.1f}s", flush=True)
