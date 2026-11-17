#!/usr/bin/env python3
"""Hot-leg run 2026-11-16 16:49 WIB. Legs 1-4 + bridge, read-only except own state files.
Leg1 Sourcify feed limit 20 -> shape-check new vs hot-leg-seen.json.
Leg2 Boltbook EN+ZH front pages -> addresses -> new vs seen.
Leg3: verify only if a new sale-shape contract appears (none expected -> skip).
Leg4: re-read 6 focus snapshot items via batched eth_call (same ITEMS as run 1630).
Bridge: read-only scan-bridge.json vs snapshot addresses.
Writes: run-hot-leg-2026-11-16-1639.json, hot-leg-2026-11-16-1639-runlog.md,
        run-2026-11-16-1639-sourcify.json, -feedshape.json, -reread.json,
        hot-leg-2026-11-16-1639-boltbook-{en,zh}.html ; updates hot-leg-seen.json only.
No preview/mint. No writes to onchain-snapshot.json or main seen files."""
import json, re, subprocess, time, urllib.request, concurrent.futures
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
RUN = "2026-11-16-1649"
t0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"

def fetch_url(url, timeout=20, ua="free-mint-hot-leg/1649"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def now_iso():
    return NOW.isoformat()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_before = len(seen)
out = {"run": "free-mint-hot-leg 2026-11-16 16:49 WIB", "started_wib": now_iso()}

# ---- Leg 1: Sourcify feed ----
feed = json.loads(fetch_url("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25).decode())
json.dump(feed, open(BASE + f"run-{RUN}-sourcify.json", "w"), indent=1)
results = feed.get("results", [])
out["feed"] = {"n": len(results),
               "newest_verifiedAt": results[0].get("verifiedAt") if results else None,
               "oldest_verifiedAt": results[-1].get("verifiedAt") if results else None}
feed_addrs = [x["address"] for x in results]
feed_new = [a for a in feed_addrs if a not in seen and a.lower() not in {k.lower() for k in seen}]
out["feed_new"] = feed_new

def shape_check(addr):
    try:
        meta = json.loads(fetch_url(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
                "free": [f.lower() for f in free_views], "agent": agent_ref, "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}", "status": "shape-check-failed"}

feed_shape = {}
if feed_new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for o in ex.map(shape_check, feed_new):
            feed_shape[o["address"]] = o
out["feed_shape"] = feed_shape
for a, o in feed_shape.items():
    seen[a] = {"first_seen_wib": now_iso(), "source": "sourcify-feed",
               "status": "checked" if o.get("status") == "checked" else o.get("status"),
               "note": f"S1={o.get('S1')} S2={o.get('S2')} mint={o.get('mint')} quote={o.get('quote')} free={o.get('free')} agent={o.get('agent')}"}

# ---- retry 404s from run 1630 ----
prev = json.load(open(BASE + "run-hot-leg-2026-11-16-1639.json"))
retry_list = prev.get("retry_404", {}).get("retried", [])
retry_results = {}
if retry_list:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for o in ex.map(shape_check, retry_list):
            retry_results[o["address"]] = o.get("status", "shape-check-failed")
            if o.get("status") == "checked":
                feed_shape[o["address"]] = o
                seen[o["address"]] = {"first_seen_wib": now_iso(), "source": "sourcify-feed-retry",
                                      "status": "checked",
                                      "note": f"S1={o.get('S1')} S2={o.get('S2')} mint={o.get('mint')} quote={o.get('quote')} free={o.get('free')} agent={o.get('agent')}"}
out["retry_404"] = {"total_failed": prev.get("retry_404", {}).get("total_failed", 206),
                    "retried": retry_list, "results": retry_results}

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang, fname):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    data = None; err = None
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", "free-mint-hot-leg/1649", url],
                           capture_output=True, timeout=30)
        if r.returncode == 0 and len(r.stdout) > 1000:
            data = r.stdout
    except Exception as ex:
        err = str(ex)[:120]
    if data is None:
        try:
            data = fetch_url(url, timeout=25)
        except Exception as ex:
            err = f"{type(ex).__name__}: {str(ex)[:120]}"
    if data is None:
        open(BASE + fname, "wb").write(b"")
        return {"bytes": 0, "addrs": [], "error": err}
    open(BASE + fname, "wb").write(data)
    txt = data.decode("utf-8", "ignore")
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", txt)), key=lambda x: x.lower())
    posts = sorted(set(re.findall(r"/p/[A-Za-z0-9_-]+", txt)))
    return {"bytes": len(data), "addrs": addrs, "posts": posts[:30]}

bb_en = boltbook("en", f"hot-leg-{RUN}-boltbook-en.html")
bb_zh = boltbook("zh", f"hot-leg-{RUN}-boltbook-zh.html")
out["boltbook_en"] = bb_en
out["boltbook_zh"] = bb_zh
bb_all = sorted(set(bb_en["addrs"] + bb_zh["addrs"]), key=lambda x: x.lower())
seen_lower = {k.lower() for k in seen}
bb_new = [a for a in bb_all if a.lower() not in seen_lower]
out["boltbook_new"] = bb_new
bb_shape = {}
if bb_new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for o in ex.map(shape_check, bb_new):
            bb_shape[o["address"]] = o
out["boltbook_new_shapecheck"] = bb_shape
for a, o in bb_shape.items():
    seen[a] = {"first_seen_wib": now_iso(), "source": "boltbook-en" if a in bb_en["addrs"] else "boltbook-zh",
               "status": "checked" if o.get("status") == "checked" else o.get("status"),
               "note": f"S1={o.get('S1')} S2={o.get('S2')} mint={o.get('mint')} quote={o.get('quote')} free={o.get('free')} agent={o.get('agent')}"}

# ---- Leg 3: any new sale shape? ----
sale_shapes = [a for a, o in {**feed_shape, **bb_shape}.items() if o.get("S1") or o.get("S2")]
out["sale_shape_new"] = sale_shapes

# ---- Leg 4: re-read focus items ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=150):
    outp = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(outp)

U = [USER]
ITEMS = {
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "ORBIT": ("0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
    ("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("claimOpen","claimOpen()",[]),("hasFreeClaimed_user","hasFreeClaimed(address)",U),
    ("totalSupply","totalSupply()",[])]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft","freeSharesLeft()",[]),("openedAt","openedAt()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeBooked_user","freeBooked(address)",U)]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
def read_one(name, addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    last = "no usable RPC response"
    for attempt in range(2):
        for ep in EPS:
            try:
                resp = post_rpc(ep, calls)
                if (isinstance(resp, list) and len(resp) == len(calls)
                        and all(isinstance(r, dict) and "result" in r for r in resp)):
                    merged = {}
                    for key, r in zip(meta, resp):
                        merged[key] = to_int(r.get("result"))
                    return merged, None
                last = f"bad response {ep}: {str(resp)[:100]}"
            except Exception as ex:
                last = str(ex)[:120]
        time.sleep(8)
    return None, last

items_list = list(ITEMS.items())
reread = {"started_wib": now_iso(), "reads": {}, "reads_ok": 0, "reads_total": len(items_list), "block": None}
block = None
for name, (addr, views) in items_list:
    merged, err = read_one(name, addr, views)
    if merged is not None:
        reread["reads"][name] = {"address": addr, "views": merged}
        reread["reads_ok"] += 1
    else:
        reread["reads"][name] = {"address": addr, "views": {}, "error": err}
# block number
try:
    b = post_rpc(EPS[0], [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=30)
    block = int(b[0]["result"], 16) if isinstance(b, list) else None
except Exception:
    block = None
reread["block"] = block
reread["elapsed_s"] = round(time.time() - t0, 1)
json.dump(reread, open(BASE + f"run-{RUN}-reread.json", "w"), indent=1)
out["reread"] = {"block": block, "reads_ok": reread["reads_ok"], "reads_total": reread["reads_total"],
                 "summary": {n: v["views"] for n, v in reread["reads"].items()}}

# ---- Bridge (read-only) ----
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    for entry in snap.get(sec, {}).values():
        if isinstance(entry, dict):
            for k in ("address", "sale", "token", "mint"):
                v = entry.get(k)
                if isinstance(v, str) and v.startswith("0x"):
                    snap_addrs.add(v.lower())
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
outside = [a for a in bcontracts if a.lower() not in snap_addrs]
discarded = [a for a, v in bcontracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
out["bridge"] = {"n": len(bcontracts), "same_owner_discarded": len(discarded), "outside_snapshot": outside}

# ---- persist own state only ----
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)
out["seen_added"] = len(seen) - seen_before
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + f"run-hot-leg-{RUN}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
