#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 15:44 WIB. Read-only except own hot-leg state files.
Adapted from hot-leg-2026-11-19-1459-run.py (feed+Boltbook+bridge) and
hot-leg-run-2026-11-19-1509-reread.py (Quicknode batch re-read). Prev full
reread = 1509 (flat structure). Never writes the main snapshot."""
import json, urllib.request, concurrent.futures, re, sys, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from fast_rpc import _single
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-19-1544"
NOW = "2026-11-19T15:44:38+07:00"
START = time.time()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-19 15:44 WIB", "started_wib": NOW}

def sel(sig):
    k = keccak(sig.encode()); return k[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_uint(n): return "%064x" % n

# ---- (1) Sourcify feed (pre-fetched /tmp/sourcify-feed.json, 200) ----
seen = json.load(open(BASE+"hot-leg-seen.json"))
try:
    feed = json.load(open("/tmp/sourcify-feed.json"))
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    addrs, vers = [], []
    for e in results:
        if isinstance(e, str): a, v = e, None
        else:
            a = e.get("address") or (e.get("contract") or {}).get("address")
            v = e.get("verifiedAt") or (e.get("contract") or {}).get("verifiedAt")
        if a: addrs.append(a); vers.append(v)
    out["sourcify_feed"] = {"total": len(addrs), "top": addrs[0] if addrs else None,
        "top_verifiedAt": vers[0] if vers else None, "all": addrs,
        "fetch": "pre-fetched /tmp/sourcify-feed.json (200, ~15:45 WIB)"}
except Exception as ex:
    addrs, vers = [], []
    out["sourcify_feed"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
seen_lower = {k.lower() for k in seen}
new = [a for a in addrs if a.lower() not in seen_lower
       and a not in EXCLUDED and a.lower() != REGISTRY]
out["sourcify_feed"]["new"] = len(new); out["sourcify_feed"]["new_contracts"] = new

def shape(addr):
    try:
        _o = subprocess.run(["curl","-sL","--max-time","20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True).stdout
        meta = json.loads(_o)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "is_nft": bool(names & {"ownerOf","tokenURI"}),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
                "verifiedAt": next((v for a,v in zip(addrs,vers) if a==addr), None)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
if new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape, new))
json.dump(shapes, open(BASE+f"hot-leg-run-{RUN}-sourcify-shape.json","w"), indent=1)
out["shape"] = shapes
out["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]
for s in shapes:
    a = s["address"]
    if s.get("error") or not s.get("n_fns"):
        continue
    if (s.get("S1") or s.get("S2")) and s.get("is_nft"):
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-track-c",
                   "note": "S1/S2 pass BUT ERC-721 NFT, not a fungible share sale; NFT early-lead stays with main job; never reported/previewed/minted."}
    elif s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "sale-shape-pass", "note": f"S1={s.get('S1')} S2={s.get('S2')} fns free={s.get('free_views')} agent={s.get('agent_ref')}"}
    else:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape",
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
out["seen_n"] = len(seen)

# ---- (2) Boltbook EN + ZH (pre-fetched /tmp/bb-en.html, /tmp/bb-zh.html, both 200) ----
out["boltbook"] = {}
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']
bb_new_all = []
for lang in ("en","zh"):
    try:
        html = open(f"/tmp/bb-{lang}.html").read()
        open(BASE+f"hot-leg-2026-11-19-1544-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen_lower = {k.lower() for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        out["boltbook"][lang] = {"bytes": len(html), "http_code": "200",
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW)}
        bb_new_all.extend(newfound)
        for a in newfound:
            s = shape(a)
            if s.get("error") or not s.get("n_fns"):
                # Sourcify 404 / unreadable: record shape-check-failed, not a lead
                seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                           "status": "shape-check-failed",
                           "note": f"Sourcify ABI unreadable ({s.get('error','no fns')}); shape-check impossible, not a lead."}
                continue
            seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                "status": "checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                         else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
    except Exception as ex:
        out["boltbook"][lang] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["seen_n_after_boltbook"] = len(seen)
out["boltbook_new_all"] = bb_new_all

# ---- bridge (read-only) ----
try:
    b = json.load(open(BASE+"scan-bridge.json"))
    bc = b.get("contracts", {})
    snap = json.load(open(BASE+"onchain-snapshot.json"))
    snap_addrs = set()
    for coll in ("contracts","track_c"):
        for v in snap.get(coll, {}).values():
            if isinstance(v, dict):
                for k in ("address","sale","token"):
                    val = v.get(k)
                    if isinstance(val, str): snap_addrs.add(val.lower())
    for v in snap.get("pending_claims", {}).values():
        if isinstance(v, dict):
            for k in ("mint","token"):
                val = v.get(k)
                if isinstance(val, str): snap_addrs.add(val.lower())
    not_in = [a for a in bc if isinstance(a, str) and a.lower() not in snap_addrs]
    discarded = [a for a,v in bc.items() if isinstance(v,dict) and v.get("same_owner_discarded")]
    out["bridge_scan"] = {"total": len(bc), "not_in_snapshot": len(not_in),
        "not_in_snapshot_list": not_in, "same_owner_discarded": len(discarded)}
except Exception as ex:
    out["bridge_scan"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "note": "bridge skip - run continues"}

# ---- (4) re-read via Quicknode batch (read-only) ----
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
def curl_json(payload, timeout=40):
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
def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user": data += enc_addr(USER)
    elif arg == "one": data += "%064x" % 1
    elif arg == "user1": data += enc_addr(USER) + "%064x" % 1
    return data
def rpc_batch(calls, timeout=40):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try: res.append(int(it["result"], 16))
            except Exception: res.append(it["result"])
        elif "error" in it: res.append(f"err:{str(it['error'])[:120]}")
        else: res.append(None)
    return res

PLAN = [
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply", "totalSupply()", None), ("freeLeft", "freeLeft()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted", "freeMinted()", None), ("FREE_TOTAL", "FREE_TOTAL()", None),
   ("freeTaken_user", "freeTaken(address)", "user")]),
 ("bsccat", "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
  [("freeMinted", "freeMinted()", None), ("totalSupply", "totalSupply()", None)]),
]
reread = {"run": "hot-leg 2026-11-19 15:44 WIB re-read", "started_wib": NOW}
try:
    blk = curl_json([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
    reread["block"] = int(blk[0]["result"], 16)
except Exception as e:
    reread["block"] = f"ERR {type(e).__name__}: {e}"
calls, labels = [], []
for name, addr, items in PLAN:
    for key, sig, arg in items:
        calls.append((addr, encode(sig, arg))); labels.append((name, key))
try:
    res = rpc_batch(calls, timeout=40)
except Exception as e:
    reread["error"] = f"{type(e).__name__}: {e}"
    res = [None] * len(calls)
for (name, key), v in zip(labels, res):
    reread.setdefault(name, {})[key] = v
# getCode for any new Boltbook addresses that are Sourcify-404 (shape-check-failed)
shape_failed = [a for a in bb_new_all if isinstance(seen.get(a), dict) and seen[a].get("status") == "shape-check-failed"]
if shape_failed:
    try:
        codes = curl_json([{"jsonrpc":"2.0","id":i+1,"method":"eth_getCode","params":[a,"latest"]} for i,a in enumerate(shape_failed)], timeout=40)
        reread["getCode"] = {a: (c.get("result","?")[:10] if isinstance(c,dict) else str(c)) for a,c in zip(shape_failed, codes)}
        reread["getCode_len"] = {a: (len(c.get("result","")) if isinstance(c,dict) and c.get("result") else 0) for a,c in zip(shape_failed, codes)}
    except Exception as e:
        reread["getCode"] = f"ERR {type(e).__name__}: {e}"
reread["elapsed_s"] = round(time.time() - START, 1)
json.dump(reread, open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_reread_file"] = f"hot-leg-run-{RUN}-reread.json"
out["leg4_block"] = reread.get("block")

# ---- change detection vs 1509 (flat structure) ----
try:
    prev = json.load(open(BASE+"hot-leg-run-2026-11-19-1509-reread.json"))
except Exception as ex:
    prev = {}
    out["leg4_prev_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
changes = {}
for k in ("STOCK AGENT","binanceai-mint","RigForge","AONE-sale","bsccat"):
    pv = prev.get(k, {}) if isinstance(prev.get(k), dict) else {}
    cv = reread.get(k, {})
    diff = {}
    for kk, vv in cv.items():
        if str(pv.get(kk)) != str(vv):
            diff[kk] = {"prev": pv.get(kk), "now": vv}
    changes[k] = diff
out["leg4_changes_vs_1509"] = changes

def pct(claimed, total):
    return round(100*claimed/total,1) if claimed is not None and total else None
st = reread.get("STOCK AGENT", {})
free_supply = st.get("FREE_SUPPLY") if isinstance(st.get("FREE_SUPPLY"), int) else None
free_left = st.get("freeLeft") if isinstance(st.get("freeLeft"), int) else None
stock_pct = pct(free_supply - free_left, free_supply) if free_supply is not None and free_left is not None else None
out["threshold_check"] = {
    "STOCKAGENT_free_pct": stock_pct,
    "STOCKAGENT": {"totalSupply": st.get("totalSupply"), "freeLeft": free_left,
        "FREE_SUPPLY": free_supply, "mintOpen": st.get("mintOpen"),
        "quote_user_1": st.get("quote_user_1"), "freeMintedByWallet_user": st.get("freeMintedByWallet_user"),
        "balanceOf_user": st.get("balanceOf_user")},
    "notes": "Strong-lead bar >70% + age <24h + slot open. STOCKAGENT age UNVERIFIED + website unverified (snapshot) - no promotion unless legs flip. binanceai-mint last verified 15:01 WIB (launched=0, failed=1, refund=1) - re-read for change only."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1)[:8000])
print("ELAPSED", out["elapsed_s"])
