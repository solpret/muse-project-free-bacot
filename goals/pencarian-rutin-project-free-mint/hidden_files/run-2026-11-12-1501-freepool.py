#!/usr/bin/env python3
"""Targeted free-pool reads, run 2026-11-12 15:01 WIB.
MECHA: freePoolSize()/freeClaimed()/AGENT_ID_REGISTRY()/maxSupply()/freeAvailable(user)/freePerWallet().
DACIT: freeInfo() raw tuple decode + mintEnd()/status()/AGENT_ID().
Read-only; writes run-2026-11-12-1501-freepool.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if r and r != "0x": return r
            if isinstance(res, dict) and "error" in res: return {"error": res["error"]}
        except Exception: continue
    return None
def uints(hexstr):
    if not hexstr or hexstr == "0x": return None
    b = bytes.fromhex(hexstr[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b) - 31, 32)]
out = {"started_wib": "2026-11-12 15:01 WIB"}
# MECHA
M = "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"
mecha = {}
for sig in ["freePoolSize()", "freeClaimed()", "AGENT_ID_REGISTRY()", "maxSupply()",
            "freePerWallet()", "totalMinted()", "mintOpen()"]:
    r = call(M, sel(sig))
    mecha[sig] = r if isinstance(r, dict) else (uints(r)[0] if uints(r) else None)
for sig in ["freeAvailable(address)", "freeUsedBy(address)", "hasAgentId(address)"]:
    r = call(M, sel(sig) + enc(USER))
    mecha[sig] = r if isinstance(r, dict) else (uints(r)[0] if uints(r) else None)
out["MECHA"] = mecha
print("MECHA:", mecha)
# DACIT
D = "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"
dacit = {}
for sig in ["freeInfo()", "mintEnd()", "status()", "AGENT_ID()", "mintStart()", "agentFreeUsed()", "totalMinted()"]:
    r = call(D, sel(sig))
    dacit[sig] = r if isinstance(r, dict) else uints(r)
for sig in ["freeUsedByWallet(address)", "walletInfo(address)"]:
    r = call(D, sel(sig) + enc(USER))
    dacit[sig] = r if isinstance(r, dict) else uints(r)
out["DACIT"] = dacit
print("DACIT:", dacit)
json.dump(out, open(BASE + "run-2026-11-12-1501-freepool.json", "w"), indent=1)
