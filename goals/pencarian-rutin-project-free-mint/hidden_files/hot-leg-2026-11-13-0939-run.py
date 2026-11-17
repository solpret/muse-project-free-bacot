"""Hot-leg run 2026-11-13 09:39 WIB - LEAN (0924 lineage).
Global deadline T0+150s. Read-only except hot-leg-seen.json (own file) + own run file.
State carried in:
- Main job 09:31: feed 1 new (0x86b7 non-sale); Boltbook no new; OBFG 633/1230 (51.5%)
  slot open gate-blocked (reported by main job); JNTM freeClaimed 322/1000 (32.2%),
  quote NULL; AgentMuse user-minted (done); NOTV not open (totalMinted 0); Sol sold out.
- Leg4lite 09:36: Agentx 663/1111 (59.7%) slot open; BC1B/RESUME freeCount 461/3000 (15.4%);
  JNTM totalMinted 395, freeClaimed 327; quote NULL.
- 0x70fd JAGENT: START 2026-11-14 23:00 WIB, freeOpen 0 - not started, no action.
- Agentx 50%-crossed reported 08:29 (website unverified). BC1B gate-blocked reported 00:17.
- BinanceLife age-exclusion reported 23:59 12 Nov. Stampooor age-excluded. Game/Sol sold out.
This run: legs 1+2 delta, leg3 re-read OBFG/JNTM/Agentx/BC1B/NOTV (+quotes), leg4-lite
parallel re-read of remaining live snapshot targets, bridge read-only, change compare
vs 09:31 main verify + 09:36 leg4lite baselines. retry_404 list SKIPPED this run (0924
already retried; 0x70fd resolved S1+S2, rest still 404) - retry next run.
"""
import json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-13-0939"
T0 = time.time()
GLOBAL_DEADLINE = T0 + 150
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-13 09:39 WIB", "started_wib": now_wib}

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

# ---- Leg 1: Sourcify feed ----
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
new = [a for a in feed_addrs if a.lower() not in seen_lc]
out["feed_new"] = new
shapes = {}
for a in new:
    if time.time() > T0 + 45:
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

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang):
    url = "https://boltbook.fun/?lang=zh" if lang == "zh" else "https://boltbook.fun/?lang=en"
    return curl(url, 10).decode(errors="replace")

addrs = set()
for lang in ("en", "zh"):
    if time.time() > T0 + 70:
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
    if time.time() > T0 + 80:
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
def _post_one(ep, payload, timeout=8):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=8):
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
    res = post_rpc_race(calls, timeout=10)
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
def quote_user_1(addr):
    data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}], timeout=8)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
            tail = None
            if len(words) >= 5 and words[4] < len(b):
                off = words[4]
                ln = int.from_bytes(b[off:off + 32], "big")
                tail = b[off + 32:off + 32 + ln].decode(errors="replace")
            return {"words": words, "tail_string": tail}
        except Exception as e:
            return {"decode_error": str(e)[:100]}
    return None
def note_append(addr, text):
    if isinstance(seen.get(addr), dict):
        _old = seen[addr].get("note", "")
        _old = _old[-400:] if len(_old) > 400 else _old
        seen[addr]["note"] = (_old + text).strip()[:900]

# ---- Leg 3+4 combined: parallel re-reads ----
OBFG = "0x5314071bba19943f58347ba5dec423e5032a6818"
JNTM = "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b"
AGENTX = "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"
BC1B = "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053"
NOTV = "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01"
SMALL_VIEWS = ["freeMinted()", "FREE_CAP()", "FREE_SHARES()", "mintOpen()", "freeClaimed(address)",
               "balanceOf(address)", "totalMinted()", "saleStart()", "mintStart()",
               "freeStart()", "freeEnd()", "freeClaimedTotal()", "mintOpensAt()", "freeRemaining()"]
OBFG_VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()",
              "saleStart()", "isFreeOpen()", "saleOpen()", "freeAvailable(address)"]
JNTM_VIEWS = ["name()", "freeClaimed()", "freeLeft()", "FREE_LOTS_CAP()", "TOTAL_LOTS()",
              "totalMinted()", "paidMinted()", "mintStart()", "opened()", "openTime()",
              "freeSharesRemaining()", "mintOpen()", "saleStart()", "token()"]
BC1B_VIEWS = ["freeCount()", "FREE_CAP()", "freeMinted()", "totalSupply()", "saleStart()",
              "refundOpen()", "freeMinted(address)", "balanceOf(address)", "paidMinted(address)"]
LEAN_VIEWS = ["totalMinted()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "FREE_CAP()",
              "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
              "launched()", "finalized()", "refunding()"]
LEG4_TARGETS = [
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA"),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("Airdrop-417d", "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
    ("RunicKey", "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"),
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
]

def _read_one(name, addr, views):
    if time.time() > T0 + 135:
        return name, {"address": addr, "error": "deadline-hit-skipped"}
    r = None
    for _a in range(2):
        r = chunked_batch(addr, views)
        if r is not None and any(v is not None for v in r.values()):
            break
        time.sleep(1)
    e = {"address": addr, "views": r}
    if r: e["summary"] = {k: v for k, v in r.items() if v is not None}
    return name, e

jobs = [("OBFG", OBFG, OBFG_VIEWS), ("JNTM", JNTM, JNTM_VIEWS),
        ("Agentx", AGENTX, SMALL_VIEWS), ("BC1B", BC1B, BC1B_VIEWS),
        ("NOTV", NOTV, SMALL_VIEWS)]
for nm, ad in LEG4_TARGETS:
    jobs.append((nm, ad, LEAN_VIEWS))
reads = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(_read_one, nm, ad, vw): nm for nm, ad, vw in jobs}
    for fut in as_completed(futs):
        try:
            n, e = fut.result(); reads[n] = e
        except Exception as ex2:
            reads[futs[fut]] = {"address": "", "error": f"parallel-error {ex2}"[:80]}
out["leg34_reads"] = reads
out["leg34_ok"] = sum(1 for e in reads.values()
                      if e.get("views") and any(v is not None for v in e["views"].values()))

# quotes for OBFG + JNTM (cheap single calls, only if time)
out["quotes"] = {}
for nm, ad in (("OBFG", OBFG), ("JNTM", JNTM)):
    if time.time() < T0 + 140:
        out["quotes"][nm] = quote_user_1(ad)
    else:
        out["quotes"][nm] = "deadline-skipped"

# pct computations
def pct(num, den):
    return round(100 * num / den, 1) if num is not None and den else None
ob = reads.get("OBFG", {}).get("summary") or {}
jn = reads.get("JNTM", {}).get("summary") or {}
ax = reads.get("Agentx", {}).get("summary") or {}
bc = reads.get("BC1B", {}).get("summary") or {}
out["pct"] = {
    "OBFG_free": pct(ob.get("freeMinted"), ob.get("FREE_SUPPLY")),
    "JNTM_free": pct(jn.get("freeClaimed"), jn.get("FREE_LOTS_CAP")),
    "Agentx_free": pct(ax.get("freeMinted"), ax.get("FREE_CAP")),
    "BC1B_free": pct(bc.get("freeCount"), bc.get("FREE_CAP")),
}
# age: OBFG saleStart 1794488476 = 2026-11-12 20:01:16 WIB; now ~13.6h old, <24h until 20:01 WIB today
out["age_note"] = "OBFG saleStart 1794488476 (20:01:16 WIB 12 Nov) -> age-exclusion at 20:01 WIB 13 Nov; JNTM mintStart 1794525192 (06:33:12 WIB 13 Nov)"

# ---- Compare vs baselines (0931 main verify + 0936 leg4lite) ----
changes = []
try:
    base = {}
    d = json.load(open(BASE + "run-2026-11-13-0931-verify.json"))
    for _n, _e in (d.get("reads") or {}).items():
        _v = _e.get("views") or {}
        base[_n] = {k: v for k, v in _v.items() if isinstance(v, (int, float))}
    lite = json.load(open(BASE + "hot-leg-2026-11-13-0924-leg4lite.json"))
    if lite.get("agentx"):
        base["Agentx"] = {k: v for k, v in lite["agentx"].items() if isinstance(v, (int, float))}
    if lite.get("resume"):
        base["BC1B"] = {k: v for k, v in lite["resume"].items() if isinstance(v, (int, float))}
    if lite.get("jntm_views"):
        base["JNTM"] = {k: v for k, v in lite["jntm_views"].items() if isinstance(v, (int, float))}
    KEY = {"freeMinted", "freeClaimed", "totalMinted", "mintOpen", "freeClaimed_user",
           "balanceOf_user", "launched", "finalized", "refunding", "FREE_CAP", "FREE_SUPPLY",
           "freeCount", "freeLeft"}
    for name, e in reads.items():
        v = e.get("views") or {}
        pv = base.get(name, {})
        for k, val in v.items():
            if val is None: continue
            if k in pv and pv[k] is not None and pv[k] != val:
                changes.append(f"{name}.{k}: {pv[k]} -> {val}")
            elif (k not in pv or pv.get(k) is None) and k in KEY:
                changes.append(f"{name}.{k}: (new read) {val}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["leg34_changes_vs_0931_0936"] = changes

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

# ---- Notes back into seen (append-only, one dump) ----
for nm, ad in (("OBFG", OBFG), ("JNTM", JNTM), ("Agentx", AGENTX), ("BC1B", BC1B), ("NOTV", NOTV)):
    e = reads.get(nm, {})
    ssum = e.get("summary") or {}
    if ssum and isinstance(seen.get(ad), dict):
        note_append(ad, f" | LEG3-0939 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300])
    elif isinstance(seen.get(ad), dict):
        note_append(ad, f" | LEG3-0939 {now_wib}: views NULL (RPC batch failure, not on-chain state) - retry next run.")
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
