#!/usr/bin/env python3
"""Run 2031 triage: probe 6 true first-seen scan contracts for agent shape.
Read-only. Writes run-2026-11-06-2131-triage.json."""
import json, subprocess, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2201"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org"]

FIRST_SEEN = []

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data, timeout=5):
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

def sourcify_abi(addr):
    for attempt in range(2):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "20",
                                f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                               capture_output=True, text=True, timeout=30)
            d = json.loads(r.stdout)
            if d.get("abi") is not None: return ("verified", d["abi"])
            return ("not_verified", None)
        except Exception as e:
            time.sleep(2)
            last = e
    return (f"error:{last}", None)

def registry_bytes(addr):
    try:
        code = _single(RPCS[0], "eth_getCode", [addr, "latest"], 8, retries=1)
        if isinstance(code, str) and len(code) > 2:
            return REG_BYTES in code.lower()
    except Exception:
        pass
    return None

GATE_WORDS = ["agentid", "agent_id", "agentregistry", "agent_registry",
              "agentgate", "agent_gate", "hasagentid", "isagent"]
FREE_WORDS = ["free", "freemint", "freesupply", "freeclaim", "freeminted"]

out = {}
for addr, name, mints, minters in FIRST_SEEN:
    r = {"name": name, "address": addr, "window_mints": mints, "window_minters": minters}
    st, abi = sourcify_abi(addr)
    r["sourcify"] = st
    if isinstance(abi, list):
        fns = [f.get("name", "") for f in abi if isinstance(f, dict)]
        r["fns"] = len(fns)
        r["mint_fns"] = [f for f in fns if "mint" in f.lower()]
        r["free_views"] = [f for f in fns if any(w in f.lower() for w in FREE_WORDS)]
        r["gate_fns"] = [f for f in fns if any(w in f.lower().replace("_", "") for w in GATE_WORDS)]
        r["registry_in_abi"] = REGISTRY.lower() in json.dumps(abi).lower()
    else:
        r["fns"] = 0; r["mint_fns"] = []; r["free_views"] = []; r["gate_fns"] = []
        r["registry_in_abi"] = False
    r["registry_bytes"] = registry_bytes(addr)
    r["totalSupply"] = call(addr, "totalSupply()")
    r["MAX_SUPPLY"] = call(addr, "MAX_SUPPLY()")
    r["FREE_SUPPLY"] = call(addr, "FREE_SUPPLY()")
    r["freeClaimed"] = call(addr, "freeClaimed()")
    r["freeMinted"] = call(addr, "freeMinted()")
    r["mintOpen"] = call(addr, "mintOpen()")
    r["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    r["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + format(1, "064x"))
    agent_shaped = bool(r["gate_fns"]) or bool(r["registry_in_abi"]) or bool(r["registry_bytes"] and (r["free_views"] or r["mint_fns"]))
    r["agent_shaped"] = agent_shaped
    r["verdict"] = "AGENT-SHAPED" if agent_shaped else "not agent-shaped"
    out[name] = r
    print(name, json.dumps(r), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-triage.json", "w"), indent=1)
print("TRIAGE DONE", flush=True)
