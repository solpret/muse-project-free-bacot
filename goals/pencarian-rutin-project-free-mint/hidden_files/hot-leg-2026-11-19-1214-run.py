#!/usr/bin/env python3
"""hot-leg run 2026-11-19 12:14 WIB (light pattern: light leg-4 done 12:09, 5 min ago, THVX sellout reported 1209).
Legs 1+2 (Sourcify feed + Boltbook EN/ZH), shape-check new contracts,
leg 3 on-chain verify for new S1/S2 contracts, bridge leg (read-only),
light leg 4: targeted re-read STOCKAGENT / Lumenhold / AgentBubble / AUGENT / binanceai-mint vs 1204.
Read-only except hot-leg-seen.json notes and this run's own outputs. No preview/mint/claim."""
import json, re, time, urllib.request, subprocess, base64
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "free-mint-hot-leg 2026-11-19 12:14 WIB"
out = {"run": RUN, "started_wib": NOW}

def fetch(url, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))

# --- Leg 1: Sourcify feed ---
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    items = feed if isinstance(feed, list) else feed.get("results", [])
    contracts = []
    va = []
    for c in items:
        if isinstance(c, dict) and c.get("address"):
            contracts.append(c["address"])
            if c.get("verifiedAt"): va.append(c["verifiedAt"])
    seen_l = {k.lower() for k in seen}
    new = [a for a in contracts if a.lower() not in seen_l and a.lower() != REGISTRY.lower()]
    out["sourcify_feed"] = {"total": len(contracts), "new": len(new), "new_contracts": new,
                            "top": contracts[0] if contracts else None,
                            "top_verifiedAt": max(va) if va else None,
                            "all": contracts, "fetch": "direct curl"}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}
    new = []

# --- Leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = fetch(url, timeout=20)
    open(BASE + f"hot-leg-2026-11-19-1214-boltbook-{lang}.html", "wb").write(raw)
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    low = text.lower()
    figs = re.findall(r"[^<>]{0,90}(?:1,?[0-9]{2,3}/1,?[0-9]{2,3}|minted|free)[^<>]{0,60}", text)[:8]
    return {"bytes": len(raw), "http_code": "200", "full_address_contracts": len(addrs),
            "addresses": addrs, "new": 0, "new_contracts": [],
            "free_kw": sum(low.count(k) for k in ("free share", "first share free", "1 free share", "free mint share")),
            "zh_free_kw": sum(text.count(k) for k in ("免费份额", "首个免费", "免费铸造", "免费mint")),
            "figures": figs}
bb = {}
for lang in ("en", "zh"):
    try: bb[lang] = boltbook(lang)
    except Exception as e: bb[lang] = {"error": f"{type(e).__name__}: {e}"}
out["boltbook_en"] = bb["en"]; out["boltbook_zh"] = bb["zh"]
bb_new = []
seen_l = {k.lower() for k in seen}
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addresses", []):
        if a.lower() not in seen_l and a.lower() not in [x.lower() for x in bb_new]:
            bb_new.append(a)
for lang in ("en", "zh"):
    if "new_contracts" in bb.get(lang, {}):
        bb[lang]["new"] = len([a for a in bb[lang]["addresses"] if a.lower() not in seen_l])
        bb[lang]["new_contracts"] = [a for a in bb[lang]["addresses"] if a.lower() not in seen_l]

# --- Shape-check new contracts ---
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
def shape(addr):
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
        va2 = d.get("verifiedAt") or (d.get("stdJson", {}) or {}).get("verifiedAt")
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {e}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and noarg_free and bool(free) and agent
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free, "agent_ref": agent, "is_token": tokenish,
            "n_fns": len(abi), "status": "checked", "verifiedAt": va2}
EXCLUDED = ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493")
shape_res = {}
for a in (new + bb_new):
    if a.lower() in EXCLUDED:
        shape_res[a] = {"status": "excluded-example"}
        continue
    shape_res[a] = shape(a)
out["shape_check_targets"] = new + bb_new
out["shape_check"] = [dict({"address": a}, **shape_res[a]) for a in (new + bb_new)]
out["shape_hits"] = [a for a in (new + bb_new) if shape_res.get(a, {}).get("S1") or shape_res.get(a, {}).get("S2")]
out["seen_added"] = [a for a in (new + bb_new) if a.lower() not in seen_l]

# --- Leg 3 helpers ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def dec_str(hexs):
    try:
        b = bytes.fromhex(hexs[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", errors="ignore")
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

leg3 = {}
U = [USER]
snap_cache = None
for a in (new + bb_new):
    sh = shape_res.get(a, {})
    if not (sh.get("S1") or sh.get("S2")):
        continue
    views = [("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
             ("FREE_PER_WALLET", "FREE_PER_WALLET()", []), ("freeLeft_user", "freeLeft(address)", U),
             ("freeUsed_user", "freeUsed(address)", U), ("freeFor_user1", "freeFor(address,uint256)", [USER, 1]),
             ("quote_user1", "quote(address,uint256)", [USER, 1]),
             ("AGENT_ID", "AGENT_ID()", []), ("agentIdRequired", "agentIdRequired()", []),
             ("mintOpen", "mintOpen()", []), ("totalSupply", "totalSupply()", []),
             ("name", "name()", []), ("symbol", "symbol()", []), ("contractURI", "contractURI()", [])]
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": a, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if isinstance(res, list) and len(res) == len(calls):
                got = (res, ep); break
        except Exception as e:
            print("  leg3 ep", ep, "exc", str(e)[:80], flush=True); continue
    if got is None:
        leg3[a] = {"error": "all RPC endpoints failed"}
        continue
    res, ep = got
    vals = {}
    for it, key in zip(res, meta):
        if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
            vals[key] = None
        else:
            r = it["result"]
            if key in ("name", "symbol", "contractURI"):
                vals[key] = dec_str(r)
            elif key == "AGENT_ID":
                vals[key] = "0x" + r[-40:] if len(r) >= 42 else r
            else:
                vals[key] = to_int(r[:66]) if len(r) >= 66 else r
    cu = vals.get("contractURI") or ""
    ext = None
    if cu.startswith("data:application/json;base64,"):
        try:
            ext = json.loads(base64.b64decode(cu.split(",", 1)[1]).decode("utf-8", errors="ignore"))
        except Exception as e:
            ext = {"decode_error": str(e)[:80]}
    elif cu.startswith("{"):
        try: ext = json.loads(cu)
        except Exception: ext = None
    vals["contractURI_json"] = ext
    if snap_cache is None:
        snap_cache = json.load(open(BASE + "onchain-snapshot.json"))
    in_snap = False
    for sec in ("contracts", "track_c"):
        for v in (snap_cache.get(sec) or {}).values():
            if isinstance(v, dict):
                for f in ("address", "sale", "contract", "token"):
                    if isinstance(v.get(f), str) and v[f].lower() == a.lower():
                        in_snap = True
    vals["in_main_snapshot"] = in_snap
    vals["rpc_ep"] = ep
    leg3[a] = vals
out["leg3"] = leg3

for a in (new + bb_new):
    if a.lower() not in seen_l:
        note = json.dumps(shape_res.get(a, {}))[:300]
        if a in leg3:
            note = json.dumps(leg3[a])[:400]
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new else "boltbook",
                   "status": shape_res.get(a, {}).get("status", "checked"),
                   "note": note}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_n"] = len(seen)

# --- Bridge leg (read-only) ---
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    def _addr_vals(section, fields):
        o = set()
        for v in (snap.get(section) or {}).values():
            if isinstance(v, dict):
                for f in fields:
                    x = v.get(f)
                    if isinstance(x, str) and x.startswith("0x") and len(x) == 42:
                        o.add(x.lower())
        return o
    snap_addrs = (_addr_vals("contracts", ["address", "sale", "contract"])
                  | _addr_vals("track_c", ["sale", "address", "token", "contract"])
                  | _addr_vals("pending_claims", ["address", "sale", "mint"]))
    outside = []
    discarded = 0
    for addr, info in bcontracts.items():
        if info.get("same_owner_discarded"):
            discarded += 1
            continue
        if addr.lower() not in snap_addrs:
            outside.append(addr)
    out["bridge_scan"] = {"total": len(bcontracts), "not_in_snapshot": len(outside),
                          "not_in_snapshot_list": outside, "same_owner_discarded": discarded}
    out["snapshot_counts"] = {"contracts": len(snap.get("contracts") or {}),
                              "track_c": len(snap.get("track_c") or {}),
                              "pending_claims": len(snap.get("pending_claims") or {})}
except Exception as e:
    out["bridge_scan"] = {"error": f"{type(e).__name__}: {e}"}

# --- Light leg 4: targeted re-read vs 1204 ---
V = lambda name, sig, args=None: (name, sig, args or [])
TARGETS = {
 "STOCKAGENT": ("0xba7068233da805bdebcc167be361c219002e6b7f",
    [V("totalSupply","totalSupply()"), V("freeLeft","freeLeft()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("quote_user_1","quote(address,uint256)",[USER,1]),
     V("freeMintedByWallet_user","freeMintedByWallet(address)",U), V("balanceOf_user","balanceOf(address)",U)]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f",
    [V("totalSupply","totalSupply()"), V("freeClaimed","freeClaimed()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U),
     V("mintedBy_user","mintedBy(address)",U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b",
    [V("freeMinted","freeMinted()"), V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "AUGENT": ("0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
    [V("freeClaimed","freeClaimed()"), V("freeClaimedByWallet_user","freeClaimedByWallet(address)",U),
     V("totalSupply","totalSupply()"), V("name","name()"), V("symbol","symbol()")]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [V("launched","launched()"), V("failed","failed()"), V("isRefundPhase","isRefundPhase()"),
     V("totalShares","totalShares()"), V("tokenClaimed_user","tokenClaimed(address)",U)]),
}
def read_views(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            o = {}
            for it, key in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o[key] = None
                else:
                    r = it["result"]
                    if key in ("name", "symbol"):
                        o[key] = dec_str(r)
                    else:
                        o[key] = to_int(r[:66]) if len(r) >= 66 else r
            return o, ep
        except Exception:
            continue
    return None, None

reads = {}
for name, (addr, views) in TARGETS.items():
    v, ep = read_views(addr, views)
    reads[name] = {"address": addr, "views": v, "rpc_ep": ep}
    print(f"target {name}: {v} via {ep} ({time.time()-T0:.0f}s)", flush=True)

blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=10)
        if isinstance(r, dict) and r.get("result"):
            blk = int(r["result"], 16); break
    except Exception:
        continue
reread = {"started_wib": NOW, "reads": reads, "reads_total": len(TARGETS),
          "elapsed_s": round(time.time() - T0, 1), "block": blk}
json.dump(reread, open(BASE + "hot-leg-run-2026-11-19-1214-reread.json", "w"), indent=1)
out["leg4_reread_file"] = "hot-leg-run-2026-11-19-1214-reread.json"
out["leg4_block"] = blk

# --- Diff vs 1204 ---
try:
    prev = json.load(open(BASE + "hot-leg-run-2026-11-19-1209.json"))
    tc_prev = prev.get("threshold_check") or {}
    changes = {}
    # STOCKAGENT / Lumenhold / AgentBubble from 1134 threshold_check
    prev_sa = tc_prev.get("STOCKAGENT") or {}
    cur_sa = (reads.get("STOCKAGENT") or {}).get("views") or {}
    changes["STOCKAGENT"] = {k: {"prev": prev_sa.get(k), "now": cur_sa.get(k)}
                             for k in set(list(prev_sa.keys()) + list(cur_sa.keys()))
                             if prev_sa.get(k) != cur_sa.get(k)}
    prev_lu = tc_prev.get("Lumenhold") or {}
    cur_lu = (reads.get("Lumenhold") or {}).get("views") or {}
    changes["Lumenhold"] = {k: {"prev": prev_lu.get(k), "now": cur_lu.get(k)}
                            for k in set(list(prev_lu.keys()) + list(cur_lu.keys()))
                            if prev_lu.get(k) != cur_lu.get(k)}
    prev_ab = tc_prev.get("AgentBubble") or {}
    cur_ab = (reads.get("AgentBubble") or {}).get("views") or {}
    changes["AgentBubble"] = {k: {"prev": prev_ab.get(k), "now": cur_ab.get(k)}
                              for k in set(list(prev_ab.keys()) + list(cur_ab.keys()))
                              if prev_ab.get(k) != cur_ab.get(k)}
    prev_au = tc_prev.get("AUGENT") or {}
    cur_au = (reads.get("AUGENT") or {}).get("views") or {}
    changes["AUGENT"] = {k: {"prev": prev_au.get(k), "now": cur_au.get(k)}
                         for k in set(list(prev_au.keys()) + list(cur_au.keys()))
                         if prev_au.get(k) != cur_au.get(k)}
    prev_bn = tc_prev.get("binanceai_pending") or {}
    cur_bn = (reads.get("binanceai-mint") or {}).get("views") or {}
    changes["binanceai_pending"] = {k: {"prev": prev_bn.get(k), "now": cur_bn.get(k)}
                                    for k in set(list(prev_bn.keys()) + list(cur_bn.keys()))
                                    if prev_bn.get(k) != cur_bn.get(k)}
    out["leg4_changes_vs_1209"] = changes
except Exception as e:
    out["leg4_changes_vs_1209"] = {"error": f"{type(e).__name__}: {e}"}

# --- Threshold check (strong lead >70% + age <24h + slot open) ---
tc = {"notes": "Strong-lead bar >70% + age <24h + slot open. STOCKAGENT 77.1% at 1209 but age UNVERIFIED + websiteGate unverified (snapshot); 70% crossing reported 18 Nov 18:49. Lumenhold 84.2% at 1209 but age UNVERIFIED + website None + slot-free UNVERIFIED (watchlist-only-age-unverified 17 Nov) - no promotion. AgentBubble sold out total 2222/2222 (reported 03:59 change-observed-not-reported). No promotion unless a leg flips."}
try:
    sa = (reads.get("STOCKAGENT") or {}).get("views") or {}
    if sa.get("freeLeft") is not None and sa.get("FREE_SUPPLY"):
        tc["STOCKAGENT_free_pct"] = round(100 * (sa["FREE_SUPPLY"] - sa["freeLeft"]) / sa["FREE_SUPPLY"], 1)
    tc["STOCKAGENT"] = {k: sa.get(k) for k in ("totalSupply","freeLeft","FREE_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user")}
    lu = (reads.get("Lumenhold") or {}).get("views") or {}
    if lu.get("freeClaimed") is not None and lu.get("FREE_SUPPLY"):
        tc["Lumenhold_free_pct"] = round(100 * lu["freeClaimed"] / lu["FREE_SUPPLY"], 1)
    tc["Lumenhold"] = {k: lu.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","mintOpen","balanceOf_user","mintedBy_user")}
    ab = (reads.get("AgentBubble") or {}).get("views") or {}
    if ab.get("freeMinted") is not None and ab.get("MAX_SUPPLY"):
        tc["AgentBubble_free_pct"] = round(100 * ab["freeMinted"] / ab["MAX_SUPPLY"], 1)
    tc["AgentBubble"] = {k: ab.get(k) for k in ("freeMinted","totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user")}
    au = (reads.get("AUGENT") or {}).get("views") or {}
    tc["AUGENT"] = {k: au.get(k) for k in ("freeClaimed","freeClaimedByWallet_user","totalSupply","name","symbol")}
    bn = (reads.get("binanceai-mint") or {}).get("views") or {}
    tc["binanceai_pending"] = {k: bn.get(k) for k in ("launched","failed","isRefundPhase","totalShares","tokenClaimed_user")}
except Exception as e:
    tc["error"] = f"{type(e).__name__}: {e}"
out["threshold_check"] = tc

# --- Poffzi FCFS process check ---
try:
    r = subprocess.run(["pgrep", "-af", "fcfs"], capture_output=True, text=True)
    out["poffzi_fcfs"] = r.stdout.strip() if r.stdout.strip() else "NO PROCESS FOUND"
except Exception as e:
    out["poffzi_fcfs"] = f"check error: {e}"

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE + "hot-leg-run-2026-11-19-1214.json", "w"), indent=1)
print("DONE block", blk, "elapsed", round(time.time() - T0, 1))
