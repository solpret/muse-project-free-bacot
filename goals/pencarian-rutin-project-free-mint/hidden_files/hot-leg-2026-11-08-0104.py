#!/usr/bin/env python3
"""Hot-leg 2026-11-08 01:04 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state.
Derived from 0054 script. Compares leg-4 vs hot-leg-run-2026-11-08-0059.json (prev run).
Tri333 already minted 22:46 (#590) - NEVER re-mint/re-report; slot-2 open is NOT a new order.
WAR3 stays STOPPED (preview 351805). HOG ORBIT is main-job early-lead tier only."""
import json, re, subprocess, sys, time, os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0104"
RUN_WIB = "2026-11-08T01:04:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
BRIDGE_MTIME_KNOWN = 1793933280.7650242
out = {"run": "free-mint-hot-leg 2026-11-08 01:04:38 WIB", "leg1_feed": {}, "leg2_boltbook": {},
       "leg3_new_contracts": "none", "leg4_priority": {}, "leg4_bulk": "not attempted - see note",
       "leg4_summary": {}, "bridge_leg": {},
       "pending_claims": "snapshot pending_claims empty at run start - nothing to re-read"}
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
    _old = seen.get(addr)
    first = _old.get("first_seen_wib") if isinstance(_old, dict) else None
    first = first or RUN_WIB
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

# ---- Leg 2: Boltbook.fun EN + ZH ----
KW = ["free share", "first share free", "1 free share", "free mint share",
      "免费份额", "首个免费", "免费铸造", "免费mint"]
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

# ---- Retry: 6 shape-check-failed - SKIPPED this run ----
# All 6 still return match=null on Sourcify (unverified contracts, NOT a transient
# failure). Retrying every 5 min with 12s timeouts cost ~30-40s and pushed the 0044
# run to 156.5s (over the 2-min target). Retry cadence: once per hour, next ~01:44.
# If they later verify, the main 30-min job scan leg still catches on-chain activity.
out["leg_retry_0104"] = "skipped - 6 contracts match=null on Sourcify (unverified); hourly retry, next ~01:44"

# ---- Leg 3: new sale-shape contracts ----
sale_new = [a for a, s in list(shapes.items()) + list(shapes_bb.items()) if s.get("S1") or s.get("S2")]
out["leg3_new_contracts"] = f"{len(sale_new)} S1/S2 new: {sale_new}" if sale_new else "No S1/S2 hits from feed or Boltbook.fun - no leg-3 on-chain verification needed."

# ---- Leg 4: priority re-read (parallel single calls) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return to_int(_single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0))
        except Exception:
            continue
    return None

# (name, addr, [(key, sig, arg)]) ; arg "" = no-arg, "USER" = address arg, "1" = uint256 1
JOBS = [
 ("Tri333", "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f",
  [("freeMinted", "freeMinted()", ""), ("FREE_CAP", "FREE_CAP()", ""),
   ("freeCount_user", "freeCount(address)", "USER"), ("mintOpen", "mintOpen()", ""),
   ("balanceOf_user", "balanceOf(address)", "USER")]),
 ("WAR3", "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe",
  [("freeMinted", "freeMinted()", ""), ("totalSupply", "totalSupply()", ""),
   ("balanceOf_user", "balanceOf(address)", "USER")]),
 ("HUNT PASS", "0x885128Cf234c768F1353e2C1432D55873C6b67dD",
  [("totalMinted", "totalMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
   ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", "USER"),
   ("mintedBy_user", "mintedBy(address)", "USER")]),
 ("fab7-variant", "0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72",
  [("freeMinted", "freeMinted()", ""), ("FREE_SHARES", "FREE_SHARES()", ""),
   ("totalMinted", "totalMinted()", ""), ("finalized", "finalized()", "")]),
 ("DinoAgent", "0xcE19D6A5FF15e088D4bf23614242927139084895",
  [("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
   ("freeClaimed_user", "freeClaimed(address)", "USER")]),
 ("LOCKSMITH", "0x05e8738290be6639fD0f7236ebF444E5466D3164",
  [("totalMinted", "totalMinted()", ""), ("freeMintedTotal", "freeMintedTotal()", ""),
   ("FREE_CAP", "FREE_CAP()", ""), ("mintActive", "mintActive()", "")]),
 ("HOG ORBIT", "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5",
  [("freeLeft", "freeLeft()", ""), ("totalSupply", "totalSupply()", ""),
   ("balanceOf_user", "balanceOf(address)", "USER")]),
 ("AgentBook", "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0",
  [("FREE_QUOTA", "FREE_QUOTA()", ""), ("remainingFree", "remainingFree()", "")]),
 ("Night Bandits Club", "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf",
  [("freeUsed", "freeUsed()", ""), ("freeTakenBy_user", "freeTakenBy(address)", "USER")]),
 ("Ink Koi", "0xbd4B4e7189ae9356514664146b0eD683601200A9",
  [("freeMinted", "freeMinted()", ""), ("freeClaimed_user", "freeClaimed(address)", "USER")]),
 ("AURISLE", "0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D",
  [("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
   ("freeClaimed_user", "freeClaimed(address)", "USER")]),
 ("CipherAgent", "0x158b5e25015758a94703A27c152889451E5d52E5",
  [("totalMints", "totalMints()", ""), ("mintOpen", "mintOpen()", ""),
   ("balanceOf_user", "balanceOf(address)", "USER")]),
 ("MarsAgent", "0x2231FdAe405c33dc4993f8C577c453802FF1AcE9",
  [("totalMints", "totalMints()", ""), ("mintOpen", "mintOpen()", ""),
   ("balanceOf_user", "balanceOf(address)", "USER")]),
 ("OnlyAI", "0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba",
  [("totalSupply", "totalSupply()", ""), ("balanceOf_user", "balanceOf(address)", "USER")]),
 ("Gloops", "0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE",
  [("totalMinted", "totalMinted()", ""), ("mintOpen", "mintOpen()", "")]),
 ("Saturnagent", "0xef870a9b4a529373fb2e174b59ca7a66eb018074",
  [("freeClaimed", "freeClaimed()", ""), ("quote_user1", "quote(address,uint256)", "USER1")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("freeClaimed", "freeClaimed()", ""), ("quote_user1", "quote(address,uint256)", "USER1")]),
]

def do_job(job):
    name, addr, views = job
    d = {"address": addr}
    for key, sig, arg in views:
        a = enc(USER) if arg == "USER" else (enc(USER) + enc_uint(1)[2:] if arg == "USER1" else arg)
        d[key] = single(addr, sig, a)
    return name, d

try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception:
    blk = None
out["leg4_priority"] = {"block": blk, "items": {}}
with ThreadPoolExecutor(max_workers=6) as ex:
    for name, d in ex.map(do_job, JOBS):
        out["leg4_priority"]["items"][name] = d
json.dump(out["leg4_priority"], open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)

# ---- summary vs 2249 run ----
prev = {}
try:
    r04 = json.load(open(f"{BASE}/hot-leg-run-2026-11-08-0059.json"))
    prev = r04.get("leg4_priority", {})
except Exception:
    pass
pi = prev.get("items", {}) if isinstance(prev, dict) else {}
summ = {"block": blk, "prev_block_0059": prev.get("block")}
cur = out["leg4_priority"]["items"]
def g(name, key, src):
    return (src.get(name) or {}).get(key)

# Tri333
t = cur["Tri333"]; fm, fmo = t.get("freeMinted"), g("Tri333", "freeMinted", pi)
s = f"freeMinted {fmo}->{fm} = {fm/2222*100:.2f}% of FREE_CAP 2222" if fm is not None and fmo is not None else (f"freeMinted recheck {fm}/2222 = {fm/2222*100:.2f}% (0059: 769)" if fm is not None else f"freeMinted {fm}")
s += f", freeCount(user)={t.get('freeCount_user')}, balance={t.get('balanceOf_user')}, mintOpen={t.get('mintOpen')}"
s += " - MINTED #590 22:46, already reported; slot-2 open is NOT a new order, NO re-mint, NO re-report"
if fm is not None and fm >= 2222: s += " - SELLOUT (2222/2222) - REPORT ONCE"
summ["Tri333"] = s
# WAR3
w = cur["WAR3"]; fm, fmo = w.get("freeMinted"), g("WAR3", "freeMinted", pi)
s = f"freeMinted {fmo}->{fm} = {fm/3500*100:.2f}% of 3500" if fm is not None and fmo is not None else (f"freeMinted recheck {fm}/3500 = {fm/3500*100:.2f}% (0059: 2252)" if fm is not None else f"freeMinted {fm}")
s += f", totalSupply {w.get('totalSupply')}, balance={w.get('balanceOf_user')}"
s += " - candidate stays STOPPED (preview 351805, 17:12 block); NOT re-previewed"
if fm is not None and fm >= 3500: s += " - SELLOUT (3500/3500) - REPORT ONCE as change"
summ["WAR3"] = s
# HUNT PASS
h = cur["HUNT PASS"]; tm = h.get("totalMinted")
s = f"totalMinted recheck {tm} (0059: 1450) of FREE_SUPPLY {h.get('FREE_SUPPLY')}"
if tm is not None and h.get("FREE_SUPPLY"):
    s += f" = {tm/h['FREE_SUPPLY']*100:.1f}%"
s += f", freeMinted={h.get('freeMinted')}, balance={h.get('balanceOf_user')}, mintedBy(user)={h.get('mintedBy_user')}"
s += " - gate FAILED, blocked reported 22:18; no tier change unless sellout (3000)"
if tm is not None and tm >= 3000: s += " - SELLOUT - REPORT ONCE as change"
summ["HUNT PASS"] = s
# fab7
f = cur["fab7-variant"]; fm, fs = f.get("freeMinted"), f.get("FREE_SHARES")
s = f"freeMinted recheck {fm}/{fs} (0059: 91)" + (f" = {fm/fs*100:.1f}%" if fm is not None and fs else "")
s += f", totalMinted {f.get('totalMinted')}, finalized {f.get('finalized')}"
s += " - variant flagged for main-job shape-check (2129); never a lead, NOT reported; sellout would only close the variant watch"
if fm is not None and fs and fm >= fs: s += " - FREE POOL SOLD OUT"
summ["fab7-variant"] = s
# DinoAgent
d = cur["DinoAgent"]; fm = d.get("freeMinted"); fmo = g("DinoAgent", "freeMinted", pi)
s = f"freeMinted {fmo}->{fm}/777" + (f" = {fm/777*100:.2f}%" if fm is not None else (f" (0059: 680)" if fm is None else ""))
s += f", freeClaimed(user)={d.get('freeClaimed_user')} - gate-blocked strong lead, no tier change unless sellout"
if fm is not None and fm >= 777: s += " - SELLOUT - REPORT ONCE as change"
summ["DinoAgent"] = s
# LOCKSMITH
l = cur["LOCKSMITH"]; tm = l.get("totalMinted")
s = f"totalMinted {tm}, freeMintedTotal {l.get('freeMintedTotal')}/FREE_CAP {l.get('FREE_CAP')}, mintActive {l.get('mintActive')}"
s += (" - FIRST MINT EXISTS: age now corroborable - flag to main job, NOT a lead yet" if (tm or 0) > 0
      else " - still 0 mints, age still UNVERIFIED - watchlist-only, NO promotion")
summ["LOCKSMITH"] = s
# HOG ORBIT
hg = cur["HOG ORBIT"]; fl = hg.get("freeLeft"); ts = hg.get("totalSupply")
flo = g("HOG ORBIT", "freeLeft", pi)
s = f"freeLeft {flo}->{fl} (0059: 1084)" + (f" (used {1500-fl}/1500 = {(1500-fl)/1500*100:.1f}%)" if fl is not None else "")
s += f", totalSupply {ts}, balance={hg.get('balanceOf_user')}"
if hg.get('balanceOf_user') == 1:
    s += (" - MINTED #421 by MAIN JOB 00:31 run (tx 0x28f650d774144ce817d672a8fc377935e0f7d602b4134dd1b0669cc5e0d59b38, "
          "block 132245054, receipt 1, gas 111214; gate verified that run via tokenURI site hog-orbit.pages.dev). "
          "NOT a hot-leg action; NO re-mint, NO re-report as a new lead. Hot leg only observes the change.")
elif fl is not None and (1500 - fl) >= 375:
    s += " - CROSSED 25% (375) strong-lead legs on counts BUT gate NOT checked + main-job early-lead tier: FLAG to main job, NOT previewed/minted by hot leg"
else:
    s += " - below 25% (375), early-lead tier, main job only"
summ["HOG ORBIT"] = s
# AgentBook
ab = cur["AgentBook"]
s = f"FREE_QUOTA {ab.get('FREE_QUOTA')}, remainingFree {ab.get('remainingFree')} - sold out reported 22:24; paid lane only, never auto-executed"
summ["AgentBook"] = s
# NBC
n = cur["Night Bandits Club"]
s = f"freeUsed {n.get('freeUsed')}/444, freeTakenBy(user)={n.get('freeTakenBy_user')} - sold out reported 22:18, no change"
summ["Night Bandits Club"] = s
# Ink Koi
ik = cur["Ink Koi"]
s = f"freeMinted {ik.get('freeMinted')}/2777, freeClaimed(user)={ik.get('freeClaimed_user')} - own #712 held, no promotion"
summ["Ink Koi"] = s
# AURISLE
au = cur["AURISLE"]
s = f"freeMinted {au.get('freeMinted')}/FREE_SUPPLY {au.get('FREE_SUPPLY')}, freeClaimed(user)={au.get('freeClaimed_user')} - early lead (main job 2001), re-read only, no promotion"
summ["AURISLE"] = s
# CipherAgent / MarsAgent
for nm in ("CipherAgent", "MarsAgent"):
    c = cur[nm]
    summ[nm] = (f"totalMints {c.get('totalMints')}, mintOpen {c.get('mintOpen')}, balance={c.get('balanceOf_user')} "
                "- gate-blocked track-C lead reported 17:40, count move not reportable")
# OnlyAI
o = cur["OnlyAI"]; ots = o.get("totalSupply"); ots_o = g("OnlyAI", "totalSupply", pi)
s = f"totalSupply {ots_o}->{ots} (0059: 1925)" if ots is not None and ots_o is not None else f"totalSupply {ots}"
s += " - watchlist, free% UNVERIFIED (free views revert), no tier change"
summ["OnlyAI"] = s
# Gloops
gl = cur["Gloops"]
s = f"totalMinted {gl.get('totalMinted')}, mintOpen {gl.get('mintOpen')} - PRE-LAUNCH (opens 2026-11-08 12:00 UTC), watchlist-only"
summ["Gloops"] = s
# Saturnagent / Lumenhold
for nm in ("Saturnagent", "Lumenhold"):
    c = cur[nm]
    summ[nm] = (f"freeClaimed {c.get('freeClaimed')}, quote(user,1)={c.get('quote_user1')} "
                "- S1 pass, pool+slot open, age UNVERIFIED - watchlist-only, NO promotion")
summ["note"] = ("Single-call reads only (LEAN; batch whole-batch-revert quirk per AGENTS.md). "
                "None = read artifact, NOT a state change. Bulk leg-4 (2129 ITEMS minimal batch) skipped this run: "
                "0044 run hit 156.5s (over 2-min target); bulk leg skipped; priority items cover all promotion/sellout watches.")
out["leg4_summary"] = summ

# ---- Bridge leg ----
try:
    mtime = os.path.getmtime(f"{BASE}/scan-bridge.json")
    b = json.load(open(f"{BASE}/scan-bridge.json"))
    c = b.get("contracts", {})
    snap_txt = open(f"{BASE}/onchain-snapshot.json").read()
    in_snap = sum(1 for a in c if a.lower() in snap_txt.lower())
    out["bridge_leg"] = {"status": "unchanged" if abs(mtime - BRIDGE_MTIME_KNOWN) < 1 else "CHANGED - check",
        "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(mtime)),
        "total": len(c), "same_owner_discarded": sum(1 for v in c.values() if isinstance(v, dict) and v.get("same_owner_discarded")),
        "in_snapshot_by_substring": in_snap, "not_in_snapshot": len(c) - in_snap,
        "note": "no new promotions, no tier change"}
except Exception as e:
    out["bridge_leg"] = {"status": "skip - unreadable", "error": str(e)}

json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)
out["duration_sec"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:12000])
