#!/usr/bin/env python3
"""hot-leg 2026-11-09 21:49 WIB fix-up: (a) Boltbook leg from curl-fetched
pages (/tmp/bb-en.html, /tmp/bb-zh.html) + shape-check of the 2 new
addresses; (b) leg-4 re-read with chunked RPC batches (20 calls each);
(c) corrected bridge computation (snapshot addresses extracted from
contracts[].address + track_c[].sale/token). Updates the 21:49 run log,
reread file and hot-leg-seen.json. Read-only on-chain."""
import json, re, time, urllib.request, urllib.error

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]
T0 = time.time()
UA = {"User-Agent": "hot-leg/1.0"}

try:
    from Crypto.Hash import keccak as _k
    def sel(sig):
        h = _k.new(digest_bits=256); h.update(sig.encode())
        return "0x" + h.hexdigest()[:8]
except Exception:
    sel = None

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

RPCS = ["https://bsc-dataseed.bnbchain.org", "https://rpc.ankr.com/bsc"]

def rpc_batch(calls, url):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)]).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.load(r)
    if isinstance(resp, list):
        return [it.get("result") if isinstance(it, dict) else None for it in resp]
    return None

def rpc_calls_chunked(calls, chunk=20):
    out = []
    used = None
    for i in range(0, len(calls), chunk):
        part = calls[i:i + chunk]
        got = None
        for url in RPCS:
            try:
                got = rpc_batch(part, url)
                used = url
                break
            except Exception:
                continue
        if got is None:
            out.extend([None] * len(part))
        else:
            out.extend(got)
    return out, used

def decode_int(r):
    if isinstance(r, str) and r.startswith("0x") and len(r) > 2:
        try:
            return int(r, 16)
        except Exception:
            return None
    return None

def find_abi(obj):
    if isinstance(obj, list) and obj and all(
            isinstance(x, dict) and x.get("type") in ("function", "event", "constructor", "error")
            for x in obj if isinstance(x, dict)):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            a = find_abi(v)
            if a is not None:
                return a
    if isinstance(obj, list):
        for v in obj:
            a = find_abi(v)
            if a is not None:
                return a
    return None

def shape_check(addr):
    abi = None
    abi_err = None
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}", timeout=15)
        abi = find_abi(json.loads(raw))
        if abi is None:
            abi_err = "v2-no-abi"
    except Exception as e:
        abi_err = f"{type(e).__name__}: {e}"
    names = set()
    if abi:
        for fn in abi:
            if isinstance(fn, dict) and fn.get("type") == "function":
                names.add(fn.get("name", ""))
    probe = {}
    if sel is not None:
        calls, labels = [], []
        for fn in ["name()", "symbol()", "decimals()", "totalSupply()",
                   "freeClaimed()", "freeMinted()", "freeSharesRemaining()",
                   "freeLeft()", "freeAvailable()", "freeSharePoolExhausted()",
                   "freeSharesClaimed()", "FREE_SLOTS()", "FREE_SUPPLY()",
                   "FREE_CAP()", "FREE_AMOUNT()", "agentRegistry()", "registry()",
                   "mintOpen()", "totalMinted()", "mintFree()"]:
            calls.append((addr, sel(fn)))
            labels.append(fn)
        calls.append((addr, sel("quote(address,uint256)") + "00" * 32 + "01".rjust(64, "0")))
        labels.append("quote(address,uint256)")
        res, _ = rpc_calls_chunked(calls, chunk=10)
        for lab, r in zip(labels, res):
            probe[lab] = decode_int(r) if (isinstance(r, str) and r and r != "0x") else None
    code_has_registry = None
    try:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}).encode()
        req = urllib.request.Request(RPCS[0], data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            code = json.load(r).get("result", "")
        code_has_registry = REGISTRY[2:].lower() in (code or "").lower()
    except Exception as e:
        code_has_registry = f"err:{type(e).__name__}"
    has_mint = bool(names & set(MINT_FNS)) or probe.get("mintFree()") is not None
    has_quote = bool(names & set(QUOTE_FNS)) or probe.get("quote(address,uint256)") is not None
    free_found = [f for f in FREE_VIEWS if f in names or probe.get(f + "()") is not None]
    has_agent = bool(names & set(AGENT_MARKERS)) or code_has_registry is True \
        or probe.get("agentRegistry()") is not None or probe.get("registry()") is not None
    is_token = bool(names & set(TOKEN_FNS)) or all(
        probe.get(f + "()") is not None for f in ["name()", "symbol()", "decimals()", "totalSupply()"])
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and (("mintFree" in names) or probe.get("mintFree()") is not None) \
        and (("freeClaimed" in names or "freeMinted" in names) or free_found) \
        and (any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) or
             probe.get("FREE_SLOTS()") is not None or probe.get("FREE_SUPPLY()") is not None) \
        and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2),
            "mint": bool(has_mint), "quote": bool(has_quote),
            "free": free_found, "agent": bool(has_agent),
            "token": bool(is_token), "abi_err": abi_err,
            "code_registry": code_has_registry}

# ---------- (a) Boltbook from curl-fetched pages ----------
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("sale", "token"):
            if v.get(k):
                snap_addrs.add(v[k].lower())

en = open("/tmp/bb-en.html", encoding="utf-8", errors="ignore").read()
zh = open("/tmp/bb-zh.html", encoding="utf-8", errors="ignore").read()
en_a = list(dict.fromkeys(a.lower() for a in re.findall(r"0x[a-fA-F0-9]{40}", en)))
zh_a = list(dict.fromkeys(a.lower() for a in re.findall(r"0x[a-fA-F0-9]{40}", zh)))
allb = list(dict.fromkeys(en_a + zh_a))
kw_hits = {}
for k in ["free share", "first share free", "1 free share", "free mint share"]:
    kw_hits[k] = en.lower().count(k) + zh.lower().count(k)
for k in ["免费份额", "首个免费", "免费铸造", "免费mint"]:
    kw_hits[k] = en.count(k) + zh.count(k)
# context of keyword hits: which address sits near each hit
kw_context = []
for src_name, src in (("en", en), ("zh", zh)):
    low = src.lower()
    for m in re.finditer(r"free share|1 free share", low):
        ctx = src[max(0, m.start() - 400):m.end() + 400]
        addrs = re.findall(r"0x[a-fA-F0-9]{40}", ctx)
        kw_context.append({"page": src_name, "at": m.start(),
                           "addrs_nearby": list(dict.fromkeys(addrs))})
bb_new = [a for a in allb if a.lower() not in seen_lower]
bb_new_vs_snap = [a for a in bb_new if a.lower() not in snap_addrs]
bb_shapes = {a: shape_check(a) for a in bb_new_vs_snap}
for a in bb_new:
    seen[a] = "2026-11-09 21:49 WIB"
leg2 = {"en_bytes": len(en), "en_err": None, "en_via": "curl -L retry (urllib RemoteDisconnected)",
        "zh_bytes": len(zh), "zh_err": None, "zh_via": "curl retry (urllib IncompleteRead)",
        "en_addrs": len(en_a), "zh_addrs": len(zh_a),
        "unique_addrs": len(allb), "keyword_hits": kw_hits,
        "keyword_context": kw_context,
        "new_vs_seen": bb_new, "new_vs_snapshot": bb_new_vs_snap,
        "shape_check": bb_shapes, "seen_total": len(seen)}

# ---------- (b) leg-4 re-read, chunked ----------
NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive",
         "totalSkunksMinted", "freeSkunksClaimed", "freeSkunksRemaining",
         "freeWindowOpen", "agentFreeUsed", "AGENT_FREE_CAP", "paidMinted"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed",
           "freeCount", "freeMinted", "mintedCount", "freeAvailable",
           "hasMinted", "quotaOf", "freeTakenBy", "priceFor", "freeClaimedBy",
           "freeUsedByWallet"]
ADDRUINT = ["quote", "freeFor"]

def calldata(field):
    if field in ("address", "_batch_fail"):
        return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT and sel:
            return sel(f"{fn}(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x")
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG and sel:
            return sel(f"{fn}(address)") + USER[2:].lower().rjust(64, "0")
        return None
    if field in NOARG and sel:
        return sel(f"{field}()")
    return None

prev_rr = json.load(open(BASE + "hot-leg-2026-11-09-2144-reread.json"))
prev_items = prev_rr.get("items", {})
jobs = []
for name, entry in prev_items.items():
    for field in entry:
        if field == "address":
            continue
        d = calldata(field)
        if d:
            jobs.append((name, field, entry["address"], d))
res, rpc_used = rpc_calls_chunked([(to, data) for (_, _, to, data) in jobs], chunk=20)
items_now = {}
if res is not None and len(res) == len(jobs):
    for (name, field, addr, _), r in zip(jobs, res):
        items_now.setdefault(name, {"address": addr})
        items_now[name][field] = decode_int(r)
    blk = None
    try:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}).encode()
        req = urllib.request.Request(rpc_used, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as rr2:
            blk = int(json.load(rr2).get("result", "0x0"), 16)
    except Exception:
        blk = None
else:
    blk = None
    items_now = {name: dict(entry) for name, entry in prev_items.items()}
    rpc_used = f"FAILED len(res)={len(res) if res else res} vs jobs={len(jobs)}"
changes = []
for name, entry in items_now.items():
    old = prev_items.get(name, {})
    for field, val in entry.items():
        if field == "address":
            continue
        if old.get(field) != val:
            changes.append({"item": name, "field": field, "old": old.get(field), "new": val})
leg4 = {"block": blk, "prev_block": prev_rr.get("block"), "rpc": rpc_used,
        "items_n": len(items_now), "calls": len(jobs), "changes": changes,
        "mode": "chunked eth_call batches of 20 (read-only)"}

# promo / sellout flags
promo_flags = []
snap_contracts = snap.get("contracts", {}) or {}
snap_trackc = snap.get("track_c", {}) or {}
for name, entry in items_now.items():
    free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
    cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
          entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = entry.get("freeClaimed_user") in (0, False, None)
        if free >= cap:
            promo_flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4),
                                "free": free, "cap": cap})
        elif pct >= 0.25 and user_open:
            meta = snap_contracts.get(name) or snap_trackc.get(name) or {}
            promo_flags.append({"item": name, "flag": "promo-candidate-check",
                                "pct": round(pct, 4), "free": free, "cap": cap,
                                "meta_keys": list(meta.keys())[:14] if isinstance(meta, dict) else "?"})

# ---------- (c) corrected bridge ----------
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_disc = sum(1 for e in bcontracts.values()
             if isinstance(e, dict) and e.get("same_owner_discarded"))
b_in = sum(1 for a in bcontracts if a.lower() in snap_addrs)
b_not = [a for a in bcontracts if a.lower() not in snap_addrs]
bridge_leg = {"total": len(bcontracts), "same_owner_discarded": b_disc,
              "in_snapshot_addr": b_in, "not_in_snapshot_addr": len(b_not),
              "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}

# ---------- update run log / reread / seen ----------
log = json.load(open(BASE + "hot-leg-run-2026-11-09-2149.json"))
log["leg2_boltbook"] = leg2
log["leg4"] = leg4
log["leg4_items"] = items_now
log["leg4_promo_flags"] = promo_flags
log["bridge_leg"] = bridge_leg
log["leg3_new_sale_shapes"] = [s for s in log.get("leg1", {}).get("shapes", [])
                                if s["S1"] or s["S2"]] + \
                               [dict(s, address=a) for a, s in bb_shapes.items()
                                if s["S1"] or s["S2"]]
log["leg3_verify"] = "None - no new sale-shape contract this run" \
    if not log["leg3_new_sale_shapes"] else "pending-manual"
log["duration_s"] = round(time.time() - T0 + 33.9, 1)
with open(BASE + "hot-leg-run-2026-11-09-2149.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-2026-11-09-2149-reread.json", "w") as f:
    json.dump({"block": blk, "items": items_now, "duration_sec": log["duration_s"]},
              f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps({"leg2": leg2, "leg4": leg4, "promo_flags": promo_flags,
                  "bridge": bridge_leg, "leg3_sale": log["leg3_new_sale_shapes"],
                  "duration_s": log["duration_s"]}, indent=2, ensure_ascii=False))
