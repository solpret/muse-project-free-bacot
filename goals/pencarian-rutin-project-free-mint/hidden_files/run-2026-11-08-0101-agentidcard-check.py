#!/usr/bin/env python3
"""Run 0101: AGENT ID Card 0x486d0947cAa3d70c19e38f6C789489d39291E9e7 — shape check only (read-only).
Surfaced by discovery sweep (Substack 22-project list, 11 days old); never seen in any file.
Decide: agent-shaped? first mints? free pool? (NO preview/mint — early-lead triage only.)"""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR = "0x486d0947cAa3d70c19e38f6C789489d39291E9e7"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(sig, ep, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
    return r[0]
out = {"address": ADDR}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
try:
    code = batch([("eth_getCode", [ADDR, "latest"])], endpoint=ep, timeout=10)[0]
    out["registry_bytes_hit"] = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    out["code_len"] = len(code) if isinstance(code, str) else None
except Exception as e:
    out["registry_bytes_hit"] = None; out["code_err"] = str(e)[:80]
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{ADDR}", headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.load(r)
    out["sourcify"] = j.get("stdJson", {}).get("status") or j.get("status") or "fetched"
    abi = j.get("stdJson", {}).get("abi") or j.get("abi")
    if isinstance(abi, list):
        fns = [i.get("name","") for i in abi if isinstance(i, dict) and i.get("type")=="function"]
        out["abi_fns"] = fns
        out["has_agent_registry"] = any("agent" in f.lower() for f in fns)
        out["free_fns"] = [f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")]
        out["mint_fns"] = [f for f in fns if "mint" in f.lower()]
    else:
        out["abi_fns"] = None
except Exception as e:
    out["sourcify"] = f"error:{type(e).__name__}:{str(e)[:80]}"
for sig in ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()", "freeMinted()", "freeClaimed()", "mintOpen()"]:
    try: out[sig.split("(")[0]] = to_int(single(sig, ep))
    except Exception: out[sig.split("(")[0]] = None
for sig in ["freeClaimed(address)", "balanceOf(address)"]:
    try: out[sig.split("(")[0]+"_user"] = to_int(single(sig, ep, USER))
    except Exception: out[sig.split("(")[0]+"_user"] = None
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0101-agentidcard-check.json", "w"), indent=1)
