#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-09 21:49 WIB (scheduled 21:49:38).
Lightweight 5-min companion. Legs: (1) Sourcify recently-verified feed
(limit 20) + shape-check new contracts; (2) Boltbook.fun EN+ZH front pages;
(3) on-chain verify of any new sale-shape; (4) read-only re-read of the
main snapshot priority items (baseline = 21:44 reread file); bridge leg
read-only. Read-only except own hot-leg state files. No chain-wide scan.
RPC: public BSC dataseed, fallback Ankr (project's documented free endpoint).
"""
import json, re, time, urllib.request, urllib.error, sys

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {
    "0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
    "0x8b47354e7b76b1970a0d06365c8244a810d37493",
}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]

T0 = time.time()
RUN = "free-mint-hot-leg 2026-11-09 22:04 WIB (scheduled 22:04:38 WIB)"
UA = {"User-Agent": "hot-leg/1.0"}

try:
    from Crypto.Hash import keccak as _k
    def sel(sig):
        h = _k.new(digest_bits=256); h.update(sig.encode())
        return "0x" + h.hexdigest()[:8]
except Exception:
    try:
        from eth_hash.auto import keccak as _ek
        def sel(sig):
            return "0x" + _ek(sig.encode()).hex()[:8]
    except Exception:
        sel = None

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def rpc_batch(calls, url):
    """calls: list of (to, data). Returns list of raw hex results or None."""
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)]).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.load(r)
    if isinstance(resp, list):
        out = []
        for item in resp:
            out.append(item.get("result") if isinstance(item, dict) else None)
        return out
    return None

RPCS = ["https://bsc-dataseed.bnbchain.org", "https://rpc.ankr.com/bsc"]

def rpc_calls(calls):
    last_err = None
    for url in RPCS:
        try:
            res = rpc_batch(calls, url)
            if res is not None:
                return res, url
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
    return None, last_err

def decode_int(r):
    if isinstance(r, str) and r.startswith("0x") and len(r) > 2:
        try:
            return int(r, 16)
        except Exception:
            return None
    return None

def find_abi(obj):
    """Recursively find a list that looks like an ABI."""
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
    """Returns shape dict. ABI via Sourcify v2 contract endpoint; fallback
    on-chain selector probing."""
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
    # on-chain probing (single batch) for registry bytes + key views
    probe = {}
    if sel is not None:
        calls = []
        labels = []
        calls.append((addr, "0x" + "00" * 0))  # placeholder replaced below
        calls = []
        # eth_getCode handled separately
        for fn in ["name()", "symbol()", "decimals()", "totalSupply()",
                   "freeClaimed()", "freeMinted()", "freeSharesRemaining()",
                   "freeLeft()", "freeAvailable()", "freeSharePoolExhausted()",
                   "freeSharesClaimed()", "FREE_SLOTS()", "FREE_SUPPLY()",
                   "FREE_CAP()", "FREE_AMOUNT()", "agentRegistry()", "registry()",
                   "mintOpen()", "totalMinted()", "mintFree()"]:
            calls.append((addr, sel(fn)))
            labels.append(fn)
        # quote(address,uint256) zero addr + 1
        data = sel("quote(address,uint256)") + "00" * 32 + "01".rjust(64, "0")
        calls.append((addr, data))
        labels.append("quote(address,uint256)")
        res, _ = rpc_calls(calls)
        if res:
            for lab, r in zip(labels, res):
                probe[lab] = decode_int(r) if (isinstance(r, str) and r and r != "0x") else (None if r in (None, "0x") else "empty")
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

# ---------- state ----------
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c"):
    for k in snap.get(sec, {}):
        snap_addrs.add(k.lower())
snap_pending = snap.get("pending_claims", {}) or {}

log = {"run": RUN}

# ---------- leg 1: Sourcify feed ----------
feed_addrs = []
feed_err = None
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    items = feed.get("results", feed) if isinstance(feed, dict) else feed
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
except Exception as e:
    feed_err = f"{type(e).__name__}: {e}"
log["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs, "error": feed_err}

new_feed = [a for a in feed_addrs
            if a.lower() not in seen_lower and a.lower() != REGISTRY.lower()
            and a.lower() not in EXCLUDED]
new_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = [shape_check(a) for a in new_feed]
for a in new_feed:
    seen[a] = "2026-11-09 22:04 WIB"
log["leg1"] = {"new": new_feed, "new_excluded_rediscovered": new_excluded,
               "shapes": shapes, "seen_total": len(seen)}

# ---------- leg 2: Boltbook EN + ZH ----------
def boltbook(url):
    try:
        raw = fetch(url, timeout=15)
        return raw, None
    except Exception as e:
        return b"", f"{type(e).__name__}: {e}"

en_raw, en_err = boltbook("https://boltbook.fun/")
zh_raw, zh_err = boltbook("https://boltbook.fun/?lang=zh")
en_txt = en_raw.decode("utf-8", "ignore")
zh_txt = zh_raw.decode("utf-8", "ignore")
en_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", en_txt)))
zh_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", zh_txt)))
all_bb = list(dict.fromkeys(en_addrs + zh_addrs))
kw_en = ["free share", "first share free", "1 free share", "free mint share"]
kw_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
kw_hits = {}
for k in kw_en:
    kw_hits[k] = en_txt.lower().count(k.lower()) + zh_txt.lower().count(k.lower())
for k in kw_zh:
    kw_hits[k] = en_txt.count(k) + zh_txt.count(k)
bb_new = [a for a in all_bb if a.lower() not in seen_lower]
bb_new_vs_snap = [a for a in bb_new if a.lower() not in snap_addrs]
bb_shapes = {}
for a in bb_new_vs_snap:
    bb_shapes[a] = shape_check(a)
for a in bb_new:
    seen[a] = "2026-11-09 22:04 WIB"
log["leg2_boltbook"] = {
    "en_bytes": len(en_raw), "en_err": en_err,
    "zh_bytes": len(zh_raw), "zh_err": zh_err,
    "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs),
    "unique_addrs": len(all_bb), "keyword_hits": kw_hits,
    "new_vs_seen": bb_new, "new_vs_snapshot": bb_new_vs_snap,
    "shape_check": bb_shapes, "seen_total": len(seen)}

# ---------- leg 3: verify any new sale-shape ----------
sale_shapes = [s for s in shapes if s["S1"] or s["S2"]]
sale_shapes += [dict(s, address=a) for a, s in bb_shapes.items() if s["S1"] or s["S2"]]
log["leg3_new_sale_shapes"] = sale_shapes
log["leg3_verify"] = "None - no new sale-shape contract this run" if not sale_shapes else "pending-manual"

# ---------- bridge leg (read-only) ----------
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_total = len(bcontracts)
b_disc = 0
b_in_snap = 0
b_not_snap = []
for addr, ent in bcontracts.items():
    if isinstance(ent, dict) and ent.get("same_owner_discarded"):
        b_disc += 1
    if addr.lower() in snap_addrs:
        b_in_snap += 1
    else:
        b_not_snap.append(addr)
log["bridge_leg"] = {"total": b_total, "same_owner_discarded": b_disc,
                     "in_snapshot_addr": b_in_snap,
                     "not_in_snapshot_addr": len(b_not_snap),
                     "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}

# ---------- leg 4: re-read baseline items ----------
NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive",
         "totalSkunksMinted", "freeSkunksClaimed", "freeSkunksRemaining",
         "freeRemaining", "mintCount", "MAX_MINTS", "opened", "openedAt", "saleActive",
         "soldShares", "publicMinted", "launchTime", "totalShares", "totalFreeShares",
         "mintingOpen", "TOTAL_SHARES", "MAX_FREE_SHARES", "SALE_START", "isSaleEnded",
         "remaining", "freeRemaining", "mintEnd", "mintStart", "SALE_END", "startTime",
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

prev_rr = json.load(open(BASE + "hot-leg-2026-11-09-2149-reread.json"))
prev_items = prev_rr.get("items", {})
prev_block = prev_rr.get("block")

# --- extra active snapshot items (added run 2204; prev values from snapshot lastRead ~22:07 WIB) ---
EXTRA = {
  "Agentic": {"address": "0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5", "freeMinted": 456, "FREE_SUPPLY": 1000, "totalMinted": 456, "balanceOf_user": 0, "hasFreeMinted_user": 0},
  "BAHUANG3": {"address": "0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591", "freeMinted": 2374, "FREE_CAP": 6000, "totalMinted": 2374, "freeAllowance_user": 2},
  "ShadowSquad": {"address": "0x0bc496BC51D14ae6C4A7003B05061323d4De9206", "freeClaimed": 412, "FREE_SUPPLY": 819, "mintOpen": 1, "balanceOf_user": 0},
  "Lenx Agent Pass": {"address": "0x6E252E3a3584BD6a64C103e4eDFa761f6335980F", "freeClaimed": 128, "freeMinted": 799, "FREE_CAP": 1000, "freeRemaining": 208, "freeClaimed_user": 0, "balanceOf_user": 0},
  "PIXEL MONSTERS": {"address": "0x3f508d8826517123Fdd39c776e55F85Fa188E5fD", "freeMinted": 61, "FREE_CAP": 2000, "freeLeft": 1939, "mintOpen": 1, "freeClaimed_user": 0, "balanceOf_user": 0},
  "Agentite": {"address": "0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2", "freeMinted": 47, "FREE_SUPPLY": 1000, "totalMinted": 47, "publicMinted": 0, "balanceOf_user": 0},
  "Golden Agents": {"address": "0x4233C62919CC03168a361C547117c1553C375bfC", "totalSupply": 653, "publicMinted": 117, "balanceOf_user": 0},
  "Meow Cards": {"address": "0xb8164afefc53910D7A74cEcE15A60a9e0C86089e", "totalSupply": 28, "totalMinted": 28, "balanceOf_user": 0},
  "Reel": {"address": "0xB31947A80AC2e72390B84e3d503d9148f4A9d1ca", "totalSupply": 151, "totalMinted": 151, "mintOpen": 1, "balanceOf_user": 0},
  "BHTB": {"address": "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", "freeUsed": 96, "FREE_QUOTA": 555, "freeClaimed_user": 0, "maxShares_user": 10, "remainingShares_user": 10},
  "AgentGrid": {"address": "0x651302C0043040D48EaAF85605E12F0549aD6D89", "freeUsed": 19, "FREE_SHARES": 500, "balanceOf_user": 0},
  "YAMA": {"address": "0x86d779fc4d83044cceccb53639f9a98e367d6e46", "freeMinted": 413, "freeRemaining": 99572, "mintingOpen": 1, "balanceOf_user": 0},
  "FMA": {"address": "0xA45CA208d015C81Bf2f5e606437e4f9d1D8C2FE8", "mintCount": 505, "MAX_MINTS": 10000, "totalSupply": 505000000000000000000000, "hasMinted_user": 0, "balanceOf_user": 0},
  "NIBULL": {"address": "0x29666Bc0004824dc2B282c82aAC206b8b1711839", "opened": 0, "soldShares": 1018, "FREE_SHARES": 500, "TOTAL_SHARES": 10000, "isSaleEnded": 0, "balanceOf_user": 0},
  "0x260bf39a-sale": {"address": "0x260bf39a6f3aB5E459856297178CC0DF6003374a", "launched": 0, "launchTime": 0, "freeClaimed": 500, "FREE_SLOTS": 500, "balanceOf_user": 0},
  "0x4Bc1A172-sale": {"address": "0x4Bc1A1723a5D8A893695f78c8b2cD39028478d43", "saleActive": 0, "opened": 0, "freeMinted": 0, "MAX_FREE_SHARES": 100, "SALE_START": 1794286800},
  "0x5f76cAb7": {"address": "0x5f76cAb7B054e088563D5098E17bD0dc430e61aE", "totalSupply": 271800000000000000000000000, "freeUsed_user": 0, "balanceOf_user": 0},
}
for _ek_name, _ev in EXTRA.items():
    if _ek_name not in prev_items:
        prev_items[_ek_name] = _ev
log["leg4_extra_items"] = sorted(EXTRA.keys())

jobs = []  # (name, field, address, data)
for name, entry in prev_items.items():
    for field in entry:
        if field == "address":
            continue
        d = calldata(field)
        if d:
            jobs.append((name, field, entry["address"], d))
calls = [(to, data) for (_, _, to, data) in jobs]
res, rpc_used = rpc_calls(calls)
items_now = {}
if res is not None:
    for (name, field, addr, _), r in zip(jobs, res):
        items_now.setdefault(name, {"address": addr})
        items_now[name][field] = decode_int(r)
    # current block
    blk = None
    try:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}).encode()
        req = urllib.request.Request(rpc_used if isinstance(rpc_used, str) else RPCS[0],
                                     data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as rr2:
            blk = int(json.load(rr2).get("result", "0x0"), 16)
    except Exception:
        blk = None
else:
    blk = None
    items_now = {name: dict(entry) for name, entry in prev_items.items()}

changes = []
for name, entry in items_now.items():
    old = prev_items.get(name, {})
    for field, val in entry.items():
        if field == "address":
            continue
        if old.get(field) != val:
            changes.append({"item": name, "field": field, "old": old.get(field), "new": val})
log["leg4"] = {"block": blk, "prev_block": prev_block, "rpc": rpc_used,
               "items_n": len(items_now), "changes": changes,
               "mode": "single-batch eth_call (read-only)"}
log["leg4_items"] = items_now

# promo / sellout / slot-loss flags (checked against snapshot metadata)
promo_flags = []
snap_contracts = snap.get("contracts", {}) or {}
snap_trackc = snap.get("track_c", {}) or {}
for name, entry in items_now.items():
    meta = snap_contracts.get(name) or snap_trackc.get(name) or {}
    # find free claimed + cap from re-read fields
    free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
    cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
          entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = entry.get("freeClaimed_user") in (0, False, None) or entry.get("balanceOf_user") == 0
        sold_out = free >= cap
        if sold_out:
            promo_flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4),
                                "free": free, "cap": cap})
        elif pct >= 0.25 and user_open and name not in ("Agentic", "BAHUANG3", "ShadowSquad", "Lenx Agent Pass", "YAMA"):
            promo_flags.append({"item": name, "flag": "promo-candidate-check",
                                "pct": round(pct, 4), "free": free, "cap": cap,
                                "meta_keys": list(meta.keys())[:12] if isinstance(meta, dict) else type(meta).__name__})
log["leg4_promo_flags"] = promo_flags
log["pending_claims"] = "snapshot pending_claims empty at run start - nothing to re-read" \
    if not snap_pending else f"{len(snap_pending)} pending claims - NOT re-read this run (bulk leg skipped)"
log["duration_s"] = round(time.time() - T0, 1)

# ---------- write outputs ----------
with open(BASE + "hot-leg-run-2026-11-09-2204.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-2026-11-09-2204-reread.json", "w") as f:
    json.dump({"block": blk, "items": items_now, "duration_sec": log["duration_s"]},
              f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps({k: log[k] for k in ("leg1", "leg2_boltbook", "leg3_new_sale_shapes",
                                      "bridge_leg", "leg4", "leg4_promo_flags",
                                      "pending_claims", "duration_s")}, indent=2, ensure_ascii=False))
