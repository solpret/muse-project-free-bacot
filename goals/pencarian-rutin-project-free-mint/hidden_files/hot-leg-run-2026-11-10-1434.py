#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 14:34 WIB. Legs: (1) Sourcify feed fresh fetch
(limit 20) + shape-check new contracts; (2) Boltbook EN+ZH boltbook.fun fresh
fetch; (3) leg4 re-read of 48-item set vs 1354 baseline; (4) bridge read-only.
Read-only except own hot-leg state files. No preview/mint, no chain scan."""
import json, time, urllib.request, concurrent.futures, subprocess, re
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
NOW_ISO = "2026-11-10T14:36:30+07:00"
RUN = "2026-11-10 14:34 WIB"
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
    json.dump(feed, open(BASE + "hot-leg-2026-11-10-1434-feed.json", "w"))
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
bb_note = ""
try:
    try:
        st_en, en = get("https://boltbook.fun/", 15)
        st_zh, zh = get("https://boltbook.fun/?lang=zh", 15)
    except Exception as e1:
        bb_note = f"Boltbook fetch FAILED first try: {type(e1).__name__}({str(e1)[:40]}); RETRY: "
        time.sleep(2)
        st_en, en = get("https://boltbook.fun/", 15)
        st_zh, zh = get("https://boltbook.fun/?lang=zh", 15)
        bb_note += "OK: "
    open(BASE + "hot-leg-2026-11-10-1434-boltbook-en.html", "wb").write(en)
    open(BASE + "hot-leg-2026-11-10-1434-boltbook-zh.html", "wb").write(zh)
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
            seen[a] = {"first_seen_wib": NOW_ISO,
                       "note": "Boltbook front-page mention, not yet shape-checked - recorded; shape-check deferred to next run leg or main job.",
                       "source": "boltbook-frontpage", "status": "seen-unchecked"}
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    bb_note = f"Boltbook fetch FAILED: {type(e).__name__}: {str(e)[:80]} - leg skipped, retried next run"

# ---- Leg 4: re-read vs 1354 baseline ----
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

prev = json.load(open(BASE + "hot-leg-2026-11-10-1429-reread.json"))
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
reread["diffs_vs_1424"] = diffs
reread["baseline_note"] = f"diffs vs 14:29 leg4 (block {prev.get(chr(98)+chr(108)+chr(111)+chr(99)+chr(107))})"
json.dump(reread, open(BASE + "hot-leg-2026-11-10-1434-reread.json", "w"), indent=1)

# promo flags + new-flag detection vs 1354 flags
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
    pf = json.load(open(BASE + "hot-leg-run-2026-11-10-1429-leg4.json"))
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

s1s2_note = f"S1_PASS={s1_pass} S2_PASS={s2_pass}"
out = {"run": RUN, "legs": {
  "sourcify_feed": f"{feed_note}; {len(ALREADY)} already seen, {len(NEW)} new shape-checked, {len(EXCL_HIT)} excluded hit. ALL new not sale shape: {', '.join(a[:6] for a in NEW) or 'none'}. {s1s2_note}. Recorded in hot-leg-seen.json.",
  "boltbook": bb_note,
  "leg4_reread": f"{len(items)}-item set re-read at block {block} via bsc.nodereal.io eth_call batches; vs 14:19 baseline (block 132735511) {len(diffs)} diffs: {diffs}. {len(read_failed2)} read-failed fields kept baseline values, never treated as change. New promo flags vs 1429: {new_flags or 'none'}.",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat.",
 "duration_sec": round(time.time() - T0, 1)}
leg4out = {"leg4": {"block": block, "prev_block": prev.get("block"), "rpc": EP,
                    "items_n": len(items), "changes": diffs,
                    "failed_call_idx": [{"item": n, "field": f} for n, f in failed],
                    "read_failed": reread["read_failed"],
                    "mode": "chunked eth_call batches of <=25 (read-only); null reads keep baseline, never a change"},
           "leg4_promo_flags": flags, "new_promo_flags": new_flags,
           "pending_claims": "snapshot pending_claims empty - nothing to re-read" if not pend else f"{len(pend)} pending claims present",
           "duration_sec": round(time.time() - T0, 1)}
json.dump(leg4out, open(BASE + "hot-leg-run-2026-11-10-1434-leg4.json", "w"), indent=1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-1434.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("LEG4:", json.dumps(leg4out, indent=1)[:4000])
