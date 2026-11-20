#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 19:49 WIB. Read-only except own hot-leg state files.
Based on hot-leg-2026-11-19-1944-run.py. Fixes: num() guard so error-dict RPC
values can never reach pct()/subtraction (1914 crash bug). Leg-4 = trimmed
focus set via sequential race() single calls (batch stalled 19:04) + AONE /
bsccat track-C re-reads. Feeds pre-fetched to /tmp (200s, fresh this run)."""
import json, re, sys, time, subprocess, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-19-1949"
START = time.time()
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-19 19:49 WIB", "started_wib": NOW}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
def num(v):
    """int only; error dicts / None / strings -> None (1914 crash guard)."""
    return v if isinstance(v, int) and not isinstance(v, bool) else None

# ---- (1) Sourcify feed (pre-fetched /tmp/sourcify-feed-1949.json, 200) ----
seen = json.load(open(BASE+"hot-leg-seen.json"))
try:
    feed = json.load(open("/tmp/sourcify-feed-1949.json"))
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    addrs, vers = [], []
    for e in results:
        if isinstance(e, str): a, v = e, None
        else:
            a = e.get("address") or (e.get("contract") or {}).get("address")
            v = e.get("verifiedAt") or (e.get("contract") or {}).get("verifiedAt")
        if a: addrs.append(a); vers.append(v)
    out["sourcify_feed"] = {"total": len(addrs), "top": addrs[0] if addrs else None,
        "top_verifiedAt": vers[0] if vers else None, "all": addrs, "fetch": "pre-fetched /tmp/sourcify-feed-1949.json (200)"}
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
# fresh reload before write (concurrent-writer race with main 30-min job)
seen = json.load(open(BASE+"hot-leg-seen.json"))
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
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["seen_n_after_feed"] = len(seen)

# ---- (2) Boltbook EN + ZH (pre-fetched /tmp/bb-{en,zh}-1949.html, both 200) ----
out["boltbook"] = {}
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']
for lang in ("en","zh"):
    try:
        html = open(f"/tmp/bb-{lang}-1949.html").read()
        open(BASE+f"hot-leg-2026-11-19-1949-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen = json.load(open(BASE+"hot-leg-seen.json"))  # fresh reload each write
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
        json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    except Exception as ex:
        out["boltbook"][lang] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}
out["seen_n_after_boltbook"] = len(json.load(open(BASE+"hot-leg-seen.json")))

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
    out["bridge_scan"] = {"total": len(bc), "not_in_snapshot": len(not_in),
        "not_in_snapshot_list": not_in, "same_owner_discarded": len(discarded),
        "note": "DGF 0x01f9... unchanged vs 18:44/18:49/18:54/18:59/19:04/19:14/19:24/19:44 runs if still the only one; noted for main 30-min job only, NOT a new lead."}
except Exception as ex:
    out["bridge_scan"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "note": "bridge skip - run continues"}

# ---- (3) leg 3: on-chain verify of any new sale-shape hits ----
def call(to, data):
    try:
        return race("eth_call", [{"to": to, "data": data}, "latest"], timeout=10)
    except Exception as ex:
        return {"error": f"{type(ex).__name__}: {str(ex)[:100]}"}
leg3 = {}
for a in out["shape_hits"]:
    s = next((x for x in shapes if x["address"]==a), {})
    vals = {}
    for fv in (s.get("free_views") or [])[:3]:
        r = call(a, sel(fv+"()"))
        vals[fv] = iv(r) if isinstance(r, str) else r
    r = call(a, sel("freeClaimed(address)")+UA)
    vals["freeClaimed_user"] = iv(r) if isinstance(r, str) else r
    leg3[a] = vals
    seen = json.load(open(BASE+"hot-leg-seen.json"))
    seen[a] = {"first_seen_wib": NOW, "source": seen.get(a,{}).get("source","sourcify-feed"),
               "status": "sale-shape-pass-age-unverified",
               "note": "Sale shape pass, pool/slot read this run, launch age UNVERIFIED -> watchlist-only, never reported as lead; main 30-min job to verify age."}
    json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["leg3"] = leg3 if leg3 else "none - shape_hits empty"

# ---- (4) leg-4 trimmed focus set, sequential race() single calls ----
ITEMS = [
 ("STOCKAGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply","totalSupply()",""),("freeLeft","freeLeft()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("mintOpen","mintOpen()",""),("quote_user_1","quote(address,uint256)","addr_uint1"),
   ("freeMintedByWallet_user","freeMintedByWallet(address)","addr"),
   ("balanceOf_user","balanceOf(address)","addr")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply","totalSupply()",""),("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("mintOpen","mintOpen()",""),("balanceOf_user","balanceOf(address)","addr"),
   ("mintedBy_user","mintedBy(address)","addr")]),
 ("AUGENT", "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
  [("freeClaimed","freeClaimed()",""),("freeClaimed_user","freeClaimed(address)","addr"),
   ("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched","launched()",""),("failed","failed()",""),("isRefundPhase","isRefundPhase()",""),
   ("totalShares","totalShares()",""),("tokenClaimed_user","tokenClaimed(address)","addr")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),("totalSupply","totalSupply()","")]),
 ("bsccat-sale", "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
  [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()","")]),
]
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
    for vk, sig, argt in views:
        data = sel(sig)
        if argt == "addr": data += UA
        elif argt == "addr_uint1": data += UA + enc_uint(1)[2:]
        r = call(addr, data)
        reads[name]["views"][vk] = iv(r) if isinstance(r, str) else r
try:
    blk = int(race("eth_blockNumber", [], timeout=8), 16)
except Exception:
    blk = None
json.dump({"started_wib": NOW, "block": blk, "reads": reads},
          open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["leg4_block"] = blk
out["leg4_items"] = len(reads)
try:
    prev = json.load(open(BASE+"hot-leg-run-2026-11-19-1944-reread.json"))
    prev_reads = prev.get("reads", {})
except Exception as ex:
    prev_reads = {}
    out["leg4_prev_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
changes = {}
for k, cur in reads.items():
    pv = prev_reads.get(k, {}).get("views", {})
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        pvv = pv.get(kk)
        # compare only int-vs-int; error dicts / None count as unreadable, not a change
        if isinstance(vv, int) and isinstance(pvv, int) and pvv != vv:
            diff[kk] = {"prev": pvv, "now": vv}
        elif isinstance(vv, int) and pvv is None:
            diff[kk] = {"prev": "unreadable-1944", "now": vv}
    changes[k] = diff
out["leg4_changes_vs_1944_reread"] = changes
def pct(c, t):
    c, t = num(c), num(t)
    return round(100*c/t, 1) if c is not None and t else None
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
st_fs, st_fl = num(st.get("FREE_SUPPLY")), num(st.get("freeLeft"))
stock_pct = pct((st_fs - st_fl) if st_fs is not None and st_fl is not None else None, st_fs)
lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY"))
aone = reads["AONE-sale"]["views"]; bsc = reads["bsccat-sale"]["views"]
out["threshold_check"] = {
  "STOCKAGENT_free_pct": stock_pct,
  "STOCKAGENT": st,
  "Lumenhold_free_pct": lumen_pct,
  "Lumenhold": lu,
  "AUGENT": reads["AUGENT"]["views"],
  "binanceai": reads["binanceai-mint"]["views"],
  "AONE_sale": aone,
  "bsccat_sale": bsc,
  "notes": "Strong-lead bar >70% + age <24h + slot open + website gate. STOCKAGENT 70% crossing reported 18 Nov 18:49; Lumenhold age UNVERIFIED + website None - no promotion. AONE sold out already reported; bsccat watch only. No promotion unless a leg flips."}
out["elapsed_s"] = round(time.time()-START, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
json.dump(out, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
