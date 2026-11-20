#!/usr/bin/env python3
"""Hot-leg run 2026-11-20 06:14 WIB. Read-only except own hot-leg state files.
Adapted from hot-leg-run-2026-11-19-1544.py + 06:09 run pattern (flat reread).
Sourcify feed leg SKIPPED this run (503 x2, upstream reset) - retry next run.
Never writes the main snapshot."""
import json, re, sys, time, subprocess, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many
from eth_hash.auto import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0614"
NOW = "2026-11-20T06:14:38+07:00"
START = time.time()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-20 06:14 WIB", "started_wib": NOW}

def sel(sig):
    return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()

# ---- (1) Sourcify feed: SKIPPED (503 x2 upstream reset, verified via curl) ----
out["sourcify_feed"] = {"error": "HTTP 503 x2: upstream connect error / remote connection failure",
                        "fetch": "SKIPPED - retry next run"}
seen = json.load(open(BASE+"hot-leg-seen.json"))

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
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

# ---- (2) Boltbook EN + ZH (pre-fetched /tmp/bb-en.html, /tmp/bb-zh.html, both 200) ----
out["boltbook"] = {}
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']
bb_new_all = []
shapes_all = []
for lang in ("en","zh"):
    try:
        html = open(f"/tmp/bb-{lang}.html").read()
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen_lower = {k.lower() for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        bb = {"bytes": len(html), "http_code": "200",
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW)}
        bb_new_all.extend(newfound)
        shapes = []
        for a in newfound:
            s = shape(a)
            shapes.append(s)
            if s.get("error") or not s.get("n_fns"):
                seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                           "status": "shape-check-failed",
                           "note": f"Sourcify ABI unreadable ({s.get('error','no fns')}); shape-check impossible, not a lead."}
                continue
            seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                "status": "checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                         else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
        bb["shapes"] = shapes
        bb["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]
        shapes_all.extend(shapes)
        out["boltbook"][lang] = bb
    except Exception as ex:
        out["boltbook"][lang] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["seen_n_after_boltbook"] = len(seen)
out["boltbook_new_all"] = bb_new_all
out["shape_hits_all"] = [s["address"] for s in shapes_all if s.get("S1") or s.get("S2")]

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
        "not_in_snapshot_list": not_in, "same_owner_discarded": len(discarded),
        "note": "Noted for main 30-min job only, NOT a new lead."}
except Exception as ex:
    out["bridge_scan"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "note": "bridge skip - run continues"}

# ---- (4) re-read via batch_race -> call_many -> curl-batch fallback (read-only) ----
def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user": data += enc_addr(USER)
    elif arg == "one": data += "%064x" % 1
    elif arg == "user1": data += enc_addr(USER) + "%064x" % 1
    return data
PLAN = [
 ("STOCKAGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply", "totalSupply()", None), ("freeLeft", "freeLeft()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user"),
   ("mintedBy_user", "mintedBy(address)", "user")]),
 ("AUGENT", "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
  [("freeClaimed", "freeClaimed()", None),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("totalSupply", "totalSupply()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted", "freeMinted()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("totalSupply", "totalSupply()", None)]),
 ("bsccat-sale", "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
  [("freeMinted", "freeMinted()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None)]),
]
calls, labels = [], []
for name, addr, items in PLAN:
    for key, sig, arg in items:
        calls.append({"to": addr, "data": encode(sig, arg)}); labels.append((name, key))
reread = {"started_wib": NOW, "reads": {}, "method": None}
t0 = time.time()
res = None
try:
    res = batch_race(calls, timeout=10)
    reread["method"] = "batch_race"
except Exception as e:
    out["leg4_batch_race_error"] = f"{type(e).__name__}: {str(e)[:200]}"
    try:
        res = call_many(calls)
        reread["method"] = "call_many"
    except Exception as e2:
        out["leg4_call_many_error"] = f"{type(e2).__name__}: {str(e2)[:200]}"
        # curl-batch fallback (same as 06:09 run)
        try:
            payload = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call",
                        "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(calls)]
            _o = subprocess.run(["curl","-sL","--max-time","60","-X","POST",
                "https://bsc-dataseed.binance.org/",
                "-H","Content-Type: application/json","-d", json.dumps(payload)],
                capture_output=True, text=True).stdout
            resp = json.loads(_o)
            by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
            res = []
            for i in range(len(calls)):
                it = by_id.get(i+1, {})
                if "result" in it and it["result"] not in (None,"0x"):
                    try: res.append(int(it["result"],16))
                    except Exception: res.append(it["result"])
                elif "error" in it: res.append({"error": str(it["error"])[:120]})
                else: res.append(None)
            reread["method"] = "curl-batch-fallback"
        except Exception as e3:
            out["leg4_curl_error"] = f"{type(e3).__name__}: {str(e3)[:200]}"
            res = [None]*len(calls)
if res is not None and reread["method"] in ("batch_race","call_many"):
    # fast_rpc returns hex strings; normalize to ints like curl path
    norm = []
    for v in res:
        if isinstance(v, str) and v.startswith("0x"):
            try: norm.append(int(v,16))
            except Exception: norm.append(v)
        else: norm.append(v)
    res = norm
reread["leg4_batch_s"] = round(time.time()-t0, 1)
try:
    blk = subprocess.run(["curl","-sL","--max-time","20","-X","POST",
        "https://bsc-dataseed.binance.org/","-H","Content-Type: application/json",
        "-d",'{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'],
        capture_output=True, text=True).stdout
    reread["block"] = int(json.loads(blk)["result"], 16)
except Exception as e:
    reread["block"] = f"ERR {type(e).__name__}: {str(e)[:120]}"
for (name, key), v in zip(labels, res if res else [None]*len(labels)):
    reread["reads"].setdefault(name, {"address": dict(PLAN)[name] if False else None, "views": {}})
    reread["reads"][name]["views"][key] = v
for name, addr, _ in PLAN:
    reread["reads"][name]["address"] = addr
json.dump(reread, open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_method"] = reread["method"]
out["leg4_batch_s"] = reread["leg4_batch_s"]
out["leg4_block"] = reread.get("block")
out["leg4_items"] = list(reread["reads"].keys())

# ---- change detection vs 06:09 reread ----
try:
    prev = json.load(open(BASE+"hot-leg-run-2026-11-20-0609-reread.json"))
    prev_reads = prev.get("reads", {})
except Exception as ex:
    prev_reads = {}
    out["leg4_prev_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
changes = {}
for name in reread["reads"]:
    pv = prev_reads.get(name, {}).get("views", {}) if isinstance(prev_reads.get(name), dict) else {}
    cv = reread["reads"][name]["views"]
    diff = {}
    for kk, vv in cv.items():
        if str(pv.get(kk)) != str(vv):
            diff[kk] = {"prev": pv.get(kk), "now": vv}
    changes[name] = diff
out["leg4_changes_vs_0609_reread"] = changes

def pct(claimed, total):
    return round(100*claimed/total,1) if isinstance(claimed,int) and isinstance(total,int) and total else None
st = reread["reads"].get("STOCKAGENT", {}).get("views", {})
lu = reread["reads"].get("Lumenhold", {}).get("views", {})
bn = reread["reads"].get("binanceai-mint", {}).get("views", {})
stock_pct = pct(st.get("FREE_SUPPLY")-st.get("freeLeft"), st.get("FREE_SUPPLY")) if isinstance(st.get("FREE_SUPPLY"),int) and isinstance(st.get("freeLeft"),int) else None
lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY")) if isinstance(lu.get("freeClaimed"),int) and isinstance(lu.get("FREE_SUPPLY"),int) else None
out["threshold_check"] = {
    "STOCKAGENT_free_pct": stock_pct,
    "STOCKAGENT": {"totalSupply": st.get("totalSupply"), "freeLeft": st.get("freeLeft"),
        "FREE_SUPPLY": st.get("FREE_SUPPLY"), "mintOpen": st.get("mintOpen"),
        "quote_user_1": st.get("quote_user_1"), "freeMintedByWallet_user": st.get("freeMintedByWallet_user"),
        "balanceOf_user": st.get("balanceOf_user")},
    "Lumenhold_free_pct": lumen_pct,
    "Lumenhold": {"totalSupply": lu.get("totalSupply"), "freeClaimed": lu.get("freeClaimed"),
        "FREE_SUPPLY": lu.get("FREE_SUPPLY"), "mintOpen": lu.get("mintOpen"),
        "balanceOf_user": lu.get("balanceOf_user"), "mintedBy_user": lu.get("mintedBy_user")},
    "binanceai": {"launched": bn.get("launched"), "failed": bn.get("failed"),
        "isRefundPhase": bn.get("isRefundPhase"), "totalShares": bn.get("totalShares"),
        "tokenClaimed_user": bn.get("tokenClaimed_user")},
    "notes": "Strong-lead bar >70% + age <24h + slot open + website gate. STOCKAGENT/Lumenhold age UNVERIFIED + website unverified (snapshot) - no promotion unless legs flip. binanceai-mint refund phase already reported - re-read for change only."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
