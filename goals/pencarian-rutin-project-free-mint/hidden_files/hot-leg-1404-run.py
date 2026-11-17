#!/usr/bin/env python3
"""Hot-leg run 2026-11-16 14:04 WIB. Read-only legs 1/2/4 + bridge + PEPE.
Leg1 Sourcify feed, Leg2 Boltbook EN+ZH, Leg4 reread of the 22-item active
set vs 1359 baseline, chunked eth_call batches of 8 to bsc-dataseed.
Writes only hot-leg-run-2026-11-16-1404.json + hot-leg-seen.json additions.
No preview/mint/claim, no snapshot rewrite."""
import json, re, subprocess, time, urllib.request
from datetime import datetime, timezone

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
WIB = timezone.utc  # times recorded as WIB strings manually
now_wib = datetime.now(timezone.utc).astimezone(
    __import__("zoneinfo").ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")

def curl(url, timeout=25):
    p = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-w", "\n%{http_code}",
                        url], capture_output=True, text=True)
    lines = p.stdout.rsplit("\n", 1)
    body = lines[0] if len(lines) > 1 else p.stdout
    code = lines[1] if len(lines) > 1 else ""
    return body, code

def keccak_sel(sig):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-16 14:04 WIB", "started_wib": now_wib}

# ---------- Leg 1: Sourcify feed ----------
feed_body, feed_code = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
feed_addrs, top_verified = [], None
try:
    fd = json.loads(feed_body)
    items = fd.get("results", fd if isinstance(fd, list) else [])
    for it in items:
        a = it.get("address")
        if a: feed_addrs.append(a)
        if top_verified is None: top_verified = it.get("verifiedAt")
except Exception as e:
    out["sourcify_feed_error"] = str(e)[:200]
new_feed = [a for a in feed_addrs if a.lower() not in seen_lc and a.lower() not in EXCLUDED]
out["sourcify_feed"] = {"total": len(feed_addrs), "new": len(new_feed),
    "new_contracts": new_feed, "top": feed_addrs[0] if feed_addrs else None,
    "top_verifiedAt": top_verified, "http_code": feed_code, "all": feed_addrs}

# ---------- Leg 2: Boltbook EN + ZH ----------
EN_KW = ["free share", "first share free", "1 free share", "free mint share"]
ZH_KW = ["免费份额", "首个免费", "免费铸造", "免费mint"]
def boltbook(url):
    body, code = curl(url)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))
    low = body.lower()
    return {"bytes": len(body), "http_code": code,
            "full_address_contracts": len(addrs), "addresses": addrs,
            "new": 0, "new_contracts": [],
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(body.count(k) for k in ZH_KW)}
bb_en = boltbook("https://boltbook.fun/")
bb_zh = boltbook("https://boltbook.fun/?lang=zh")
bb_new = []
for a in bb_en["addresses"] + bb_zh["addresses"]:
    if a.lower() not in seen_lc and a.lower() not in EXCLUDED and a not in bb_new:
        bb_new.append(a)
bb_en["new"] = len([a for a in bb_en["addresses"] if a.lower() not in seen_lc])
bb_en["new_contracts"] = [a for a in bb_en["addresses"] if a.lower() not in seen_lc]
bb_zh["new"] = len([a for a in bb_zh["addresses"] if a.lower() not in seen_lc])
bb_zh["new_contracts"] = [a for a in bb_zh["addresses"] if a.lower() not in seen_lc]
out["boltbook_en"] = bb_en
out["boltbook_zh"] = bb_zh

# ---------- Shape check for any new contracts ----------
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeSupply"}
def shape_check(addr):
    """Returns dict with S1/S2 booleans; fetches Sourcify ABI + code."""
    abi_body, _ = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 20)
    fns, has_mint, has_quote, free_hits, agent_ref, is_token = [], False, False, [], False, False
    try:
        d = json.loads(abi_body)
        abi = d.get("abi", [])
        for f in abi:
            if f.get("type") != "function": continue
            nm = f.get("name", "")
            fns.append(nm)
            ins = f.get("inputs", [])
            if nm.lower().startswith("mint"): has_mint = True
            if nm in ("quote", "cost", "costOf", "priceFor", "getPrice"): has_quote = True
            if nm in FREE_VIEWS: free_hits.append(nm)
            if "agent" in nm.lower() or "registry" in nm.lower(): agent_ref = True
            if nm == "mintFree" and len(ins) == 0: has_mint = True
        names = set(fns)
        is_token = {"name", "symbol", "decimals", "totalSupply"} <= names
    except Exception:
        return {"address": addr, "abi_error": True, "S1": False, "S2": False, "fns": fns}
    # registry bytes in code
    code_body, _ = curl(EP, 20)  # placeholder no-op
    p = subprocess.run(["curl", "-s", "--max-time", "20", "-X", "POST", EP,
                        "-H", "Content-Type: application/json",
                        "--data", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                              "params": [addr, "latest"]})],
                       capture_output=True, text=True)
    try:
        code = json.loads(p.stdout).get("result", "")
        if REGISTRY[2:].lower() in code.lower(): agent_ref = True
    except Exception:
        pass
    s1 = has_mint and has_quote and bool(free_hits) and agent_ref
    s2 = is_token and ("mintFree" in fns) and bool(free_hits) and \
        bool({"FREE_SLOTS", "FREE_SUPPLY"} & set(fns)) and agent_ref
    return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_hits, "agent": agent_ref, "token": is_token, "n_fns": len(fns)}

shape_targets = list(dict.fromkeys(new_feed + bb_new))
shape_results = [shape_check(a) for a in shape_targets]
out["shape_check_targets"] = shape_targets
out["shape_check"] = shape_results
out["shape_hits"] = [r for r in shape_results if r.get("S1") or r.get("S2")]

# record newly seen (feed + boltbook) in hot-leg-seen.json
ts = datetime.now(timezone.utc).astimezone(
    __import__("zoneinfo").ZoneInfo("Asia/Jakarta")).isoformat()
for a in shape_targets:
    if a.lower() not in seen_lc:
        r = next((x for x in shape_results if x["address"] == a), {})
        seen[a] = {"first_seen_wib": ts,
                   "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')} token={r.get('token')}",
                   "source": "hot-leg-1404 sourcify/boltbook",
                   "status": "sale-shape" if (r.get("S1") or r.get("S2")) else "checked-not-sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))

# ---------- Leg 4: reread 22-item active set vs 1359 baseline ----------
prev = json.load(open(BASE + "hot-leg-run-2026-11-16-1359.json"))
base = prev["leg4_reread"]["reads"]
NOARG = {"totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY", "FREE_SHARES",
         "freeRemaining", "MAX_SUPPLY", "mintOpen", "launched", "failed",
         "isRefundPhase", "totalShares", "standardRemaining",
         "legendaryRemaining", "soldShares", "opened", "totalFreeShares"}
ADDRARG = {"balanceOf", "mintedBy", "freeUsed", "freeClaimed", "tokenClaimed",
           "hasMinted"}
def calldata(field):
    if field == "address": return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ("cost", "quote", "freeFor"):
            return keccak_sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG:
            return keccak_sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return keccak_sel(f"{field}()")
    if field == "costOf_1": return keccak_sel("costOf(uint256)") + enc_uint(1)
    return None

jobs = []
for name, entry in base.items():
    for field in entry.get("views", {}):
        data = calldata(field)
        if data: jobs.append((name, field, entry["address"], data))

def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": (p.stdout + p.stderr)[:200]}

p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                   capture_output=True, text=True)
try: block = int(json.loads(p.stdout)["result"], 16)
except Exception: block = None

results, chunk_errors = {}, []
for i in range(0, len(jobs), 8):
    chunk = jobs[i:i + 8]
    resp = run_batch([(to, data) for (_, _, to, data) in chunk])
    if isinstance(resp, dict) and "_curl_error" in resp:
        for (name, field, to, data) in chunk:
            results[(name, field)] = None
        chunk_errors.append(i)
        continue
    if isinstance(resp, dict): resp = [resp]
    for j, item in enumerate(resp):
        name, field, to, data = chunk[j]
        if isinstance(item, dict) and "result" in item and isinstance(item["result"], str):
            try: results[(name, field)] = int(item["result"], 16)
            except Exception: results[(name, field)] = None
        else:
            results[(name, field)] = None

reads, diffs = {}, []
for name, entry in base.items():
    row = {"address": entry["address"], "views": {}}
    for field, old in entry.get("views", {}).items():
        v = results.get((name, field))
        row["views"][field] = v if v is not None else old
        if v is not None and v != old:
            diffs.append({"item": name, "field": field, "old": old, "new": v})
    reads[name] = row
out["leg4_reread"] = {"reads": reads, "endpoint": EP, "n_calls": len(jobs),
                      "chunk_size": 8, "chunk_errors": chunk_errors,
                      "note": "chunked batches of 8 (0714 lesson: 56-call single batch silently all-null)",
                      "block": block, "diffs_vs_1359": diffs}

# ---------- PEPE reread (track_c, minted-by-user) ----------
pepe_addr = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
pepe_calls = [("freeMinted", keccak_sel("freeMinted()")),
              ("soldShares", keccak_sel("soldShares()")),
              ("FREE_SHARES", keccak_sel("FREE_SHARES()")),
              ("opened", keccak_sel("opened()")),
              ("costOf_1", keccak_sel("costOf(uint256)") + enc_uint(1)),
              ("hasMinted_user", keccak_sel("hasMinted(address)") + enc_addr(USER))]
presp = run_batch([(pepe_addr, d) for (_, d) in pepe_calls])
pepe = {}
if isinstance(presp, list):
    for (fn, _), item in zip(pepe_calls, presp):
        if isinstance(item, dict) and "result" in item and isinstance(item["result"], str):
            try: pepe[fn] = int(item["result"], 16)
            except Exception: pepe[fn] = None
        else: pepe[fn] = None
out["pepe_reread"] = pepe

# ---------- Bridge (read-only) ----------
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c", "pending_claims"):
        for e in (snap.get(sec) or {}).values():
            if isinstance(e, dict) and e.get("address"): snap_addrs.add(e["address"].lower())
            if isinstance(e, dict) and e.get("token"): snap_addrs.add(e["token"].lower())
    baddrs = []
    if isinstance(bridge, dict):
        bl = bridge.get("contracts") or bridge.get("items") or []
        for e in bl:
            a = e.get("address") if isinstance(e, dict) else e
            if a: baddrs.append((a, bool(isinstance(e, dict) and e.get("same_owner_discarded"))))
    elif isinstance(bridge, list):
        for e in bridge:
            a = e.get("address") if isinstance(e, dict) else e
            if a: baddrs.append((a, bool(isinstance(e, dict) and e.get("same_owner_discarded"))))
    not_in = [a for a, _ in baddrs if a.lower() not in snap_addrs]
    sod = sum(1 for _, s in baddrs if s)
    out["bridge_scan"] = {"total": len(baddrs), "not_in_snapshot": len(not_in),
                          "not_in_snapshot_list": not_in, "same_owner_discarded": sod}
except Exception as e:
    out["bridge_scan"] = {"error": str(e)[:200]}

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE + "hot-leg-run-2026-11-16-1404.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("leg4_reread",)}, indent=1)[:4000])
print("LEG4_DIFFS:", json.dumps(diffs))
print("LEG4_BLOCK:", block, "elapsed:", out["elapsed_s"])
