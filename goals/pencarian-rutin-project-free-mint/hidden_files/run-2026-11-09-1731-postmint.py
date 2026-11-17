#!/usr/bin/env python3
"""Post-mint Marbleworks: ownerOf(456), tierOf(456), tierName, revealed;
track-C 0x260bf39a: launched/launchTime/FREE_SLOTS/freeClaimed/freeClaimedAddr(user)/claimFree sig + code registry bytes.
Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
REG = "60b9262456de011f7d15a54CdD8c48bAaa8B022F".lower()
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
def call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]})
            if isinstance(res, dict):
                if "result" in res: return res["result"]
                if "error" in res: return {"error": str(res["error"])[:100]}
        except Exception: continue
    return None
def rd(addr, sig, *args):
    data = sel(sig)
    for a in args:
        data += enc(a) if isinstance(a, str) and a.startswith("0x") else str(int(a)).rjust(64, "0")
    r = call(addr, data)
    return r if isinstance(r, dict) else to_int(r)
def code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=25)
            if isinstance(r, dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
out = {}
MARB = "0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0"
out["marbleworks_postmint"] = {
    "ownerOf_456": rd(MARB, "ownerOf(uint256)", 456),
    "tierOf_456": rd(MARB, "tierOf(uint256)", 456),
    "revealed": rd(MARB, "revealed()"),
    "tierName_0": None,
}
# tierName(uint256) returns string - raw
r = call(MARB, sel("tierName(uint256)") + str(0).rjust(64, "0"))
out["marbleworks_postmint"]["tierName_0_raw"] = (r or "")[:200]
# tierOf value -> tierName of that tier
t = out["marbleworks_postmint"]["tierOf_456"]
if isinstance(t, int):
    r = call(MARB, sel("tierName(uint256)") + str(t).rjust(64, "0"))
    out["marbleworks_postmint"]["tierName_tier_raw"] = (r or "")[:200]
    r2 = call(MARB, sel("tierReward(uint256)") + str(t).rjust(64, "0"))
    out["marbleworks_postmint"]["tierReward_tier"] = to_int(r2) if not isinstance(r2, dict) else r2
print("MARBLE POSTMINT", json.dumps(out["marbleworks_postmint"]), flush=True)
NEW = "0x260bf39a6f3aB5E459856297178CC0DF6003374a"
c = code(NEW)
out["new_260bf39a"] = {
    "launched": rd(NEW, "launched()"), "launchTime": rd(NEW, "launchTime()"),
    "FREE_SLOTS": rd(NEW, "FREE_SLOTS()"), "freeClaimed": rd(NEW, "freeClaimed()"),
    "freeClaimedAddr_user": rd(NEW, "freeClaimedAddr(address)", USER),
    "PRICE": rd(NEW, "PRICE()"), "name": None, "symbol": None,
    "code_len": len(c) if c else None, "registry_bytes": (REG in c.lower()) if c else None,
}
for fn in ("name()", "symbol()", "decimals()", "totalSupply()"):
    r = call(NEW, sel(fn))
    out["new_260bf39a"][fn] = (r or "")[:200] if fn in ("name()", "symbol()") else to_int(r)
print("NEW260B", json.dumps(out["new_260bf39a"]), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1731-postmint.json", "w"), indent=1)
print("POSTMINT DONE", flush=True)
