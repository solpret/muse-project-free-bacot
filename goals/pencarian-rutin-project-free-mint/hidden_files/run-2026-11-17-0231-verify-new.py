#!/usr/bin/env python3
"""Run 0231 follow-up verification: DRAGON 0xfc19 + XCOPY 0x3fbe (Boltbook FIND-31).
Read-only: Sourcify ABI shape + fresh batch reads + owner()."""
import json, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
T0 = time.time()

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def call(to, sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "u1":
        data += enc_addr(USER) + "%064x" % 1
    return (to, data)

def batch_read(calls, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    body = json.dumps(payload).encode()
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            res = []
            by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
            for i in range(len(calls)):
                it = by_id.get(i + 1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try:
                        res.append(int(it["result"], 16))
                    except Exception:
                        res.append(it["result"])
                else:
                    res.append(None)
            return res, ep
        except Exception:
            continue
    # curl fallback
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout),
                        "https://bsc-dataseed.binance.org/",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps(payload)],
                       capture_output=True, timeout=timeout + 5)
    resp = json.loads(r.stdout.decode())
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        else:
            res.append(None)
    return res, "direct-curl-bsc-dataseed"

TARGETS = {
    "DRAGON": "0xfc191b76041498b14dcae3c802af3389c74263e6",
    "XCOPY": "0x3fbec44c7c845374267b06033940abe45c63edfa",
}
out = {"run": "free-mint-search 2026-11-17 02:31 WIB follow-up verification"}

for name, addr in TARGETS.items():
    # Sourcify ABI shape
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
        meta = json.loads(raw.decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        raw_abi = json.dumps(abi)
        shape = {
            "verified": True, "verifiedAt": meta.get("verifiedAt"),
            "n_fns": len(names),
            "has_mint": any(n.lower().startswith("mint") for n in names),
            "mint_fns": sorted(n for n in names if n.lower().startswith("mint")),
            "has_quote": bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"}),
            "free_views": sorted(names & {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
                                          "freeUsed", "freeAvailable", "freeSharePoolExhausted",
                                          "freeSharesClaimed", "freeMinted", "freeCardsRemaining",
                                          "freeSold", "freeSupply", "FREE_SUPPLY", "FREE_CAP"}),
            "agent_ref": bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"}),
            "registry_addr_in_abi": REGISTRY[2:].lower() in raw_abi.lower(),
            "registry_in_abi": "60B9262456dE011F7d15a54CdD8c48bAaa8B022F" in raw_abi,
            "is_token": bool(names & {"name", "symbol", "decimals", "totalSupply"}),
            "all_fns": sorted(names),
        }
    except Exception as e:
        shape = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}
    out[name] = {"address": addr, "shape": shape}

# Fresh batch reads for both
VIEWS = [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
         ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
         ("freeSold", "freeSold()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
         ("FREE_CAP", "FREE_CAP()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
         ("mintOpen", "mintOpen()", None), ("owner", "owner()", None),
         ("balanceOf_user", "balanceOf(address)", "user"),
         ("mintedBy_user", "mintedBy(address)", "user"),
         ("freeUsed_user", "freeUsed(address)", "user"),
         ("freeClaimed_user", "freeClaimed(address)", "user"),
         ("quote_user_1", "quote(address,uint256)", "u1"),
         ("cost_user_1", "cost(address,uint256)", "u1")]
calls, meta = [], []
for name, addr in TARGETS.items():
    for label, sig, arg in VIEWS:
        calls.append(call(addr, sig, arg))
        meta.append((name, addr, label))
try:
    res, ep = batch_read(calls)
    out["reads_endpoint"] = ep
    for (name, addr, label), val in zip(meta, res):
        out.setdefault(name, {}).setdefault("reads", {})[label] = val
    # block number
    try:
        payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode()
        req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            out["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
    except Exception as e:
        out["block_error"] = str(e)[:120]
except Exception as e:
    out["reads_error"] = f"{type(e).__name__}: {str(e)[:300]}"

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-17-0231-verify-new.json", "w"), indent=1)
print(json.dumps(out, indent=1))
