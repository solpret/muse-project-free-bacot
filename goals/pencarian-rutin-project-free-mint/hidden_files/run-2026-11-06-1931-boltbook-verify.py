#!/usr/bin/env python3
"""Run 1931 Boltbook-lead verify (parent). READ-ONLY.
Sourcify ABI (curl) + agent-shape classify + on-chain view probe for:
STRAWBS + MERGEBORN (not in snapshot), Cogito-COG-A, Pulsekeep,
Ringgent-f1d1 (promotion checks), Botphoenix (MAX_SUPPLY sold-out check).
Writes run-2026-11-06-1931-boltbook-verify.json."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1931"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
GATE_WORDS = ["agentid", "agent_id", "agentregistry", "agent_registry",
              "agentgate", "agent_gate", "hasagentid", "isagent"]

ITEMS = {
 "STRAWBS": "0x9Bed5d806Ed91675127f81d1F13C6Ab3eF9430Cc",
 "MERGEBORN": "0x348455be18b700cae8aa425bd84e456e47f16e8b",
 "Cogito-COG-A": "0x5ae2be6bba1bd4f561dc13158c7f5b95992e045b",
 "Pulsekeep": "0x65c89bd01a03b9b9b73ed29d3b3af8d2eb034dfc",
 "Ringgent-f1d1": "0xf1d1650dbfeb0fa8082481c8213accd59af3cf4a",
 "Botphoenix-221f": "0x221F42a2516Dd4462C572F84b777a6f4e94135a4",
}
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "freeLeft()", "remainingFree()", "freeQuota()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "mintedBy(address)", "freeUsed(address)",
         "canFreeMint(address)", "claimedFree(address)", "balanceOf(address)",
         "costOf(address,uint256)", "quote(address,uint256)", "price()"]

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
            if "error" in out: return "ERR:" + str(out["error"].get("message", ""))[:40]
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return "TIMEOUT"

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def sourcify_abi(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            d = json.loads(r.stdout)
            if d.get("abi") is not None: return ("verified", d.get("abi"))
            return ("not_verified", None)
    except Exception as e:
        print("  curl err", addr, e, flush=True)
    return ("error", None)

def classify(abi):
    funcs = [it.get("name", "") for it in abi if isinstance(it, dict) and it.get("type") == "function"]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    free = [f for f in funcs if "free" in f.lower() or f.lower() in ("mintfree", "claimfree")]
    mint = [f for f in funcs if "mint" in f.lower()]
    return {"gate_fns": gate, "free_fns": free, "mint_fns": mint, "n_fns": len(funcs)}

out = {}
for name, a in ITEMS.items():
    st, abi = sourcify_abi(a)
    r = {"address": a, "sourcify": st}
    if isinstance(abi, list):
        r.update(classify(abi))
        r["agent_shaped"] = bool(r["gate_fns"]) or bool(r["free_fns"])
    else:
        r["agent_shaped"] = None
        # registry bytes fallback
        for ep in EPS:
            try:
                code = _single(ep, "eth_getCode", [a, "latest"], 8, retries=0)
                if isinstance(code, str) and len(code) > 2:
                    r["registry_bytes"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code[2:].lower()
                    break
            except Exception:
                continue
    for sig in VIEWS:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(a, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(a, sig, enc(USER)); key += "_user"
        else:
            v = call(a, sig)
        r[key] = v
    out[name] = r
    print(name, a, "src:", st, "shaped:", r.get("agent_shaped"),
          "ts:", r.get("totalSupply"), "tm:", r.get("totalMinted"),
          "fc:", r.get("freeClaimed"), "fm:", r.get("freeMinted"),
          "max:", r.get("MAX_SUPPLY"), "open:", r.get("mintOpen"),
          "quote:", r.get("costOf_user_1"), r.get("quote_user_1"),
          "bal:", r.get("balanceOf_user"), flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-boltbook-verify.json", "w"), indent=1)
print("BOLTBOOK-VERIFY DONE", flush=True)
