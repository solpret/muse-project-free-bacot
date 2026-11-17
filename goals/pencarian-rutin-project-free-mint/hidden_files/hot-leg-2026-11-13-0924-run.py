"""Hot-leg run 2026-11-13 09:24 WIB - legs 1+2+retry+leg3+leg4-LEAN (0844 lineage).
Global deadline T0+180s. Read-only except hot-leg-seen.json (own file) + own run files.
State carried from 0844 (elapsed 176,4 dtk):
- Feed 0844 n=20: 15 baru, 2 checked non-sale, 13 shape-check-failed (Sourcify 404 flaky).
  3 old 404s (0809) resolved non-sale at 0844.
- OBFG 0x5314: 621/1230 (50,5%), slot open, quote OK, gate-blocked SUDAH dilaporkan, DIAM.
- Agentx 0x64a5: 626/1111 (56,3%) di 0809; reads NULL di 0844 (RPC batch failure) - RE-READ.
- JNTM 0x1320: track-C lead, pool totalMinted 318, quote MASIH NULL - RETRY quote.
- BC1B/RESUME 0xBC1B: reads NULL di 0844; terakhir 444/3000 ~00:04, prediksi sellout ~09:30 WIB - RE-READ.
- Sol 0xF4D7: sold out 333/333 (dilaporkan 03:40). Game sold out. DIAM.
- Bridge 0844: 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded.
- BinanceLife age-exclusion SUDAH dilaporkan 23:59 12 Nov. Do NOT re-report.
- Feed this run (09:25 WIB): 5 baru (verified 08:51-09:25 WIB).
"""



import json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-13-0924"
T0 = time.time()
GLOBAL_DEADLINE = T0 + 180
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-13 09:24 WIB", "started_wib": now_wib}

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
retry = ["0x3D4e66dffa8A83cD50573833653A91a779fA46Ea",
         "0xf95553b6A57937468847dc61C47F2DD619FEDE5D",
         "0xEC8208709F9A2FD56F4029E23E3BE555Ec4212dC",
         "0xAd4743EAD580A984d23Bb41161BA58fB3F540726",
         "0xF268D325F097333d1e620BA4033B39da8bBA0B82",
         "0x70FdD1a7f382893708d00fC2eF9C38cAe7DEC92B",
         "0x043d60d568456DE954D405cf69ABf65C624c4139",
         "0x190c669849322B489ba719da8408C9b3F1bB2D54",
         "0x9a631A11e547C87e61497Df68d686bE95D1A8D83",
         "0xD86679AcC5C79038ED192f52217B9Acb16b4313e",
         "0xEe71a51e4EB815e52B036Ada9C041D479fB336eA",
         "0x813d705A97a8600cE28651E119EF57338181b6Ea",
         "0xd91A76878bCd95f6f55A3A70f2Af3C3c1691a152"]  # 0844 shape-check-failed (Sourcify 404 flaky)
out["retry_404"] = {"total_failed": len(retry_all), "retried": retry, "results": {}}
for a in retry:
    if time.time() > T0 + 115:
        out["retry_404"]["results"][a] = "deadline-skipped"; continue
    s = shape_check(a)
    out["retry_404"]["results"][a] = {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
    if isinstance(seen.get(a), dict):
        if s.get("status") == "checked":
            seen[a]["status"] = "checked"
            seen[a]["note"] = (f"RETRY {now_wib}: ABI now fetchable — S1={s.get('S1')} S2={s.get('S2')} "
                               f"mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}")
        else:
            seen[a]["note"] = (seen[a].get("note", "") + f" | retry {now_wib}: still 404").strip()[:400]
    time.sleep(0.1)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
# ---- Retry: shape-check-deferred from 0109 (10) ----
deferred_all = [a for a, v in seen.items() if st(v) == "shape-check-deferred"]
deferred = []  # SKIPPED 0744: retried 0724, save time
out["retry_deferred"] = {"total_deferred": len(deferred_all), "retried": deferred, "results": {}}
for a in deferred:
    if time.time() > T0 + 122:
        out["retry_deferred"]["results"][a] = "deadline-skipped"; continue
    s = shape_check(a)
    out["retry_deferred"]["results"][a] = {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
    if isinstance(seen.get(a), dict):
        if s.get("status") == "checked":
            seen[a]["status"] = "checked"
            seen[a]["note"] = (f"RETRY-DEFERRED {now_wib}: S1={s.get('S1')} S2={s.get('S2')} "
                               f"mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}")
        else:
            seen[a]["note"] = (seen[a].get("note", "") + f" | retry-deferred {now_wib}: still {s.get('status')}").strip()[:400]
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
LEG4_DEADLINE = T0 + 130
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

# ---- Leg 3a: OBFG re-check (small batch) ----
OBFG = "0x5314071bba19943f58347bA5deC423E5032A6818"
OBFG_VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()",
              "saleStart()", "isFreeOpen()", "saleOpen()", "freeAvailable(address)"]
obfg_r = None
for _attempt in range(3):
    if time.time() > T0 + 130:
        break
    obfg_r = raw_batch(OBFG, OBFG_VIEWS)
    if obfg_r is not None and any(v is not None for v in obfg_r.values()):
        break
    time.sleep(2)
obfg_quote = None
if time.time() < T0 + 140:
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
    note_append(OBFG, f" | LEG3-0924 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300] +
                f" | quote1={obfg_quote}")
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
for _a, _s in (out.get("retry_deferred", {}).get("results", {}) or {}).items():
    if isinstance(_s, dict) and (_s.get("S1") or _s.get("S2")) and _a not in leg3_targets:
        leg3_targets.append(_a)
for _a, _s in (out.get("retry_404", {}).get("results", {}) or {}).items():
    if isinstance(_s, dict) and (_s.get("S1") or _s.get("S2")) and _a not in leg3_targets:
        leg3_targets.append(_a)
out["leg3_targets"] = leg3_targets
leg3 = {}
for a in leg3_targets:
    if time.time() > T0 + 125:
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

# ---- Leg 4: re-read snapshot watchlist/track_c/pending (LEAN 12-view batches) ----
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
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("Agentx", "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"),
    ("Game", "0x9c204b333538F853cD5FD8306277130514B86F04"),
]

block = get_block()
reads = {}
def _leg4_one(item):
    name, addr = item
    if time.time() > LEG4_DEADLINE:
        return name, {"address": addr, "error": "deadline-hit-skipped"}
    r = chunked_batch(addr, LEAN_VIEWS, chunk=8)
    e = {"address": addr, "views": r}
    if r: e["summary"] = {k: v for k, v in r.items() if v is not None}
    return name, e
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(_leg4_one, it): it[0] for it in TARGETS}
    for fut in as_completed(futs):
        try:
            n, e = fut.result()
            reads[n] = e
        except Exception as ex2:
            reads[futs[fut]] = {"address": "", "error": f"parallel-error {ex2}"[:80]}
out["leg4_block"] = block
out["leg4_reads"] = reads
out["leg4_ok"] = sum(1 for e in reads.values()
                     if e.get("views") and any(v is not None for v in e["views"].values()))
json.dump({"started_wib": now_wib, "block": block, "reads": reads,
           "elapsed_s": round(time.time() - T0, 1)},
          open(BASE + f"run-{TAG}-verify2.json", "w"), indent=1)

# ---- Leg 3 re-check: watchlist S1s (Agc/Sol/cfD4/Steady/NOTV) — small batch ----
NEW_S1 = [("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b", "JNTM-0x1320"),
          ("0x779fa133848d23052B7345F63B3b2E5309cd13ed", "AgentMuse"),
          ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", "NOTV"),
          ("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606", "Sol"),
          ("0x530695a8e3eb9a1253cafc9239811f4ca88791f9", "Tidalune"),
          ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", "Agentx"),
          ("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf", "Steady"),
          ("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", "BC1B"),
          ("0x0c222b11A380DF4F68ceE7CAcB162357E60c7215", "Ponke")]
leg3_new2129 = {}
for addr, nm in NEW_S1:
    r = None
    for _attempt in range(2):
        if time.time() > T0 + 172:
            break
        r = chunked_batch(addr, SMALL_VIEWS)
        if r is not None and any(v is not None for v in r.values()):
            break
        time.sleep(1)
    leg3_new2129[addr] = {"name": nm, "views": r,
                          "summary": {k: v for k, v in r.items() if v is not None} if r else None}
    if r and isinstance(seen.get(addr), dict):
        ssum = leg3_new2129[addr]["summary"] or {}
        note_append(addr, f" | LEG3-0924 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300])
out["leg3_new2129"] = leg3_new2129
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Agent Muse (0x779f) open-state check: DOORS_OPEN 06:00 WIB 13 Nov just passed ----
MUSE = "0x779fa133848d23052B7345F63B3b2E5309cd13ed"
MUSE_VIEWS = ["openedAt()", "freeClaimed()", "FREE_SHARES()", "bookedTotal()", "totalMinted()",
              "freeClaimed(address)", "balanceOf(address)", "mintOpen()", "DOORS_OPEN()",
              "FALLBACK_OPEN()", "afterSold()", "paidSold()"]
muse_r = None
if time.time() < T0 + 175:
    for _attempt in range(2):
        muse_r = chunked_batch(MUSE, MUSE_VIEWS)
        if muse_r is not None and any(v is not None for v in muse_r.values()):
            break
        time.sleep(1)
out["leg3_agentmuse"] = {"views": muse_r,
                         "summary": {k: v for k, v in muse_r.items() if v is not None} if muse_r else None,
                         "website_verified_0604": "https://agentmuse.fcfs.workers.dev"}
if muse_r and isinstance(seen.get(MUSE), dict):
    ssum = out["leg3_agentmuse"]["summary"] or {}
    note_append(MUSE, f" | LEG3-0924 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300])
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- JNTM targeted retry: slot/quote + name + method H contractURI ----
JNTM = "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b"
JNTM_VIEWS = ["name()", "symbol()", "freeClaimed()", "freeLeft()", "FREE_LOTS_CAP()",
              "TOTAL_LOTS()", "totalMinted()", "paidMinted()", "mintStart()", "opened()",
              "openTime()", "mintedLots(address)", "balanceOf(address)", "registry()",
              "freeSharesRemaining()", "mintOpen()", "saleStart()", "token()"]
jntm_r = None
for _attempt in range(2):
    if time.time() > T0 + 176:
        break
    jntm_r = chunked_batch(JNTM, JNTM_VIEWS)
    if jntm_r is not None and any(v is not None for v in jntm_r.values()):
        break
    time.sleep(1)
# quote(address,uint256) decode (first word = cost)
jntm_quote = None
if time.time() < T0 + 176:
    data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": JNTM, "data": data}, "latest"]}], timeout=8)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
            tail = None
            if len(words) >= 5 and words[4] < len(b):
                off = words[4]
                ln = int.from_bytes(b[off:off + 32], "big")
                tail = b[off + 32:off + 32 + ln].decode(errors="replace")
            jntm_quote = {"words": words, "tail_string": tail}
        except Exception as e:
            jntm_quote = {"decode_error": str(e)[:100]}
# method H: contractURI() dynamic string
jntm_uri = None
if time.time() < T0 + 176:
    data = sel("contractURI()")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": JNTM, "data": data}, "latest"]}], timeout=8)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            if len(b) >= 64:
                off = int.from_bytes(b[0:32], "big")
                ln = int.from_bytes(b[off:off + 32], "big")
                jntm_uri = b[off + 32:off + 32 + ln].decode(errors="replace")
        except Exception as e:
            jntm_uri = f"decode_error {e}"[:100]
out["leg3_jntm_retry"] = {"views": jntm_r,
                          "summary": {k: v for k, v in jntm_r.items() if v is not None} if jntm_r else None,
                          "quote_user_1": jntm_quote, "contractURI": jntm_uri}
if jntm_r and isinstance(seen.get(JNTM), dict):
    ssum = out["leg3_jntm_retry"]["summary"] or {}
    note_append(JNTM, f" | LEG3-0924 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300] +
                (f" | contractURI={jntm_uri}" if jntm_uri else ""))
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Agentx detail refresh ----
_ax = leg3_new2129.get("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", {})
_axv = _ax.get("views") or {}
_ax_pct = (round(100 * _axv["freeMinted"] / _axv["FREE_CAP"], 1) if _axv.get("freeMinted") is not None and _axv.get("FREE_CAP") else None)
out["leg3_agentx"] = {"address": "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
                      "freeMinted": _axv.get("freeMinted"), "FREE_CAP": _axv.get("FREE_CAP"),
                      "pct_free": _ax_pct, "totalMinted": _axv.get("totalMinted"),
                      "mintOpen": _axv.get("mintOpen"), "freeClaimed_user": _axv.get("freeClaimed_user"),
                      "balanceOf_user": _axv.get("balanceOf_user"),
                      "note": "watchlist-only; early lead already reported by main job 0101; promote only on tier change"}
json.dump(out["leg3_agentx"], open(BASE + f"hot-leg-{TAG}-agentx.json", "w"), indent=1)

# ---- Leg 3: BC1B shape-check retry + views ----
BC1B = "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053"
bc1b_shape = None
if time.time() < T0 + 172:
    bc1b_shape = shape_check(BC1B)
out["leg3_bc1b_shape"] = {k: bc1b_shape.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")} if bc1b_shape else None
bc1b_r = None
if time.time() < T0 + 175:
    for _attempt in range(2):
        bc1b_r = chunked_batch(BC1B, SMALL_VIEWS)
        if bc1b_r is not None and any(v is not None for v in bc1b_r.values()):
            break
        time.sleep(1)
out["leg3_retry_bc1b"] = {"views": bc1b_r,
                         "summary": {k: v for k, v in bc1b_r.items() if v is not None} if bc1b_r else None}
if isinstance(seen.get(BC1B), dict):
    ssum = out["leg3_retry_bc1b"]["summary"] or {}
    if bc1b_shape and bc1b_shape.get("status") == "checked":
        seen[BC1B]["status"] = "checked"
        note_append(BC1B, f" | SHAPE-0924 {now_wib}: S1={bc1b_shape.get('S1')} S2={bc1b_shape.get('S2')} mint={bc1b_shape.get('mint')} quote={bc1b_shape.get('quote')} free={bc1b_shape.get('free')} agent={bc1b_shape.get('agent')}" +
                    (f" | VIEWS " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:200] if ssum else ""))
    elif bc1b_r and ssum:
        note_append(BC1B, f" | LEG3-RETRY-0924 {now_wib}: views OK " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300])
    else:
        note_append(BC1B, f" | LEG3-RETRY-0924 {now_wib}: views STILL null (RPC batch failure, not on-chain state) - pool/slot/age UNVERIFIED, NOT a lead, never previewed/minted; retry next run.")
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Compare vs baselines (2249 first, then older) ----
KEY_NEW = {"freeMinted", "freeClaimed", "totalMinted", "mintOpen", "freeClaimed_user",
           "balanceOf_user", "launched", "finalized", "refunding", "FREE_CAP", "FREE_SUPPLY"}
changes = []
try:
    prev = {}
    for f in ("hot-leg-run-2026-11-13-0844.json", "run-2026-11-13-0844-verify2.json",
              "hot-leg-run-2026-11-13-0744.json", "run-2026-11-13-0744-verify2.json",
              "hot-leg-run-2026-11-13-0724.json", "run-2026-11-13-0724-verify2.json",
              "hot-leg-run-2026-11-13-0659.json", "run-2026-11-13-0659-verify2.json",
              "hot-leg-run-2026-11-13-0649.json", "run-2026-11-13-0649-verify2.json",
              "hot-leg-run-2026-11-13-0644.json", "run-2026-11-13-0644-verify2.json",
              "hot-leg-run-2026-11-13-0634.json", "run-2026-11-13-0634-verify2.json",
              "hot-leg-run-2026-11-13-0629.json", "run-2026-11-13-0629-verify2.json",
              "hot-leg-run-2026-11-13-0619.json", "run-2026-11-13-0619-verify2.json",
              "hot-leg-run-2026-11-13-0614.json", "run-2026-11-13-0614-verify2.json",
              "hot-leg-run-2026-11-13-0604.json", "run-2026-11-13-0604-verify2.json",
              "hot-leg-run-2026-11-13-0554.json", "run-2026-11-13-0554-verify2.json"):
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
    try:
        fu = json.load(open(BASE + "hot-leg-2026-11-12-1839-runic-retry.json"))
        prev["RunicKey"] = {"address": "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
                            "views": fu.get("views")}
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
            elif (k not in pv or pv.get(k) is None) and k in KEY_NEW:
                changes.append(f"{name}.{k}: (new read) {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["leg4_changes_vs_0249"] = changes

# ---- Bridge (read-only) ----
out["stampooor_site"] = {"note": "skipped 0744: known state (pages.dev packs does not print contract; com dead)"}
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
