#!/usr/bin/env python3
"""Salvage for run 2026-11-19 11:31 WIB: main script (run-2026-11-19-1131.py)
completed leg-4 re-read (15/15, 0 errors, block 134352903) + Boltbook EN/ZH
files, then was killed by the 420s timeout during Sourcify/shape legs.
This salvage does: Sourcify feed + shape-check new feed addrs, triage of
(sweep find), bridge read, real Ankr pre-flight. Read-only except this run's
own JSON output. No preview/mint/claim."""
import json, re, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
T0 = time.time()
out = {"run": "free-mint-search 2026-11-19 11:31 WIB (salvage)"}

def https_get(host, path, timeout=20, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301, 302, 303, 307, 308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects - 1)
        return https_get(host, loc, timeout, redirects - 1)
    return status, raw

# ---- Sourcify feed ----
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    out["sourcify_feed"] = {"http": status, "total": len(addrs), "addresses": addrs,
        "verifiedAt_top": (items[0].get("verifiedAt") if items and isinstance(items[0], dict) else None)}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- shape-check: new feed addrs + Boltbook-new + YAMA sale ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeCardsRemaining"}
def shape_check(addr):
    try:
        st2, raw2 = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        meta2 = json.loads(raw2.decode()); abi = meta2.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "agentIDRegistry", "holdsAgentID", "setAgentIDRegistry", "holdsAgentId"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked", "verifiedAt": meta2.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}

try:
    hl_seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    hl_l = {k.lower() for k in hl_seen}
    snap0 = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_l = {str(v.get("address", "")).lower() for v in snap0.get("contracts", {}).values() if isinstance(v, dict)}
    targets = [a for a in out.get("sourcify_feed", {}).get("addresses", [])
               if a.lower() not in hl_l and a.lower() not in snap_l]
    # Boltbook-new 1131: addresses on front page EN/ZH not in snapshot/track_c/hot-leg-seen
    _bb = json.load(open(f"{HF}/run-2026-11-19-1131.json"))
    _bbaddrs = set()
    for _k in ("boltbook_en", "boltbook_zh"):
        for _a in _bb.get(_k, {}).get("addresses", []):
            _bbaddrs.add(_a.lower())
    _tc = snap0.get("track_c", {}) or {}
    _tcaddrs = set()
    for _v in _tc.values():
        if isinstance(_v, dict):
            for _f in ("address", "sale", "token"):
                if isinstance(_v.get(_f), str) and _v[_f].startswith("0x"):
                    _tcaddrs.add(_v[_f].lower())
    extra = [a for a in sorted(_bbaddrs) if a not in hl_l and a not in snap_l and a not in _tcaddrs]
    extra.append("0x86D779fc4d83044cCECCb53639f9a98E367D6E46")  # YAMA sale re-check (shape record)
    out["boltbook_new_dynamic"] = extra
    for a in extra:
        if a.lower() not in snap_l and a not in targets:
            targets.append(a)
    out["shape_targets"] = targets
    out["shape_check_new"] = [shape_check(a) for a in targets]
    out["shape_check_sale_shape"] = [x for x in out["shape_check_new"] if x.get("S1") or x.get("S2")]
except Exception as e:
    out["shape_check_new"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- Bridge (read-only) ----
try:
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    baddrs = list(bridge.get("contracts", {}).keys())
    not_in = [a for a in baddrs if a.lower() not in snap_addrs]
    disc = [a for a, c in bridge.get("contracts", {}).items() if c.get("same_owner_discarded")]
    out["bridge"] = {"total": len(baddrs), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in, "same_owner_discarded": len(disc)}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- Ankr pre-flight (real, small) ----
try:
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=40)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(
            [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode(),
            headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read()
    finally:
        conn.close()
    head = int(json.loads(raw.decode())[0]["result"], 16)
    from ankr import ankr_post as _ankr_post2
    pf = _ankr_post2("ankr_getLogs", {"blockchain": "bsc", "fromBlock": head - 50, "toBlock": head,
        "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                   "0x0000000000000000000000000000000000000000000000000000000000000000"]}, timeout=45)
    out["preflight"] = {"ok": True, "head": head, "logs_returned": len(pf.get("logs", [])) if isinstance(pf, dict) else "n/a"}
    out["scan_leg"] = "PRE-FLIGHT OK - chain-wide scan NOT launched this run (run already at 420s budget; gap handled by backfill driver; watermark NOT advanced)"
except Exception as e:
    out["preflight"] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:150]}"}
    out["scan_leg"] = "FAST-FAIL (pre-flight failed); watermark NOT advanced"

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only)"
json.dump(out, open(f"{HF}/run-2026-11-19-1131-salvage.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:5000])
