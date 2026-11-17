#!/usr/bin/env python3
"""Micro-salvage 2 for hot-leg 2026-11-11 21:59 WIB. The 2159 salvage script
was killed by the 280s timeout after S1 + AGCR-ABI (RPC very slow tonight).
Remaining decision-relevant reads, minimal set, short timeouts (curl -m 6):
(1) AGCR 0x5491...: AGENT_ID_REGISTRY() value - if it equals the Agent ID
registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, AGCR IS agent-shaped and
the shape-check (set missing 'agent_id_registry') was a false negative;
then freeMinted/FREE_SUPPLY/mintOpen/slot.
(2) Stampooor freeMinted + freeAvailable(user) (gate-blocked strong lead).
(3) AgentPals freeMinted (sold-out watch).
Read-only; writes hot-leg-run-2026-11-11-2159-salvage2.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "6", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=10)
            j = json.loads(r.stdout.decode(errors="replace"))
            if "error" in j: continue
            raw = j.get("result")
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception:
            continue
    return {"error": "all-endpoints-failed"}

U = enc_addr(USER)
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
out = {}
A = "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"
ag = {}
ag["AGENT_ID_REGISTRY"] = call(A, "AGENT_ID_REGISTRY()")
reg_val = ag["AGENT_ID_REGISTRY"]
ag["registry_is_agent_id_registry"] = (isinstance(reg_val, str) and reg_val.lower().endswith(REGISTRY[2:]))
if ag["registry_is_agent_id_registry"]:
    for key, sig, args in [
        ("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
        ("mintOpen", "mintOpen()", ""), ("totalSupply", "totalSupply()", ""),
        ("freeClaimed_user", "freeClaimed(address)", U),
        ("balanceOf_user", "balanceOf(address)", U),
        ("name", "name()", ""), ("symbol", "symbol()", ""),
    ]:
        ag[key] = call(A, sig, args)
        time.sleep(0.2)
out["AGCR"] = ag
print("AGCR", json.dumps(ag, indent=1), flush=True)

st = {}
S = "0x467696af8c2206B977B24081445104632dc1D459"
st["freeMinted"] = call(S, "freeMinted()")
st["freeAvailable_user"] = call(S, "freeAvailable(address)", U)
out["Stampooor"] = st
print("STAMPOOOR", json.dumps(st, indent=1), flush=True)

ap = {}
P = "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2"
ap["freeMinted"] = call(P, "freeMinted()")
out["AgentPals"] = ap
print("AGENTPALS", json.dumps(ap, indent=1), flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-11-2159-salvage2.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"])
