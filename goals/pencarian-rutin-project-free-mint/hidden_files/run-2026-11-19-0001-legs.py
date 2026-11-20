#!/usr/bin/env python3
"""Legs 5a + bridge for run 2026-11-19 00:01 WIB (small, fast, short timeouts).
Resume script died during shape-check (egress/RPC degraded). This script:
Sourcify feed (12s timeout), shape-check new addresses (ABI names only;
registry-bytes eth_getCode attempted once with 12s timeout, failure = unchecked),
bridge read-only. Writes run-2026-11-19-0001-legs.json. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
T0 = time.time()
out = {"run": "free-mint-search 2026-11-19 00:01 WIB legs 5a+bridge"}
def https_get(host, path, timeout=12):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    return status, raw
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    out["sourcify_feed"] = {"http": status, "total": len(addrs), "addresses": addrs,
        "verifiedAt_top": (items[0].get("verifiedAt") if items and isinstance(items[0], dict) else None)}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
try:
    hl_seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    hl_l = {k.lower() for k in hl_seen}
    snap0 = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_l = {str(v.get("address","")).lower() for v in snap0.get("contracts", {}).values() if isinstance(v, dict)}
    targets = [a for a in out.get("sourcify_feed", {}).get("addresses", []) if a.lower() not in hl_l and a.lower() not in snap_l]
    FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
                  "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
    def shape_check(addr):
        try:
            st2, raw2 = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=12)
            meta2 = json.loads(raw2.decode()); abi = meta2.get("abi", [])
            fns = {}
            for e in abi:
                if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
            names = set(fns)
            has_mint = any(n.lower().startswith("mint") for n in names)
            has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
            free_views = sorted(names & FREE_VIEWS)
            agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
            registry_bytes = None
            if not agent_ref:
                try:
                    entry = dynamic_credential_entry("custom.quicknode")
                    surrogate = str(entry["surrogate"]).strip()
                    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=12)
                    try:
                        conn.request("POST", f"/{surrogate}/", body=json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}]).encode(), headers={"Content-Type":"application/json"})
                        resp = conn.getresponse(); raw3 = resp.read()
                    finally:
                        conn.close()
                    code = json.loads(raw3.decode())[0].get("result","")
                    if "60b9262456de011f7d15a54cdd8c48baa8b022f" in str(code).lower():
                        agent_ref = True; registry_bytes = True
                    else:
                        registry_bytes = False
                except Exception as e:
                    registry_bytes = f"unchecked:{type(e).__name__}"
            is_token = bool(names & {"name","symbol","decimals","totalSupply"})
            s1 = has_mint and has_quote and bool(free_views) and agent_ref
            mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
            s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
            return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                    "free_views": free_views, "agent_ref": agent_ref, "registry_bytes": registry_bytes,
                    "is_token": is_token, "n_fns": len(names), "status": "checked", "verifiedAt": meta2.get("verifiedAt")}
        except Exception as e:
            return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}
    sc = [shape_check(a) for a in targets]
    out["shape_check_new"] = sc
    out["shape_check_sale_shape"] = [x for x in sc if x.get("S1") or x.get("S2")]
    out["shape_check_targets"] = targets
except Exception as e:
    out["shape_check_new"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
try:
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        a = v.get("address")
        if a: snap_addrs.add(a.lower())
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    baddrs = list(bridge.get("contracts", {}).keys())
    not_in = [a for a in baddrs if a.lower() not in snap_addrs]
    disc = [a for a, c in bridge.get("contracts", {}).items() if c.get("same_owner_discarded")]
    out["bridge"] = {"total": len(baddrs), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in, "same_owner_discarded": len(disc)}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-19-0001-legs.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:3000])
