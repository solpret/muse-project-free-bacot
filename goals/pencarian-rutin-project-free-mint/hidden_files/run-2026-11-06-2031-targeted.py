#!/usr/bin/env python3
"""Run 2031 targeted re-read: Tampesta-6aA5 (opened 21:00 WIB), Quantumfarm
(age deadline 21:00:37 WIB passed this run), StarAgent-7d39 (deadline ~21:26 WIB).
Read-only; writes run-2026-11-06-2031-targeted.json."""
import json, urllib.request, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2031"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

TARGETS = {
    "Tampesta-6aA5": ("0x6aA51bd62C0c6B0bA206e25952F4063a7e0CCE79",
        ["totalSupply()", "totalMinted()", "publicMinted()", "phase()", "paused()",
         "mintOpen()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "maxSupply()", "remainingFree()", "freeLeft()"]),
    "Quantumfarm": ("0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010",
        ["totalSupply()", "totalMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "mintOpen()", "paused()"]),
    "StarAgent-7d39": ("0x7d390e37Ed41A359f276D8764ca15432704B99b7",
        ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "paused()"]),
}
out = {"run": TS, "read_wib": "2026-11-06 ~21:15 WIB"}
for name, (addr, views) in TARGETS.items():
    d = {"address": addr}
    for v in views:
        d[v] = call(addr, v)
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    d["freeClaimed_user"] = call(addr, "freeClaimed(address)", enc(USER))
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + format(1, "064x"))
    d["costOf_user_1"] = call(addr, "costOf(address,uint256)", enc(USER) + format(1, "064x"))
    out[name] = d
    print(name, json.dumps(d), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-targeted.json", "w"), indent=1)
print("TARGETED DONE", flush=True)
