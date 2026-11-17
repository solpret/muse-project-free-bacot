#!/usr/bin/env python3
"""Probe run 0931: track-C S1 hit 0xDDc2 full verification. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def call(addr, data):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
def dec_str(res):
    try:
        b = bytes.fromhex(res[2:])
        ln = int.from_bytes(b[32:64], 'big')
        return b[64:64+ln].decode(errors='ignore')
    except Exception: return None
def dec_addr(res):
    try: return "0x" + res[-40:]
    except Exception: return None

A = "0xDDc2352d1ceC10b42e05A297232f5328902C6c2C"
out = {"block": block(), "started_wib": "2026-11-11 09:31 WIB", "address": A}
views = ["FREE_SHARES()", "PAID_SHARES()", "TOTAL_SHARES()", "TOTAL_SUPPLY()", "TOKENS_PER_SHARE()",
         "paidMinted()", "launch()", "launchBlock()", "deadline()", "SALE_DURATION()",
         "priceOfShare()", "mintCost()", "raised()", "owner()", "projectWallet()",
         "freeClaimed(address)", "mintedBy(address)", "balanceOf(address)", "decimals()",
         "OPEN_USDT_PER_TOKEN_E18()", "TARGET_RAISE()"]
res = {}
for sig in views:
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    else:
        data = sel(sig); key = base
    res[key] = to_int(call(A, data))
    print(f"  {key} = {res[key]}", flush=True)
res["name"] = dec_str(call(A, sel("name()")))
res["symbol"] = dec_str(call(A, sel("symbol()")))
res["owner_addr"] = dec_addr(call(A, sel("owner()")))
print("  name =", res["name"], "symbol =", res["symbol"], "owner =", res["owner_addr"], flush=True)
# quoteMint(user,1): try quoteMint(address,uint256)
q = call(A, sel("quoteMint(address,uint256)") + enc(USER) + enc_u(1))
res["quoteMint_user_1"] = to_int(q)
print("  quoteMint(user,1) =", res["quoteMint_user_1"], flush=True)
# also quoteMint(uint256)
q2 = call(A, sel("quoteMint(uint256)") + enc_u(1))
res["quoteMint_1"] = to_int(q2)
print("  quoteMint(1) =", res["quoteMint_1"], flush=True)
# launchBlock -> timestamp via eth_getBlockByNumber
lb = res.get("launchBlock")
if lb:
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                          "params": [hex(lb), False]}, timeout=25)
            ts = r.get("result", {}).get("timestamp")
            if ts:
                res["launchBlock_timestamp"] = int(ts, 16)
                print("  launchBlock ts =", res["launchBlock_timestamp"], flush=True)
                break
        except Exception: continue
out["DDc2"] = res
json.dump(out, open("run-2026-11-11-0931-probe-ddc2.json", "w"), indent=1)
print("DONE block", out["block"], flush=True)
