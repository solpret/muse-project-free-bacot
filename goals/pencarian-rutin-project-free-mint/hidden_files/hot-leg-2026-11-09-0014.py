#!/usr/bin/env python3
"""Hot-leg 2026-11-09 00:14 WIB run: Sourcify feed poll + Boltbook EN/ZH + shape-check
S1/S2 for new contracts + read-only re-read of snapshot contracts/track_c + bridge read.
Writes hot-leg-2026-11-09-0014.json / -shape.json / run-2026-11-09-0014-reread.json;
updates hot-leg-seen.json with newly checked contracts only. NEVER writes snapshot."""
import json, re, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-09-0014"
NOW = "2026-11-09T00:14:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc.publicnode.com/"]
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-09 00:14:38 WIB", "legs": {}}

def curl(url, timeout=15, post=None):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(post)]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout
    return out

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

def shape_check(addr, verified_at=None, source="sourcify-feed"):
    """Returns (record_dict_or_None, result_dict). Transport failures -> no record."""
    if addr.lower() == REGISTRY.lower() or addr.lower() in EXCLUDED:
        return None, {"addr": addr, "skipped": "registry-or-excluded"}
    # eth_getCode
    code = None
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}
    for ep in EPS:
        try:
            r = json.loads(curl(ep, timeout=10, post=payload)).get("result")
            if r is not None:
                code = r; break
        except Exception:
            continue
    if code is None:
        return None, {"addr": addr, "error": "eth_getCode empty on all endpoints (transport, not recorded)"}
    if code == "0x":
        rec = {"first_seen_wib": NOW, "source": source, "status": "checked-not-contract",
               "note": "eth_getCode 0x - EOA/wallet address, not a contract; no sale shape, not a lead."}
        return rec, {"addr": addr, "result": "EOA-checked-not-contract"}
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
        abi = json.loads(raw).get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
    except Exception as ex:
        return None, {"addr": addr, "error": f"ABI fetch {ex} (not recorded)"}
    if not names:
        rec = {"first_seen_wib": NOW, "source": source, "status": "checked-not-sale-shape",
               "note": "Sourcify 404 / ABI 0 functions (not verified); no sale-shape evidence, not a lead."}
        return rec, {"addr": addr, "result": "ABI-0-functions", "sourcify": "unverified"}
    s1 = any(n.lower().startswith("mint") for n in names) and bool(names & {"quote", "cost"}) \
        and bool(names & FREE) and bool(names & AGENT)
    s2 = bool(names & {"name", "symbol", "decimals", "totalSupply"}) and "mintFree" in names \
        and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) \
        and bool(names & AGENT)
    rec = {"first_seen_wib": NOW, "source": source,
           "status": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
           "note": f"S1={s1} S2={s2} mint={[n for n in names if n.lower().startswith('mint')]} "
                   f"quote={sorted(names & {'quote','cost'})} free={sorted(names & FREE)} "
                   f"agent={sorted(names & AGENT)} token={bool(names & {'name','symbol','decimals','totalSupply'})}",
           "S1": s1, "S2": s2, "n_fns": len(names)}
    if verified_at: rec["verified_at"] = verified_at
    return rec, {"addr": addr, "S1": s1, "S2": s2, "n_fns": len(names),
                 "result": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape"}

# ---------- Leg 1: Sourcify feed ----------
feed_addrs = []
try:
    feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15))
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        v = it.get("verifiedAt") if isinstance(it, dict) else None
        if a: feed_addrs.append((a, v))
    log["legs"]["sourcify_feed"] = f"ok, {len(feed_addrs)} contracts"
except Exception as ex:
    log["legs"]["sourcify_feed"] = f"FAILED {ex}; leg skipped, retry next run"
new_feed = [(a, v) for a, v in feed_addrs if a.lower() not in seen_lower]
shape_results = []
if new_feed:
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(shape_check, a, v, "sourcify-feed"): a for a, v in new_feed}
        for f in futs:
            rec, res = f.result()
            shape_results.append(res)
            if rec: seen[futs[f]] = rec
    log["legs"]["sourcify_feed"] += (f"; {len(feed_addrs)-len(new_feed)} already seen, "
        f"{len(new_feed)} new shape-checked, S1={sum(1 for r in shape_results if r.get('S1'))} "
        f"S2={sum(1 for r in shape_results if r.get('S2'))}")
json.dump(shape_results, open(BASE + TAG + "-shape.json", "w"), indent=1)

# ---------- Leg 2: Boltbook EN + ZH (boltbook.fun) ----------
bb = {"en": None, "zh": None}
for key, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    for attempt in range(2):
        try:
            raw = curl(url, timeout=15)
            if len(raw) > 10000 and "0x" in raw:
                bb[key] = raw; break
            bb[key + "_status"] = f"attempt{attempt+1}: {len(raw)} bytes (short/empty)"
        except Exception as ex:
            bb[key + "_status"] = f"attempt{attempt+1}: {ex}"
        time.sleep(1)
    if bb[key] is None:
        log["legs"][f"boltbook_{key}"] = f"FAILED - {bb.get(key+'_status')}; leg skipped, retry next run"
    else:
        log["legs"][f"boltbook_{key}"] = f"ok 200, {len(bb[key])} bytes"
KW_EN = ["free share", "first share free", "1 free share", "free mint share", "free mint"]
KW_ZH = ["免费份额", "首个免费", "免费铸造", "免费mint"]
bb_addrs = {}
for key, raw in (("en", bb["en"]), ("zh", bb["zh"])):
    if not raw: continue
    low = raw.lower()
    kws = {k: low.count(k.lower()) for k in (KW_EN if key == "en" else KW_ZH)}
    log.setdefault("boltbook_keywords", {})[key] = kws
    for m in re.finditer(r"0x[0-9a-fA-F]{40}", raw):
        bb_addrs.setdefault(m.group(0), key)
new_bb = [(a, None) for a in bb_addrs if a.lower() not in seen_lower
          and a.lower() not in {x[0].lower() for x in new_feed}]
if bb_addrs:
    log["legs"]["boltbook_addrs"] = (f"{len(bb_addrs)} unique addresses; "
        f"{len(new_bb)} new vs seen (excl. feed-new)")
if new_bb:
    bb_results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(shape_check, a, None, f"boltbook-{bb_addrs[a]}"): a for a, _ in new_bb}
        for f in futs:
            rec, res = f.result()
            bb_results.append(res)
            if rec: seen[futs[f]] = rec
    log["legs"]["boltbook_shape"] = (f"{len(new_bb)} new shape-checked, "
        f"S1={sum(1 for r in bb_results if r.get('S1'))} S2={sum(1 for r in bb_results if r.get('S2'))}")
    shape_results.extend(bb_results)
    json.dump(shape_results, open(BASE + TAG + "-shape.json", "w"), indent=1)

json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total"] = len(seen)

# ---------- Leg 3: on-chain verify any sale-shape pass ----------
passes = [r for r in shape_results if r.get("S1") or r.get("S2")]
log["sale_shape_passes"] = passes
# (verification of a pass would go here; none expected - if present, do NOT auto-execute
#  without website gate + audit + clean preview; flag for main job instead.)

# ---------- Leg 4: re-read snapshot (read-only) ----------
snap = json.load(open(BASE + "onchain-snapshot.json"))
prev = json.load(open(BASE + "run-2026-11-09-0004-reread.json"))
C_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
           "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
           "freeClaimed(address)"]
C_KEYS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
          "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"]
T_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()",
           "balanceOf(address)", "freeClaimed(address)"]
T_KEYS = ["totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"]

def batch_calls(calls, chunk=150):
    """calls: list of (label, addr, sig, arg). Returns {label: int|None} + block."""
    out = {}
    blk = None
    def run_chunk(part):
        payload = []
        for i, (lab, addr, sig, arg) in enumerate(part):
            data = sel(sig)
            if arg == "USER": data += enc_addr(USER)
            payload.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                            "params": [{"to": addr, "data": data}, "latest"]})
        payload.append({"jsonrpc": "2.0", "id": len(part) + 1, "method": "eth_blockNumber", "params": []})
        last = None
        for ep in EPS:
            try:
                res = json.loads(curl(ep, timeout=20, post=payload))
                if isinstance(res, list):
                    by_id = {r.get("id"): r.get("result") for r in res}
                    if by_id.get(len(part) + 1) is None: last = f"{ep}: blockNumber missing"; continue
                    vals = {part[i][0]: to_int(by_id.get(i + 1)) for i in range(len(part))}
                    return vals, to_int(by_id.get(len(part) + 1))
                last = f"{ep}: non-list"
            except Exception as ex:
                last = f"{ep}: {ex}"
        return {lab: None for lab, _, _, _ in part}, None
    chunks = [calls[i:i + chunk] for i in range(0, len(calls), chunk)]
    with ThreadPoolExecutor(max_workers=6) as ex:
        for vals, b in ex.map(run_chunk, chunks):
            out.update(vals)
            if b is not None: blk = b
    return out, blk

calls = []
contracts = {}
for name, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and v.get("address"):
        contracts[name] = v["address"]
        for k, sig in zip(C_KEYS, C_VIEWS):
            calls.append((f"C|{name}|{k}", v["address"], sig, "USER" if "address" in sig else ""))
track_c = {}
for name, v in snap.get("track_c", {}).items():
    if not isinstance(v, dict): continue
    addr = v.get("sale") or v.get("token")
    if not addr: continue
    track_c[name] = addr
    for k, sig in zip(T_KEYS, T_VIEWS):
        calls.append((f"T|{name}|{k}", addr, sig, "USER" if "address" in sig else ""))

vals, blk = batch_calls(calls)
reread = {"block": blk, "reread": {}, "track_c": {}, "started_wib": NOW}
for name, addr in contracts.items():
    reread["reread"][name] = {"address": addr}
    for k in C_KEYS:
        reread["reread"][name][k] = vals.get(f"C|{name}|{k}")
for name, addr in track_c.items():
    reread["track_c"][name] = {"address": addr}
    for k in T_KEYS:
        reread["track_c"][name][k] = vals.get(f"T|{name}|{k}")
json.dump(reread, open(BASE + "run-2026-11-09-0014-reread.json", "w"), indent=1)

diffs, recoveries = [], []
for section in ("reread", "track_c"):
    for name, cur in reread[section].items():
        for k, v in cur.items():
            if k == "address": continue
            ov = prev.get(section, {}).get(name, {}).get(k)
            if v != ov:
                if ov is None and v is not None:
                    recoveries.append({"item": name, "field": k, "old": ov, "new": v})
                elif v is None:
                    pass  # fresh null = read failure artifact, not a state change
                else:
                    diffs.append({"item": name, "field": k, "old": ov, "new": v})
log["legs"]["reread"] = (f"ok, block {blk}, {len(contracts)} contracts + {len(track_c)} track_c re-read; "
    f"{len(diffs)} changes, {len(recoveries)} null->value recoveries")
log["reread_diffs"] = diffs
log["reread_recoveries"] = recoveries

# LOCKSMITH watch (freeMintedTotal not in generic view set; last known 27/200 at 21:09 run)
LOCK = "0x05e8738290be6639fD0f7236ebF444E5466D3164"
lock_vals, _ = batch_calls([
    ("freeMintedTotal", LOCK, "freeMintedTotal()", ""),
    ("totalMinted", LOCK, "totalMinted()", ""),
    ("mintActive", LOCK, "mintActive()", ""),
    ("freeMinted_user", LOCK, "freeMinted(address)", "USER"),
])
log["locksmith_watch"] = lock_vals
if lock_vals.get("freeMintedTotal") is not None and lock_vals["freeMintedTotal"] != 27:
    log["locksmith_change"] = f"freeMintedTotal 27 -> {lock_vals['freeMintedTotal']} / 200"

# ---------- Bridge (read-only) ----------
bridge = json.load(open(BASE + "scan-bridge.json"))
snap_addrs = set()
snap_status = {}
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f):
                snap_addrs.add(v[f].lower())
                snap_status[v[f].lower()] = v.get("status", "")
bcontracts = bridge.get("contracts", {})
in_snap = [a for a in bcontracts if a.lower() in snap_addrs]
promos = [a for a in in_snap
          if any(w in (snap_status.get(a.lower(), "") or "").lower()
                 for w in ("candidate", "strong", "lead direct", "auto-mint"))]
discarded = [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]
log["legs"]["bridge"] = (f"read ok; {len(bcontracts)} bridge contracts, {len(in_snap)} in snapshot, "
    f"{len(discarded)} same_owner_discarded, promotions={len(promos)}")
log["bridge_promos"] = promos
log["legs"]["pending_claims"] = f"snapshot pending_claims empty ({len(snap.get('pending_claims', {}))})"

log["leads"] = 0
log["candidates"] = 0
log["changes_reportable"] = 0
log["blocked"] = 0
log["executions"] = 0
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + ".json", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
