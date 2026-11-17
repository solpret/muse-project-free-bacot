#!/usr/bin/env python3
"""Run 2101 triage: FMA (Boltbook new) + NEURA distributor (Boltbook new) + 5a shape-check
of 25 new Sourcify feed addresses. Read-only; writes run-2026-11-09-2101-triage.json."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
        "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return None if v in (None, "0x") else int(v, 16)
    except Exception: return None

def rpc(method, params, timeout=25):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for u in RPCS:
        try:
            req = urllib.request.Request(u, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None

def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    v = rpc("eth_call", [{"to": addr, "data": data}, "latest"])
    return to_int(v)

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.load(r)
        return d.get("abi"), d.get("verifiedAt") or d.get("creationMatch")
    except Exception as e:
        return {"_error": str(e)}, None

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "FREE_SLOTS", "FREE_SUPPLY", "freeClaimCount", "freeMintsLeft"]

def shape(addr):
    abi, verified_at = fetch_abi(addr)
    if not isinstance(abi, list):
        return {"address": addr, "error": str(abi), "verifiedAt": verified_at}
    fns = {}
    for f in abi:
        if f.get("type") == "function":
            fns.setdefault(f.get("name"), []).append(f)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or n in ("cost", "price", "getPrice", "mintPrice") for n in names)
    free = [n for n in FREE_VIEWS if n in names]
    src = json.dumps(abi).lower()
    agent = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agentid" in src
             or "agentgate" in src or "agentregistry" in src or "registry" in names)
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and ("mintFree" in names or "mintfree" in [n.lower() for n in names]) and bool(free) and agent
    return {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
            "mint": has_mint, "quote": has_quote, "free": free, "agent": agent,
            "token": tokenish, "fns": sorted(names)}

out = {"run": "2026-11-09-2101", "block": None}
blk = rpc("eth_blockNumber", [])
out["block"] = int(blk, 16) if blk else None
print("BLOCK", out["block"], flush=True)

# --- FMA ---
FMA = "0xA45CA208d015C81Bf2f5e606437e4f9d1D8C2FE8"
fma = shape(FMA)
fma_views = {}
for sig in ["mintCount()", "MAX_MINTS()", "totalSupply()", "decimals()", "name()", "symbol()"]:
    fma_views[sig] = call(FMA, sig)
for sig in ["freeClaimed(address)", "hasMinted(address)", "minted(address)", "claimed(address)",
            "freeMinted(address)", "balanceOf(address)"]:
    fma_views[sig + "_user"] = call(FMA, sig, USER)
# quote/cost variants (no-arg and (address,uint256))
for sig in ["quote(address,uint256)", "cost(uint256)", "mintPrice()", "price()"]:
    try:
        if "(address" in sig:
            d = sel(sig) + enc(USER) + "1".rjust(64, "0")
            v = rpc("eth_call", [{"to": FMA, "data": d}, "latest"])
            fma_views[sig + "_user1"] = to_int(v)
        else:
            fma_views[sig] = call(FMA, sig)
    except Exception as e:
        fma_views[sig] = f"ERR {e}"
# registry-ish views
for sig in ["agentRegistry()", "registry()", "AGENT_ID()", "agentId()"]:
    fma_views[sig] = call(FMA, sig)
out["FMA"] = {"shape": fma, "views": fma_views}
print("FMA shape S1", fma.get("S1"), "S2", fma.get("S2"), "views", fma_views, flush=True)

# --- NEURA distributor + token ---
NEU_DIST = "0xf027b84d8b1ae4025fbda156e843b2773b953dfc"
NEU = "0x77da87aEebe07448e896bB5e41da74b451C1e665"
nd = shape(NEU_DIST)
nd_views = {}
for sig in ["freeClaimCount()", "totalClaims()", "claimCount()", "MAX_CLAIMS()", "token()",
            "paused()", "claimOpen()", "isOpen()"]:
    nd_views[sig] = call(NEU_DIST, sig)
for sig in ["claimed(address)", "hasClaimed(address)", "freeClaimed(address)", "claimFree()"]:
    if sig == "claimFree()":
        continue
    nd_views[sig + "_user"] = call(NEU_DIST, sig, USER)
for sig in ["agentRegistry()", "registry()", "AGENT_ID()", "agentId()"]:
    nd_views[sig] = call(NEU_DIST, sig)
nt = shape(NEU)
nt_views = {"totalSupply()": call(NEU, "totalSupply()"),
            "decimals()": call(NEU, "decimals()"),
            "balanceOf_user": call(NEU, "balanceOf(address)", USER)}
out["NEURA"] = {"distributor_shape": nd, "distributor_views": nd_views,
                "token_shape": nt, "token_views": nt_views}
print("NEURA dist S1", nd.get("S1"), "S2", nd.get("S2"), "views", nd_views, flush=True)
print("NEU token views", nt_views, "fns", nt.get("fns"), flush=True)


with open(f"{BASE}/run-2026-11-09-2101-triage.json", "w") as f:
    json.dump(out, f, indent=1)
print("TRIAGE DONE", flush=True)
