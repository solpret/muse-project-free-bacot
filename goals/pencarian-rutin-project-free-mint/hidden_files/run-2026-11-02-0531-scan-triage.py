#!/usr/bin/env python3
"""Run 0531 scan triage: totals-check for 5 verified+free-shaped+registry-bytes first-seen contracts. Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
def iv(v): return int(v, 16) if v else None
def dec_str(v):
    if not v: return None
    b = bytes.fromhex(v[2:])
    if len(b) >= 64:
        ln = int.from_bytes(b[32:64], "big")
        if 0 < ln <= len(b) - 64: return b[64:64+ln].decode("utf-8", "replace")
    return None
cands = {"0x9873bD06d2615472dC40412D841d222Bf629Cd7B": 203, "0xD713DDFd37B8fF759afaeedAEdaD632d1985ed9c": 33,
         "0xf85ddB8A16a03a9d6d05D0e912f24fF9572ABBcb": 2, "0x343711EE8B8a5Ed2168a05E456C193734AD3Ef12": 2,
         "0x6912aD805cB3E0FDd6330F27347193E4EFC0742d": 1}
out = {}
for C, wm in cands.items():
    r = {"window_mints": wm, "name": dec_str(call(C, sel("name()"))), "symbol": dec_str(call(C, sel("symbol()")))}
    for fn in ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeClaimed()", "freeMinted()", "mintOpen()"]:
        r[fn] = iv(call(C, sel(fn)))
    for fn in ["AGENT_ID()", "agentIdRegistry()", "registry()", "agentRegistry()"]:
        r[fn] = call(C, sel(fn))
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp: d = json.load(resp)
        abi = d.get("abi") or []
        r["abi_functions"] = sorted({e.get("name") for e in abi if e.get("type") == "function" and e.get("name")})
    except Exception as e: r["abi_error"] = f"{type(e).__name__}: {str(e)[:120]}"
    out[C] = r; print(C, json.dumps(r))
json.dump(out, open(f"{HF}/run-2026-11-02-0531-scan-triage.json", "w"), indent=1)
print("saved triage")
