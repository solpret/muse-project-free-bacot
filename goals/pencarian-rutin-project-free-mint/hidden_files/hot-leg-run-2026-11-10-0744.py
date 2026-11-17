#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 07:44 WIB. Legs 1-4 + bridge (read-only).
Writes only own hot-leg state files + run JSON. No preview/mint.
No snapshot writes. Hard-capped; stalled legs skipped, not waited on.
Leg 4: batched eth_call re-read of 0729 baseline items + THYRK/SAKURA probes."""
import json, re, time, urllib.request, concurrent.futures, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed.bnbchain.org", "https://bsc.nodereal.io/",
        "https://bsc-dataseed1.binance.org/"]
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
RUN_WIB = "2026-11-10 07:44 WIB"
NOW_ISO = "2026-11-10T07:44:00+07:00"
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def fetch(url, timeout=15, ua="hot-leg/1.0"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
reported = json.load(open(BASE + "hot-leg-reported.json"))
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    discard_l = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
except Exception:
    discard_l = set()
out = {"run": RUN_WIB, "leg1_feed": 0, "leg1_new": [], "leg1_shape": "",
       "leg2_boltbook": "", "leg3": "no new sale-shape contract; nothing to verify",
       "leg4_file": "hot-leg-run-2026-11-10-0744-leg4.json", "leg4_notes": "",
       "bridge": "", "promotions": [], "changes": [], "report": "NONE - silent run"}

# ---- Leg 1: Sourcify recently-verified feed ----
feed_addrs = []
feed_raw = []
try:
    st, body = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    data = json.loads(body.decode())
    items = data if isinstance(data, list) else data.get("results", data.get("contracts", []))
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
            feed_raw.append((a, it.get("verifiedAt") if isinstance(it, dict) else None))
    out["leg1_feed"] = len(feed_addrs)
    json.dump({"run": RUN_WIB, "feed": feed_raw},
              open(BASE + "hot-leg-2026-11-10-0744-feed.json", "w"), indent=1)
except Exception as e:
    out["leg1_feed"] = f"ERR:{type(e).__name__}"

new_feed = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in EXCLUDED]
out["leg1_new"] = new_feed

# ---- Leg 2: Boltbook front page EN + ZH (boltbook.fun) ----
def fetch_bb(url):
    try:
        return fetch(url, timeout=15)
    except Exception:
        r = subprocess.run(["curl", "-sS", "-m", "20", "-A", "hot-leg/1.0", url],
                           capture_output=True, timeout=25)
        if r.returncode != 0 or not r.stdout:
            raise RuntimeError(f"curl rc={r.returncode}")
        return 200, r.stdout

bb_addrs, bb_notes = [], []
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        st, body = fetch_bb(url)
        txt = body.decode(errors="ignore")
        addrs = sorted(set(ADDR_RE.findall(txt)))
        bb_addrs += addrs
        hits = [k for k in ("free share", "first share free", "1 free share", "free mint share",
                            "免费份额", "首个免费", "免费铸造", "免费mint")
                if k.lower() in txt.lower()]
        bb_notes.append(f"{lang.upper()} {st} ({len(body)}B, {len(addrs)} addrs, kw={hits})")
        open(BASE + f"hot-leg-2026-11-10-0744-boltbook-{lang}.html", "wb").write(body)
    except Exception as e:
        bb_notes.append(f"{lang.upper()} ERR:{type(e).__name__}")
bb_new = sorted({a for a in bb_addrs if a.lower() not in seen_l
                 and a.lower() != REG.lower() and a.lower() not in EXCLUDED})
out["leg2_boltbook"] = "; ".join(bb_notes) + f"; new addrs: {bb_new}"

# ---- Shape-check any new contract (S1/S2 via Sourcify ABI) ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
def shape_check(addr):
    try:
        st, body = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        meta = json.loads(body.decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

all_new = sorted(set(new_feed) | set(bb_new))
shape_results = []
if all_new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        shape_results = list(ex.map(shape_check, all_new))
    out["leg1_shape"] = json.dumps(shape_results)
    for r in shape_results:
        a = r["address"]
        if a.lower() in discard_l:
            stt, note = "blocked-same-owner-discarded", "in same-owner-discards.json - never promoted/reported"
        elif a.lower() in EXCLUDED:
            stt, note = "excluded", "excluded example rediscovered; not reported"
        elif r.get("S1") or r.get("S2"):
            stt, note = "sale-shape", f"S1={r.get('S1')} S2={r.get('S2')} free={r.get('free_views')}"
        else:
            stt, note = "checked-not-sale-shape", (
                f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('has_mint')} "
                f"quote={r.get('has_quote')} free={r.get('free_views')} "
                f"agent={r.get('agent_ref')} token={r.get('is_token')}")
        seen[a] = {"first_seen_wib": NOW_ISO, "note": note,
                   "source": "hot-leg-0744", "status": stt}
else:
    out["leg1_shape"] = "all feed/Boltbook contracts already in hot-leg-seen.json; no new contract to shape-check"

sale_shape = [r for r in shape_results if (r.get("S1") or r.get("S2"))
                and r["address"].lower() not in discard_l]
if sale_shape:
    out["leg3"] = f"NEW SALE-SHAPE: {sale_shape} - needs on-chain verify + gate (not auto-handled here; flagged for main job)"
    for r in sale_shape:
        seen[r["address"]]["status"] = "watchlist-only-age-unverified"
        seen[r["address"]]["note"] += " | age UNVERIFIED - watchlist-only, never lead"

# ---- Leg 4: batched re-read of 0729 baseline items + THYRK/SAKURA probes ----
def sel(sig):
    h = keccak.new(digest_bits=256); h.update(sig.encode()); return "0x" + h.hexdigest()[:8]

def calldata(field):
    if field.endswith("_user1"):
        return sel(f"{field[:-6]}(address,uint256)") + "000000000000000000000000" + USER[2:].lower() + format(1, "064x")
    if field.endswith("_user"):
        return sel(f"{field[:-5]}(address)") + "000000000000000000000000" + USER[2:].lower()
    return sel(f"{field}()")

def post_rpc(ep, payload):
    req = urllib.request.Request(ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

prev_reread = json.load(open(BASE + "hot-leg-run-2026-11-10-0734-leg4.json"))
prev_items = prev_reread.get("leg4", prev_reread.get("items", {}))
prev_probes = prev_reread.get("probes", {})
extra = {
    "THYRK": ("0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",
              ["totalSupply", "freeMinted", "mintActive", "freeUsed_user", "priceFor_user1"]),
    "SAKURA": ("0xF2705A84602369069782624279837A08bdbBf6D6",
               ["totalSupply", "freeMinted"]),
}
jobs = []  # (kind, name, field, address, data)
for name, entry in prev_items.items():
    addr = entry.get("address")
    if not addr:
        continue
    for field in entry:
        if field == "address":
            continue
        jobs.append(("item", name, field, addr, calldata(field)))
for name, (addr, fields) in extra.items():
    for f in fields:
        jobs.append(("probe", name, f, addr, calldata(f)))

block = None
rpc = None
for ep in RPCS:
    try:
        bn = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
        block = int(bn["result"], 16)
        rpc = ep
        break
    except Exception:
        continue
t4 = time.time()
results, failed = {}, []
if block is not None:
    for i in range(0, len(jobs), 25):
        chunk = jobs[i:i + 25]
        payload = [{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                    "params": [{"to": to, "data": data}, "latest"]}
                   for j, (_, _, _, to, data) in enumerate(chunk)]
        try:
            resp = post_rpc(rpc, payload)
            if isinstance(resp, dict):
                resp = [resp]
            for j, item in enumerate(resp):
                kind, n, f, _, _ = chunk[j]
                if isinstance(item, dict) and isinstance(item.get("result"), str) and item["result"] not in ("0x", ""):
                    try:
                        results[(kind, n, f)] = int(item["result"], 16)
                    except Exception:
                        results[(kind, n, f)] = None; failed.append((kind, n, f))
                else:
                    results[(kind, n, f)] = None; failed.append((kind, n, f))
        except Exception:
            for (kind, n, f, _, _) in chunk:
                results[(kind, n, f)] = None; failed.append((kind, n, f))

leg4_items, diffs = {}, []
for name, entry in prev_items.items():
    row = {"address": entry.get("address")}
    for field in entry:
        if field == "address":
            continue
        v = results.get(("item", name, field))
        if v is None:
            row[field] = entry.get(field)
        else:
            row[field] = v
            bv = entry.get(field)
            if isinstance(bv, int) and v != bv:
                diffs.append({"item": name, "field": field, "was": bv, "now": v})
    leg4_items[name] = row
probes = {}
for name, (addr, fields) in extra.items():
    probes[name] = {"address": addr}
    for f in fields:
        v = results.get(("probe", name, f))
        probes[name][f] = v
        pv = prev_probes.get(name, {}).get(f)
        if isinstance(v, int) and isinstance(pv, int) and v != pv:
            diffs.append({"item": name, "field": f, "was": pv, "now": v})
json.dump({"run": RUN_WIB, "block": block, "leg4": leg4_items, "probes": probes,
           "diffs": diffs, "elapsed_s": round(time.time() - t4, 1),
           "read_failed": [[k, n, f] for (k, n, f) in failed]},
          open(BASE + "hot-leg-run-2026-11-10-0744-leg4.json", "w"), indent=1)

notes = []
for d in diffs:
    notes.append(f"{d['item']} {d['field']}: {d['was']}->{d['now']}")
out["leg4_notes"] = "; ".join(notes) if notes else "no numeric change vs 07:29 reads"
sak = probes.get("SAKURA", {}).get("totalSupply")
if isinstance(sak, int):
    out["leg4_notes"] += f" | SAKURA totalSupply {sak}; free% max ~{round(sak/6000*100,1)}% (<25%, stays early lead)" if sak < 1500 else f" | SAKURA totalSupply {sak} - CROSSED 25% (~{round(sak/6000*100,1)}%); needs slot+website check before any promotion"
th = probes.get("THYRK", {})
if isinstance(th.get("totalSupply"), int):
    out["leg4_notes"] += (f" | THYRK totalSupply {th.get('totalSupply')}, "
                          f"freeMinted {th.get('freeMinted')} (no free cap, stays early lead)")
if failed:
    out["leg4_notes"] += f" | read_failed {len(failed)} (view mismatch/transient; prev value kept)"

# ---- Bridge leg (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        coll = snap.get(sec, {})
        if isinstance(coll, dict):
            vals = coll.values()
        else:
            vals = coll
        for v in vals:
            if isinstance(v, dict):
                for f in ("address", "sale", "token", "contract"):
                    if v.get(f):
                        snap_addrs.add(str(v[f]).lower())
    pc = snap.get("pending_claims", {})
    vals = pc.values() if isinstance(pc, dict) else pc
    for v in vals:
        if isinstance(v, dict):
            for f in ("address", "sale", "token", "contract", "mint"):
                if v.get(f):
                    snap_addrs.add(str(v[f]).lower())
    bcontracts = bridge.get("contracts", {})
    blist = list(bcontracts.items()) if isinstance(bcontracts, dict) else [(None, c) for c in bcontracts]
    not_in_snap = []
    disc = []
    for k, c in blist:
        if isinstance(c, dict):
            a = (c.get("address") or c.get("contract") or k or "").lower()
            tier = c.get("tier") or c.get("status") or ""
            if c.get("same_owner_discarded"):
                disc.append(a[:10])
            if a and a not in snap_addrs:
                not_in_snap.append((a[:10], tier))
    out["bridge"] = (f"read-only; {len(blist)} contracts, {len(not_in_snap)} not in snapshot "
                     f"{not_in_snap} - none meets a Free Bacot tier; noted for main job only, "
                     f"no report. same_owner_discarded in bridge: {disc} - never promoted.")
except Exception as e:
    out["bridge"] = f"SKIP - bridge unreadable ({type(e).__name__}); run continues normally"

# ---- Persist own state only ----
if all_new:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-0744.json", "w"), indent=1)
print(json.dumps(out, indent=1))
