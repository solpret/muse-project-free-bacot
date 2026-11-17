#!/usr/bin/env python3
"""Triage run 2026-11-11 20:49 WIB: curl-retry failed ABI fetches from legs,
triage early-shape 0x2A3dFcBf..., diff reread vs snapshot for changes.
Read-only except run-2026-11-11-2049-triage.json."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-2049"
T0 = time.time()
out = {"started_wib": "2026-11-11 20:49 WIB"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def curl(url, timeout=30):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

def shape(addr):
    try:
        meta = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names), "fn_names": sorted(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

legs = json.load(open(BASE + "run-2026-11-11-2049-legs.json"))
failed = [s["address"] for s in legs["feed_shape"]["shapes"] if "error" in s]
print("RETRY", len(failed), failed, flush=True)
with ThreadPoolExecutor(max_workers=7) as ex:
    retried = list(ex.map(shape, failed))
out["retry_shapes"] = retried
for s in retried:
    print("RETRY", s.get("address"), "S1", s.get("S1"), "S2", s.get("S2"),
          "early", s.get("early_shape"), "fns", s.get("fn_count"), "err", s.get("error"), flush=True)

# --- triage early-shape 0x2A3dFcBf ---
EARLY = "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"
try:
    meta = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{EARLY}?fields=abi,metadata"))
    abi = meta.get("abi", [])
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = sorted(fns)
    out["early_abi"] = {"fn_count": len(names), "names": names,
                        "metadata_sources": (meta.get("metadata") or {}).get("sources", {}) if isinstance(meta.get("metadata"), dict) else None}
    print("EARLY ABI fns:", len(names), flush=True)
    print("EARLY names:", names, flush=True)
except Exception as ex:
    out["early_abi"] = {"error": f"{type(ex).__name__}: {str(ex)[:150]}"}
    print("EARLY ABI FAIL", ex, flush=True)

# on-chain reads for the early candidate
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def eth_call(to, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": to, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if "result" in res:
                return res["result"]
        except Exception:
            continue
    return None
def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None
def dec_str(v):
    try:
        if not v or v == "0x": return None
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception:
        return None

ec = {}
ec["name"] = dec_str(eth_call(EARLY, sel("name()")))
ec["symbol"] = dec_str(eth_call(EARLY, sel("symbol()")))
ec["decimals"] = to_int(eth_call(EARLY, sel("decimals()")))
ec["totalSupply"] = to_int(eth_call(EARLY, sel("totalSupply()")))
ec["freeLeft"] = to_int(eth_call(EARLY, sel("freeLeft()")))
ec["freeClaimed"] = to_int(eth_call(EARLY, sel("freeClaimed()")))
ec["freeMinted"] = to_int(eth_call(EARLY, sel("freeMinted()")))
ec["totalMinted"] = to_int(eth_call(EARLY, sel("totalMinted()")))
ec["code"] = None
try:
    r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", EPS[0],
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                          "params": [EARLY, "latest"]})],
                       capture_output=True, text=True, timeout=30)
    ec["code_len"] = len(json.loads(r.stdout).get("result", "") or "")
except Exception as e:
    ec["code_len"] = f"err {e}"
out["early_chain"] = ec
print("EARLY CHAIN:", ec, flush=True)

# --- diff reread vs snapshot ---
snap = json.load(open(BASE + "onchain-snapshot.json"))
rr = json.load(open(BASE + "run-2026-11-11-2049-reread.json"))
out["block"] = rr.get("block")
changes = []
contracts = snap.get("contracts", {})
for name, d in rr.get("reread", {}).items():
    prev = contracts.get(name, {}) if isinstance(contracts.get(name), dict) else {}
    if not isinstance(prev, dict):
        continue
    for key in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "balanceOf_user", "freeClaimed_user"):
        pv, nv = prev.get(key), d.get(key)
        if isinstance(pv, (int, float)) and isinstance(nv, (int, float)) and pv != nv:
            changes.append({"kind": "contract", "name": name, "field": key, "old": pv, "new": nv,
                            "status": prev.get("status")})
tc = snap.get("track_c", {})
for name, d in rr.get("track_c", {}).items():
    prev = tc.get(name, {}) if isinstance(tc.get(name), dict) else {}
    if not isinstance(prev, dict):
        continue
    for key in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        pv, nv = prev.get(key), d.get(key)
        if isinstance(pv, (int, float)) and isinstance(nv, (int, float)) and pv != nv:
            changes.append({"kind": "track_c", "name": name, "field": key, "old": pv, "new": nv,
                            "status": prev.get("status")})
out["changes"] = changes
print(f"CHANGES {len(changes)}", flush=True)
for c in changes:
    print("CHANGE", c, flush=True)

# key watch items quick state
for name in ("Stampooor Stamp Packs", "AgentPals", "Kitebots", "REWINDCLUB", "LCDSPRITE", "RIMEVAULT", "MYCELIX", "SOLDERCATS", "ORBITJANITOR"):
    print("WATCH", name, rr.get("reread", {}).get(name), "snap_status", (contracts.get(name) or {}).get("status"), flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "run-2026-11-11-2049-triage.json", "w"), indent=1)
print("TRIAGE DONE in", out["elapsed_s"], "s", flush=True)
