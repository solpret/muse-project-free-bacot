#!/usr/bin/env python3
"""Hot-leg run 2026-11-20 15:29 WIB. Read-only except own hot-leg state files.
Based on hot-leg-2026-11-20-1514-run.py (flat reads).
Leg-4 focus set = 15:14 set (20 items: Turtle/Lion/AgentForge/AgentMintPass/
AGATE-Pass/AgentDrop/DeepShard/Navigara/binanceai/Lumenhold/STOCK/Race/AUGENT/
bsccat/Grove/YAMA/CTXGRAPH4/ONI/CappyBNB/Coffee Agents).
Transport: batch_race try (8s) then direct urllib chunked batch (12/call) to
bsc-dataseed.bnbchain.org (proven 13:34 + 13:39), curl fallback to other
dataseeds. Null/error reads keep baseline, never a change. No preview/mint."""
import json, re, sys, time, subprocess, concurrent.futures, os, urllib.request
os.environ["TZ"] = "Asia/Jakarta"
time.tzset()
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-1544"
START = time.time()
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-20 15:29 WIB", "started_wib": NOW}

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
    addrs = []
    if isinstance(results, list):
        for e in results:
            if isinstance(e, dict) and e.get("address"): addrs.append(e["address"])
    out["sourcify_feed"] = {"total": len(addrs), "top": addrs[0] if addrs else None,
        "all": addrs, "fetch": "curl 200 in-script"}
except Exception as ex:
    addrs = []
    out["sourcify_feed"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
seen_lower = {k.lower() for k in seen}
new = [a for a in addrs if a.lower() not in seen_lower
       and a not in EXCLUDED and a.lower() != REGISTRY]
out["sourcify_feed"]["new"] = new

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
    if s.get("error") or not s.get("n_fns"): continue
    if s.get("is_proxy") and not s.get("n_fns"):
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape",
                   "note": "Sourcify ABI = proxy only - not a sale shape; recorded so it stops reappearing as new."}
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
        open(BASE+f"hot-leg-2026-11-20-1544-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen = json.load(open(BASE+"hot-leg-seen.json"))
        seen_lower = {k.lower() for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        out["boltbook"][lang] = {"bytes": len(html), "http_code": code,
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW)}
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
    out["bridge"] = {"contracts": len(bc), "in_snapshot": len(in_snap),
        "not_in_snapshot": len(not_in), "not_in_snapshot_list": not_in,
        "same_owner_discarded": len(discarded),
        "verdict": "no complement finding" if not not_in else "NOTED for main 30-min job only, NOT a new lead"}
except Exception as ex:
    out["bridge"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "note": "bridge skip - run continues"}

# ---- (4) leg-4 focus set (15:29 set) ----
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
   ("totalShares","totalShares()",""),("tokenClaimed_user","tokenClaimed(address)","addr"),
   ("refundClaimed_user","refundClaimed(address)","addr")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply","totalSupply()",""),("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("freeLeft","freeLeft()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply","totalSupply()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("freeLeft","freeLeft()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("Race Agents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
  [("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("AUGENT", "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
  [("freeClaimed","freeClaimed()",""),("totalSupply","totalSupply()",""),
   ("balanceOf_user","balanceOf(address)","addr"),("paused","paused()",""),
   ("sold","sold()","")]),
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
 ("ONI", "0x74BDA11E34EB02121104Ff38471D91Fe1C37F81A",
  [("totalSupply","totalSupply()",""),("totalMinted","totalMinted()",""),
   ("freeMinted","freeMinted()","")]),
 ("CappyBNB", "0xD5E04D58E7DCE419B6531EaF62f7Dfe93A4dCf3e",
  [("freeMinted","freeMinted()",""),("FREE_LOTS","FREE_LOTS()",""),
   ("mintOpen","mintOpen()",""),("FREE_FEE","FREE_FEE()","")]),
 ("Coffee Agents", "0xc1fAd916153d1b91d6ba9a2253450A6eB2f48245",
  [("totalMinted","totalMinted()",""),("mintActive","mintActive()","")]),
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

def urllib_chunked(calls, chunk=12, ep="https://bsc-dataseed.bnbchain.org"):
    res = [None]*len(calls)
    for s in range(0, len(calls), chunk):
        part = calls[s:s+chunk]
        payload = json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call",
            "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(part)]).encode()
        req = urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                resp = json.load(r)
        except Exception:
            continue
        by_id = {x.get("id"): x for x in resp if isinstance(x, dict)} if isinstance(resp, list) else {}
        for i in range(len(part)):
            x = by_id.get(i, {})
            if "result" in x: res[s+i] = x["result"]
            elif "error" in x: res[s+i] = {"error": str(x["error"])[:120]}
    return res

def curl_chunk(chunk, base_id, eps):
    payload = [{"jsonrpc":"2.0","id":base_id+i,"method":"eth_call",
                "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(chunk)]
    for ep in eps:
        p = subprocess.run(["curl","-s","--max-time","25","-H","Content-Type: application/json",
            "-d", json.dumps(payload), ep], capture_output=True, text=True)
        try: resp = json.loads(p.stdout)
        except Exception: continue
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

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/")
t0 = time.time()
results = None; leg4_method = None
try:
    results = batch_race(calls, timeout=8)
    leg4_method = "batch_race"
except Exception as ex:
    out["leg4_batch_race_error"] = f"{type(ex).__name__}: {str(ex)[:160]}"
    results = urllib_chunked(calls)
    if any(r is not None for r in results):
        leg4_method = "urllib-chunked-batch(12) bsc-dataseed.bnbchain.org"
    else:
        # curl fallback, 10/call
        results = [None]*len(calls)
        notes = []
        for s in range(0, len(calls), 10):
            chunk = calls[s:s+10]
            res, ep = curl_chunk(chunk, s, EPS)
            if res is None:
                time.sleep(3)
                res, ep = curl_chunk(chunk, s, EPS)
            if res is None:
                notes.append({"start": s, "status": "FAILED-both-attempts"})
            else:
                results[s:s+len(chunk)] = res
                notes.append({"start": s, "status": "ok", "endpoint": ep})
        leg4_method = "chunked-curl-batch-fallback"
        out["leg4_chunks"] = notes
out["leg4_method"] = leg4_method
out["leg4_batch_s"] = round(time.time()-t0, 1)

reads = {}
for name, addr, views in ITEMS:
    reads[name] = {}
if results:
    for (name, vk), r in zip(keys, results):
        if isinstance(r, str):
            reads[name][vk] = iv(r)
        elif isinstance(r, dict):
            reads[name][vk] = "err:" + str(r.get("error", r))[:120]
        else:
            reads[name][vk] = None
try:
    p = subprocess.run(["curl","-s","--max-time","15","-H","Content-Type: application/json",
        "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}',
        "https://bsc-dataseed.binance.org/"], capture_output=True, text=True)
    blk = int(json.loads(p.stdout)["result"], 16)
except Exception:
    blk = None
json.dump({"started_wib": NOW, "block": blk, "transport": leg4_method, "reads": reads,
           "elapsed_s": round(time.time()-t0, 1)},
          open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_block"] = blk
out["leg4_items"] = len(reads)

# diff vs 15:24 baseline (flat reads)
try:
    prev = json.load(open(BASE+"hot-leg-run-2026-11-20-1529-reread.json"))
    prev_reads = prev.get("reads", {})
    prev_block = prev.get("block")
except Exception as ex:
    prev_reads, prev_block = {}, None
    out["leg4_prev_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
changes = {}
for k, cur in reads.items():
    pv = prev_reads.get(k, {})
    diff = {}
    for kk, vv in cur.items():
        pvv = pv.get(kk)
        if isinstance(vv, int) and isinstance(pvv, int) and pvv != vv:
            diff[kk] = {"prev": pvv, "now": vv}
        elif isinstance(vv, int) and pvv is None:
            diff[kk] = {"prev": "unreadable-prev", "now": vv}
    changes[k] = diff
out["leg4_changes_vs_1529"] = changes
out["leg4_prev_block"] = prev_block

def pct(c, t):
    c, t = num(c), num(t)
    return round(100*c/t, 1) if c is not None and t else None
tu = reads["Prosperity Turtle Agents"]; li = reads["Guardian Lion Agents"]
st = reads["STOCK AGENT"]; lu = reads["Lumenhold"]
cp = reads["CappyBNB"]; au = reads["AUGENT"]; na = reads["Navigara"]
out["threshold_check"] = {
  "Turtle_free_pct": pct(tu.get("freeClaimed"), tu.get("FREE_SUPPLY")),
  "Turtle": tu,
  "Lion_free_pct": pct(li.get("freeClaimed"), li.get("FREE_SUPPLY")),
  "Lion": li,
  "STOCKAGENT_free_pct": pct((num(st.get("FREE_SUPPLY")) - num(st.get("freeLeft"))) if num(st.get("FREE_SUPPLY")) is not None and num(st.get("freeLeft")) is not None else None, st.get("FREE_SUPPLY")),
  "STOCKAGENT": st,
  "Lumenhold_free_pct": pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY")),
  "Lumenhold": lu,
  "Navigara_free_pct": pct(na.get("freeClaimed"), na.get("FREE_SUPPLY")),
  "Navigara": na,
  "AUGENT": au,
  "AUGENT_free_pct": pct(au.get("freeClaimed"), 2999),
  "CappyBNB": cp,
  "CappyBNB_free_pct": pct(cp.get("freeMinted"), cp.get("FREE_LOTS")),
  "ONI": reads["ONI"],
  "AgentMintPass": reads["AgentMintPass"],
  "AGATE-Pass": reads["AGATE-Pass"],
  "AgentDrop": reads["AgentDrop"],
  "DeepShard": reads["DeepShard"],
  "binanceai": reads["binanceai-mint"],
  "bsccat_sale": reads["bsccat-sale"],
  "AgentGrove": reads["Agent Grove"],
  "YAMA": reads["YAMA-sale"],
  "CTXGRAPH4": reads["CTXGRAPH4-nodesv2"],
  "CoffeeAgents": reads["Coffee Agents"],
  "AgentForgeHero": reads["AgentForge Hero"],
  "notes": "Strong-lead bar >70% free + age <24h verified + user slot open + verified website gate. Turtle/Lion below 50% track-A. Lumenhold ~85% + STOCK ~84.2% but age UNVERIFIED + no website - NOT strong lead. Navigara same-owner-discarded - NEVER promoted, log only. CappyBNB FREE_FEE 0.000051 BNB - NOT gas-only, never executable. AUGENT age UNVERIFIED - not a track-C lead. No promotion unless a leg flips."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
