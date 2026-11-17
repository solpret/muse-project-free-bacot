#!/usr/bin/env python3
"""Probe run 1031: Fira Agent shape/free, Baby Neiro track-C legs, binanceai pending claim.
Read-only. curl transport, 25s/call."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
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
            res = post(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception: continue
    return None
def code(addr):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}, timeout=25)
            if isinstance(r, dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
out = {"block": block(), "started_wib": "2026-11-11 ~10:40 WIB"}
# Fira Agent
fira = "0x7d46023bf2c3732f5fd30321cfce1ca91684408d"
fv = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "owner()"]
out["fira"] = batch(fira, fv) or {"_batch_fail": True}
c = code(fira)
out["fira_code_len"] = len(c) - 2 if c else None
out["fira_code_has_registry"] = (REG in (c or "").lower()) if c else None
# Baby Neiro
bneiro = "0x10f84859562B0FCbB7464b17dfC84C809CfbD674"
bv = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SHARES()", "opened()", "OPEN_AT()", "freeClaimed(address)", "quotaOf(address)", "mintedById(address)", "balanceOf(address)", "owner()"]
out["bneiro"] = batch(bneiro, bv) or {"_batch_fail": True}
c2 = code(bneiro)
out["bneiro_code_has_registry"] = (REG in (c2 or "").lower()) if c2 else None
# binanceai.fun pending claim
mint = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
tok = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
out["binanceai_mint"] = batch(mint, ["launched()", "tokenClaimed(address)", "claimable(address)"]) or {"_batch_fail": True}
out["binanceai_token_bal"] = batch(tok, ["balanceOf(address)"]) or {"_batch_fail": True}
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-2026-11-11-1031-probe.json", "w"), indent=1)
