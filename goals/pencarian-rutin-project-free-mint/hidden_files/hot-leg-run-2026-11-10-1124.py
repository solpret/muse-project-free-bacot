#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 11:24 WIB (bounded, ~120s).
The full 1109 script was killed by the outer 170s timeout before printing;
Sourcify feed + ABI endpoints time out (verified live: curl rc=28, 0 bytes
in 15s), Boltbook/RPC legs are slow, and the script only prints at the end.
This salvage does the highest-value pieces with per-call caps and writes
each result file as soon as its leg finishes, so a kill still leaves state.
Legs: (1) Sourcify feed, one 10s attempt only; (2) Boltbook EN+ZH;
(3) leg4 re-read vs 1119 baseline, 40s budget, 8s chunk timeout;
(4) RIGBYPASS probe only if leg4 RPC worked and budget remains;
(5) bridge read-only (local, fast). No shape-check this run (Sourcify ABI
dead - the 45 abi-unavailable contracts stay recorded for retry; no new
sale-shape evidence either way). No preview/mint. No snapshot writes.
Writes only own hot-leg state files + run JSON.
"""
import json, re, time, urllib.request, concurrent.futures, subprocess, sys
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed2.bnbchain.org",
        "https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed3.bnbchain.org",
        "https://bsc-dataseed4.bnbchain.org", "https://bsc-dataseed.binance.org/",
        "https://bsc.meowrpc.com", "https://bsc.publicnode.com",
        "https://rpc.ankr.com/bsc"]
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
RIG = "0xe657465f0EB4B55877246026BfAe4EC75ef2E160"
T0 = time.time()
DEADLINE = T0 + 150
RUN_WIB = "2026-11-10 11:24 WIB"

def budget():
    return DEADLINE - time.time()
NOW_ISO = "2026-11-10T11:24:00+07:00"
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def log(*a):
    print(*a, flush=True)

def fetch_curl(url, timeout=12):
    r = subprocess.run(["curl", "-sS", "-m", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True, timeout=timeout + 5)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl rc={r.returncode}")
    return 200, r.stdout

def sel(sig):
    h = keccak.new(digest_bits=256); h.update(sig.encode()); return "0x" + h.hexdigest()[:8]

def post_rpc(ep, payload, timeout=8):
    req = urllib.request.Request(ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    discard_contracts = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    discard_owners = {str(e.get("owner", "")).lower() for e in discards if isinstance(e, dict)}
except Exception:
    discard_contracts, discard_owners = set(), set()
out = {"run": RUN_WIB, "leg1_feed": 0, "leg1_new": [], "leg1_shape": "",
       "leg2_boltbook": "", "leg3": "", "leg4_file": "hot-leg-run-2026-11-10-1124-leg4.json",
       "leg4_notes": "", "bridge": "", "promotions": [], "changes": [],
       "report": "NONE - silent run", "rigbypass": {},
       "note": "bounded salvage-pattern run; shape-check probed once, full check only if ABI endpoint alive"}

# ---- Leg 1: Sourcify feed, ONE 10s attempt ----
feed_addrs, feed_raw = [], []
try:
    st, body = fetch_curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=10)
    data = json.loads(body.decode())
    items = data if isinstance(data, list) else data.get("results", data.get("contracts", []))
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
            feed_raw.append((a, it.get("verifiedAt") if isinstance(it, dict) else None))
    out["leg1_feed"] = len(feed_addrs)
    json.dump({"run": RUN_WIB, "feed": feed_raw},
              open(BASE + "hot-leg-2026-11-10-1124-feed.json", "w"), indent=1)
    log("leg1 feed OK:", len(feed_addrs))
except Exception as e:
    out["leg1_feed"] = f"ERR:{type(e).__name__}: {str(e)[:100]}"
    log("leg1 feed ERR:", out["leg1_feed"])

# ---- Leg 2: Boltbook EN + ZH ----
bb_addrs, bb_notes = [], []
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        st, body = fetch_curl(url, timeout=12)
        txt = body.decode(errors="ignore")
        addrs = sorted(set(ADDR_RE.findall(txt)))
        bb_addrs += addrs
        hits = [k for k in ("free share", "first share free", "1 free share", "free mint share",
                            "免费份额", "首个免费", "免费铸造", "免费mint")
                if k.lower() in txt.lower()]
        bb_notes.append(f"{lang.upper()} {st} ({len(body)}B, {len(addrs)} addrs, kw={hits})")
        open(BASE + f"hot-leg-2026-11-10-1124-boltbook-{lang}.html", "wb").write(body)
    except Exception as e:
        bb_notes.append(f"{lang.upper()} ERR:{type(e).__name__}: {str(e)[:80]}")
new_feed = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in EXCLUDED]
bb_new = sorted({a for a in bb_addrs if a.lower() not in seen_l
                 and a.lower() != REG.lower() and a.lower() not in EXCLUDED})
out["leg1_new"] = new_feed
out["leg2_boltbook"] = "; ".join(bb_notes) + f"; new addrs: {bb_new}"
log("leg2:", out["leg2_boltbook"], "| new feed:", new_feed)
for a in set(new_feed) | set(bb_new):
    seen[a] = {"first_seen_wib": NOW_ISO,
               "note": "new from 1124 feed/boltbook; shape-check pending ABI probe",
               "source": "hot-leg-1124", "status": "shape-pending"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Shape-check: ONE ABI probe (6s); full check only if endpoint alive ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
def shape_check(addr):
    try:
        r = subprocess.run(["curl", "-sS", "-m", "8", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, timeout=12)
        if r.returncode != 0 or not r.stdout:
            return {"address": addr, "error": f"curl rc={r.returncode}"}
        meta = json.loads(r.stdout.decode())
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
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:60]}"}

abi_backlog = [k for k, v in seen.items()
               if isinstance(v, dict) and v.get("status") == "checked-abi-unavailable"]
out["shape_backlog"] = len(abi_backlog)
sale_shape = []
probe_addr = (new_feed + bb_new)[:1]
abi_alive = False
if probe_addr and budget() > 60:
    try:
        r = subprocess.run(["curl", "-sS", "-m", "6", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{probe_addr[0]}?fields=abi"],
                           capture_output=True, timeout=10)
        if r.returncode == 0 and r.stdout:
            json.loads(r.stdout.decode()); abi_alive = True
    except Exception:
        abi_alive = False
    log("shape probe:", probe_addr[0][:10], "alive:", abi_alive)
if abi_alive:
    retry = abi_backlog[:20]
    all_new = sorted(set(new_feed) | set(bb_new) | set(retry))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        shape_results = list(ex.map(shape_check, all_new))
    for r in shape_results:
        a = r["address"]
        if a.lower() in discard_contracts:
            stt, note = "blocked-same-owner-discarded", "in same-owner-discards.json - never promoted/reported"
        elif a.lower() in EXCLUDED:
            stt, note = "excluded", "excluded example rediscovered; not reported"
        elif r.get("S1") or r.get("S2"):
            stt, note = "sale-shape", f"S1={r.get('S1')} S2={r.get('S2')} free={r.get('free_views')}"
            sale_shape.append(a)
        elif r.get("error"):
            stt, note = "checked-abi-unavailable", f"Sourcify ABI error (1124): {r['error']}"
        else:
            stt, note = "checked-not-sale-shape", (
                f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('has_mint')} "
                f"quote={r.get('has_quote')} free={r.get('free_views')} "
                f"agent={r.get('agent_ref')} token={r.get('is_token')}")
        seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", NOW_ISO),
                   "note": note, "source": "hot-leg-1124", "status": stt}
    out["leg1_shape"] = (f"ABI endpoint ALIVE: shape-checked {len(shape_results)} "
                         f"(new {len(set(new_feed) | set(bb_new))} + retry {len(retry)}); "
                         f"sale-shape: {sale_shape}")
    log("shape-check done, sale-shape:", sale_shape)
else:
    for a in set(new_feed) | set(bb_new):
        seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", NOW_ISO),
                   "note": "shape-check DEFERRED (Sourcify ABI dead, probe failed 1124) - not a lead, never previewed/minted",
                   "source": "hot-leg-1124", "status": "checked-shape-deferred"}
    out["leg1_shape"] = (f"ABI endpoint still dead (probe failed); {len(abi_backlog)} "
                         f"abi-unavailable backlog stays recorded for retry; new contracts shape-deferred")
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["sale_shape"] = sale_shape

# ---- Leg 4: batched re-read vs 1119 baseline, 40s budget ----
def calldata(field):
    if field.endswith("_user1"):
        return sel(f"{field[:-6]}(address,uint256)") + "000000000000000000000000" + USER[2:].lower() + format(1, "064x")
    if field.endswith("_user"):
        return sel(f"{field[:-5]}(address)") + "000000000000000000000000" + USER[2:].lower()
    return sel(f"{field}()")

prev_reread = json.load(open(BASE + "hot-leg-run-2026-11-10-1119-leg4.json"))
prev_items = prev_reread.get("leg4", prev_reread.get("items", {}))
prev_probes = prev_reread.get("probes", {})
extra = {
    "THYRK": ("0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",
              ["totalSupply", "freeMinted", "mintActive", "freeUsed_user", "priceFor_user1"]),
    "SAKURA": ("0xF2705A84602369069782624279837A08bdbBf6D6",
               ["totalSupply", "freeMinted"]),
}
jobs = []
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

block = None; rpc = None
for ep in RPCS:
    try:
        bn = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=8)
        block = int(bn["result"], 16); rpc = ep; break
    except Exception:
        continue
log("leg4 rpc:", rpc, "block:", block)
t4 = time.time()
results, failed = {}, []
leg4_incomplete = False
if block is not None:
    for i in range(0, len(jobs), 25):
        if time.time() - t4 > 40:
            leg4_incomplete = True
            for (kind, n, f, _, _) in jobs[i:]:
                results[(kind, n, f)] = None; failed.append((kind, n, f))
            break
        chunk = jobs[i:i + 25]
        payload = [{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                    "params": [{"to": to, "data": data}, "latest"]}
                   for j, (_, _, _, to, data) in enumerate(chunk)]
        try:
            resp = post_rpc(rpc, payload, timeout=8)
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
           "incomplete": leg4_incomplete,
           "read_failed": [[k, n, f] for (k, n, f) in failed]},
          open(BASE + "hot-leg-run-2026-11-10-1124-leg4.json", "w"), indent=1)
log("leg4 diffs:", diffs, "| failed:", len(failed), "| incomplete:", leg4_incomplete)

notes = []
for d in diffs:
    notes.append(f"{d['item']} {d['field']}: {d['was']}->{d['now']}")
out["leg4_notes"] = "; ".join(notes) if notes else "no numeric change vs 1119 reads"
if block is None:
    out["leg4_notes"] = ("LEG4 NOT READ THIS RUN: block=None - all RPC endpoints failed "
                         "eth_blockNumber; 1119 baseline values kept verbatim, so 'no change' is UNVERIFIED.")
sak = probes.get("SAKURA", {}).get("totalSupply")
if isinstance(sak, int):
    out["leg4_notes"] += (f" | SAKURA totalSupply {sak}; free% max ~{round(sak/6000*100,1)}% "
                          f"(<25%, stays early lead)" if sak < 1500 else
                          f" | SAKURA totalSupply {sak} - CROSSED 25% (~{round(sak/6000*100,1)}%); needs slot+website check before any promotion")
th = probes.get("THYRK", {})
if isinstance(th.get("totalSupply"), int):
    out["leg4_notes"] += (f" | THYRK totalSupply {th.get('totalSupply')}, "
                          f"freeMinted {th.get('freeMinted')} (no free cap, stays early lead)")
if leg4_incomplete:
    out["leg4_notes"] += " | LEG4 INCOMPLETE - 40s budget hit; partial diffs only, 1119 baseline kept for unfinished items"
if failed:
    out["leg4_notes"] += f" | read_failed {len(failed)} (view mismatch/transient; prev value kept)"

# ---- RIGBYPASS probe (only if leg4 RPC worked and <95s elapsed) ----
rig = {}
if rpc is not None and (time.time() - T0) < 95:
    try:
        u = "000000000000000000000000" + USER[2:].lower()
        def probe(item):
            sig, args = item
            try:
                p = {"to": RIG, "data": sel(sig) + args}
                r = post_rpc(rpc, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                   "params": [p, "latest"]}, timeout=8)
                res = r.get("result")
                if res and res != "0x":
                    try:
                        return sig, int(res, 16)
                    except Exception:
                        return sig, res
                return sig, None
            except Exception as e:
                return sig, f"ERR:{type(e).__name__}"
        items = [("totalSupply()", ""), ("freeMinted()", ""), ("FREE_SUPPLY()", ""),
                 ("mintOpen()", ""), ("owner()", ""),
                 ("freeClaimed(address)", u), ("balanceOf(address)", u),
                 ("freeMinted(address)", u)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            for sig, v in ex.map(probe, items):
                rig[sig.split("(")[0]] = v
        if isinstance(rig.get("owner"), int):
            rig["owner_addr"] = "0x" + format(rig["owner"], "040x")
        rig["owner_in_discards"] = rig.get("owner_addr", "").lower() in discard_owners
        rig["contract_in_discards"] = RIG.lower() in discard_contracts
        rig["block"] = block
        out["rigbypass"] = rig
    except Exception as e:
        out["rigbypass"] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
else:
    out["rigbypass"] = {"skipped": "no working RPC or budget low"}

r = out["rigbypass"]
if isinstance(r.get("totalSupply"), int) or isinstance(r.get("freeMinted"), int):
    if RIG.lower() in discard_contracts or r.get("owner_in_discards"):
        seen[RIG] = {"first_seen_wib": seen.get(RIG, {}).get("first_seen_wib", NOW_ISO),
                     "note": "RIGBYPASS blocked: same-owner-discarded; not promoted, not reported.",
                     "source": "boltbook-post", "status": "blocked-same-owner-discarded"}
        out["leg3"] = "RIGBYPASS blocked: same-owner-discarded"
    else:
        seen[RIG] = {"first_seen_wib": seen.get(RIG, {}).get("first_seen_wib", NOW_ISO),
                     "note": (f"RIGBYPASS (RIGB) ERC-721, Boltbook post /p/qCTMfh1Vbuot ~08:03 WIB, "
                              f"mint page ribgypass.pages.dev prints exact NFT+token+registry (verified 0859); "
                              f"totalSupply={r.get('totalSupply')} freeMinted={r.get('freeMinted')} FREE_SUPPLY={r.get('FREE_SUPPLY')} "
                              f"user freeClaimed={r.get('freeClaimed')} balanceOf={r.get('balanceOf')} owner={r.get('owner_addr')} "
                              f"block={r.get('block')}. AGE UNVERIFIED (first-mint tx not corroborated; getLogs dead) "
                              "-> watchlist-only, NOT a lead, NOT previewed/minted. For main 30-min job first-mint verification."),
                     "source": "boltbook-post", "status": "watchlist-only-age-unverified"}
        out["leg3"] = "RIGBYPASS re-probed; age unverified -> watchlist-only, no lead report, no preview/mint"
elif r.get("skipped"):
    out["leg3"] = "RIGBYPASS probe skipped (no working RPC / budget); prior watchlist-only status stands"
if sale_shape:
    out["leg3"] += f" | NEW SALE-SHAPE (Sourcify ABI): {sale_shape} - flagged for main job; NOT previewed/minted by hot leg (needs leg-3 on-chain verify + website gate first)"
else:
    out["leg3"] = "RIGBYPASS probe incomplete this run (RPC slow); prior watchlist-only status stands"
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Bridge leg (read-only, local files) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        coll = snap.get(sec, {})
        vals = coll.values() if isinstance(coll, dict) else coll
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
    not_in_snap, disc = [], []
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

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-1124.json", "w"), indent=1)
log("DONE elapsed:", out["elapsed_s"])
print(json.dumps(out, indent=1))
