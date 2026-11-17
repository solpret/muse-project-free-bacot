#!/usr/bin/env python3
"""Hot-leg run 2026-11-11 00:04 WIB — fresh implementation from task body.
Leg 1 Sourcify feed + shape-check, Leg 2 Boltbook EN+ZH, Leg 4 priority
re-read vs 00:01 baseline, bridge read-only, NIGHTFORGE/EMBERANVIL site
re-check. Read-only except hot-leg-seen.json + own run outputs.
"""
import json, subprocess, time, re, datetime
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-11-0004"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493",
            "0x60b9262456de011f7d15a54cdd8c48baa8b022f"}
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")

def curl(url, max_time=20, post=None):
    cmd = ["curl", "-s", "--max-time", str(max_time), url]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data", post]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=max_time + 5)
        return p.stdout
    except Exception as e:
        return ""

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return hex(n)[2:].rjust(64, "0")

def words(h):
    if not isinstance(h, str) or not h.startswith("0x"): return None
    s = h[2:]
    if not s or len(s) % 64: return None
    try: return [int(s[i:i+64], 16) for i in range(0, len(s), 64)]
    except Exception: return None

def batch_call(rpc, calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    out = curl(rpc, 25, post=payload)
    try:
        r = json.loads(out)
        return r if isinstance(r, list) else {"_err": str(r)[:150]}
    except Exception:
        return {"_err": (out)[:150]}

def call_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_uint(a)
    return d

def read_item(addr, views):
    """views: list of (key, sig, args). Returns (dict, rpc or None, err)."""
    calls = [(addr, call_data(sig, args)) for _, sig, args in views]
    for rpc in RPCS:
        r = batch_call(rpc, calls)
        if isinstance(r, list) and len(r) == len(calls):
            out = {}; ok = 0
            for (key, _, _), resp in zip(views, r):
                val = resp.get("result") if isinstance(resp, dict) else None
                w = words(val) if val else None
                if w is not None:
                    out[key] = w if len(w) > 1 else w[0]; ok += 1
                else:
                    out[key] = None
            if ok: return out, rpc, None
    return {k: None for k, _, _ in views}, None, "batch-fail-all-rpcs"

# ---------- state ----------
seen = json.load(open(BASE + "hot-leg-seen.json"))
try:
    base_reread = json.load(open(BASE + "run-2026-11-11-0001-reread.json"))["reread"]
except Exception:
    base_reread = {}

out = {"tag": TAG, "run_wib": NOW, "legs": {}}

# ---------- Leg 1: Sourcify feed ----------
feed_raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25)
feed_addrs = []
try:
    fj = json.loads(feed_raw)
    items = fj.get("results", fj if isinstance(fj, list) else [])
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a: feed_addrs.append(a)
except Exception as e:
    out["legs"]["feed_error"] = str(e)[:200] + " raw=" + feed_raw[:200]
new_feed = [a for a in feed_addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
out["legs"]["feed"] = {"count": len(feed_addrs), "addrs": feed_addrs, "new": new_feed}

FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"}
def shape_check(addr):
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 25)
    try:
        abi = json.loads(raw).get("abi", [])
    except Exception:
        return {"verified": False, "err": raw[:120]}
    fns = [e.get("name", "") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    names = set(fns)
    mint = [f for f in fns if re.search(r"mint|claim", f, re.I)]
    quote = [f for f in fns if re.search(r"quote|cost", f, re.I)]
    free = [f for f in fns if f in FREE_VIEWS]
    agent = [f for f in fns if re.search(r"agent|registry", f, re.I)]
    token = [f for f in ("name", "symbol", "decimals", "totalSupply") if f in names]
    s1 = bool(mint and quote and free and agent)
    s2 = bool(len(token) == 4 and "mintFree" in names and
              ({"freeClaimed", "freeMinted"} & names) and
              ({"FREE_SLOTS", "FREE_SUPPLY"} & names) and agent)
    return {"verified": True, "S1": s1, "S2": s2, "mint": mint, "quote": quote,
            "free": free, "agent": agent, "token": token, "fns": len(fns)}

shapes = {}
for a in new_feed:
    shapes[a] = shape_check(a)
out["legs"]["shape"] = shapes

# ---------- Leg 2: Boltbook ----------
bb = {}
for label, url in [("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")]:
    raw = curl(url, 25)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", raw)))
    bb[label] = {"bytes": len(raw), "addrs": addrs}
    for a in addrs:
        if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED and a not in shapes:
            shapes[a] = shape_check(a)
            bb[label].setdefault("shape_checked", []).append(a)
out["legs"]["boltbook"] = bb
out["legs"]["shape"] = shapes

# ---------- Leg 4: priority re-read ----------
U = USER
V = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("status", "status()", []), ("agentFreeUsed", "agentFreeUsed()", []),
    ("freeLeft", "freeLeft()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", [U])]),
 "EMBERANVIL": ("0x7673c596a6702d32f844266dc2ca7b1fd6d7df21", [
    ("status", "status()", []), ("agentFreeUsed", "agentFreeUsed()", []),
    ("freeLeft", "freeLeft()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", [U])]),
 "SOLDERCATS": ("0x3D972EBbF7488f21b95250B867e2406c723C9DDC", [
    ("totalSupply", "totalSupply()", []), ("agentFreeUsed", "agentFreeUsed()", []),
    ("mintOpen", "mintOpen()", []), ("mintStart", "mintStart()", []),
    ("balanceOf_user", "balanceOf(address)", [U]),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)", [U])]),
 "ORBITJANITOR": ("0x8d5a0555446d37afaba75e36da318646a4b32420", [
    ("totalSupply", "totalSupply()", []), ("agentFreeUsed", "agentFreeUsed()", []),
    ("mintOpen", "mintOpen()", []), ("mintStart", "mintStart()", []),
    ("balanceOf_user", "balanceOf(address)", [U]),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)", [U])]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("balanceOf_user", "balanceOf(address)", [U]),
    ("freeClaimed_user", "freeClaimed(address)", [U])]),
 "RigForge": ("0xa1Cc0D7C0534F824F2cf6eEb865A8fEde96c8f7d", [
    ("FREE_SHARES", "FREE_SHARES()", []), ("openedAt", "openedAt()", []),
    ("SALE_START", "SALE_START()", []),
    ("canClaimFree_user", "canClaimFree(address)", [U])]),
 "SynthMinds": ("0x36E655717BA3fB01268b6069a88Cc5D4a982EA15", [
    ("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", [U])]),
 "Cryptlichor": ("0xb792Bf600DF37EB7638fb16434E813FC0c90C3C8", [
    ("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", [U])]),
 "Gachagent": ("0xE23d1DC8F47f6a56F436d73c52862f40F26e9D39", [
    ("freeMinted", "freeMinted()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("totalSupply", "totalSupply()", []), ("balanceOf_user", "balanceOf(address)", [U])]),
 "AuraAgents": ("0xacc6e2F1aaE42B2E5FF2758Ff078E4B1bfAc7DB1", [
    ("totalSupply", "totalSupply()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("balanceOf_user", "balanceOf(address)", [U])]),
 "AgentBone": ("0xF3072D6E047c99be2b071a07AAC600F5c8b63080", [
    ("totalSupply", "totalSupply()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("balanceOf_user", "balanceOf(address)", [U])]),
 "Unbroken": ("0x4443EA727b0761De5ff91Ac5E9F5F65C5E3C8b8c", [
    ("totalSupply", "totalSupply()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", [U])]),
 "Shroomlets": ("0xD0624b7cED1B822BCa6359302c375D8EF700a7fe", [
    ("totalSupply", "totalSupply()", []), ("balanceOf_user", "balanceOf(address)", [U]),
    ("freeClaimed_user", "freeClaimed(address)", [U])]),
 "BHTB": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("FREE_SLOTS", "FREE_SLOTS()", []), ("balanceOf_user", "balanceOf(address)", [U]),
    ("freeClaimed_user", "freeClaimed(address)", [U])]),
 "YAMA": ("0x86D779fc4d83044cCECCb53639f9a98E367D6E46", [
    ("freeSharesRemaining", "freeSharesRemaining()", []),
    ("freeClaimed", "freeClaimed()", []),
    ("freeAvailable", "freeAvailable()", []),
    ("quote_user", "quote(address,uint256)", [U, 1])]),
 "NIGHTFORGE_B": ("0x051f04ff7b095793613b9caac197cc1051c24e2b", [
    ("totalSupply", "totalSupply()", []), ("balanceOf_user", "balanceOf(address)", [U])]),
 "STALL": ("0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308", [
    ("totalSupply", "totalSupply()", []), ("balanceOf_user", "balanceOf(address)", [U])]),
}
def do_read(item):
    name, (addr, views) = item
    res, rpc, err = read_item(addr, views)
    res["_addr"] = addr
    if err: res["_err"] = err
    return name, res
reread = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for name, res in ex.map(do_read, V.items()):
        reread[name] = res
# block number
blk = curl(RPCS[0], 15, post=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}))
try: block = int(json.loads(blk)["result"], 16)
except Exception: block = None
out["legs"]["reread"] = {"block": block, "items": reread}

# ---------- diffs vs 00:01 baseline ----------
diffs = {}
for name, cur in reread.items():
    base = base_reread.get(name, {})
    for k, v in cur.items():
        if k.startswith("_"): continue
        bv = base.get(k)
        if v != bv:
            diffs.setdefault(name, {})[k] = {"was": bv, "now": v}
out["legs"]["diffs_vs_0001"] = diffs

# ---------- Bridge (read-only) ----------
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bc = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values()}
    snap_addrs |= {str(v.get("sale", "")).lower() for v in snap.get("track_c", {}).values()}
    bridge_new = [a for a in bc if a.lower() not in snap_addrs]
    bridge_disc = [a for a, v in bc.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["legs"]["bridge"] = {"contracts": len(bc), "not_in_snapshot": bridge_new[:20],
                             "same_owner_discarded": bridge_disc[:20],
                             "writer": bridge.get("writer"), "seeded": bridge.get("seeded")}
except Exception as e:
    out["legs"]["bridge"] = {"error": str(e)[:200]}

# ---------- NIGHTFORGE / EMBERANVIL site re-check ----------
gate = {}
for site, contracts in [("https://nightforge.pages.dev", ["0x22f43ba09fd4beb9417d4484c60370354b220186", "0x7673c596a6702d32f844266dc2ca7b1fd6d7df21"])]:
    checks = {}
    for path in ["/", "/llms.txt", "/skill.md", "/launch.json"]:
        raw = curl(site + path, 20)
        low = raw.lower()
        checks[path] = {"bytes": len(raw),
                        "prints_contract": any(c.lower() in low for c in contracts)}
    gate[site] = checks
out["legs"]["gate_recheck"] = gate

out["duration_sec"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "run-2026-11-11-0004-legs.json", "w"), indent=1)

# update hot-leg-seen.json with genuinely new contracts only
new_seen = {}
for a in list(new_feed) + [a for lbl in bb for a in bb[lbl]["addrs"]]:
    if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED:
        new_seen[a] = NOW
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["legs"]["seen_added"] = list(new_seen.keys())
json.dump(out, open(BASE + "run-2026-11-11-0004-legs.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_sec"], "feed_new": new_feed,
                  "diffs": diffs, "gate": gate, "bridge": out["legs"]["bridge"],
                  "seen_added": list(new_seen.keys())}, indent=1)[:4000])
