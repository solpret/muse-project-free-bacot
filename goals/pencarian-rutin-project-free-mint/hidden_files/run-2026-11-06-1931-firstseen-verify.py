#!/usr/bin/env python3
"""Run 2026-11-06 1901 WIB first-seen verify (scan triage, 6 contracts).
READ-ONLY. Sourcify via direct curl retry (scan enrichment IncompleteRead
is unreliable — 1831 precedent). On-chain probe for verified contracts.
Writes run-2026-11-06-1931-firstseen-verify.json; _meta holds only contracts
that qualify as EARLY leads (agent-shaped + first mints verified on-chain).
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1931"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

FIRST_SEEN = {
 "Zigzoo": {"addr": "0x09ADA5A12293C30D75b97c56E34967E8a4326a3C", "symbol": "ZIGZOO",
             "window": (35, 35, 132008414)},
}
GATE_WORDS = ["agentid", "agent_id", "agentregistry", "agent_registry",
              "agentgate", "agent_gate", "hasagentid", "isagent"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=8):
    for rpc in EPS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            import urllib.request
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

def call(to, sig, args=""):
    return raw(to, sel(sig) + args)

def sourcify_abi(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            d = json.loads(r.stdout)
            if d.get("abi") is not None:
                return ("verified", d.get("abi"))
            return ("not_verified", None)
    except Exception as e:
        print("  curl err", addr, e, flush=True)
    return ("error", None)

def registry_bytes(addr):
    for ep in EPS:
        try:
            code = _single(ep, "eth_getCode", [addr, "latest"], 8, retries=0)
            if isinstance(code, str) and len(code) > 2:
                return "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code[2:].lower()
            return None
        except Exception:
            continue
    return None

def classify(abi):
    funcs = [it.get("name", "") for it in abi if isinstance(it, dict) and it.get("type") == "function"]
    low = [f.lower() for f in funcs]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    free = [f for f in funcs if "free" in f.lower() or f.lower() in ("mintfree", "claimfree")]
    mint = [f for f in funcs if "mint" in f.lower()]
    return {"gate_fns": gate, "free_fns": free, "mint_fns": mint, "n_fns": len(funcs)}

out = {"_meta": {}}
for name, meta in FIRST_SEEN.items():
    a = meta["addr"]
    st, abi = sourcify_abi(a)
    r = {"address": a, "sourcify_retry": st, "window_mints": meta["window"][0],
         "window_minters": meta["window"][1], "first_block": meta["window"][2]}
    if isinstance(abi, list):
        r.update(classify(abi))
        agent_shaped = bool(r["gate_fns"]) or bool([f for f in r["mint_fns"] if "agent" in f.lower()]) or bool(r["free_fns"])
    else:
        r["registry_bytes"] = registry_bytes(a)
        agent_shaped = bool(r["registry_bytes"])
    r["agent_shaped"] = agent_shaped
    print(name, a, "sourcify:", st, "agent_shaped:", agent_shaped, flush=True)
    if agent_shaped and isinstance(abi, list):
        # on-chain probe
        for sig in ["totalSupply()", "totalMinted()", "mintOpen()", "MAX_SUPPLY()", "price()"]:
            r[sig.split("(")[0]] = call(a, sig)
        r["costOf_user_1"] = call(a, "costOf(address,uint256)", enc(USER) + enc_uint(1))
        r["mintedBy_user"] = call(a, "mintedBy(address)", enc(USER))
        r["balanceOf_user"] = call(a, "balanceOf(address)", enc(USER))
        out["_meta"][name] = {"addr": a, "symbol": meta["symbol"],
                              "window_mints": meta["window"][0],
                              "window_minters": meta["window"][1],
                              "first_block": meta["window"][2],
                              "agentShape": f"Sourcify VERIFIED (direct curl retry): gate={r['gate_fns']} free={r['free_fns']} mint={r['mint_fns']}"}
    out[name] = r

json.dump(out, open(f"{BASE}/run-{TS}-firstseen-verify.json", "w"), indent=1)
print("FIRSTSEEN DONE early-lead candidates:", list(out["_meta"].keys()), flush=True)
