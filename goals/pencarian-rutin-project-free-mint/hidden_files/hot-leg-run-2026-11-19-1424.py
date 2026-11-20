#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 14:24 WIB. Read-only except own hot-leg state files."""
import json, urllib.request, concurrent.futures, re, sys, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-19-1424"
START = time.time()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-19 14:24 WIB", "started_wib": "2026-11-19T14:24:38+07:00"}

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def call(to, data):
    err = None
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0), None, ep
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err, None
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
def collect(to, tests):
    res = {}
    for name, arg in tests:
        val, err, ep = call(to, sel(name)+arg)
        res[name] = iv(val)
        if val is None: res[name+"_err"] = err
    return res

# ---- (1) Sourcify feed ----
seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_before = len(seen)
try:
    feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    addrs, vers = [], []
    for e in results:
        if isinstance(e, str): a, v = e, None
        else:
            a = e.get("address") or (e.get("contract") or {}).get("address")
            v = e.get("verifiedAt") or (e.get("contract") or {}).get("verifiedAt")
        if a: addrs.append(a); vers.append(v)
    json.dump(feed, open(BASE+f"hot-leg-run-{RUN}-sourcify.json","w"), indent=1)
    out["sourcify_feed"] = {"total": len(addrs), "top": addrs[0] if addrs else None,
        "top_verifiedAt": vers[0] if vers else None, "all": addrs, "fetch": "direct urllib"}
except Exception as ex:
    addrs = []
    out["sourcify_feed"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
new = [a for a in addrs if a not in seen and a.lower() not in {x.lower() for x in seen}
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
        continue  # retry next run, do not record as checked
    if (s.get("S1") or s.get("S2")) and s.get("is_nft"):
        seen[a] = {"first_seen_wib":"2026-11-19T14:24:38+07:00","source":"sourcify-feed",
                   "status":"checked-not-track-c",
                   "note":"S1/S2 pass BUT ERC-721 NFT, not a fungible share sale; NFT early-lead stays with main job; never reported/previewed/minted."}
    elif s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib":"2026-11-19T14:24:38+07:00","source":"sourcify-feed",
                   "status":"sale-shape-pass","note":f"S1={s.get('S1')} S2={s.get('S2')} fns free={s.get('free_views')} agent={s.get('agent_ref')}"}
    else:
        seen[a] = {"first_seen_wib":"2026-11-19T14:24:38+07:00","source":"sourcify-feed",
                   "status":"checked-not-sale-shape",
                   "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
out["seen_added"] = new
out["seen_n"] = len(seen)

# ---- (2) Boltbook EN + ZH ----
out["boltbook"] = {}
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']
for lang, url in [("en","https://boltbook.fun/"),("zh","https://boltbook.fun/?lang=zh")]:
    try:
        html = get(url, timeout=12)
        open(BASE+f"hot-leg-run-{RUN}-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen_lower = {k.lower(): k for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        out["boltbook"][lang] = {"bytes": len(html), "http_code": "200",
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW)}
        for a in newfound:
            s = shape(a)
            if s.get("error") or not s.get("n_fns"): continue
            seen[a] = {"first_seen_wib":"2026-11-19T14:24:38+07:00","source":f"boltbook-{lang}",
                "status":"checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                         else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
    except Exception as ex:
        out["boltbook"][lang] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["seen_n_after_boltbook"] = len(seen)

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
                    if v.get(k): snap_addrs.add(v[k].lower())
    for v in snap.get("pending_claims", {}).values():
        if isinstance(v, dict):
            for k in ("mint","token"):
                if v.get(k): snap_addrs.add(v[k].lower())
    not_in = [a for a in bc if a.lower() not in snap_addrs]
    discarded = [a for a,v in bc.items() if isinstance(v,dict) and v.get("same_owner_discarded")]
    out["bridge_scan"] = {"total": len(bc), "not_in_snapshot": len(not_in),
        "not_in_snapshot_list": not_in, "same_owner_discarded": len(discarded)}
except Exception as ex:
    out["bridge_scan"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "note": "bridge skip - run continues"}

# ---- (4) re-read live snapshot items (read-only) ----
UA = enc_addr(USER)[2:]
def q2(to, sig, args):
    val, err, ep = call(to, sel(sig)+args)
    return iv(val), ep
reads = {}
# STOCKAGENT
a = "0xba7068233da805bdebcc167be361c219002e6b7f"
q,_ = q2(a, "quote(address,uint256)", UA+enc_uint(1)[2:])
reads["STOCKAGENT"] = {"address": a, "views": {
    "totalSupply": collect(a, [("totalSupply()",""),("freeLeft()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("freeMintedByWallet(address)",UA),("balanceOf(address)",UA)]),
    "quote_user_1": q}}
reads["STOCKAGENT"]["views"] = {**reads["STOCKAGENT"]["views"]["totalSupply"], "quote_user_1": q}
# Lumenhold
a = "0x9701980b0afd825134390ee46fb3bd675a2f356f"
reads["Lumenhold"] = {"address": a, "views": collect(a, [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("balanceOf(address)",UA),("mintedBy(address)",UA)])}
# AgentBubble
a = "0x0d72970046c056db90888351b739246f468bff0b"
reads["AgentBubble"] = {"address": a, "views": collect(a, [("freeMinted()",""),("totalSupply()",""),("totalMinted()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("balanceOf(address)",UA)])}
# AUGENT
a = "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393"
reads["AUGENT"] = {"address": a, "views": collect(a, [("freeClaimed()",""),("freeClaimed(address)",UA),("totalSupply()",""),("balanceOf(address)",UA)])}
# THVX
a = "0x37d39fcc21addbb753e9366216e494d7956bd859"
reads["THVX"] = {"address": a, "views": collect(a, [("freeClaimed()",""),("totalSupply()",""),("mintOpen()",""),("balanceOf(address)",UA)])}
# binanceai-mint (track-B pending)
a = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
reads["binanceai-mint"] = {"address": a, "views": collect(a, [("launched()",""),("failed()",""),("isRefundPhase()",""),("totalShares()",""),("tokenClaimed(address)",UA)])}
# block number
try:
    blk = int(_single(EPS[0],"eth_blockNumber",[],8,retries=0),16)
except Exception:
    blk = None
reread = {"started_wib": "2026-11-19T14:24:38+07:00", "block": blk, "reads": reads,
          "rpc_ep": EPS[0]}
json.dump(reread, open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_reread_file"] = f"hot-leg-run-{RUN}-reread.json"
out["leg4_block"] = blk

# ---- change detection vs 1419 ----
prev = json.load(open(BASE+"hot-leg-run-2026-11-19-1419-reread.json"))
changes = {}
for k, cur in reads.items():
    pv = prev.get("reads", {}).get(k, {}).get("views", {})
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        if kk.endswith("_err"): continue
        if pv.get(kk) != vv:
            diff[kk] = {"prev": pv.get(kk), "now": vv}
    changes[k] = diff
out["leg4_changes_vs_1419"] = changes
# threshold check
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]; ab = reads["AgentBubble"]["views"]
def pct(claimed, total):
    return round(100*claimed/total,1) if claimed is not None and total else None
stock_pct = pct(st.get("FREE_SUPPLY",1111)-st.get("freeLeft",0) if st.get("FREE_SUPPLY") and st.get("freeLeft") is not None else None, st.get("FREE_SUPPLY"))
lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY"))
out["threshold_check"] = {
    "STOCKAGENT_free_pct": stock_pct,
    "STOCKAGENT": {"totalSupply": st.get("totalSupply()"), "freeLeft": st.get("freeLeft()"),
        "FREE_SUPPLY": st.get("FREE_SUPPLY()"), "mintOpen": st.get("mintOpen()"),
        "quote_user_1": st.get("quote_user_1"), "freeMintedByWallet_user": st.get("freeMintedByWallet(address)"),
        "balanceOf_user": st.get("balanceOf(address)")},
    "Lumenhold_free_pct": lumen_pct,
    "Lumenhold": {"totalSupply": lu.get("totalSupply()"), "freeClaimed": lu.get("freeClaimed()"),
        "FREE_SUPPLY": lu.get("FREE_SUPPLY()"), "mintOpen": lu.get("mintOpen()"),
        "balanceOf_user": lu.get("balanceOf(address)"), "mintedBy_user": lu.get("mintedBy(address)")},
    "AgentBubble_free_pct": pct(ab.get("freeMinted"), ab.get("MAX_SUPPLY()")),
    "notes": "Strong-lead bar >70% + age <24h + slot open. STOCKAGENT age UNVERIFIED + websiteGate unverified (snapshot); 70% crossing reported 18 Nov 18:49. Lumenhold age UNVERIFIED + website None + slot-free UNVERIFIED (watchlist-only-age-unverified 17 Nov) - no promotion. AgentBubble sold out total 2222/2222 (reported 03:59 change-observed-not-reported). No promotion unless a leg flips."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
print("ELAPSED", out["elapsed_s"])
