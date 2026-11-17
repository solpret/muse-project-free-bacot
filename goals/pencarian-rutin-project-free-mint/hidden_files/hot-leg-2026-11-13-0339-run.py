#!/usr/bin/env python3
"""Hot-leg run 2026-11-13 03:39 WIB - legs 1+2+shape+LEG4-FIRST+leg3-trimmed (0319 lineage).
Global deadline T0+180s. Read-only except hot-leg-seen.json (own file) + own run files.
Never writes main snapshot / main seen files.
State carried from 0334 (elapsed 198,7 dtk, OVERRAN; leg4 8/43 OK) + main job 0331 (block 133224677; feed newest 20:36:47Z at 0334):
- Agc 0xdAc2: 333/333 SELLOUT - already reported, do NOT re-report.
- Game-9c20: 333/333 SELLOUT confirmed at 0334 (2 independent reads) - REPORTED once as change-sellout (hot-leg-reported.json) ~03:44, do NOT re-report.
- Game-9c20: SELLOUT already reported at 0334 - do NOT re-report.
- Sol 0xF4D7: 310/333 (93,1%) at 0334 (+2), slot open; strong-lead gate-blocked reported 23:30 WIB 12 Nov - DIAM unless SELLOUT.
- OBFG 0x5314: 553/1230 (45,0%) at 0334 (+2), slot open, quote OK, saleStart 20:01:16 WIB 12 Nov. Track-C lead gate-blocked - DIAM unless change.
- BC1B (RESUME): freeCount 448/3000 (14,9%) at main 0331, gate-blocked reported 00:17 13 Nov - DIAM unless change.
- Agentx 0x64a5: 347/1111 (31,2%) at 0334 (+4) - watchlist-only - DIAM.
- NOTV 0x0415: totalMinted 0, freeStart 1794567600 = 18:00 WIB 13 Nov - NOT open yet.
- OUTY 0xDBE8: freeSold 8/1500, FREE_FEE 0,0001 BNB - BUKAN gas-only, bukan lead.
- LuckyCatch 0xD405: totalMinted 21 at 0334; age deadline 04:06:03 WIB 13 Nov - re-read this run.
- binanceai-mint: launched 0, failed 1, isRefundPhase 1 (main 0331) - refund/failed ALREADY reported hot-leg 20:24 WIB 12 Nov - do NOT re-report.
- BinanceLife age-exclusion ALREADY REPORTED 23:59 12 Nov. Do NOT re-report.
- 0334 leftovers: 0xF1E0D446... now shape-checked (S1/S2 false, not sale-shape); 0xf1b0f2dd53b46c18ceb839838b6caf64e9f95fb7 still 404 - retry this run.
- RPC: egress flapping (leg4 8/43 OK at 0334, up from 0/40 at 0319). Leg4 SEQUENTIAL, leg4 BEFORE heavy leg3 extras this run.
- Feed stale window (newest verifiedAt 20:36:47Z 12 Nov at 0334); Boltbook EN+ZH OK at 0334 (44.864/43.197 byte).
- Bridge 0334: 116 contracts, 0 not in snapshot, 7 same-owner-discarded - no promotion/change.
"""

import json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-13-0339"
T0 = time.time()
GLOBAL_DEADLINE = T0 + 180
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-13 03:39 WIB", "started_wib": now_wib}

def curl(url, timeout=10, data=None):
    cmd = ["curl", "-sL", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

def curl_json(url, timeout=10):
    try:
        return json.loads(curl(url, timeout).decode(errors="replace"))
    except Exception:
        return None

seen = json.load(open(BASE + "hot-leg-seen.json"))
def st(v): return v.get("status") if isinstance(v, dict) else str(v)
seen_lc = {k.lower(): k for k in seen}

FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeamount", "free_supply", "freeslots", "free_slots",
              "freeminted", "freemint", "freesupply"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def shape_check(a):
    al = a.lower()
    if al in EXCLUDED or al == REGISTRY:
        return {"status": "excluded-or-registry"}
    abi_j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 6)
    abi = None
    if isinstance(abi_j, dict):
        abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
    if not abi:
        return {"status": "shape-check-failed", "note": "ABI unfetchable (404 or error)"}
    names = set()
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") in ("function", None):
            names.add((fn.get("name") or "").lower())
    has_mint = any("mint" in n for n in names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice", "getprice")) for n in names)
    free_views = sorted(n for n in names if n in FREE_VIEWS or "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) or n in
                ("agentregistry", "agentgate", "agent_id_registry", "registry") for n in names)
    src = json.dumps(abi).lower()
    agent = agent or ("agent_id_registry" in src) or ("agentgate" in src) or (REGISTRY[2:].lower() in src)
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    has_mintfree = "mintfree" in names
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = is_token and has_mintfree and bool(free_views) and agent
    return {"status": "checked", "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_views, "agent": agent, "n_fns": len(names)}

# ---- Leg 1: Sourcify feed (one quick retry if empty) ----
feed = curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 10)
items = []
if isinstance(feed, dict):
    items = feed.get("results") or feed.get("contracts") or []
elif isinstance(feed, list):
    items = feed
if not items:
    time.sleep(3)
    feed = curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 10)
    if isinstance(feed, dict):
        items = feed.get("results") or feed.get("contracts") or []
    elif isinstance(feed, list):
        items = feed
feed_addrs, feed_meta = [], {}
for it in items:
    a = (it.get("address") or "").strip()
    if a:
        feed_addrs.append(a); feed_meta[a] = it.get("verifiedAt") or ""
out["feed"] = {"n": len(feed_addrs),
               "newest_verifiedAt": max(feed_meta.values()) if feed_meta else None,
               "oldest_verifiedAt": min(feed_meta.values()) if feed_meta else None}
json.dump({"addrs": feed_addrs, "meta": feed_meta},
          open(BASE + f"hot-leg-{TAG}-feed.json", "w"), indent=1)
new = [a for a in feed_addrs if a.lower() not in seen_lc]
out["feed_new"] = new
shapes = {}
SHAPE_DEADLINE = T0 + 50
for a in new:
    if time.time() > SHAPE_DEADLINE:
        shapes[a] = {"status": "shape-check-deferred", "note": "deadline, retry next run"}
        continue
    shapes[a] = shape_check(a); time.sleep(0.1)
out["feed_shape"] = {a: {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
                     for a, s in shapes.items()}
for a in new:
    s = shapes.get(a, {})
    seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
               "status": s.get("status", "checked"),
               "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
    seen_lc[a.lower()] = a
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang):
    url = "https://boltbook.fun/?lang=zh" if lang == "zh" else "https://boltbook.fun/?lang=en"
    raw = curl(url, 10)
    open(BASE + f"hot-leg-{TAG}-boltbook-{lang}.html", "wb").write(raw)
    return raw.decode(errors="replace")

addrs = set()
for lang in ("en", "zh"):
    if time.time() > T0 + 75:
        out[f"boltbook_{lang}"] = {"bytes": -1, "note": "deadline-skipped"}; continue
    html = boltbook(lang)
    found = set(re.findall(r"0x[a-fA-F0-9]{40}", html))
    addrs |= found
    out[f"boltbook_{lang}"] = {"bytes": len(html), "addrs": sorted(found)}
    time.sleep(0.2)
bb_new = sorted(a for a in addrs if a.lower() not in seen_lc)
out["boltbook_new"] = bb_new
bb_shapes = {}
for a in bb_new:
    if time.time() > T0 + 88:
        bb_shapes[a] = {"status": "shape-check-deferred", "note": "deadline, retry next run"}
        continue
    bb_shapes[a] = shape_check(a); time.sleep(0.1)
out["boltbook_new_shapecheck"] = {a: {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
                                  for a, s in bb_shapes.items()}
for a in bb_new:
    s = bb_shapes.get(a, {})
    seen[a] = {"first_seen_wib": now_wib, "source": "boltbook",
               "status": s.get("status", "checked"),
               "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
    seen_lc[a.lower()] = a
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Retry: main-0331 leftovers (shape-check failed there, not in hot-leg-seen) ----
LEFTOVERS = ["0xF1E0D4461273d9923181716E3691Db5126900629",
             "0xf1b0f2dd53b46c18ceb839838b6caf64e9f95fb7"]
out["retry_0331_leftovers"] = {}
for a in LEFTOVERS:
    if time.time() > T0 + 95:
        out["retry_0331_leftovers"][a] = "deadline-skipped"; continue
    s = shape_check(a)
    out["retry_0331_leftovers"][a] = {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
    seen[a] = {"first_seen_wib": "2026-11-13T03:31:00+07:00 (main job 0331)",
               "source": "main-0331-leftover",
               "status": s.get("status", "checked"),
               "note": f"RETRY-0339: S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
    seen_lc[a.lower()] = a
    time.sleep(0.1)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Retry: last 2 shape-check-failed + last 2 deferred (tight) ----
retry_all = [a for a, v in seen.items() if st(v) == "shape-check-failed"]
retry = [a for a in retry_all if a not in LEFTOVERS][-2:]
out["retry_404"] = {"total_failed": len(retry_all), "retried": retry, "results": {}}
for a in retry:
    if time.time() > T0 + 100:
        out["retry_404"]["results"][a] = "deadline-skipped"; continue
    s = shape_check(a)
    out["retry_404"]["results"][a] = s.get("status")
    if isinstance(seen.get(a), dict):
        if s.get("status") == "checked":
            seen[a]["status"] = "checked"
            seen[a]["note"] = (f"RETRY {now_wib}: ABI now fetchable — S1={s.get('S1')} S2={s.get('S2')} "
                               f"mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}")
        else:
            seen[a]["note"] = (seen[a].get("note", "") + f" | retry {now_wib}: still 404").strip()[:400]
    time.sleep(0.1)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)

# ---- RPC helpers (raced batch, 3 endpoints) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res = post_rpc_race(calls, timeout=12)
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}
def chunked_batch(addr, views, chunk=8):
    merged = {}
    for i in range(0, len(views), chunk):
        c = raw_batch(addr, views[i:i + chunk])
        if c:
            merged.update(c)
    return merged if merged else None
def get_block():
    try:
        r = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=10)
        if isinstance(r, list) and r:
            return int(r[0]["result"], 16)
    except Exception:
        pass
    return None
def note_append(addr, text):
    if isinstance(seen.get(addr), dict):
        _old = seen[addr].get("note", "")
        _old = _old[-400:] if len(_old) > 400 else _old
        seen[addr]["note"] = (_old + text).strip()[:900]

SMALL_VIEWS = ["freeMinted()", "FREE_CAP()", "FREE_SHARES()", "mintOpen()", "freeClaimed(address)",
               "balanceOf(address)", "totalMinted()", "saleStart()", "mintStart()",
               "freeStart()", "freeEnd()", "freeClaimedTotal()", "mintOpensAt()", "freeRemaining()"]

# ---- Leg 4 FIRST: re-read snapshot watchlist/track_c/pending (LEAN 12-view batches, sequential) ----
LEAN_VIEWS = ["totalMinted()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "FREE_CAP()",
              "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
              "launched()", "finalized()", "refunding()"]
TARGETS = [
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA"),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("Airdrop-417d", "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
    ("RunicKey", "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"),
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("Ronin", "0xF62FA2ee1490708D51DeF7212493D5c7878Fa110"),
    ("DragonAgent", "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"),
    ("Kitebots", "0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0"),
    ("Kongtou-AirdropCnNFT", "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
    ("POCKET", "0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102"),
    ("Snailings", "0x5d8f22549fdba6a437c40564d2a65664e714034b"),
    ("RAMRAIDERS", "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"),
    ("Pathwyrm", "0xf100c608913dc07ed268bea865fca10004f04657"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
    ("NOVA2", "0xdbbc87ae7734e4a16958426f204e6f79ce92e630"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("0x016b9CE7", "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7"),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("AgenticGangster", "0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),
    ("AGENT COSMOS", "0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69"),
    ("AGENT ID card", "0x486d0947caa3d70c19e38f6c789489d39291e9e7"),
    ("Cobalt Agent", "0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0"),
    ("DRAGON-0xad0d", "0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998"),
    ("ROBO", "0xf8b6867efa31bbd76e10d0bcefbdb22abc6b07fb"),
    ("SYNERGYPASS", "0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e"),
    ("Thor", "0x8aa9d6a09caf475593852e681b58b26dc94edd56"),
    ("Vexa", "0x6c17af4fac529e5679686e121a75e85b1063cd45"),
    ("OUTY", "0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412"),
    ("Agentx", "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"),
    ("Game", "0x9c204b333538F853cD5FD8306277130514B86F04"),
]
block = get_block()
reads = {}
LEG4_DEADLINE = T0 + 125
PRIORITY = ["LuckyCatch", "binanceai-mint", "OliverAgents", "MECHA", "BUCKET", "NOVA2",
            "CRTSAINTS", "SUDOSAINTS", "DACIT", "POCKET", "Snailings", "RAMRAIDERS",
            "Pathwyrm", "Kitebots", "DragonAgent", "Kongtou-AirdropCnNFT", "0x7Eb9",
            "0x016b9CE7", "0x2e50", "MOONDRILL", "NAOMI", "AgenticGangster", "AGENT COSMOS",
            "AGENT ID card", "Cobalt Agent", "DRAGON-0xad0d", "ROBO", "SYNERGYPASS", "Thor",
            "Vexa", "RigForge", "SEVEN", "WFPASS", "Airdrop-417d", "RunicKey", "Ronin",
            "AGCR", "Stampooor", "Pickgrid", "BinanceLife", "OUTY", "Agentx", "Game"]
tmap = {n: a for n, a in TARGETS}
for name in PRIORITY:
    addr = tmap.get(name)
    if not addr:
        continue
    if time.time() > LEG4_DEADLINE:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}
        continue
    r = chunked_batch(addr, LEAN_VIEWS, chunk=8)
    if r is None or not any(v is not None for v in r.values()):
        time.sleep(0.5)
        r2 = chunked_batch(addr, LEAN_VIEWS, chunk=8)
        if r2 is not None and any(v is not None for v in r2.values()):
            r = r2
    e = {"address": addr, "views": r}
    if r: e["summary"] = {k: v for k, v in r.items() if v is not None}
    reads[name] = e
out["leg4_block"] = block
out["leg4_reads"] = reads
out["leg4_ok"] = sum(1 for e in reads.values()
                     if e.get("views") and any(v is not None for v in e["views"].values()))
json.dump({"started_wib": now_wib, "block": block, "reads": reads,
           "elapsed_s": round(time.time() - T0, 1)},
          open(BASE + f"run-{TAG}-verify2.json", "w"), indent=1)

# ---- Compare leg4 vs baselines ----
KEY_NEW = {"freeMinted", "freeClaimed", "totalMinted", "mintOpen", "freeClaimed_user",
           "balanceOf_user", "launched", "finalized", "refunding", "FREE_CAP", "FREE_SUPPLY"}
changes = []
try:
    prev = {}
    for f in ("hot-leg-run-2026-11-13-0334.json", "run-2026-11-13-0334-verify2.json",
              "hot-leg-run-2026-11-13-0319.json", "run-2026-11-13-0319-verify2.json",
              "run-2026-11-13-0331-verify.json",
              "hot-leg-run-2026-11-13-0314.json", "run-2026-11-13-0314-verify2.json",
              "hot-leg-run-2026-11-13-0309.json", "run-2026-11-13-0309-verify2.json",
              "hot-leg-run-2026-11-13-0304.json", "run-2026-11-13-0304-verify2.json",
              "hot-leg-run-2026-11-13-0259.json", "run-2026-11-13-0259-verify2.json",
              "hot-leg-run-2026-11-13-0254.json", "run-2026-11-13-0254-verify2.json",
              "hot-leg-run-2026-11-13-0249.json", "run-2026-11-13-0249-verify2.json",
              "hot-leg-run-2026-11-13-0239.json", "run-2026-11-13-0239-verify2.json",
              "hot-leg-run-2026-11-13-0229.json", "run-2026-11-13-0229-verify2.json",
              "hot-leg-run-2026-11-13-0224.json", "run-2026-11-13-0224-verify2.json",
              "hot-leg-run-2026-11-13-0204.json", "run-2026-11-13-0204-verify2.json",
              "hot-leg-run-2026-11-13-0159.json", "run-2026-11-13-0159-verify2.json",
              "hot-leg-run-2026-11-12-2249.json", "run-2026-11-12-2249-verify2.json"):
        try:
            d = json.load(open(BASE + f))
            for _n, _e in (d.get("leg4_reads") or d.get("reads") or {}).items():
                if _n in prev:
                    continue
                _v = _e.get("views") if isinstance(_e, dict) else None
                if _v:
                    prev[_n] = _e
        except Exception:
            pass
    for name, e in reads.items():
        if "views" not in e or not e["views"]: continue
        p = prev.get(name, {})
        pv = p.get("views") or {}
        for k, v in e["views"].items():
            if v is None: continue
            if k in pv and pv[k] is not None and pv[k] != v:
                changes.append(f"{name}.{k}: {pv[k]} -> {v}")
            elif (k not in pv or pv.get(k) is None) and k in KEY_NEW:
                changes.append(f"{name}.{k}: (new read) {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["leg4_changes_vs_baseline"] = changes

# ---- Leg 3 TRIMMED: OBFG + Sol + Game + Agentx + BC1B-small + NOTV (1 attempt each) ----
LEG3_DEADLINE = T0 + 165
OBFG = "0x5314071bba19943f58347bA5deC423E5032A6818"
OBFG_VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()",
              "saleStart()", "isFreeOpen()", "saleOpen()", "freeAvailable(address)"]
obfg_r = raw_batch(OBFG, OBFG_VIEWS) if time.time() < LEG3_DEADLINE else None
obfg_quote = None
if time.time() < LEG3_DEADLINE:
    data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": OBFG, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
            tail = None
            if len(words) >= 5 and words[4] < len(b):
                off = words[4]
                ln = int.from_bytes(b[off:off + 32], "big")
                tail = b[off + 32:off + 32 + ln].decode(errors="replace")
            obfg_quote = {"words": words, "tail_string": tail}
        except Exception as e:
            obfg_quote = {"decode_error": str(e)[:100]}
out["leg3_obfg"] = {"views": obfg_r,
                    "summary": {k: v for k, v in obfg_r.items() if v is not None} if obfg_r else None,
                    "quote_user_1": obfg_quote}
if obfg_r and isinstance(seen.get(OBFG), dict):
    ssum = out["leg3_obfg"]["summary"] or {}
    note_append(OBFG, f" | LEG3-0339 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300] +
                f" | quote1={obfg_quote}")
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

HOT3 = [("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606", "Sol"),
        ("0x9c204b333538F853cD5FD8306277130514B86F04", "Game-9c20"),
        ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", "Agentx"),
        ("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", "BC1B"),
        ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", "NOTV"),
        ("0xdAc222886b887fC5b6262889B189B8eb57e99794", "Agc")]
leg3_hot = {}
for addr, nm in HOT3:
    if time.time() > LEG3_DEADLINE:
        leg3_hot[addr] = {"name": nm, "error": "deadline-skipped"}; continue
    r = chunked_batch(addr, SMALL_VIEWS)
    leg3_hot[addr] = {"name": nm, "views": r,
                      "summary": {k: v for k, v in r.items() if v is not None} if r else None}
    if r and isinstance(seen.get(addr), dict):
        ssum = leg3_hot[addr]["summary"] or {}
        note_append(addr, f" | LEG3-0339 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300])
out["leg3_hot"] = leg3_hot
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 3: on-chain verify NEW sale-shape passes from this run ----
LEG3_VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
              "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()", "MAX_SUPPLY()",
              "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
              "mintedBy(address)", "mintStart()", "freeLeft()", "freeAvailable(address)",
              "saleStart()", "saleEnd()", "PRICE()", "price()", "launched()",
              "freeSharesLeft()", "freeSharesRemaining()", "freeClaimedByWallet(address)",
              "currentState()", "finalized()", "refunding()", "totalFreeMinted()", "openedAt()"]
leg3_targets = []
for a, s in list(shapes.items()) + list(bb_shapes.items()):
    if s.get("S1") or s.get("S2"):
        leg3_targets.append(a)
for _a, _s in (out.get("retry_0331_leftovers", {}) or {}).items():
    if isinstance(_s, dict) and (_s.get("S1") or _s.get("S2")) and _a not in leg3_targets:
        leg3_targets.append(_a)
out["leg3_targets"] = leg3_targets
leg3 = {}
for a in leg3_targets:
    if time.time() > LEG3_DEADLINE:
        leg3[a] = {"error": "deadline-skipped"}; continue
    r = chunked_batch(a, LEG3_VIEWS)
    leg3[a] = {"views": r, "chunked": True}
    if r:
        leg3[a]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg3"] = leg3
for a, e in leg3.items():
    if isinstance(seen.get(a), dict) and e.get("views"):
        ssum = e.get("summary", {})
        note_append(a, f" | LEG3 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300])
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Site checks (Stampooor) ----
def site_check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "8", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, timeout=12)
        return r.stdout.decode(errors="replace").strip()
    except Exception: return "000 0"
packs_raw = curl("https://stampooor.pages.dev/packs/", 10)
out["stampooor_site"] = {"root_com": site_check("https://stampooor.com/"),
                         "pages_dev_packs": site_check("https://stampooor.pages.dev/packs/"),
                         "packs_contract_prints": packs_raw.decode(errors="replace").lower().count(
                             "0x467696af8c2206b977b24081445104632dc1d459")}

# ---- Bridge (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict):
                a = v.get("address") or v.get("sale") or v.get("contract")
                if a: snap_addrs.add(str(a).lower())
    not_in = [a for a in contracts if a.lower() not in snap_addrs]
    disc = [a for a, v in contracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": not_in,
                     "same_owner_discarded": disc}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
