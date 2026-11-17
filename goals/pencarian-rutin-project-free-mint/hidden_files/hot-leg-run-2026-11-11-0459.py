#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 04:59 WIB. Legs: (1) Sourcify feed fresh fetch
(limit 20) + shape-check new contracts; (2) Boltbook EN+ZH boltbook.fun fresh
fetch; (3) leg4 re-read of 48-item set vs 0454 baseline; (4) bridge read-only.
Read-only except own hot-leg state files. No preview/mint, no chain scan."""
import json, time, urllib.request, concurrent.futures, subprocess, re
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 04:59 WIB"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}

# ---- Leg 1: Sourcify feed ----
feed_addrs, feed_times, feed_note = [], {}, ""
try:
    st, body = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 15)
    feed = json.loads(body.decode())
    items = feed.get("results", feed if isinstance(feed, list) else [])
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
            feed_times[a] = it.get("verifiedAt") or it.get("matchDate") or ""
    json.dump(feed, open(BASE + "hot-leg-2026-11-11-0459-feed.json", "w"))
    feed_note = f"feed HTTP {st}, {len(feed_addrs)} contracts"
except Exception as e:
    feed_note = f"feed fetch FAILED: {type(e).__name__}: {str(e)[:80]} - leg skipped, retried next run"
NEW = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
ALREADY = [a for a in feed_addrs if a.lower() in seen_l]
EXCL_HIT = [a for a in feed_addrs if a.lower() in EXCLUDED]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:100]}"}

shapes = []
if NEW:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(fetch_abi, NEW))
s1_pass = [s["address"] for s in shapes if s.get("S1")]
s2_pass = [s["address"] for s in shapes if s.get("S2")]
for s in shapes:
    a = s["address"]
    if s.get("error"):
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"Sourcify ABI fetch error: {s['error']} - no sale-shape evidence; recorded, not a lead, never previewed/minted.",
                   "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    else:
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"S1={s['S1']} S2={s['S2']} mint={s['has_mint']} quote={s['has_quote']} free={s['free_views']} agent={s['agent_ref']} token={s['is_token']}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 2: Boltbook EN + ZH (one retry on transient failure, per 14:14 run) ----
def curl_get(url, timeout=20):
    p = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError(f"curl rc={p.returncode} bytes={len(p.stdout)} err={p.stderr[:80]!r}")
    return 200, p.stdout

bb_note = ""
try:
    st_en, en = curl_get("https://boltbook.fun/", 20)
    st_zh, zh = curl_get("https://boltbook.fun/?lang=zh", 20)
    open(BASE + "hot-leg-2026-11-11-0459-boltbook-en.html", "wb").write(en)
    open(BASE + "hot-leg-2026-11-11-0459-boltbook-zh.html", "wb").write(zh)
    addrs = set(ADDR_RE.findall(en.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh.decode("utf-8", "ignore")))
    fresh = sorted(a for a in addrs if a.lower() not in {k.lower() for k in seen})
    bb_note += (f"EN HTTP {st_en} ({len(en)}B) + ZH HTTP {st_zh} ({len(zh)}B) boltbook.fun; "
               f"{len(addrs)} unique addresses, {len(fresh)} not in hot-leg-seen.json: {fresh or 'none'}")
    _txhash = set()
    for _pg in (en.decode("utf-8", "ignore"), zh.decode("utf-8", "ignore")):
        for _m in re.finditer(r"0x[0-9a-fA-F]{64}", _pg):
            _txhash.add("0x" + _m.group(0)[2:42].lower())
    for a in fresh:
        if a.lower() in _txhash:
            seen[a] = {"first_seen_wib": NOW_ISO,
                       "note": "First 40 hex chars of a 64-hex TX HASH inside a Boltbook post text, not a contract address - no shape-check, never a lead.",
                       "source": "boltbook-frontpage", "status": "checked-not-contract"}
        else:
            _s = fetch_abi(a)
            if _s.get("error"):
                seen[a] = {"first_seen_wib": NOW_ISO,
                           "note": f"Boltbook front-page mention; Sourcify ABI fetch error: {_s['error']} - no sale-shape evidence; recorded, not a lead, never previewed/minted.",
                           "source": "boltbook-frontpage", "status": "checked-abi-unavailable"}
            else:
                seen[a] = {"first_seen_wib": NOW_ISO,
                           "note": f"Boltbook front-page mention; shape-check in-run: S1={_s['S1']} S2={_s['S2']} mint={_s['has_mint']} quote={_s['has_quote']} free={_s['free_views']} agent={_s['agent_ref']} token={_s['is_token']}",
                           "source": "boltbook-frontpage", "status": "checked-not-sale-shape" if not (_s['S1'] or _s['S2']) else "sale-shape-pass"}
                if _s['S1'] or _s['S2']:
                    bb_note += f" SALE-SHAPE PASS from Boltbook: {a} (S1={_s['S1']} S2={_s['S2']})."
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    bb_note = f"Boltbook fetch FAILED: {type(e).__name__}: {str(e)[:80]} - leg skipped, retried next run"

# ---- Leg 4: re-read vs 0454 baseline ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")
NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
 "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY", "FREE_SHARES",
 "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree", "MAX_SUPPLY", "MAX_FREE",
 "sharesMinted", "sold", "phase", "launched", "soldOut", "closed", "finalized",
 "mintOpen", "mintActive", "totalSkunksMinted", "freeSkunksClaimed",
 "freeSkunksRemaining", "freeRemaining", "mintCount", "MAX_MINTS", "opened",
 "openedAt", "saleActive", "soldShares", "publicMinted", "launchTime", "totalShares",
 "totalFreeShares", "mintingOpen", "TOTAL_SHARES", "MAX_FREE_SHARES", "SALE_START",
 "isSaleEnded", "remaining", "mintEnd", "mintStart", "SALE_END", "startTime",
 "freeWindowOpen", "agentFreeUsed", "AGENT_FREE_CAP", "paidMinted"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed", "freeCount",
 "freeMinted", "mintedCount", "freeAvailable", "hasMinted", "quotaOf", "freeTakenBy",
 "priceFor", "freeClaimedBy", "freeUsedByWallet", "hasFreeMinted", "freeAllowance",
 "maxShares", "remainingShares"]
ADDRUINT = ["quote", "freeFor"]
def calldata(field):
    if field in ("address", "_batch_fail"): return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT: return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None
def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200] + p.stderr[:200]}
def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"): return None
    try: return int(r, 16)
    except Exception: return None

prev = json.load(open(BASE + "hot-leg-2026-11-11-0454-reread.json"))
items = prev["items"]
jobs = []
for name, entry in items.items():
    for field in entry:
        data = calldata(field)
        if data: jobs.append((name, field, entry["address"], data))
p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                   capture_output=True, text=True)
try: block = int(json.loads(p.stdout)["result"], 16)
except Exception: block = None
results, failed = {}, []
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i + 25]
    resp = run_batch([(to, data) for (_, _, to, data) in chunk])
    if isinstance(resp, dict) and "_curl_error" in resp:
        for (name, field, to, data) in chunk:
            results[(name, field)] = None; failed.append((name, field))
        continue
    if isinstance(resp, dict): resp = [resp]
    for j, item in enumerate(resp):
        name, field, to, data = chunk[j]
        if isinstance(item, dict) and "result" in item:
            results[(name, field)] = decode(item["result"])
        else:
            results[(name, field)] = None; failed.append((name, field))
reread = {"block": block, "items": {}, "duration_sec": round(time.time() - T0, 1)}
read_failed2 = []
for name, entry in items.items():
    row = {"address": entry["address"]}
    for field in entry:
        if field == "address": continue
        v = results.get((name, field))
        if v is None:
            row[field] = entry.get(field)
            read_failed2.append((name, field))
        else:
            row[field] = v
    reread["items"][name] = row
reread["read_failed"] = [{"item": n, "field": f} for n, f in read_failed2]
diffs = []
for name, row in reread["items"].items():
    base = items.get(name, {})
    for field, val in row.items():
        if field == "address": continue
        old = base.get(field)
        if old is None and val is None: continue
        if old != val: diffs.append({"item": name, "field": field, "old": old, "new": val})
reread["diffs_vs_2349"] = diffs
reread["baseline_note"] = f"diffs vs 0454 leg4 (block {prev.get(chr(98)+chr(108)+chr(111)+chr(99)+chr(107))})"
json.dump(reread, open(BASE + "hot-leg-2026-11-11-0459-reread.json", "w"), indent=1)

# promo flags + new-flag detection vs 1929 flags
snap2 = json.load(open(BASE + "onchain-snapshot.json"))
sc = snap2.get("contracts", {}) or {}
st = snap2.get("track_c", {}) or {}
flags = []
for name, entry in reread["items"].items():
    meta = sc.get(name) or st.get(name) or {}
    status = (meta.get("status") or "") if isinstance(meta, dict) else ""
    free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
    cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
          entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = entry.get("freeClaimed_user") in (0, False, None) or entry.get("balanceOf_user") == 0
        if free >= cap:
            flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
        elif pct >= 0.25 and user_open:
            flags.append({"item": name, "flag": "promo-candidate-check", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
prev_flags = {}
try:
    pf = json.load(open(BASE + "hot-leg-run-2026-11-11-0454-leg4.json"))
    for f in pf.get("leg4_promo_flags", []):
        prev_flags[(f["item"], f["flag"])] = f
except Exception:
    pass
new_flags = [f for f in flags if (f["item"], f["flag"]) not in prev_flags]
pend = snap2.get("pending_claims", {}) or {}

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    in_bridge_new = [a for a in NEW if a.lower() in {k.lower() for k in bcontracts}]
    discarded_n = sum(1 for v in bcontracts.values() if v.get("same_owner_discarded"))
    _addr_by_name = {n: e.get("address", "").lower() for n, e in reread["items"].items()}
    _bridge_flagged = [f["item"] for f in new_flags if _addr_by_name.get(f["item"], "") in {k.lower() for k in bcontracts}]
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, last written "
                   f"{br.get('last_written', br.get('written', 'n/a'))}); {discarded_n} same_owner_discarded; "
                   f"new feed contracts in bridge: {in_bridge_new or 'none'}; bridge contracts among new promo flags: {_bridge_flagged or 'none'}")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    in_discards = [a for a in NEW if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts in same-owner-discards.json: {in_discards or 'none'}"


# ---- CHEEMSA watchlist re-check (pre-launch 17:00 WIB, run 1604) ----
CHEEMSA = "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
cheemsa_note = ""
try:
    calls = [("FREE_SHARES", sel("FREE_SHARES()")), ("totalFreeMinted", sel("totalFreeMinted()")),
             ("totalMinted", sel("totalMinted()")), ("mintStart", sel("mintStart()")),
             ("currentState", sel("currentState()")), ("finalized", sel("finalized()")),
             ("refunding", sel("refunding()")),
             ("freeClaimedByWallet_user", sel("freeClaimedByWallet(address)") + enc_addr(USER)),
             ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
             ("quote1_cost", sel("quote(uint256)") + enc_uint(1))]
    resp = run_batch([(CHEEMSA, d) for _, d in calls])
    vals = {}
    if isinstance(resp, dict): resp = [resp]
    for j, (nm, _) in enumerate(calls):
        it = resp[j] if j < len(resp) else {}
        raw = it.get("result") if isinstance(it, dict) else None
        if nm == "quote1_cost" and isinstance(raw, str) and len(raw) >= 130:
            # quote(uint256) returns a tuple (cost, ...) - decode first word as cost
            try:
                vals[nm] = int(raw[2:66], 16)
                vals["quote1_second"] = int(raw[66:130], 16)
            except Exception:
                vals[nm] = decode(raw)
        else:
            vals[nm] = decode(raw) if isinstance(raw, str) else None
    ms = vals.get("mintStart")
    ms_str = ""
    if isinstance(ms, int):
        ms_str = datetime.fromtimestamp(ms, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
    launched = isinstance(ms, int) and ms <= int(time.time())
    tfm = vals.get('totalFreeMinted')
    launched_live = launched and isinstance(tfm, int) and tfm > 0
    slot_open = vals.get('freeClaimedByWallet_user') in (0, False) and vals.get('balanceOf_user') == 0
    fs = vals.get('FREE_SHARES')
    cheemsa_sellout = isinstance(tfm, int) and isinstance(fs, int) and fs > 0 and tfm >= fs
    cheemsa_slot_lost = launched_live and not slot_open
    cheemsa_note = (f"CHEEMSA 0x00b4...28b2 re-check run 0459: FREE_SHARES={fs}, "
                    f"totalFreeMinted={tfm}, totalMinted={vals.get('totalMinted')}, currentState={vals.get('currentState')}, "
                    f"finalized={vals.get('finalized')}, refunding={vals.get('refunding')}, mintStart={ms} ({ms_str}), "
                    f"freeClaimedByWallet(user)={vals.get('freeClaimedByWallet_user')}, balanceOf(user)={vals.get('balanceOf_user')}, "
                    f"quote(1) cost(first word)={vals.get('quote1_cost')} wei, second word={vals.get('quote1_second')}; launched_now={launched}. "
                    + ("SELLOUT 1000/1000 - gate-blocked lead sold out; REPORT ONCE as change (no preview/mint ever happened)."
                       if cheemsa_sellout else
                       ("SLOT LOST (user slot no longer open) - gate-blocked lead; REPORT ONCE as change."
                       if cheemsa_slot_lost else
                       ("LAUNCHED + pool open, slot open - GATE-BLOCKED (methods A-N failed, reported once run 1631; main run 1701 confirmed no re-report); NO preview/mint; watching only for sellout/slot-lost/website-appearing."
                       if launched_live else ("LAUNCHED (mintStart passed) but totalFreeMinted still 0 - no first share mint yet; launch age NOT yet corroborated by a first mint; stays WATCHLIST-ONLY, never previewed/minted."
                       if launched else "STILL PRE-LAUNCH - stays WATCHLIST-ONLY, never previewed/minted; website gate still unsatisfied.")))))
    # update seen note (own state file) with the re-check line
    if CHEEMSA in seen:
        seen[CHEEMSA]["note"] = seen[CHEEMSA]["note"] + " " + cheemsa_note
        json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    cheemsa_note = f"CHEEMSA re-check FAILED: {type(e).__name__}: {str(e)[:80]} - kept prior watchlist state, retried next run"


# ---- Pickgrid c2BE watchlist re-check (S1 pass, pre-launch at 1649) ----
PICK = "0xc2BEAaD13Ef2833D976957E41B03b6B2661cFAB0"
pick_note = ""
try:
    calls = [("live", sel("live()")), ("freeMinted", sel("freeMinted()")),
             ("FREE_CAP", sel("FREE_CAP()")), ("goLive", sel("goLive()")),
             ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER))]
    resp = run_batch([(PICK, d) for _, d in calls])
    vals = {}
    if isinstance(resp, dict): resp = [resp]
    for j, (nm, _) in enumerate(calls):
        it = resp[j] if j < len(resp) else {}
        vals[nm] = decode(it.get("result")) if isinstance(it, dict) else None
    gl = vals.get("goLive")
    gl_str = ""
    if isinstance(gl, int) and gl > 0:
        gl_str = datetime.fromtimestamp(gl, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
    pick_note = (f"Pickgrid 0xc2BE...FAB0 post-mint re-check run 0459: live={vals.get('live')}, freeMinted={vals.get('freeMinted')}, "
                 f"FREE_CAP={vals.get('FREE_CAP')}, goLive={gl} ({gl_str}), balanceOf(user)={vals.get('balanceOf_user')}; "
                 f"mint #243 executed run 1654 (tx 0xa7d71a83...fa32, block 132758318) - post-mint state re-verified, no re-mint (slot used).")
except Exception as e:
    pick_note = f"Pickgrid re-check FAILED: {type(e).__name__}: {str(e)[:80]} - kept prior watchlist state, retried next run"


# ---- Pickgrid bookkeeping (deferred by run 1654; no 1659/1704/1709 run happened) ----
pick_book = ""
try:
    reported = json.load(open(BASE + "hot-leg-reported.json"))
    PICKC = "0xc2BEAaD13Ef2833D976957E41B03b6B2661cFAB0"
    if PICKC not in reported:
        reported[PICKC] = {
            "detail": "PICKGRID PICKAXE #243 minted free (strong-lead direct mint, run 1654): live 16:59:30 WIB, freeMinted 239/300=79.7% at pre-check, slot open freeEligible=1, agentIdClaimed=0; website pickgrid.xyz config JS (www) prints contract exactly 1x; audit Binance hasResult=false (no result, not a pass), riskLevel -1, no RISK hit; preview clean 000000000 (+1 ERC721 #243, no authority/allowance/risk); tx 0xa7d71a836c98d5f12bf3f23ed8cb707216d8b3fb50c6e9e7a1f24ff23e1dfa32, block 132758318, receipt 1, gas 167273; balanceOf 0->1, ownerOf(243)=agent wallet, agentIdClaimed 0->1, freeMinted 239->243, isFree(243)=1, lockedUntil 1794910386 = 2026-11-17 17:13:06 WIB (non-transferable 7 days). Rarity: tier NOT verified (tokenURI -> pickgrid.xyz/meta/free.json shared, no Rarity/Tier trait). Own market NOT live verified -> NOT listed (auto-list rule; Element fallback manual only). Bookkeeping completed by run 1744 (no 1659/1704/1709 run).",
            "reported_wib": "2026-11-10T17:14:00+07:00",
            "what": "minted"}
        json.dump(reported, open(BASE + "hot-leg-reported.json", "w"), indent=1)
        pick_book = "Pickgrid #243 mint recorded in hot-leg-reported.json by run 1744 (deferred bookkeeping from run 1654)."
    else:
        pick_book = "Pickgrid already in hot-leg-reported.json - no duplicate entry."
    if PICKC in seen and "MINTED run 1654" not in seen[PICKC].get("note", ""):
        seen[PICKC]["note"] = seen[PICKC].get("note", "") + " MINTED run 1654 #243 (tx 0xa7d71a83...fa32, block 132758318); bookkeeping done run 1744."
        json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    pick_book = f"Pickgrid bookkeeping FAILED: {type(e).__name__}: {e}"


# ---- Priority re-read run 0459: NIGHTFORGE (gate-blocked strong lead),
# SOLDERCATS (early, 12.85% at 22:54 - watch 25%), CosmicSentinel (watchlist-only),
# EMBERANVIL + BYTEBLOOM (minted - confirm slot used) ----
prio_report = []
def words_of(raw):
    if not isinstance(raw, str) or not raw.startswith("0x"): return None
    h = raw[2:]
    if not h or len(h) % 64: return None
    return [int(h[i:i+64], 16) for i in range(0, len(h), 64)]
def call1(addr, data):
    resp = run_batch([(addr, data)])
    if isinstance(resp, dict): resp = [resp]
    if resp and isinstance(resp[0], dict):
        return resp[0].get("result")
    return None
PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("mintStart", "mintStart()"), ("freeMinted", "freeMinted()"),
    ("agentFreeUsed", "agentFreeUsed()"), ("status_w2", "status()"),
    ("freeLeft_w0", "freeLeft()"), ("freeLeft_w1", "freeLeft()"),
    ("balanceOf_user", "balanceOf(address)"), ("freeClaimed_user", "freeClaimed(address)")]),
 "SOLDERCATS": ("0x3D972EBbF7488f21b95250B867e2406c723C9DDC", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("agentFreeLeft", "agentFreeLeft()"), ("mintOpen", "mintOpen()"),
    ("mintStart", "mintStart()"), ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
    ("totalSupply", "totalSupply()"), ("freeMinted", "freeMinted()"),
    ("mintOpen", "mintOpen()"), ("balanceOf_user", "balanceOf(address)"),
    ("freeClaimed_user", "freeClaimed(address)")]),
 "EMBERANVIL": ("0x7673c596a6702d32f844266dc2ca7b1fd6d7df21", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("agentFreeLeft", "agentFreeLeft()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "BYTEBLOOM": ("0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("agentFreeLeft", "agentFreeLeft()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
}
# batched priority calls (fix for 2344 overrun: was 1 POST per field, ~46 calls)
_prio_jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        if sig.endswith("(address)"):
            data = sel(sig) + enc_addr(USER)
        else:
            data = sel(sig)
        _prio_jobs.append((name, fname, addr, data))
_prio_raw = {}
for _i in range(0, len(_prio_jobs), 25):
    _chunk = _prio_jobs[_i:_i+25]
    _resp = run_batch([(to, data) for (_, _, to, data) in _chunk])
    if isinstance(_resp, dict) and "_curl_error" in _resp:
        for (_nm, _fn, _to, _d) in _chunk:
            _prio_raw[(_nm, _fn)] = None
        print("PRIO batch chunk failed (curl/parse error) - all fields in chunk kept None, retried next run")
        continue
    if isinstance(_resp, dict): _resp = [_resp]
    for _j, _item in enumerate(_resp):
        _nm, _fn, _to, _d = _chunk[_j]
        _prio_raw[(_nm, _fn)] = _item.get("result") if isinstance(_item, dict) else None
prio_vals = {}
for name, (addr, fields) in PRIO.items():
    vals = {}
    for fname, sig in fields:
        raw = _prio_raw.get((name, fname))
        if fname == "status_w2":
            w = words_of(raw); vals[fname] = w[2] if w and len(w) > 2 else None
        elif fname == "freeLeft_w0":
            w = words_of(raw); vals[fname] = w[0] if w else None
        elif fname == "freeLeft_w1":
            w = words_of(raw); vals[fname] = w[1] if w and len(w) > 1 else None
        else:
            vals[fname] = decode(raw) if isinstance(raw, str) else None
    prio_vals[name] = vals
    print("PRIO", name, json.dumps(vals))
prio_notes = []
nf = prio_vals["NIGHTFORGE"]
if isinstance(nf.get("agentFreeUsed"), int):
    prio_notes.append(f"NIGHTFORGE agentFreeUsed={nf['agentFreeUsed']}/2000 ({nf['agentFreeUsed']/20:.2f}%), freeLeft={nf.get('freeLeft_w0')}/{nf.get('freeLeft_w1')}, status[2]={nf.get('status_w2')}, balanceOf(user)={nf.get('balanceOf_user')}, mintOpen={nf.get('mintOpen')} (baseline 22:47: 657/2000=32.85%, slot open). Gate-blocked (website unverified) - no mint unless gate recheck passes.")
sc = prio_vals["SOLDERCATS"]
if isinstance(sc.get("agentFreeUsed"), int) and isinstance(sc.get("agentFreeLeft"), int):
    cap = sc["agentFreeUsed"] + sc["agentFreeLeft"]
    pct = sc["agentFreeUsed"] / cap if cap else 0
    prio_notes.append(f"SOLDERCATS agentFreeUsed={sc['agentFreeUsed']}/{cap} ({pct*100:.2f}%), mintOpen={sc.get('mintOpen')}, balanceOf(user)={sc.get('balanceOf_user')}, agentFreeByWallet(user)={sc.get('agentFreeByWallet_user')} (baseline 22:54: 12.85%)." + (" PROMO-CANDIDATE-CHECK: >=25% + slot open - needs website gate before any mint." if pct >= 0.25 and sc.get('balanceOf_user') == 0 else ""))
    if pct >= 0.25 and sc.get('balanceOf_user') == 0:
        prio_report.append(f"SOLDERCATS crossed 25% free ({pct*100:.2f}%) with slot open - PROMO-CANDIDATE-CHECK, website gate pending")
cs = prio_vals["CosmicSentinel"]
prio_notes.append(f"CosmicSentinel freeMinted={cs.get('freeMinted')}/225000, mintOpen={cs.get('mintOpen')}, balanceOf(user)={cs.get('balanceOf_user')} (baseline: 271/225000, watchlist-only).")
for mn in ("EMBERANVIL", "BYTEBLOOM"):
    v = prio_vals[mn]
    prio_notes.append(f"{mn} totalSupply={v.get('totalSupply')}, agentFreeUsed={v.get('agentFreeUsed')}, balanceOf(user)={v.get('balanceOf_user')}, agentFreeByWallet(user)={v.get('agentFreeByWallet_user')} (minted earlier - slot expected used).")
json.dump(prio_vals, open(BASE + "hot-leg-run-2026-11-11-0459-prio.json", "w"), indent=1)
prio_note = " | ".join(prio_notes)

s1s2_note = f"S1_PASS={s1_pass} S2_PASS={s2_pass}"
report_items = []
report_items.extend(prio_report)
try:
    _rep = json.load(open(BASE + "hot-leg-reported.json"))
except Exception:
    _rep = {}
_cheemsa_keys = [k for k in _rep if k.startswith("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2")]
_slot_reported = any("#slot-used" in k for k in _cheemsa_keys)
_sellout_reported = any("#sellout" in k for k in _cheemsa_keys)
if 'cheemsa_sellout' in dir() and cheemsa_sellout and not _sellout_reported:
    report_items.append("CHEEMSA SELLOUT (gate-blocked lead, free pool 1000/1000) - report once as change")
    _rep["0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2#sellout-20261111-0459"] = {
        "detail": "CHEEMSA (Cheems Agent) free pool SOLD OUT 1000/1000 (gate-blocked lead; user slot already used via main-job run 1731 mint). No preview/mint by hot leg.",
        "reported_wib": "2026-11-11T04:59:00+07:00", "what": "change"}
    json.dump(_rep, open(BASE + "hot-leg-reported.json", "w"), indent=1)
if 'cheemsa_slot_lost' in dir() and cheemsa_slot_lost and not _slot_reported:
    report_items.append("CHEEMSA slot lost - report once as change")
if new_flags:
    report_items.append(f"new promo flags: {new_flags}")
if s1_pass or s2_pass:
    report_items.append(f"new sale-shape pass needs lead evaluation: S1={s1_pass} S2={s2_pass}")
report_str = ("REPORT: " + "; ".join(report_items)) if report_items else "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat."
out = {"run": RUN, "legs": {
  "sourcify_feed": f"{feed_note}; {len(ALREADY)} already seen, {len(NEW)} new shape-checked, {len(EXCL_HIT)} excluded hit. ALL new not sale shape: {', '.join(a[:6] for a in NEW) or 'none'}. {s1s2_note}. Recorded in hot-leg-seen.json.",
  "boltbook": bb_note,
  "leg4_reread": f"{len(items)}-item set re-read at block {block} via bsc.nodereal.io eth_call batches; vs 0454 baseline (block {prev.get("block")}) {len(diffs)} diffs: {diffs}. {len(read_failed2)} read-failed fields kept baseline values, never treated as change. New promo flags vs previous run: {new_flags or 'none'}.",
  "bridge": bridge_note,
  "cheemsa_watchlist": cheemsa_note,
  "priority_reread": prio_note,
  "pickgrid_watchlist": pick_note,
  "pickgrid_bookkeeping": pick_book,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": report_str,
 "duration_sec": round(time.time() - T0, 1)}
leg4out = {"leg4": {"block": block, "prev_block": prev.get("block"), "rpc": EP,
                    "items_n": len(items), "changes": diffs,
                    "failed_call_idx": [{"item": n, "field": f} for n, f in failed],
                    "read_failed": reread["read_failed"],
                    "mode": "chunked eth_call batches of <=25 (read-only); null reads keep baseline, never a change"},
           "leg4_promo_flags": flags, "new_promo_flags": new_flags,
           "pending_claims": "snapshot pending_claims empty - nothing to re-read" if not pend else f"{len(pend)} pending claims present",
           "duration_sec": round(time.time() - T0, 1)}
json.dump(leg4out, open(BASE + "hot-leg-run-2026-11-11-0459-leg4.json", "w"), indent=1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-11-0459.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("LEG4:", json.dumps(leg4out, indent=1)[:4000])
