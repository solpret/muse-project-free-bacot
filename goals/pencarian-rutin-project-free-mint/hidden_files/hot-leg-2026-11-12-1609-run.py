#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 16:09 WIB — legs 1+2+retry+leg3+leg4, tight-bounded (1554 lineage; Boltbook fix: /?lang=en + curl -L per 1554 supplement root-cause).
Global deadline T0+210s. Read-only except hot-leg-seen.json (own file) + own run files.
Never writes main snapshot / main seen files. Leg4 uses raced batches (2 endpoints
in parallel, first complete response wins)."""
import json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1609"
T0 = time.time()
GLOBAL_DEADLINE = T0 + 210
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 16:09 WIB", "started_wib": now_wib}

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
SHAPE_DEADLINE = T0 + 55
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
    if time.time() > T0 + 85:
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
    if time.time() > T0 + 100:
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

# ---- Retry: last 4 shape-check-failed ----
retry_all = [a for a, v in seen.items() if st(v) == "shape-check-failed"]
retry = retry_all[-4:]
out["retry_404"] = {"total_failed": len(retry_all), "retried": retry, "results": {}}
for a in retry:
    if time.time() > T0 + 115:
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

# ---- RPC helpers (raced batch, per-item error tolerant) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
LEG4_DEADLINE = T0 + 200
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=2) as ex:
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
def get_block():
    try:
        r = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=10)
        if isinstance(r, list) and r:
            return int(r[0]["result"], 16)
    except Exception:
        pass
    return None

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
out["leg3_targets"] = leg3_targets
leg3 = {}
for a in leg3_targets:
    if time.time() > T0 + 125:
        leg3[a] = {"error": "deadline-skipped"}; continue
    r = raw_batch(a, LEG3_VIEWS)
    leg3[a] = {"views": r}
    if r:
        leg3[a]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg3"] = leg3
for a, e in leg3.items():
    if isinstance(seen.get(a), dict) and e.get("views"):
        ssum = e.get("summary", {})
        seen[a]["note"] = (seen[a].get("note", "") +
            f" | LEG3 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300]).strip()[:600]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: re-read (priority order; 1534 list + Ronin/DragonAgent/Kitebots) ----
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
         "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
         "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
         "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
TARGETS = [
    ("Ronin", "0xF62FA2ee1490708D51DeF7212493D5c7878Fa110"),
    ("DragonAgent", "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"),
    ("Kitebots", "0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0"),
    ("Kongtou-AirdropCnNFT", "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("AgenticGangster", "0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
    ("NAPPER", "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("Airdrop-417d", "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
    ("POCKET", "0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102"),
    ("Snailings", "0x5d8f22549fdba6a437c40564d2a65664e714034b"),
    ("Pathwyrm", "0xf100c608913dc07ed268bea865fca10004f04657"),
    ("RAMRAIDERS", "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"),
    ("NOVA2", "0xdbbc87ae7734e4a16958426f204e6f79ce92e630"),
    ("0x016b9CE7", "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7"),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA"),
]

block = get_block()
reads = {}
for name, addr in TARGETS:
    if time.time() > LEG4_DEADLINE:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    r = raw_batch(addr, VIEWS)
    reads[name] = {"address": addr, "views": r}
    if r: reads[name]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg4_block"] = block
out["leg4_reads"] = reads
json.dump({"started_wib": now_wib, "block": block, "reads": reads,
           "elapsed_s": round(time.time() - T0, 1)},
          open(BASE + f"run-{TAG}-verify2.json", "w"), indent=1)

# ---- Compare vs newest baselines (1534 first, then older) ----
changes = []
try:
    prev = {}
    for f in reversed(("hot-leg-run-2026-11-12-1554.json", "run-2026-11-12-1554-verify2.json", "hot-leg-run-2026-11-12-1549.json", "run-2026-11-12-1549-verify2.json",
              "hot-leg-run-2026-11-12-1544.json", "run-2026-11-12-1544-verify2.json",
              "hot-leg-run-2026-11-12-1534.json", "run-2026-11-12-1534-verify2.json",
              "hot-leg-run-2026-11-12-1529.json", "run-2026-11-12-1529-verify2.json",
              "hot-leg-run-2026-11-12-1524.json", "run-2026-11-12-1524-verify2.json",
              "hot-leg-run-2026-11-12-1519.json", "hot-leg-run-2026-11-12-1514.json",
              "run-2026-11-12-1514-verify2.json", "hot-leg-run-2026-11-12-1509.json",
              "run-2026-11-12-1501-verify.json", "run-2026-11-12-1501-retry.json")):
        try:
            d = json.load(open(BASE + f))
            prev.update(d.get("leg4_reads") or d.get("reads") or {})
        except Exception:
            pass
    try:
        fu = json.load(open(BASE + "hot-leg-2026-11-12-1459-followup.json"))
        lc = fu.get("leg4_retry_LuckyCatch")
        if lc:
            prev["LuckyCatch"] = {"address": "0xD405C90079c594DA2456F5b37B4158A12f1382e5", "views": lc.get("views")}
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
            elif k not in pv or pv.get(k) is None:
                changes.append(f"{name}.{k}: (new read) {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["leg4_changes_vs_1549"] = changes

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
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
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
