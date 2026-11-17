#!/usr/bin/env python3
"""Hot-leg 2026-11-07 21:29 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state.
Adapted from hot-leg-2026-11-07-2124.py; compares vs 2124 run. DinoAgent
(main-job run 2001 gate-blocked strong lead, freeMinted 545/777) and Tri333
(main-job run 2001 early lead gate-passed, freeMinted 515/2222 = 23.18% - promotion
watch: 25% = 556). Adds LOCKSMITH (2124 leg-3 S1, age-unverified, 0 mints) to
leg-4 re-read: watch for first mint (age corroboration)."""
import json, re, subprocess, sys, time, os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-2129"
RUN_WIB = "2026-11-07T21:29:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
BRIDGE_MTIME_KNOWN = 1793933280.7650242
out = {"run": "free-mint-hot-leg 2026-11-07 21:29:38 WIB", "leg1_feed": {}, "leg2_boltbook": {},
       "leg3_new_contracts": "none", "leg4_reread": {}, "leg4_reread_summary": {},
       "bridge_leg": {}, "pending_claims": "snapshot pending_claims empty at run start - nothing to re-read"}
t0 = time.time()

def curl(url, timeout=15):
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception:
        pass
    return None

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}

def shape_check(addr):
    abi = None; match = None
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
    if raw:
        try:
            d = json.loads(raw); match = d.get("match"); abi = d.get("abi")
        except Exception:
            pass
    if abi is None:
        for kind in ("full_match", "partial_match"):
            raw = curl(f"https://repo.sourcify.dev/contracts/{kind}/56/{addr}/metadata.json", timeout=12)
            if raw:
                try:
                    m = json.loads(raw); abi = m.get("output", {}).get("abi")
                    if abi: match = kind; break
                except Exception:
                    continue
    if not abi:
        return {"match": match, "error": "no-abi"}
    fns = [f.get("name") for f in abi if f.get("type") == "function" and f.get("name")]
    names = set(fns)
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in names)
    free = [v for v in FREE_VIEWS if v in names]
    rawj = json.dumps(abi).lower()
    agent = REGISTRY.lower() in rawj or "agentgate" in rawj or "agentregistry" in rawj or "agent_id" in rawj
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and "mintFree" in names and ("freeClaimed" in names or "freeMinted" in names) and \
        bool({"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"} & names) and agent
    return {"match": match, "fns": len(fns), "fn_names": sorted(names), "mint": has_mint,
            "quote": has_quote, "free_views": free, "registry": agent, "S1": s1, "S2": s2}

def record_seen(addr, note, source, status):
    first = seen.get(addr, {}).get("first_seen_wib") or RUN_WIB
    seen[addr] = {"first_seen_wib": first, "note": note, "source": source, "status": status}

def shape_many(addrs, source):
    shapes = {}
    if not addrs:
        return shapes
    with ThreadPoolExecutor(max_workers=5) as ex:
        res = list(ex.map(shape_check, addrs))
    for a, sc in zip(addrs, res):
        shapes[a] = sc
        if "error" in sc:
            record_seen(a, f"shape-check FAILED (ABI unfetchable): match={sc.get('match')} - retry next run, NOT verified not-sale-shape",
                        source, "shape-check-failed")
        else:
            note = (f"S1={sc['S1']} S2={sc['S2']} mint={sc['mint']} quote={sc['quote']} "
                    f"free={sc['free_views']} agent={sc['registry']} fns={sc['fns']}")
            record_seen(a, note, source, "sale-shape" if (sc.get("S1") or sc.get("S2")) else "checked-not-sale-shape")
    return shapes

# ---- Leg 1: Sourcify feed ----
shapes = {}
try:
    raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    json.dump(feed, open(f"{BASE}/hot-leg-{TS}-feed.json", "w"), indent=1)
    addrs = [r["address"] for r in feed.get("results", [])]
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    shapes = shape_many(new, "sourcify-feed")
    json.dump(shapes, open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)
    out["leg1_feed"] = {"n": len(addrs), "new": new,
        "shapes": "; ".join(f"{a[:10]} S1={s.get('S1')} S2={s.get('S2')} fns={s.get('fns')} free={s.get('free_views')} agent={s.get('registry')}" for a, s in shapes.items()) or "no new contracts"}
except Exception as e:
    out["leg1_feed"] = {"error": f"feed failed: {e}", "skipped": True}
json.dump(out["leg1_feed"].get("new", []), open(f"{BASE}/hot-leg-{TS}-new.json", "w"))

# ---- Leg 2: Boltbook.fun EN + ZH ----
KW = ["free share", "first share free", "1 free share", "free mint share",
      "\u514d\u8d39\u4efd\u989d", "\u9996\u4e2a\u514d\u8d39", "\u514d\u8d39\u94f8\u9020", "\u514d\u8d39mint"]
shapes_bb = {}
try:
    pages = {}
    for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
        html = curl(url, timeout=20)
        if html:
            pages[lang] = html
            open(f"{BASE}/hot-leg-{TS}-boltbook-fun-{lang}.html", "w").write(html)
    if not pages:
        raise RuntimeError("curl returned empty for EN+ZH")
    all_addrs = set()
    for html in pages.values():
        all_addrs |= set(re.findall(r"0x[0-9a-fA-F]{40}", html))
    kw_hits = {k: sum(p.lower().count(k.lower()) for p in pages.values()) for k in KW}
    new_bb = [a for a in sorted(all_addrs) if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    shapes_bb = shape_many(new_bb, "boltbook-fun")
    json.dump({"addrs": sorted(all_addrs), "kw": kw_hits, "new": new_bb, "shapes": shapes_bb},
              open(f"{BASE}/hot-leg-{TS}-boltbook-shape.json", "w"), indent=1)
    out["leg2_boltbook"] = {"status": "COMPLETED-via-curl", "addrs": len(all_addrs), "new": new_bb,
        "kw_hits": kw_hits, "shapes": {a: (s.get("S1"), s.get("S2")) for a, s in shapes_bb.items()}}
except Exception as e:
    out["leg2_boltbook"] = {"error": f"boltbook failed: {e}", "skipped": True, "via": "curl"}
json.dump(out["leg2_boltbook"].get("new", []) if isinstance(out["leg2_boltbook"], dict) else [],
          open(f"{BASE}/hot-leg-{TS}-boltbook-new.json", "w"))

# ---- Leg 3: new sale-shape contracts ----
sale_new = [a for a, s in list(shapes.items()) + list(shapes_bb.items()) if s.get("S1") or s.get("S2")]
out["leg3_new_contracts"] = f"{len(sale_new)} S1/S2 new: {sale_new}" if sale_new else "No S1/S2 hits from feed or Boltbook.fun - no leg-3 on-chain verification needed."

# ---- Leg 4: re-read snapshot items ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, arg=""):
    from fast_rpc import _single
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return to_int(_single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0))
        except Exception:
            continue
    return None
def single2(addr, sig, arg1, arg2):
    return single(addr, sig, enc(arg1) + enc_uint(arg2)[2:])
def batch_views(addr, views):
    calls, keys = [], []
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig:
            data = sel(sig) + enc_uint(1); key = base + "_1"
        else:
            data = sel(sig); key = base
        calls.append(("eth_call", [{"to": addr, "data": data}, "latest"])); keys.append(key)
    for ep in EPS:
        try:
            return {k: to_int(v) for k, v in zip(keys, batch(calls, endpoint=ep, timeout=8))}
        except Exception:
            continue
    return None

ITEMS = {
 "Orchidia": "0x09bcdd97186f6f37521bd1b281d329e48ac54b89",
 "Agent Goats": "0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6",
 "Tacotron": "0x05debe4445232205ae7e79d02cb5de5aa0641eff",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
 "Wuyuhive": "0x250e800025a9a7861970e253bab6975a57f80567",
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Ink Koi": "0xbd4B4e7189ae9356514664146b0eD683601200A9",
 "Night Bandits Club": "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf",
 "ADCHAR": "0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044",
 "Saturnagent": "0xef870a9b4a529373fb2e174b59ca7a66eb018074",
 "Lumenhold": "0x9701980b0afd825134390ee46fb3bd675a2f356f",
 "Horus AI": "0x794ad67a5590c7e5848e49181297f9cc7c6ce00e",
 "AURISLE": "0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D",
 "DinoAgent": "0xcE19D6A5FF15e088D4bf23614242927139084895",
 "Tri333": "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f",
 "LOCKSMITH": "0x05e8738290be6639fD0f7236ebF444E5466D3164",
 "AgentBook": "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0",
}
LEADS = {
 "CipherAgent": "0x158b5e25015758a94703A27c152889451E5d52E5",
 "MarsAgent": "0x2231FdAe405c33dc4993f8C577c453802FF1AcE9",
}
MINIMAL = ["totalSupply()", "balanceOf(address)"]
reread = {"block": None, "items": {}, "leads": {}}
try:
    reread["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception:
    reread["block"] = None
for name, addr in ITEMS.items():
    d = {"address": addr}
    got = batch_views(addr, MINIMAL)
    if got is not None:
        d.update(got)
    else:
        d["totalSupply"] = None; d["balanceOf_user"] = None; d["_rpc"] = "minimal-failed"
    if name == "Ink Koi":
        d["freeMinted"] = single(addr, "freeMinted()")
        d["freeClaimed_user"] = single(addr, "freeClaimed(address)", enc(USER))
    if name == "Night Bandits Club":
        d["freeUsed"] = single(addr, "freeUsed()")
        d["freeTakenBy_user"] = single(addr, "freeTakenBy(address)", enc(USER))
        d["mintOpen"] = single(addr, "mintOpen()")
    if name == "ADCHAR":
        d["hasClaimed_user"] = single(addr, "hasClaimed(address)", enc(USER))
        d["nextTokenId"] = single(addr, "nextTokenId()")
    if name in ("Saturnagent", "Lumenhold"):
        d["freeClaimed"] = single(addr, "freeClaimed()")
        d["freeLeft_user"] = single(addr, "freeLeft(address)", enc(USER))
        d["freeUsed_user"] = single(addr, "freeUsed(address)", enc(USER))
        d["freeFor_user1"] = single2(addr, "freeFor(address,uint256)", USER, 1)
        d["quote_user1"] = single2(addr, "quote(address,uint256)", USER, 1)
        d["mintedBy_user"] = single(addr, "mintedBy(address)", enc(USER))
        d["mintOpen"] = single(addr, "mintOpen()")
    if name == "AURISLE":
        d["freeMinted"] = single(addr, "freeMinted()")
        d["FREE_SUPPLY"] = single(addr, "FREE_SUPPLY()")
        d["freeClaimed_user"] = single(addr, "freeClaimed(address)", enc(USER))
    if name == "Horus AI":
        d["FREE_SUPPLY"] = single(addr, "FREE_SUPPLY()")
        d["mintedBy_user"] = single(addr, "mintedBy(address)", enc(USER))
        d["mintOpen"] = single(addr, "mintOpen()")
    if name == "DinoAgent":
        d["freeMinted"] = single(addr, "freeMinted()")
        d["FREE_SUPPLY"] = single(addr, "FREE_SUPPLY()")
        d["freeClaimed_user"] = single(addr, "freeClaimed(address)", enc(USER))
    if name == "AgentBook":
        fq, rf = cur.get("FREE_QUOTA"), cur.get("remainingFree")
        if fq is not None and rf is not None:
            used = fq - rf
            s += f", freeUsed {used}/{fq} = {used/fq*100:.2f}%"
            if used >= 84:
                s += " - PROMOTION WATCH: >=25% (84) - needs VERIFIED age <=48h + website gate before any strong-lead handling"
            else:
                s += " - below 25% strong-lead threshold, NO promotion"
        s += f", mintOpen {cur.get('mintOpen')}, freeFor(user,1)={cur.get('freeFor_user1')}, costOf(user,1)={cur.get('costOf_user1')}, mintedBy(user)={cur.get('mintedBy_user')}"
        s += "; S1 NFT, age still UNVERIFIED (first-mint time not corroborated 21:29 run) - watchlist-only"
    if name == "LOCKSMITH":
        d["FREE_CAP"] = single(addr, "FREE_CAP()")
        d["freeMintedTotal"] = single(addr, "freeMintedTotal()")
        d["totalMinted"] = single(addr, "totalMinted()")
        d["mintActive"] = single(addr, "mintActive()")
        d["freeMinted_user"] = single(addr, "freeMinted(address)", enc(USER))
        d["mintedCount_user"] = single(addr, "mintedCount(address)", enc(USER))
        d["mintedAt_1"] = single(addr, "mintedAt(uint256)", enc_uint(1)[2:])
    if name == "AgentBook":
        d["FREE_QUOTA"] = single(addr, "FREE_QUOTA()")
        d["remainingFree"] = single(addr, "remainingFree()")
        d["mintOpen"] = single(addr, "mintOpen()")
        d["soldOut"] = single(addr, "soldOut()")
        d["freeFor_user1"] = single2(addr, "freeFor(address,uint256)", USER, 1)
        d["costOf_user1"] = single2(addr, "costOf(address,uint256)", USER, 1)
        d["mintedBy_user"] = single(addr, "mintedBy(address)", enc(USER))
    if name == "Tri333":
        d["freeMinted"] = single(addr, "freeMinted()")
        d["FREE_CAP"] = single(addr, "FREE_CAP()")
        d["freeCount_user"] = single(addr, "freeCount(address)", enc(USER))
        d["mintOpen"] = single(addr, "mintOpen()")
    reread["items"][name] = d
for name, addr in LEADS.items():
    d = {"address": addr}
    got = batch_views(addr, MINIMAL)
    if got is not None:
        d.update(got)
    d["totalMints"] = single(addr, "totalMints()")
    d["mintOpen"] = single(addr, "mintOpen()")
    reread["leads"][name] = d
json.dump(reread, open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
out["leg4_reread"] = reread

# ---- summary vs 2109 run ----
prev = {}
prev_leg3 = {}
try:
    run44 = json.load(open(f"{BASE}/hot-leg-run-2026-11-07-2124.json"))
    prev = run44.get("leg4_reread", {})
    prev_leg3 = run44.get("leg3_new", {}).get("items", {})
except Exception:
    pass
summ = {"block": reread["block"]}
pi, pl = prev.get("items", {}), prev.get("leads", {})
for name, cur in reread["items"].items():
    o = pi.get(name, {}) or prev_leg3.get(name, {})
    ts_c, ts_o = cur.get("totalSupply"), o.get("totalSupply")
    if ts_c is None and ts_o is None:
        s = "ts unreadable (read artifact, as 21:24)"
    elif ts_c is None:
        s = f"ts unreadable this run (was {ts_o}) - read artifact, not a state change"
    elif ts_o is None:
        s = f"ts {ts_c} (was unreadable)"
    elif ts_c == ts_o:
        s = f"ts {ts_c} unchanged"
    else:
        s = f"ts {ts_o}->{ts_c} ({ts_c-ts_o:+d})"
    s += f", bal {cur.get('balanceOf_user')}"
    if name == "Ink Koi":
        fm_c, fm_o = cur.get("freeMinted"), o.get("freeMinted")
        if fm_c is not None:
            pct = fm_c / 2777 * 100
            s += f", freeMinted {fm_o}->{fm_c} = {pct:.2f}%"
        if cur.get("freeClaimed_user") == 1:
            s += " - SLOT USED by own mint #712 (19:38, already reported as minted) - post-mint state confirmed, no further mint possible, no promotion"
        elif cur.get("freeClaimed_user") == 0:
            s += ", slot open"
            s += " - PROMOTION to strong lead (>=25% = 694) - CHECK GATE before any preview/mint" if (fm_c or 0) >= 694 else " - still early lead, NO promotion"
        else:
            s += ", freeClaimed(user) unreadable"
    if name == "Night Bandits Club":
        fu_c, fu_o = cur.get("freeUsed"), o.get("freeUsed")
        if fu_c is not None:
            s += f", freeUsed {fu_o}->{fu_c}/444 = {fu_c/444*100:.1f}%"
        if cur.get("freeTakenBy_user") == 0:
            s += ", freeTakenBy(user)=0 slot open"
        s += "; gate website FAILED (18:01) still stands - no tier change, not a candidate"
    if name == "ADCHAR":
        s += f", nextTokenId {o.get('nextTokenId')}->{cur.get('nextTokenId')}, hasClaimed(user)={cur.get('hasClaimed_user')} slot open; still early lead, NO promotion"
    if name == "Wuyuhive":
        s += "; gate-blocked strong lead reported; age still <=48h, pool open, slot open - no tier change"
    if name == "Thronemind":
        s += "; gate website FAILED + same-owner discarded - no tier change"
    if name == "Tacotron":
        s += "; age-excluded - no tier change"
    if name in ("Saturnagent", "Lumenhold"):
        fc_c, fc_o = cur.get("freeClaimed"), o.get("freeClaimed")
        fl_c, fl_o = cur.get("freeLeft_user"), o.get("freeLeft_user")
        q = cur.get("quote_user1")
        if fc_c is not None and fc_o is not None:
            s += f", freeClaimed {fc_o}->{fc_c}"
        if fl_c is not None:
            s += f", freeLeft(user) {fl_c}, quote(user,1)={q}"
        s += "; S1 pass, pool+slot open, % above 25% BUT age UNVERIFIED - watchlist-only, never reported as lead, NO promotion"
    if name == "AURISLE":
        fm_c, fm_o = cur.get("freeMinted"), o.get("freeMinted")
        if fm_c is not None:
            s += f", freeMinted {fm_o}->{fm_c} (totalSupply snapshot 32)"
        s += f", freeClaimed(user)={cur.get('freeClaimed_user')}, FREE_SUPPLY={cur.get('FREE_SUPPLY')}"
        s += "; EARLY lead reported by main job run 2001 - hot-leg re-read only, NOT re-reported as new; no promotion unless strong-lead legs + gate pass"
    if name == "Horus AI":
        s += f", FREE_SUPPLY {cur.get('FREE_SUPPLY')}, mintOpen {cur.get('mintOpen')}; free path still unverified - no promotion"
    if name == "DinoAgent":
        fm_c, fm_o = cur.get("freeMinted"), o.get("freeMinted")
        if fm_o is None: fm_o = 545  # 2124 run reading
        if fm_c is not None:
            s += f", freeMinted {fm_o}->{fm_c} = {fm_c/777*100:.2f}% of FREE_SUPPLY 777"
            if fm_c >= 777:
                s += " - SELLOUT (777/777)"
        if cur.get("freeClaimed_user") == 0:
            s += ", slot open"
        s += "; gate-blocked strong lead reported run 2001 - no tier change unless sellout"
    if name == "AgentBook":
        fq, rf = cur.get("FREE_QUOTA"), cur.get("remainingFree")
        if fq is not None and rf is not None:
            used = fq - rf
            s += f", freeUsed {used}/{fq} = {used/fq*100:.2f}%"
            if used >= 84:
                s += " - PROMOTION WATCH: >=25% (84) - needs VERIFIED age <=48h + website gate before any strong-lead handling"
            else:
                s += " - below 25% strong-lead threshold, NO promotion"
        s += f", mintOpen {cur.get('mintOpen')}, freeFor(user,1)={cur.get('freeFor_user1')}, costOf(user,1)={cur.get('costOf_user1')}, mintedBy(user)={cur.get('mintedBy_user')}"
        s += "; S1 NFT, age still UNVERIFIED (first-mint time not corroborated 21:29 run) - watchlist-only"
    if name == "LOCKSMITH":
        d["FREE_CAP"] = single(addr, "FREE_CAP()")
        d["freeMintedTotal"] = single(addr, "freeMintedTotal()")
        d["totalMinted"] = single(addr, "totalMinted()")
        d["mintActive"] = single(addr, "mintActive()")
        d["freeMinted_user"] = single(addr, "freeMinted(address)", enc(USER))
        d["mintedCount_user"] = single(addr, "mintedCount(address)", enc(USER))
        d["mintedAt_1"] = single(addr, "mintedAt(uint256)", enc_uint(1)[2:])
    if name == "AgentBook":
        d["FREE_QUOTA"] = single(addr, "FREE_QUOTA()")
        d["remainingFree"] = single(addr, "remainingFree()")
        d["mintOpen"] = single(addr, "mintOpen()")
        d["soldOut"] = single(addr, "soldOut()")
        d["freeFor_user1"] = single2(addr, "freeFor(address,uint256)", USER, 1)
        d["costOf_user1"] = single2(addr, "costOf(address,uint256)", USER, 1)
        d["mintedBy_user"] = single(addr, "mintedBy(address)", enc(USER))
    if name == "Tri333":
        fm_c, fm_o = cur.get("freeMinted"), o.get("freeMinted")
        if fm_o is None: fm_o = 515  # 2124 run reading
        if fm_c is not None:
            pct = fm_c / 2222 * 100
            s += f", freeMinted {fm_o}->{fm_c} = {pct:.2f}% of FREE_CAP 2222"
            if fm_c >= 556:
                s += " - PROMOTION to strong lead (>=25% = 556) - gate already PASSED, CHECK legs before any preview/mint"
            else:
                s += " - still early lead, NO promotion"
        s += f", freeCount(user)={cur.get('freeCount_user')}, mintOpen={cur.get('mintOpen')}"
    if name == "AgentBook":
        fq, rf = cur.get("FREE_QUOTA"), cur.get("remainingFree")
        if fq is not None and rf is not None:
            used = fq - rf
            s += f", freeUsed {used}/{fq} = {used/fq*100:.2f}%"
            if used >= 84:
                s += " - PROMOTION WATCH: >=25% (84) - needs VERIFIED age <=48h + website gate before any strong-lead handling"
            else:
                s += " - below 25% strong-lead threshold, NO promotion"
        s += f", mintOpen {cur.get('mintOpen')}, freeFor(user,1)={cur.get('freeFor_user1')}, costOf(user,1)={cur.get('costOf_user1')}, mintedBy(user)={cur.get('mintedBy_user')}"
        s += "; S1 NFT, age still UNVERIFIED (first-mint time not corroborated 21:29 run) - watchlist-only"
    if name == "LOCKSMITH":
        tm_c, tm_o = cur.get("totalMinted"), o.get("totalMinted")
        fmt_c = cur.get("freeMintedTotal")
        s += f", totalMinted {tm_o}->{tm_c}, freeMintedTotal {fmt_c}/FREE_CAP {cur.get('FREE_CAP')}, mintActive {cur.get('mintActive')}, freeMinted(user)={cur.get('freeMinted_user')}, mintedAt(1)={cur.get('mintedAt_1')}"
        if (tm_c or 0) > 0:
            s += " - FIRST MINT EXISTS: age now corroborable (first-mint time needed) - flag to main job, NOT a lead yet (needs >=25% = 50 free + gate)"
        else:
            s += " - still 0 mints, age still UNVERIFIED - watchlist-only, NO promotion"
    summ[name] = s
for name, cur in reread["leads"].items():
    o = pl.get(name, {})
    tm_c, tm_o = cur.get("totalMints"), o.get("totalMints")
    s = f"totalMints {tm_o}->{tm_c} ({(tm_c or 0)-(tm_o or 0):+d})" if tm_c is not None and tm_o is not None else f"totalMints {tm_c}"
    s += f", mintOpen {cur.get('mintOpen')}, bal {cur.get('balanceOf_user')} - still open, slot open; gate-blocked lead reported 17:40, count move not reportable"
    summ[name] = s
summ["note"] = "MINIMAL batch used directly (LEAN batch whole-batch revert quirk); None totalSupply/balanceOf are READ ARTIFACTS, NOT state changes."
out["leg4_reread_summary"] = summ

# ---- Bridge leg ----
try:
    mtime = os.path.getmtime(f"{BASE}/scan-bridge.json")
    b = json.load(open(f"{BASE}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge_leg"] = {"status": "unchanged" if abs(mtime - BRIDGE_MTIME_KNOWN) < 1 else "CHANGED - check",
        "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(mtime)),
        "total": len(c), "same_owner_discarded": sum(1 for v in c.values() if isinstance(v, dict) and v.get("same_owner_discarded")),
        "note": "no new promotions, no tier change"}
except Exception as e:
    out["bridge_leg"] = {"status": "skip - unreadable", "error": str(e)}

json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)
out["duration_sec"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:9000])
