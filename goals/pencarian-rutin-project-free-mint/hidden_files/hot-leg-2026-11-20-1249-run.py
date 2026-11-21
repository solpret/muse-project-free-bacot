#!/usr/bin/env python3
"""Hot-leg run 2026-11-20 12:49 WIB. Read-only except own hot-leg state files.
Based on hot-leg-2026-11-20-1239-run.py. Leg-4 = same focus set as 1129
(Turtle/Lion/AgentForge/AgentMintPass/AGATE-Pass/AgentDrop/DeepShard/
binanceai/Lumenhold) + 0934 set still active (STOCKAGENT/Race/AUGENT/bsccat/
Grove/YAMA/CTXGRAPH4) + Navigara (same-owner-discarded, log-only).
AONE dropped (sold-out-age-excluded 2026-11-19).
Prev baselines: 1244 threshold values + 1244 reread file.
Speed: batch_race timeout 8s, then straight to chunked-curl fallback
(0949 showed batch_race outage, chunked-curl fallback ok). Prev baseline: 1209 reread + threshold values."""
import json, re, sys, time, subprocess, concurrent.futures, os
os.environ["TZ"] = "Asia/Jakarta"
time.tzset()
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-1249"
START = time.time()
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-20 12:49 WIB", "started_wib": NOW}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
def num(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else None

def curl_text(url, timeout=20):
    p = subprocess.run(["curl","-sL","--max-time",str(timeout),"-A","Mozilla/5.0",
        url], capture_output=True, text=True)
    return p.stdout

def curl_text_code(url, timeout=20):
    p = subprocess.run(["curl","-sL","--max-time",str(timeout),"-A","Mozilla/5.0",
        "-w","\n__HTTP_CODE__:%{http_code}", url], capture_output=True, text=True)
    body = p.stdout
    code = "?"
    if "__HTTP_CODE__:" in body:
        body, code = body.rsplit("__HTTP_CODE__:", 1)
        code = code.strip()
    return body, code

# ---- (1) Sourcify feed ----
seen = json.load(open(BASE+"hot-leg-seen.json"))
try:
    raw = curl_text("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25)
    feed = json.loads(raw)
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    addrs, vers = [], []
    if isinstance(results, list):
        for e in results:
            if isinstance(e, dict):
                a = e.get("address"); v = e.get("verifiedAt")
            elif isinstance(e, str):
                a = e if re.match(r"^0x[0-9a-fA-F]{40}$", e) else None; v = None
            else:
                a = None; v = None
            if a: addrs.append(a); vers.append(v)
    out["sourcify_feed"] = {"total": len(addrs), "top": addrs[0] if addrs else None,
        "top_verifiedAt": vers[0] if vers else None, "all": addrs, "fetch": "curl 200 in-script",
        "feed_shape": ("dict-results" if isinstance(feed, dict) else "list"),
        "raw_head": raw[:120]}
except Exception as ex:
    addrs = []
    out["sourcify_feed"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
seen_lower = {k.lower() for k in seen}
new = [a for a in addrs if a.lower() not in seen_lower
       and a not in EXCLUDED and a.lower() != REGISTRY]
out["sourcify_feed"]["new"] = len(new); out["sourcify_feed"]["new_contracts"] = new

def shape(addr):
    try:
        _o = curl_text(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 20)
        meta = json.loads(_o)
        abi = meta.get("abi", []) if isinstance(meta, dict) else []
        fns = {}
        for e in abi:
            if isinstance(e, dict) and e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
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
                "is_proxy": bool(abi) and not fns}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
if new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape, new))
json.dump(shapes, open(BASE+f"hot-leg-run-{RUN}-sourcify-shape.json","w"), indent=1)
out["shape"] = shapes
out["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]
seen = json.load(open(BASE+"hot-leg-seen.json"))
for s in shapes:
    a = s["address"]
    if s.get("error"):
        continue
    if s.get("is_proxy") and not s.get("n_fns"):
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape",
                   "note": "Sourcify ABI = proxy only - not a sale shape; recorded so it stops reappearing as new."}
        continue
    if not s.get("n_fns"):
        continue
    if (s.get("S1") or s.get("S2")) and s.get("is_nft"):
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-track-c",
                   "note": "S1/S2 pass BUT ERC-721 NFT, not a fungible share sale; NFT early-lead stays with main job; never reported/previewed/minted."}
    elif s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "sale-shape-pass",
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} fns free={s.get('free_views')} agent={s.get('agent_ref')}"}
    else:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape",
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["seen_n_after_feed"] = len(seen)

# ---- (2) Boltbook EN + ZH ----
out["boltbook"] = {}
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']
for lang, url in (("en","https://boltbook.fun/"),("zh","https://boltbook.fun/?lang=zh")):
    try:
        html, code = curl_text_code(url, 25)
        open(BASE+f"hot-leg-2026-11-20-1249-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen = json.load(open(BASE+"hot-leg-seen.json"))
        seen_lower = {k.lower() for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        txt = re.sub(r"<[^>]+>"," ", html); txt = re.sub(r"\s+"," ", txt)
        freeposts = sorted(set(re.findall(r"([A-Za-z0-9$._-]{2,30})\s*:\s*([\d.,]+)\s*/\s*([\d.,]+)\s*free\s*\(([\d.,]+)%\)", txt)))
        out["boltbook"][lang] = {"bytes": len(html), "http_code": code,
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW),
            "free_posts": freeposts}
        bb_shapes = []
        if newfound:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                bb_shapes = list(ex.map(shape, newfound))
        out["boltbook"][lang]["shapes"] = bb_shapes
        out["boltbook"][lang]["shape_hits"] = [s["address"] for s in bb_shapes if s.get("S1") or s.get("S2")]
        for s in bb_shapes:
            a = s["address"]
            if s.get("error") or not s.get("n_fns"): continue
            seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                "status": "checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                         else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
        json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    except Exception as ex:
        out["boltbook"][lang] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
out["seen_n_after_boltbook"] = len(json.load(open(BASE+"hot-leg-seen.json")))
out["shape_hits_all"] = out["shape_hits"] + [s for lang in ("en","zh") for s in out.get("boltbook",{}).get(lang,{}).get("shape_hits",[])]

# ---- bridge (read-only) ----
try:
    b = json.load(open(BASE+"scan-bridge.json"))
    bc = b.get("contracts", {})
    snap = json.load(open(BASE+"onchain-snapshot.json"))
    snap_addrs = set()
    for coll in ("contracts","track_c"):
        for v in (snap.get(coll) or {}).values():
            if isinstance(v, dict):
                for k in ("address","sale","token"):
                    val = v.get(k)
                    if isinstance(val, str) and val.startswith("0x"): snap_addrs.add(val.lower())
    for v in (snap.get("pending_claims") or {}).values():
        if isinstance(v, dict):
            for k in ("mint","token"):
                val = v.get(k)
                if isinstance(val, str) and val.startswith("0x"): snap_addrs.add(val.lower())
    not_in = [a for a in bc if isinstance(a, str) and a.lower() not in snap_addrs]
    discarded = [a for a,v in bc.items() if isinstance(v,dict) and v.get("same_owner_discarded")]
    in_snap = [a for a in bc if isinstance(a, str) and a.lower() in snap_addrs]
    out["bridge_scan"] = {"total": len(bc), "in_snapshot": len(in_snap),
        "not_in_snapshot": len(not_in), "not_in_snapshot_list": not_in,
        "same_owner_discarded": len(discarded),
        "note": "Noted for main 30-min job only, NOT a new lead."}
except Exception as ex:
    out["bridge_scan"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "note": "bridge skip - run continues"}

# ---- (4) leg-4 focus set ----
ITEMS = [
 ("Prosperity Turtle Agents", "0x1F37Bd89349B6d14a6eF8353504C8E0DFf609C6f",
  [("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("Guardian Lion Agents", "0xdddB9129c40561B0b697D2a2Fc22429f04C181d6",
  [("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("AgentForge Hero", "0xA65944F2093e6dcFD1d1a7a4f6744f924068f878",
  [("totalSupply","totalSupply()",""),("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("freeLeft","freeLeft()",""),("balanceOf_user","balanceOf(address)","addr"),
   ("totalMinted","totalMinted()","")]),
 ("AgentMintPass", "0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0",
  [("totalMinted","totalMinted()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("AGATE-Pass", "0x5b63bd45e61a2e6540548c3509b598b6384206c5",
  [("totalMinted","totalMinted()",""),("hasMinted_user","hasMinted(address)","addr")]),
 ("AgentDrop", "0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9",
  [("totalMinted","totalMinted()",""),("hasMinted_user","hasMinted(address)","addr")]),
 ("DeepShard", "0xC463960af285b7EDA0909D362Ae31783597C2076",
  [("totalSupply","totalSupply()","")]),
 ("Navigara", "0x551f66b177dcc77f01f7503e90ba5dabf51e9dce",
  [("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("totalSupply","totalSupply()",""),("mintOpen","mintOpen()",""),
   ("balanceOf_user","balanceOf(address)","addr")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched","launched()",""),("failed","failed()",""),("isRefundPhase","isRefundPhase()",""),
   ("totalShares","totalShares()",""),("tokenClaimed_user","tokenClaimed(address)","addr")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply","totalSupply()",""),("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("freeLeft","freeLeft()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("STOCKAGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply","totalSupply()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("freeLeft","freeLeft()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("Race Agents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
  [("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("AUGENT", "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
  [("freeClaimed","freeClaimed()",""),("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("bsccat-sale", "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
  [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()","")]),
 ("Agent Grove", "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c",
  [("totalSupply","totalSupply()",""),("freeOpen","freeOpen()",""),
   ("freeClaimed_user","freeClaimed(address)","addr"),
   ("balanceOf_user","balanceOf(address)","addr")]),
 ("YAMA-sale", "0x86D779fc4d83044cCECCb53639f9a98E367D6E46",
  [("totalShares","totalShares()",""),("totalFreeShares","totalFreeShares()",""),
   ("freeUsed_user","freeUsed(address)","addr"),
   ("quote_user_1","quote(address,uint256)","addr_uint1")]),
 ("CTXGRAPH4-nodesv2", "0x189DB6602B8D41a0d14CcCc9e999DC3aF895c3f2",
  [("currentGraph","currentGraph()",""),("mintOpen","mintOpen()",""),
   ("isSealed4","isSealed(uint256)","uint4"),
   ("nodesInGraph4","nodesInGraph(uint256)","uint4"),
   ("participantsOf4","participantsOf(uint256)","uint4"),
   ("nodesOf_user_4","nodesOf(address,uint256)","addr_uint4"),
   ("priceFor_user","priceFor(address)","addr"),
   ("holdsAgentId_user","holdsAgentId(address)","addr")]),
]
calls, keys = [], []
for name, addr, views in ITEMS:
    for vk, sig, argt in views:
        data = sel(sig)
        if argt == "addr": data += UA
        elif argt == "addr_uint1": data += UA + enc_uint(1)[2:]
        elif argt == "uint4": data += enc_uint(4)[2:]
        elif argt == "addr_uint4": data += UA + enc_uint(4)[2:]
        calls.append({"to": addr, "data": data})
        keys.append((name, vk))

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/")
def curl_chunk(chunk, base_id):
    payload = [{"jsonrpc":"2.0","id":base_id+i,"method":"eth_call",
                "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(chunk)]
    for ep in EPS:
        p = subprocess.run(["curl","-s","--max-time","25","-H","Content-Type: application/json",
            "-d", json.dumps(payload), ep], capture_output=True, text=True)
        try:
            resp = json.loads(p.stdout)
        except Exception:
            continue
        if isinstance(resp, list) and len(resp) == len(chunk):
            by_id = {r.get("id"): r for r in resp if isinstance(r, dict)}
            out_l = []
            for i in range(len(chunk)):
                r = by_id.get(base_id+i, {})
                if "result" in r: out_l.append(r["result"])
                elif "error" in r: out_l.append({"error": str(r["error"])[:120]})
                else: out_l.append(None)
            return out_l, ep
    return None, None

def chunked_curl_batch():
    results = [None]*len(calls)
    notes = []
    CH = 10
    for start in range(0, len(calls), CH):
        chunk = calls[start:start+CH]
        res, ep = curl_chunk(chunk, start)
        if res is None:
            time.sleep(3)
            res, ep = curl_chunk(chunk, start)
        if res is None:
            notes.append({"start": start, "status": "FAILED-both-attempts"})
        else:
            results[start:start+len(chunk)] = res
            notes.append({"start": start, "status": "ok", "endpoint": ep})
    return results, notes

t0 = time.time()
results = None; leg4_method = None
try:
    results = batch_race(calls, timeout=8)
    leg4_method = "batch_race"
except Exception as ex:
    out["leg4_batch_race_error"] = f"{type(ex).__name__}: {str(ex)[:160]}"
    try:
        results, chunk_notes = chunked_curl_batch()
        leg4_method = "chunked-curl-batch-fallback"
        out["leg4_chunks"] = chunk_notes
    except Exception as ex3:
        out["leg4_chunked_error"] = f"{type(ex3).__name__}: {str(ex3)[:160]}"
out["leg4_method"] = leg4_method
out["leg4_batch_s"] = round(time.time()-t0, 1)
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
if results:
    for (name, vk), r in zip(keys, results):
        if isinstance(r, str):
            reads[name]["views"][vk] = iv(r)
        elif isinstance(r, dict):
            reads[name]["views"][vk] = r
        else:
            reads[name]["views"][vk] = None
try:
    p = subprocess.run(["curl","-s","--max-time","15","-H","Content-Type: application/json",
        "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}',
        "https://bsc-dataseed.binance.org/"], capture_output=True, text=True)
    blk = int(json.loads(p.stdout)["result"], 16)
except Exception:
    blk = None
json.dump({"started_wib": NOW, "block": blk, "reads": reads, "method": leg4_method},
          open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_block"] = blk
out["leg4_items"] = len(reads)

# prev baselines: 1229 threshold_check + 1224 reread file
PREV1244 = {
 "Prosperity Turtle Agents": {"freeClaimed": 42, "FREE_SUPPLY": 88, "totalSupply": 42, "balanceOf_user": 0},
 "Guardian Lion Agents": {"freeClaimed": 40, "FREE_SUPPLY": 88, "totalSupply": 40, "balanceOf_user": 0},
 "AgentMintPass": {"totalMinted": 593, "balanceOf_user": 0},
 "AGATE-Pass": {"totalMinted": 423, "hasMinted_user": 0},
 "AgentDrop": {"totalMinted": 394, "hasMinted_user": 0},
 "DeepShard": {"totalSupply": 543},
 "binanceai-mint": {"launched": 0, "failed": 1, "isRefundPhase": 1, "totalShares": 3110, "tokenClaimed_user": 0},
 "Lumenhold": {"freeClaimed": 1280, "FREE_SUPPLY": 1500, "totalSupply": 1285, "balanceOf_user": 0},
 "AUGENT": {"freeClaimed": 1595},
 "STOCKAGENT": {"totalSupply": 931, "FREE_SUPPLY": 1111, "freeLeft": 180, "balanceOf_user": 0},
 "CTXGRAPH4-nodesv2": {"nodesInGraph4": 320, "participantsOf4": 310, "currentGraph": 4, "mintOpen": 1, "isSealed4": 0, "priceFor_user": 200000000000000, "holdsAgentId_user": 1},
 "Navigara": {"freeClaimed": 979, "FREE_SUPPLY": 1470, "totalSupply": 980, "mintOpen": 1, "balanceOf_user": 0},
}
try:
    prev1244 = json.load(open(BASE+"hot-leg-run-2026-11-20-1244-reread.json"))
    prev1244_reads = {k: v.get("views", {}) for k, v in prev1244.get("reads", {}).items()}
except Exception as ex:
    prev1244_reads = {}
    out["leg4_prev1244_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
changes = {}
for k, cur in reads.items():
    pv = {}
    for kk, vv in prev1244_reads.get(k, {}).items():
        pv[kk] = vv if isinstance(vv, int) else None
    for kk, vv in PREV1244.get(k, {}).items():
        pv.setdefault(kk, vv)
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        pvv = pv.get(kk)
        if isinstance(vv, int) and isinstance(pvv, int) and pvv != vv:
            diff[kk] = {"prev": pvv, "now": vv}
        elif isinstance(vv, int) and pvv is None:
            diff[kk] = {"prev": "unreadable-prev", "now": vv}
    changes[k] = diff
out["leg4_changes_vs_1244"] = changes

def pct(c, t):
    c, t = num(c), num(t)
    return round(100*c/t, 1) if c is not None and t else None
tu = reads["Prosperity Turtle Agents"]["views"]; li = reads["Guardian Lion Agents"]["views"]
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
ra = reads["Race Agents"]["views"]; af = reads["AgentForge Hero"]["views"]
out["threshold_check"] = {
  "Turtle_free_pct": pct(tu.get("freeClaimed"), tu.get("FREE_SUPPLY")),
  "Turtle": tu,
  "Lion_free_pct": pct(li.get("freeClaimed"), li.get("FREE_SUPPLY")),
  "Lion": li,
  "STOCKAGENT_free_pct": pct((num(st.get("FREE_SUPPLY")) - num(st.get("freeLeft"))) if num(st.get("FREE_SUPPLY")) is not None and num(st.get("freeLeft")) is not None else None, st.get("FREE_SUPPLY")),
  "STOCKAGENT": st,
  "Lumenhold_free_pct": pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY")),
  "Lumenhold": lu,
  "RaceAgents": ra,
  "AgentForgeHero": af,
  "AgentMintPass": reads["AgentMintPass"]["views"],
  "AGATE-Pass": reads["AGATE-Pass"]["views"],
  "AgentDrop": reads["AgentDrop"]["views"],
  "DeepShard": reads["DeepShard"]["views"],
  "binanceai": reads["binanceai-mint"]["views"],
  "AUGENT": reads["AUGENT"]["views"],
  "bsccat_sale": reads["bsccat-sale"]["views"],
  "AgentGrove": reads["Agent Grove"]["views"],
  "YAMA": reads["YAMA-sale"]["views"],
  "CTXGRAPH4": reads["CTXGRAPH4-nodesv2"]["views"],
  "Navigara": reads["Navigara"]["views"],
  "Navigara_free_pct": pct(reads["Navigara"]["views"].get("freeClaimed"), reads["Navigara"]["views"].get("FREE_SUPPLY")),
  "notes": "Strong-lead bar >70% free + age <24h verified + user slot open + verified website gate. Turtle 47.7% / Lion 45.5% (below 50% track-A, below 70% strong-lead). Lumenhold ~85% but age UNVERIFIED + first seen 2026-11-17 22:01 WIB (>24h) + no website - no promotion. STOCKAGENT 83.8% but age UNVERIFIED + no verified website - no promotion. Navigara same-owner-discarded 2026-11-03 - NEVER promoted, log only. No promotion unless a leg flips."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
