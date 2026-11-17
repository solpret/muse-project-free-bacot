#!/usr/bin/env python3
"""Re-read run 2026-11-09 09:31 WIB — special checks (read-only).
- Track-B binanceai.fun: MINT 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E,
  TOKEN 0x209173F09aFbCA053C0de9e9763f503e9fb54a3c.
- Track-C YAMA sale 0x86d779fc4d83044cceccb53639f9a98e367d6e46 (+token).
- Alchemister-0xCafEEDDF 0xCafEEDDF3C15C5CD9A63D97021efDe845e1781Bc (LEAN read;
  already age-excluded in 0901 merge — fresh confirm only, NO snapshot write).
Curl transport (dataseed, 25s/call) like the reread script.
Writes run-2026-11-09-0931-special.json. Read-only otherwise.
"""
import json, time, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
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

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

def raw_call(addr, data):
    """Single eth_call; returns raw hex result or None."""
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(res, dict) and "error" in res:
                return None
            if isinstance(res, dict):
                return res.get("result")
            return None
        except Exception:
            continue
    return None

def call(addr, sig, args=""):
    return to_int(raw_call(addr, sel(sig) + args))

def call_tuple2(addr, sig, args=""):
    raw = raw_call(addr, sel(sig) + args)
    if not raw or raw == "0x" or len(raw) < 130:
        return None
    try:
        b = bytes.fromhex(raw[2:])
        return (int.from_bytes(b[0:32], "big"), int.from_bytes(b[32:64], "big"))
    except Exception:
        return None

def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

out = {"block": get_block(), "started_wib": "2026-11-09 09:31 WIB"}
print("BLOCK", out["block"], flush=True)

# --- binanceai ---
M = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
T = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
b = {"mint": M, "token": T}
for sig, key in [("launched()", "launched"), ("failed()", "failed"),
                 ("isRefundPhase()", "isRefundPhase"), ("totalShares()", "totalShares"),
                 ("totalSupply()", "totalSupply_mint"),
                 ("claimOpen()", "claimOpen"), ("claimsOpen()", "claimsOpen")]:
    b[key] = call(M, sig)
for sig, key in [("tokenClaimed(address)", "tokenClaimed_user"),
                 ("claimed(address)", "claimed_user"),
                 ("shares(address)", "shares_user")]:
    b[key] = call(M, sig, enc(USER))
b["token_balance_user"] = call(T, "balanceOf(address)", enc(USER))
b["token_totalSupply"] = call(T, "totalSupply()")
print("BINANCEAI", json.dumps(b), flush=True)
out["binanceai"] = b

# --- YAMA ---
Y = "0x86d779fc4d83044cceccb53639f9a98e367d6e46"
YT = "0xa84ea20a667b3b1859ab9a9984ff5f03d8688ae2"
y = {"sale": Y, "token": YT}
for sig, key in [("totalShares()", "totalShares"), ("totalFreeShares()", "totalFreeShares"),
                 ("freeMinted()", "freeMinted"), ("mintingOpen()", "mintingOpen"),
                 ("MAX_SHARES()", "MAX_SHARES"), ("totalSupply()", "totalSupply_sale")]:
    y[key] = call(Y, sig)
for sig, key in [("freeUsed(address)", "freeUsed_user"),
                 ("quotaOf(address)", "quotaOf_user"),
                 ("sharesOf(address)", "sharesOf_user"),
                 ("freeClaimed(address)", "freeClaimed_user")]:
    y[key] = call(Y, sig, enc(USER))
q = call_tuple2(Y, "quote(address,uint256)", enc(USER) + enc_uint(1))
y["quote_user_1"] = {"freeShares": q[0], "costBnb": q[1]} if q else None
y["token_balance_user"] = call(YT, "balanceOf(address)", enc(USER))
print("YAMA", json.dumps(y), flush=True)
out["yama"] = y

# --- Alchemister-0xCafEEDDF (confirm only; already age-excluded 0901 merge) ---
A = "0xCafEEDDF3C15C5CD9A63D97021efDe845e1781Bc"
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]
a = batch(A, LEAN)
a = {"address": A, **(a or {})}
print("ALCHEMISTER-CAFEEDDF", json.dumps(a), flush=True)
out["alchemister_cafeeddf"] = a

out["elapsed_s"] = round(time.time() - T0, 1)
with open(f"{BASE}/run-2026-11-09-0931-special.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"SPECIAL DONE in {out['elapsed_s']}s", flush=True)
