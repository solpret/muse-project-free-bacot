#!/usr/bin/env python3
"""Run 2026-11-06 0634 WIB: on-chain probe fallback for 0xa0F5D8FE... (Sourcify ABI fetch
retry-exhausted). Probes S1/S2-relevant views via eth_call; a revert/empty = view absent.
Read-only; updates hot-leg-seen.json note for that address only."""
import json, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xBF52870AA51347b8da0b280074B9E472d5b2C44e"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return "revert"
            v = out["result"]
            if not v or v == "0x": return "empty"
            return v
        except Exception:
            continue
    return "rpc-fail"

VIEWS = ["name()", "symbol()", "decimals()", "totalSupply()",
         "freeClaimed()", "freeMinted()", "freeLeft()", "freeAvailable()",
         "freeSharesRemaining()", "freeClaimed(address)", "freeFor(address,uint256)",
         "agentRegistry()", "agentId()", "registry()", "mintFree()",
         "quote(address,uint256)", "costOf(address,uint256)", "mintOpen()"]
found = []
for sig in VIEWS:
    if "address" in sig and "uint256" in sig:
        d = sel(sig) + enc(USER) + format(1, "064x")
    elif "address" in sig:
        d = sel(sig) + enc(USER)
    else:
        d = sel(sig)
    r = raw(ADDR, d)
    present = r not in ("revert", "empty", "rpc-fail")
    print(sig, "->", "PRESENT" if present else r, (r[:66] if present else ""), flush=True)
    if present: found.append(sig)
print("FOUND:", found)
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
hl[ADDR] = {"first_seen_wib": "2026-11-06T06:15:00+07:00",
            "note": f"probe on-chain: {found} -> bukan bentuk sale S1/S2 menurut probe (tanpa mint+quote+free view+registry lengkap)" if not (any("free" in f.lower() for f in found) and any("agent" in f.lower() or "registry" in f.lower() for f in found)) else f"probe on-chain: {found} -> PERLU shape-check lanjutan job utama",
            "source": "sourcify-feed",
            "status": "checked-not-sale-shape-probe"}
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("hot-leg-seen total now:", len(hl))
