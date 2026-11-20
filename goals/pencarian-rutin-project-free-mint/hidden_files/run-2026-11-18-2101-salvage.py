#!/usr/bin/env python3
"""Salvage for free-mint-search run 2026-11-18 21:01 WIB.
Main driver was SIGTERM-killed by a service restart at ~802s, after leg 4
reread + Boltbook ZH but before Sourcify feed/shape-check + bridge.
This script completes: (5a) Sourcify feed + shape-check, (2b) on-chain
verification of the one new Boltbook-ZH address 0x8d031126123baf88b4017a19f5d5254f61585efa.
Read-only. Writes run-2026-11-18-2101-feed.json and
run-2026-11-18-2101-boltbook-new.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPC_URL = "https://bsc-dataseed.binance.org/"
T0 = time.time()

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

def curl_json(url, payload, timeout=25):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())

def sel(sig):
    return keccak(sig.encode())[:4].hex()

out = {"run": "free-mint-search 2026-11-18 21:01 WIB salvage", "started": "21:01 WIB"}

# ---- 5a: Sourcify feed ----
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    out["sourcify_feed"] = {"http": status, "total": len(addrs), "addresses": addrs,
        "verifiedAt_top": (items[0].get("verifiedAt") if items and isinstance(items[0], dict) else None)}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape_check(addr):
    try:
        st2, raw2 = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        meta2 = json.loads(raw2.decode()); abi = meta2.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        registry_bytes = False
        if not agent_ref:
            try:
                code_resp = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}])
                code = code_resp[0].get("result", "") if isinstance(code_resp, list) else ""
                if "60b9262456de011f7d15a54cdd8c48baa8b022f" in str(code).lower():
                    agent_ref = True; registry_bytes = True
            except Exception:
                pass
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "registry_bytes": registry_bytes,
                "is_token": is_token, "n_fns": len(names), "status": "checked",
                "verifiedAt": meta2.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}

try:
    hl_seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    hl_l = {k.lower() for k in hl_seen}
    snap0 = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_l = {str(v.get("address","")).lower() for v in snap0.get("contracts", {}).values() if isinstance(v, dict)}
    pending_boltbook = ["0xd0bc754349b9f50580d567f7bd112cf0074cfb83"]
    targets = [a for a in out.get("sourcify_feed", {}).get("addresses", []) if a.lower() not in hl_l and a.lower() not in snap_l]
    targets += [a for a in pending_boltbook if a.lower() not in hl_l and a.lower() not in snap_l]
    out["shape_targets"] = targets
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        sc = list(ex.map(shape_check, targets))
    out["shape_check_new"] = sc
    out["shape_check_sale_shape"] = [x for x in sc if x.get("S1") or x.get("S2")]
except Exception as e:
    out["shape_check_new"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- 2b: verify new Boltbook-ZH address ----
NEW = "0x8d031126123baf88b4017a19f5d5254f61585efa"
new_out = {"address": NEW, "source": "boltbook.fun ZH front page 21:01 run (only ZH fetched; EN failed)"}
try:
    sc = shape_check(NEW)
    new_out["shape"] = sc
except Exception as e:
    new_out["shape"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
# on-chain state views via Quicknode batch
def enc0(sig):
    return "0x" + sel(sig)
try:
    calls = [(NEW, enc0(s)) for s in ("totalSupply()","totalMinted()","freeMinted()","freeClaimed()","freeLeft()","mintOpen()","name()","symbol()")]
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]} for i, (to, data) in enumerate(calls)]
    resp = curl_json(RPC_URL, payload, timeout=25)
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    views = {}
    for i, s in enumerate(("totalSupply()","totalMinted()","freeMinted()","freeClaimed()","freeLeft()","mintOpen()","name()","symbol()")):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            raw = it["result"]
            if s in ("name()","symbol()"):
                views[s] = raw  # raw hex, decode opportunistically below
            else:
                try: views[s] = int(raw, 16)
                except Exception: views[s] = raw
        elif "error" in it:
            views[s] = f"err:{it['error']}"
        else:
            views[s] = None
    new_out["views"] = views
    # decode name/symbol strings
    for s in ("name()","symbol()"):
        v = views.get(s)
        if isinstance(v, str) and v.startswith("0x") and len(v) > 130:
            try:
                ln = int(v[66:130], 16)
                new_out[s] = bytes.fromhex(v[130:130 + ln * 2]).decode("utf-8", errors="replace")
            except Exception:
                pass
    # registry bytes in deployed code
    code_resp = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [NEW, "latest"]}])
    code = code_resp[0].get("result", "") if isinstance(code_resp, list) else ""
    new_out["code_len"] = len(code)
    new_out["registry_bytes"] = "60b9262456de011f7d15a54cdd8c48baa8b022f" in str(code).lower()
    new_out["is_contract"] = len(code) > 2
except Exception as e:
    new_out["views_error"] = f"{type(e).__name__}: {str(e)[:200]}"

out["boltbook_new"] = new_out
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-18-2101-feed.json", "w"), indent=1)
json.dump(new_out, open(f"{HF}/run-2026-11-18-2101-boltbook-new.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("sourcify_feed","shape_check_sale_shape","boltbook_new")}, indent=1, default=str)[:3500])
print("elapsed", out["elapsed_s"])
