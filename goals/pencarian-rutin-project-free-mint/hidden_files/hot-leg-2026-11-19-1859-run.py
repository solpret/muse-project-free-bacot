#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 18:59 WIB. Read-only except own hot-leg state files.
Based on hot-leg-2026-11-19-1854-run.py; leg-4 = full focus set from
hot-leg-run-2026-11-19-1849-reread.json (45 items) + AUGENT + Mossminds + THVX.
Feed + Boltbook pre-fetched to /tmp by the parent (fresh this run, 200s).
Leg-4 uses fast_rpc batch_race in chunks (FCFS batch rule), fallback call_many."""
import json, re, sys, time, subprocess, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many, _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-19-1859"
START = time.time()
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-19 18:59 WIB", "started_wib": NOW}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None

# ---- (1) Sourcify feed (pre-fetched /tmp/sourcify-feed-1859.json, 200) ----
seen = json.load(open(BASE+"hot-leg-seen.json"))
try:
    feed = json.load(open("/tmp/sourcify-feed-1859.json"))
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    addrs, vers = [], []
    for e in results:
        if isinstance(e, str): a, v = e, None
        else:
            a = e.get("address") or (e.get("contract") or {}).get("address")
            v = e.get("verifiedAt") or (e.get("contract") or {}).get("verifiedAt")
        if a: addrs.append(a); vers.append(v)
    out["sourcify_feed"] = {"total": len(addrs), "top": addrs[0] if addrs else None,
        "top_verifiedAt": vers[0] if vers else None, "all": addrs, "fetch": "pre-fetched /tmp/sourcify-feed-1859.json (200)"}
except Exception as ex:
    addrs = []
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
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
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
out["seen_added_feed"] = new
out["seen_n"] = len(seen)

# ---- (2) Boltbook EN + ZH (pre-fetched /tmp/bb-{en,zh}-1859.html, both 200) ----
out["boltbook"] = {}
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']
for lang in ("en","zh"):
    try:
        html = open(f"/tmp/bb-{lang}-1859.html").read()
        open(BASE+f"hot-leg-2026-11-19-1859-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen_lower = {k.lower() for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        txt = re.sub(r"<[^>]+>"," ", html); txt = re.sub(r"\s+"," ", txt)
        freeposts = sorted(set(re.findall(r"([A-Za-z0-9$._-]{2,30})\s*:\s*([\d.,]+)\s*/\s*([\d.,]+)\s*free\s*\(([\d.,]+)%\)", txt)))
        out["boltbook"][lang] = {"bytes": len(html), "http_code": "200",
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW),
            "free_posts": freeposts}
        for a in newfound:
            s = shape(a)
            if s.get("error") or not s.get("n_fns"): continue
            seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                "status": "checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                         else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
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

# ---- (3) leg 3: on-chain verify of any new sale-shape hits (pool + slot only; age stays unverified) ----
def batch_calls(calls):
    """calls: list of (to, data). Chunked batch_race, fallback call_many. Returns list of hex/None."""
    res = []
    for i in range(0, len(calls), 60):
        chunk = calls[i:i+60]
        try:
            res.extend(batch_race(chunk, timeout=15))
        except Exception:
            try:
                res.extend(call_many(chunk, timeout=20))
            except Exception as ex2:
                res.extend([None]*len(chunk))
                out.setdefault("batch_errors", []).append(f"chunk@{i}: {type(ex2).__name__}: {str(ex2)[:120]}")
    return res

leg3 = {}
for a in out["shape_hits"]:
    s = next((x for x in shapes if x["address"]==a), {})
    calls, keys = [], []
    for fv in (s.get("free_views") or [])[:3]:
        calls.append((a, sel(fv+"()"))); keys.append(fv)
    calls.append((a, sel("freeClaimed(address)")+UA)); keys.append("freeClaimed_user")
    vals = batch_calls(calls)
    leg3[a] = {k: iv(v) for k, v in zip(keys, vals)}
    seen[a] = {"first_seen_wib": NOW, "source": seen.get(a,{}).get("source","sourcify-feed"),
               "status": "sale-shape-pass-age-unverified",
               "note": "Sale shape pass, pool/slot read this run, launch age UNVERIFIED -> watchlist-only, never reported as lead; main 30-min job to verify age."}
out["leg3"] = leg3
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)

# ---- (4) leg-4 re-read: full focus set (45 from 1849 reread + AUGENT + Mossminds + THVX) ----
VIEW_SIGS = {
 "totalSupply":("totalSupply()",""), "totalMinted":("totalMinted()",""),
 "freeMinted":("freeMinted()",""), "freeClaimed":("freeClaimed()",""),
 "freeLeft":("freeLeft()",""), "freeRemaining":("freeRemaining()",""),
 "freeAvailable":("freeAvailable()",""), "FREE_SUPPLY":("FREE_SUPPLY()",""),
 "MAX_SUPPLY":("MAX_SUPPLY()",""), "FREE_CAP":("FREE_CAP()",""),
 "mintOpen":("mintOpen()",""), "isFreePhase":("isFreePhase()",""),
 "launched":("launched()",""), "failed":("failed()",""),
 "isRefundPhase":("isRefundPhase()",""), "totalShares":("totalShares()",""),
 "normalMinted":("normalMinted()",""), "paidMinted":("paidMinted()",""),
 "standardRemaining":("standardRemaining()",""), "legendaryRemaining":("legendaryRemaining()",""),
 "freeSharesLeft":("freeSharesLeft()",""), "openedAt":("openedAt()",""),
 "balanceOf_user":("balanceOf(address)","addr"), "mintedBy_user":("mintedBy(address)","addr"),
 "hasClaimed_user":("hasClaimed(address)","addr"), "hasClaimedFree_user":("hasClaimedFree(address)","addr"),
 "freeMintedByWallet_user":("freeMintedByWallet(address)","addr"),
 "freeMintedBy_user":("freeMintedBy(address)","addr"),
 "freeClaimed_user":("freeClaimed(address)","addr"), "freeUsed_user":("freeUsed(address)","addr"),
 "tokenClaimed_user":("tokenClaimed(address)","addr"), "freeBooked_user":("freeBooked(address)","addr"),
 "mintedCount_user":("mintedCount(address)","addr"),
 "quote_user_1":("quote(address,uint256)","addr_uint1"),
 "cost_user_1":("cost(address,uint256)","addr_uint1"),
 "costFor_user_1":("costFor(address,uint256)","addr_uint1"),
 "mintPriceFor_user_1":("mintPriceFor(address,uint256)","addr_uint1"),
}
ITEMS = [
 ("ADRAW","0xdc167f998341aa37d734de94db2108f0983bf2a7",["freeMinted","totalSupply","balanceOf_user","hasClaimedFree_user"]),
 ("AGCLUB","0x67270bb351515abf3089ca5420456897363f5e75",["totalMinted","freeMinted","FREE_CAP","mintOpen","balanceOf_user"]),
 ("ALIEN","0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb",["totalSupply","FREE_SUPPLY","MAX_SUPPLY","mintOpen","isFreePhase","balanceOf_user"]),
 ("ARKT","0xf91b1ebbcb2b038107ed10b4cb163ed51ce39037",["totalMinted","totalSupply","MAX_SUPPLY","mintOpen","hasClaimed_user","balanceOf_user"]),
 ("ARKT8334","0x8334C7d0e8aF217EEA5251A0A181e628971535e1",["totalSupply","totalMinted","mintOpen"]),
 ("ARKTclaim","0x62a7AC33ca463331858693b8Aa05B16688bA29E0",["totalSupply","totalMinted","balanceOf_user"]),
 ("AgentBubble","0x0d72970046c056db90888351b739246f468bff0b",["freeMinted","totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("AgentEcho","0xff2dac2389a6a9593209b6008d5ffa9e73aa19c2",["totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("AgentNOVA","0x43462d7f269fde4914b03e1e07067a61b62b9540",["totalSupply"]),
 ("AgentPepe","0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d",["totalMinted","totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("AlphaPulse","0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",["totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("BNBG","0x1595013dfc8c6b3f4b172254bf09bdaf1421002b",["totalMinted"]),
 ("BoldLeonidas","0x84bcb8c16566e81ce902530c9da1e3de291f9941",["totalSupply","mintOpen","balanceOf_user"]),
 ("CPASS","0x5877d2bb9f226cc3e438f4d656caeb27deafc576",["totalMinted","mintOpen","balanceOf_user"]),
 ("ClafEye","0x1c759C4e075103b5B250DB5114B832b17B99C456",["totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user","costFor_user_1"]),
 ("DGF","0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",["totalMinted","totalSupply","mintOpen","balanceOf_user"]),
 ("DRAGON","0xfc191b76041498b14dcae3c802af3389c74263e6",["freeMinted","totalMinted","mintOpen","balanceOf_user"]),
 ("E5F8","0xe5f8f8c424821908752332d527428258EcfC245b",["totalMinted","totalSupply","mintOpen"]),
 ("EIM","0x1fccfab61461c4b5c4d1b16580d12a7e32012baa",["totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("Flare-bd6f","0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599",["totalSupply"]),
 ("HAPPE","0x72c14121681F1133545947B0735563835CC07B67",["totalMinted","freeMinted"]),
 ("Hivebyte","0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8",["totalSupply","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("JADE","0x1b8894391a3dcfe7e248c321103265ab52e273e0",["cost_user_1","freeClaimed","totalSupply","mintOpen","mintedBy_user","balanceOf_user"]),
 ("Kageveil","0xf79860f419be7b604d909e254785400d9edbd9d0",["normalMinted","totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("Kryntar","0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",["totalMinted","standardRemaining","legendaryRemaining","mintOpen"]),
 ("Ledgera","0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",["freeClaimed","totalSupply","mintOpen","freeUsed_user","balanceOf_user"]),
 ("Lumenhold","0x9701980b0afd825134390ee46fb3bd675a2f356f",["totalSupply","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","mintedBy_user"]),
 ("MORFO","0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",["totalMinted","mintOpen"]),
 ("Matrix","0x1F669b714337F3C2585072c53fdDD89581F928fF",["freeMinted","freeRemaining","totalSupply","mintOpen"]),
 ("ONI","0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",["totalMinted","totalSupply"]),
 ("PIXELFROGS","0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",["totalSupply","freeMinted","freeLeft","mintOpen","freeClaimed_user"]),
 ("Pengu","0x5AEc03C90656743475810926B2B2bd443D5c26a4",["totalMinted","freeMinted"]),
 ("PunchCard","0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",["totalSupply","totalMinted","freeMinted","paidMinted","MAX_SUPPLY","mintOpen","mintPriceFor_user_1","mintedCount_user","balanceOf_user"]),
 ("RAVE","0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",["totalMinted","freeMinted","mintOpen"]),
 ("REOPIR","0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",["freeClaimed","totalSupply","mintOpen"]),
 ("RaceAgents","0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",["totalSupply","freeMinted","mintOpen"]),
 ("RigForge","0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",["freeSharesLeft","openedAt","freeClaimed","freeBooked_user"]),
 ("SPARKS","0xd52fd117c4b47d03e4e16e778871f09faa5a024b",["totalSupply"]),
 ("STOCKAGENT","0xba7068233da805bdebcc167be361c219002e6b7f",["totalSupply","freeLeft","FREE_SUPPLY","MAX_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user"]),
 ("Stromboat","0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d",["totalMinted","freeMinted","paidMinted","mintOpen","freeMintedBy_user","balanceOf_user"]),
 ("THYRK","0x4d90ffc3075fb8897edff6d7c6269c906664a20e",["totalSupply","freeMinted","MAX_SUPPLY","balanceOf_user"]),
 ("Vitaliq","0xad0d78689d047bb9a32f5bf93438373a73da68ec",["totalSupply","totalMinted","mintOpen","balanceOf_user"]),
 ("XCOPY","0x3fbec44c7c845374267b06033940abe45c63edfa",["totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user"]),
 ("Zephyra","0x00a9791be6317d6e3a6c60f75a706c870d882048",["totalMinted"]),
 ("binanceai-mint","0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",["launched","failed","isRefundPhase","totalShares","tokenClaimed_user"]),
 ("AUGENT","0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",["freeClaimed","freeClaimed_user","totalSupply","balanceOf_user"]),
 ("Mossminds","0x5b49b06a2e25fce0bca865be70f3c62b6319367a",["freeMinted","FREE_CAP","FREE_SUPPLY","freeRemaining","freeAvailable","totalSupply","balanceOf_user"]),
 ("THVX","0x37d39fcc21addbb753e9366216e494d7956bd859",["freeClaimed","totalSupply","mintOpen","balanceOf_user"]),
]
calls, meta = [], []
for name, addr, views in ITEMS:
    for vk in views:
        sig, argt = VIEW_SIGS[vk]
        data = sel(sig)
        if argt == "addr": data += UA
        elif argt == "addr_uint1": data += UA + enc_uint(1)[2:]
        calls.append((addr, data)); meta.append((name, vk))
vals = batch_calls(calls)
ADDR = {n: a for n, a, _ in ITEMS}
reads = {}
for (name, vk), v in zip(meta, vals):
    reads.setdefault(name, {"address": ADDR[name], "views": {}})["views"][vk] = iv(v)
try:
    blk = int(_single("https://bsc-dataseed.binance.org/","eth_blockNumber",[],8,retries=0),16)
except Exception:
    blk = None
reread = {"started_wib": NOW, "block": blk, "reads": reads}
json.dump(reread, open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_reread_file"] = f"hot-leg-run-{RUN}-reread.json"
out["leg4_block"] = blk
out["leg4_items"] = len(reads)

try:
    prev = json.load(open(BASE+"hot-leg-run-2026-11-19-1849-reread.json"))
except Exception as ex:
    prev = {"reads": {}}
    out["leg4_prev_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
changes = {}
for k, cur in reads.items():
    pv = prev.get("reads", {}).get(k, {}).get("views", {})
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        if pv.get(kk) != vv:
            diff[kk] = {"prev": pv.get(kk), "now": vv}
    changes[k] = diff
out["leg4_changes_vs_1849"] = changes

def pct(claimed, total):
    return round(100*claimed/total,1) if claimed is not None and total else None
def V(n, k): return reads.get(n, {}).get("views", {}).get(k)
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
stock_pct = pct((st.get("FREE_SUPPLY")-st.get("freeLeft")) if st.get("FREE_SUPPLY") is not None and st.get("freeLeft") is not None else None, st.get("FREE_SUPPLY"))
lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY"))
ab = reads["AgentBubble"]["views"]
mo = reads["Mossminds"]["views"]
moss_cap = mo.get("FREE_CAP") or mo.get("FREE_SUPPLY")
mx = reads["Matrix"]["views"]
mx_total = (mx.get("freeMinted")+mx.get("freeRemaining")) if mx.get("freeMinted") is not None and mx.get("freeRemaining") is not None else None
ag = reads["AGCLUB"]["views"]; al = reads["ALIEN"]["views"]; th = reads["THYRK"]["views"]; pc = reads["PunchCard"]["views"]
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
    "AgentBubble_free_pct": pct(ab.get("freeMinted"), ab.get("MAX_SUPPLY")),
    "Mossminds_free_pct": pct(mo.get("freeMinted"), moss_cap),
    "Mossminds": {"freeMinted": mo.get("freeMinted"), "FREE_CAP": mo.get("FREE_CAP"),
        "FREE_SUPPLY": mo.get("FREE_SUPPLY"), "freeRemaining": mo.get("freeRemaining"),
        "totalSupply": mo.get("totalSupply"), "balanceOf_user": mo.get("balanceOf_user")},
    "AGCLUB_free_pct": pct(ag.get("freeMinted"), ag.get("FREE_CAP")),
    "ALIEN_free_pct": pct(al.get("totalSupply"), al.get("FREE_SUPPLY")),
    "Matrix_free_pct": pct(mx.get("freeMinted"), mx_total),
    "THYRK_free_pct": pct(th.get("freeMinted"), th.get("MAX_SUPPLY")),
    "PunchCard_free_pct": pct(pc.get("freeMinted"), pc.get("MAX_SUPPLY")),
    "AUGENT_freeClaimed": V("AUGENT","freeClaimed"),
    "AUGENT_slot_user": V("AUGENT","freeClaimed_user"),
    "binanceai": {"launched": V("binanceai-mint","launched"), "failed": V("binanceai-mint","failed"),
        "isRefundPhase": V("binanceai-mint","isRefundPhase"), "totalShares": V("binanceai-mint","totalShares"),
        "tokenClaimed_user": V("binanceai-mint","tokenClaimed_user")},
    "notes": "Strong-lead bar >70% + age <24h + slot open + website gate. STOCKAGENT 70% crossing reported 18 Nov 18:49; Lumenhold age UNVERIFIED + website None - no promotion. AgentBubble sold out total 2222/2222 (reported 03:59). Mossminds same-owner-discarded - re-read for change note only, NEVER promoted/reported as lead. No promotion unless a leg flips."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1)[:9000])
print("ELAPSED", out["elapsed_s"])
