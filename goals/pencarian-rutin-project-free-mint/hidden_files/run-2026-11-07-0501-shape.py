#!/usr/bin/env python3
"""Route 5a Sourcify shape-check, run 2026-11-07 05:01 WIB. Read-only.
Feed = list endpoint (no fields param — ?fields=abi is invalid there, HTTP 400).
Per-contract ABI via /v2/contract/56/{addr}?fields=abi, urllib first, curl retry.
S1: mint fn + quote/cost fn (exact-name convention: quote/cost/getCost/price/mintPrice/feeFor
    or startswith quote/cost; sharePrice/PRICE alone does NOT count as quote per job convention)
    + free-share view + registry ref/AgentGate.
S2: contract IS the token + no-arg free-mint fn + free views + registry ref/AgentGate.
Agent-mint (NFT) shape: mint fn + free-mint fn/free-supply view + registry ref/AgentGate.
Skips addresses already in hot-leg-seen / snapshot / scan-seen (dedupe, case-insensitive)."""
import json, subprocess, time, urllib.request, urllib.error

FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount", "freeclaim",
                    "freemint", "freesupply", "freecap"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"

def sourcify_abi(address, tries=3):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    # curl retry
    for i in range(3):
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "60", url],
                               capture_output=True, text=True, timeout=70)
            data = json.loads(r.stdout)
            if "abi" in data:
                return ("verified", data.get("abi"))
            if data.get("customCode"):
                return ("error:" + str(data.get("customCode")), None)
        except Exception:
            time.sleep(3)
    return ("error:retry-exhausted", None)

def classify(abi):
    funcs = []
    names_all = []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") == "function":
                funcs.append(item.get("name", ""))
            names_all.append(item.get("name", ""))
    low = [f.lower() for f in funcs]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree")]
    free_mint_fns = [f for f in funcs if "free" in f.lower() and "mint" in f.lower()]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    agent_mint = bool(mint_fns) and bool(gate) and bool(free_views or free_mint_fns)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "free_mint_fns": free_mint_fns, "S1": s1, "S2": s2, "agent_mint_shape": agent_mint}

def load_keys(path):
    try:
        d = json.load(open(path))
        if isinstance(d, dict):
            return {k.lower() for k in d.keys()}
        return set()
    except Exception:
        return set()

def main():
    feed = json.load(open("run-2026-11-07-0501-sourcify-feed.json"))
    addrs = [(it["address"], it.get("verifiedAt")) for it in feed.get("results", [])]
    hl_keys = load_keys("hot-leg-seen.json")
    seen_keys = load_keys("onchain-scan-seen.json")
    snap = json.load(open("onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        if isinstance(v, dict):
            snap_addrs.add(str(v.get("address", "")).lower())
    tc = snap.get("track_c", {})
    for v in tc.values():
        if isinstance(v, dict):
            snap_addrs.add(str(v.get("sale", "")).lower())
            snap_addrs.add(str(v.get("token", "")).lower())
    snap_addrs.discard("")
    out = []
    for addr, vat in addrs:
        r = {"address": addr, "verifiedAt": vat}
        a = addr.lower()
        if a in hl_keys:
            r["skip"] = "hot-leg-seen"
        elif a in snap_addrs:
            r["skip"] = "in-snapshot"
        elif a in seen_keys:
            r["skip"] = "scan-seen"
        else:
            status, abi = sourcify_abi(addr)
            r["sourcify"] = status
            if abi is not None:
                r.update(classify(abi))
            else:
                r["S1"] = False; r["S2"] = False; r["agent_mint_shape"] = False
        out.append(r)
        print(addr, vat, r.get("skip") or r.get("sourcify"),
              "S1=" + str(r.get("S1")), "S2=" + str(r.get("S2")), "AGENT=" + str(r.get("agent_mint_shape")),
              "fns=" + str(r.get("functions", "-")), "mint=" + str(r.get("mint_fns", [])),
              "quote=" + str(r.get("quote_fns", [])), "free=" + str(r.get("free_views", [])),
              "gate=" + str(r.get("gate_fns", [])))
    json.dump(out, open("run-2026-11-07-0501-sourcify-shape.json", "w"), indent=1)
    print("WROTE run-2026-11-07-0501-sourcify-shape.json")

main()
