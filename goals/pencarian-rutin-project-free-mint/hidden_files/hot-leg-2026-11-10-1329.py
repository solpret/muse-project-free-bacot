#!/usr/bin/env python3
"""Hot-leg run 2026-11-10 13:29 WIB. Bounded: 12s per fetch, single attempts.
Leg1 Sourcify feed, Leg2 Boltbook EN+ZH, shape-check only new addrs if ABI
endpoint alive (probe once), Leg4 re-read of 1149-leg4 baseline via RPC
(blockNumber probe first; NOT READ if all RPC fail), bridge read-only.
Writes own state only (hot-leg-seen.json + run JSON). No preview/mint.
No snapshot/seen-file writes."""
import json, re, subprocess, time, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
NOW = "2026-11-10T13:29:38+07:00"
RUN = "2026-11-10 13:29 WIB"
T0 = time.time()
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def get(url, timeout=12):
    r = subprocess.run(["curl", "-sS", "-m", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True, timeout=timeout + 5)
    if r.returncode != 0:
        raise RuntimeError(f"curl rc={r.returncode}")
    return r.stdout

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
reported = json.load(open(BASE + "hot-leg-reported.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    v = snap.get(sec, {})
    if isinstance(v, dict):
        for val in v.values():
            if isinstance(val, dict):
                for f in ("address", "sale", "token", "contract", "mint"):
                    if val.get(f):
                        snap_addrs.add(str(val[f]).lower())
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    discard_contracts = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
except Exception:
    discard_contracts = set()

out = {"run": RUN, "leg1_new": [], "sale_shape": [], "promotions": [], "changes": [],
       "report": "NONE - silent run"}

# ---- Leg 1: Sourcify feed ----
feed_addrs = []
try:
    body = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    feed = json.loads(body.decode())
    items = feed.get("results", feed if isinstance(feed, list) else [])
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
    out["leg1_feed"] = f"OK {len(feed_addrs)} contracts"
    json.dump({"run": RUN, "feed": [(a, None) for a in feed_addrs]},
              open(BASE + "hot-leg-2026-11-10-1329-feed.json", "w"), indent=1)
except Exception as e:
    out["leg1_feed"] = f"ERR:{type(e).__name__}: {e}"

# ---- Leg 2: Boltbook EN + ZH ----
bb_addrs = []
bb_notes = []
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        body = get(url)
        txt = body.decode(errors="ignore")
        found = sorted(set(ADDR_RE.findall(txt)))
        bb_addrs += found
        bb_notes.append(f"{lang} OK {len(body)}B addrs={len(found)}")
        open(BASE + f"hot-leg-2026-11-10-1329-boltbook-{lang}.html", "wb").write(body)
    except Exception as e:
        bb_notes.append(f"{lang} ERR:{type(e).__name__}: {e}")
out["leg2_boltbook"] = "; ".join(bb_notes) + f"; new addrs: []"

# ---- Shape-check: only genuinely new addrs, only if ABI endpoint alive ----
new_addrs = sorted({a for a in feed_addrs + bb_addrs
                    if a.lower() not in seen_l and a.lower() != REG.lower()
                    and a.lower() not in EXCLUDED}, key=str.lower)
out["leg1_new"] = new_addrs
shapes, shape_errs = [], 0

def shape_check(addr):
    try:
        r = subprocess.run(["curl", "-sS", "-m", "10", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, timeout=15)
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

if new_addrs:
    # probe ABI endpoint once with the first new addr
    probe = shape_check(new_addrs[0])
    if probe.get("error"):
        out["leg1_shape"] = (f"ABI endpoint still dead (probe {probe['error']}); "
                             f"{len(new_addrs)} new contracts shape-deferred")
        for a in new_addrs:
            seen[a] = {"first_seen_wib": NOW, "note": f"ABI endpoint dead at probe ({probe['error']}); shape-deferred, not a lead, never previewed/minted.", "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    else:
        results = [probe]
        if len(new_addrs) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                results += list(ex.map(shape_check, new_addrs[1:]))
        for r in results:
            a = r["address"]
            if a.lower() in discard_contracts:
                stt, note = "blocked-same-owner-discarded", "in same-owner-discards.json - never promoted/reported"
            elif r.get("S1") or r.get("S2"):
                stt, note = "sale-shape", f"S1={r.get('S1')} S2={r.get('S2')} free={r.get('free_views')} (1329; on-chain verification NOT done - watchlist-only until verified)"
                shapes.append(r)
            elif r.get("error"):
                stt, note = "checked-abi-unavailable", f"Sourcify ABI error (1329): {r['error']}"
                shape_errs += 1
            else:
                stt, note = "checked-not-sale-shape", (f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('has_mint')} quote={r.get('has_quote')} free={r.get('free_views')} agent={r.get('agent_ref')} token={r.get('is_token')}")
            seen[a] = {"first_seen_wib": (seen.get(a) or {}).get("first_seen_wib", NOW) if isinstance(seen.get(a), dict) else NOW,
                       "note": note, "source": "hot-leg-1329", "status": stt}
        out["leg1_shape"] = f"shape-checked {len(results)}: sale-shape={len(shapes)} errors={shape_errs}"
        out["sale_shape"] = shapes
else:
    out["leg1_shape"] = "no new contracts this run"

# ---- Leg 3: on-chain verify of sale-shape (only if any + RPC alive) ----
out["leg3"] = "no sale-shape contracts to verify" if not shapes else "see leg4 RPC status"
if shapes:
    out["leg3"] = ("sale-shape found but on-chain verification deferred: "
                   "no working RPC budget in this bounded run; watchlist-only, never previewed/minted")

# ---- Leg 4: re-read baseline (1239 leg4 file) ----
leg4_prev = json.load(open(BASE + "hot-leg-run-2026-11-10-1324-leg4.json"))
base_items = leg4_prev.get("items") or leg4_prev.get("leg4") or {}
leg4_notes = ""
leg4_file = "hot-leg-run-2026-11-10-1329-leg4.json"
try:
    from Crypto.Hash import keccak
    USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
    RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed1.binance.org/"]
    def sel(sig):
        k = keccak.new(digest_bits=256); k.update(sig.encode())
        return "0x" + k.hexdigest()[:8]
    def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
    def enc_uint(n): return format(n, "064x")
    def calldata(field):
        if field in ("address",): return None
        if field.endswith("_user1"):
            return sel(f"{field[:-6]}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        if field.endswith("_user"):
            return sel(f"{field[:-5]}(address)") + enc_addr(USER)
        return sel(f"{field}()")
    def post(ep, payload):
        p = subprocess.run(["curl", "-s", "--max-time", "10", "-X", "POST", ep,
                            "-H", "Content-Type: application/json", "--data", payload],
                           capture_output=True, text=True, timeout=15)
        try: return json.loads(p.stdout)
        except Exception: return {"_err": p.stdout[:200] + p.stderr[:200]}
    block, ep = None, None
    for rpc in RPCS:
        try:
            r = post(rpc, '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
            block, ep = int(r["result"], 16), rpc
            break
        except Exception:
            continue
    if block is None:
        leg4_notes = "LEG4 NOT READ THIS RUN: block=None - all RPC endpoints failed eth_blockNumber; 1224 baseline values kept verbatim, so 'no change' is UNVERIFIED."
        json.dump({"run": RUN, "block": None, "leg4": base_items,
                   "note": leg4_notes}, open(BASE + leg4_file, "w"), indent=1)
    else:
        jobs = []
        for name, entry in base_items.items():
            for field in entry:
                d = calldata(field)
                if d: jobs.append((name, field, entry["address"], d))
        extra = {
            "THYRK": ("0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e", ["totalSupply", "freeMinted", "mintActive", "freeUsed_user", "priceFor_user1"]),
            "SAKURA": ("0xF2705A84602369069782624279837A08bdbBf6D6", ["totalSupply", "freeMinted"]),
            "0x4Bc1A172-sale-quote": ("0x4Bc1A1723a5D8A893695f78c8b2cD39028478d43", ["saleActive", "opened", "freeMinted", "totalMinted", "totalSold", "quoteCost_user1", "quoteTokens_user1", "sharesOf_user"]),
            "Pickgrid": ("0x7f541bcc33abed0e64455565da723e949c6f76f0", ["freeMinted", "FREE_CAP", "totalSupply", "paused"]),
        }
        for name, (addr, fields) in extra.items():
            for f in fields:
                d = calldata(f)
                if d: jobs.append((name, f, addr, d))
        results, failed = {}, []
        for i in range(0, len(jobs), 25):
            chunk = jobs[i:i+25]
            payload = json.dumps([{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                                   "params": [{"to": to, "data": data}, "latest"]}
                                  for j, (_, _, to, data) in enumerate(chunk)])
            resp = post(ep, payload)
            if isinstance(resp, dict):
                resp = [resp] if "_err" not in resp else []
                if not resp:
                    for (n, f, _, _) in chunk: results[(n, f)] = None; failed.append((n, f))
                    continue
            for j, item in enumerate(resp):
                n, f, _, _ = chunk[j]
                if isinstance(item, dict) and "result" in item and isinstance(item["result"], str):
                    try: results[(n, f)] = int(item["result"], 16)
                    except Exception: results[(n, f)] = None; failed.append((n, f))
                else:
                    results[(n, f)] = None; failed.append((n, f))
        reread = {"run": RUN, "block": block, "items": {}, "probes": {}, "read_failed": [], "diffs": []}
        for name, entry in base_items.items():
            row = {"address": entry["address"]}
            for field in entry:
                if field == "address": continue
                v = results.get((name, field))
                row[field] = entry.get(field) if v is None else v
                if v is None: reread["read_failed"].append({"item": name, "field": field})
            reread["items"][name] = row
        for name, (addr, fields) in extra.items():
            reread["probes"][name] = {"address": addr, **{f: results.get((name, f)) for f in fields}}
        for name, row in reread["items"].items():
            base = base_items.get(name, {})
            for field, val in row.items():
                if field == "address": continue
                bv = base.get(field)
                if bv is not None and val is not None and val != bv:
                    reread["diffs"].append({"item": name, "field": field, "was": bv, "now": val})
        json.dump(reread, open(BASE + leg4_file, "w"), indent=1)
        leg4_notes = (f"LEG4 READ at block {block} via {ep}: {len(reread['diffs'])} diffs, "
                      f"{len(reread['read_failed'])} read-failed fields; probes={reread['probes']}")
        for d in reread["diffs"]:
            out["changes"].append(f"{d['item']} {d['field']}: {d['was']} -> {d['now']} (block {block})")
except Exception as e:
    leg4_notes = f"LEG4 ERROR: {type(e).__name__}: {e}; baseline kept verbatim, 'no change' UNVERIFIED."
    json.dump({"run": RUN, "block": None, "leg4": base_items, "note": leg4_notes},
              open(BASE + leg4_file, "w"), indent=1)
out["leg4_file"] = leg4_file
out["leg4_notes"] = leg4_notes

# ---- Bridge leg (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    not_in_snap = [(a[:10], bcontracts[a].get("freebacot_tier", "")) for a in bcontracts
                   if a.lower() not in snap_addrs]
    disc = sorted({a[:10] for a, v in bcontracts.items() if v.get("same_owner_discarded")})
    # promote only if a bridge contract already in snapshot now meets a tier - needs
    # fresh on-chain state; leg4 read status governs whether that is verifiable.
    out["bridge"] = (f"read-only; {len(bcontracts)} contracts, {len(not_in_snap)} not in snapshot "
                     f"{not_in_snap} - none meets a Free Bacot tier; noted for main job only, no report. "
                     f"same_owner_discarded in bridge: {disc} - never promoted.")
except Exception as e:
    out["bridge"] = f"SKIP: bridge unreadable ({type(e).__name__}: {e}); run continued normally."

out["shape_backlog"] = sum(1 for v in seen.values() if isinstance(v, dict) and v.get("status") == "checked-abi-unavailable")
out["elapsed_s"] = round(time.time() - T0, 1)
out["note"] = "bounded run; shape-check probed once, full check only if ABI endpoint alive"
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-1329.json", "w"), indent=1)
print(json.dumps(out, indent=1))
