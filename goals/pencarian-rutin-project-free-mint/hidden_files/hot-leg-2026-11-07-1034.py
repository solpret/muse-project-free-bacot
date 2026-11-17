#!/usr/bin/env python3
"""Hot-leg 1034 main: leg-1 shape-check (17 new feed contracts, parallel) +
fast leg-3 for any NEW S1 + MEMPL/B777/HALVE + bounded leg-4 re-read + bridge.
Read-only except hot-leg-seen.json / hot-leg-reported.json (own state only)."""
import json, re, subprocess, time, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1034"
T0 = time.time()
DEADLINE = 110
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MEMPL = "0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
B777 = "0x47529CF66091BeB0E8e0F78D5635e367473D52d5"
HALVE = "0xFC29876Fa700Bacb0f925e258f61D0387F73cbB8"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freemint","free_slots","free_supply","freeamount"]
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org"]
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB).isoformat(timespec="seconds")
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return format(n, "064x")
def rpc_once(rpc, method, params, timeout=8):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.load(r)
def call(to, data):
    for rpc in RPCS:
        try:
            o = rpc_once(rpc, "eth_call", [{"to": to, "data": data}, "latest"])
            if "error" in o or not o.get("result") or o["result"] == "0x": continue
            v = o["result"]
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return "err:RPC"
def call_raw(to, data):
    for rpc in RPCS:
        try:
            o = rpc_once(rpc, "eth_call", [{"to": to, "data": data}, "latest"])
            if "error" in o or not o.get("result"): continue
            return o["result"]
        except Exception: continue
    return "err:RPC"
def block_number():
    try:
        o = rpc_once(RPCS[0], "eth_blockNumber", [], 8)
        return int(o["result"], 16)
    except Exception: return None

out = {"run": TS, "t0_wib": NOW}
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))

# ---- Leg 1: feed file (fetched 1034) ----
feed = json.load(open(f"{BASE}/sourcify-feed-1034.json"))
addrs1 = [r["address"] for r in feed.get("results", [])]
new1 = [a for a in addrs1 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
out["leg1_feed"] = len(addrs1); out["leg1_new"] = new1
print("leg1 feed:", len(addrs1), "new:", len(new1), flush=True)

# ---- Leg 2: Boltbook files (fetched 1034) ----
addrs2 = []
for lang in ("en", "zh"):
    html = open(f"{BASE}/boltbook-{lang}-1034.html", encoding="utf-8", errors="ignore").read()
    addrs2 += sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
addrs2 = sorted(set(addrs2))
new2 = [a for a in addrs2 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
out["leg2_unique"] = len(addrs2); out["leg2_new"] = new2
print("leg2 unique:", len(addrs2), "new:", new2, flush=True)

# ---- Shape-check new (parallel Sourcify ABI fetch) ----
def shape_one(a):
    try:
        with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", timeout=20) as r:
            d = json.load(r)
        abi = d.get("abi") or []
        fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
        src = json.dumps(abi).lower()
        mint = [f for f in fns if "mint" in f.lower()]
        quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower() or f.lower() in ("price", "getprice")]
        free = [f for f in fns if any(k in f.lower() for k in FREE)]
        agent = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
        token = [f for f in fns if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
        s1 = bool(mint) and bool(quote) and bool(free) and (REG.lower() in src or bool(agent))
        s2 = len(token) == 4 and any("mintfree" in f.lower() for f in fns) and bool(free) and (REG.lower() in src or bool(agent))
        return a, {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free,
                   "agent": agent, "token": token, "n_fns": len(fns)}
    except Exception as e:
        return a, {"error": f"{type(e).__name__}: {e}"}
to_check = sorted(set([a.lower() for a in new1 + new2]))
shape = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for a, s in ex.map(shape_one, to_check):
        shape[a] = s
        print(a, "S1", s.get("S1"), "S2", s.get("S2"), s.get("error", ""), flush=True)
out["shape"] = shape
for a, s in shape.items():
    if "error" in s: continue
    if a not in seen_lc:
        seen[a] = {"first_seen_wib": NOW,
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={bool(s.get('mint'))} quote={bool(s.get('quote'))} free={s.get('free')} agent={bool(s.get('agent'))} token={s.get('token')}",
                   "source": f"hot-leg-{TS}",
                   "status": "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)

# ---- Fast leg-3 for NEW S1/S2 found this run (not the 3 already handled in leg3) ----
new_sales = [a for a, s in shape.items() if s.get("S1") or s.get("S2")]
out["new_sale_shape_this_run"] = new_sales
print("new sale-shape this run:", new_sales, flush=True)
leg3fast = {}
for a in new_sales:
    s = shape[a]
    d = {}
    try:
        d["sharesSold"] = call(a, sel("sharesSold()"))
        d["MAX_SHARES"] = call(a, sel("MAX_SHARES()"))
        d["totalMinted"] = call(a, sel("totalMinted()"))
        d["freeMinted"] = call(a, sel("freeMinted()"))
        d["FREE_SUPPLY"] = call(a, sel("FREE_SUPPLY()"))
        q = call_raw(a, sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1))
        d["quote_user_1_raw"] = q
        if isinstance(q, str) and q.startswith("0x") and len(q) == 130:
            d["quote_user_1"] = {"free_flag": int(q[2:66], 16), "cost_wei": int(q[66:], 16)}
        d["freeUsed_user"] = call(a, sel("freeUsed(address)") + enc_addr(USER))
        d["freeClaimed_user"] = call(a, sel("freeClaimed(address)") + enc_addr(USER))
        d["mintedBy_user"] = call(a, sel("mintedBy(address)") + enc_addr(USER))
        d["balanceOf_user"] = call(a, sel("balanceOf(address)") + enc_addr(USER))
    except Exception as e:
        d["error"] = f"{type(e).__name__}: {e}"
    leg3fast[a] = d
    print(a, d, flush=True)
out["leg3fast"] = leg3fast

# ---- Bridge (read-only) ----
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap_text = open(f"{BASE}/onchain-snapshot.json", encoding="utf-8", errors="ignore").read().lower()
    disc = [a for a, v in contracts.items() if v.get("same_owner_discarded")]
    in_snap = [a for a in contracts if a.lower() in snap_text]
    not_in = [a for a in contracts if a.lower() not in snap_text]
    out["bridge"] = {"total": len(contracts), "same_owner_discarded": len(disc),
                     "in_snapshot_by_text": len(in_snap), "not_in_snapshot": len(not_in)}
    print("bridge:", out["bridge"], flush=True)
except Exception as e:
    out["bridge_error"] = str(e); print("bridge FAILED:", e, flush=True)

# ---- MEMPL / B777 / HALVE re-read (parallel) ----
blk = block_number()
out["leg4_block"] = blk
print("block:", blk, flush=True)
USER_PAD = "0x" + "0"*24 + USER[2:].lower()
def read_trio(addr, views):
    d = {}
    for sig in views:
        d[sig.split("(")[0]] = call(addr, sel(sig))
    d["freeLeft_user"] = call(addr, sel("freeLeft(address)") + USER_PAD[2:])
    d["quote_user_1"] = call(addr, sel("quote(address,uint256)") + USER_PAD[2:] + format(1, "064x"))
    d["mintedBy_user"] = call(addr, sel("mintedBy(address)") + USER_PAD[2:])
    d["balanceOf_user"] = call(addr, sel("balanceOf(address)") + USER_PAD[2:])
    return d
TRIO = {
 "mempl": (MEMPL, ["totalMints()", "mintOpen()", "FREE_PER_WALLET()", "MAX_MINTS()"]),
 "b777": (B777, ["totalMints()", "MAX_MINTS()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()"]),
 "halve": (HALVE, ["totalMints()", "mintOpen()", "FREE_PER_WALLET()", "MAX_MINTS()"]),
}
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(read_trio, addr, views): k for k, (addr, views) in TRIO.items()}
    for f in as_completed(futs):
        out[futs[f] + "_state"] = f.result()
        print(futs[f], out[futs[f] + "_state"], flush=True)

# ---- Leg 4: bounded re-read of live snapshot items ----
ITEMS = {
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", ["totalMinted()", "remainingFree()", "freeQuota()", "mintOpen()"]),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", ["freeMinted()", "FREE_CAP()", "totalSupply()"]),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()"]),
 "ChimpAgent": ("0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689", ["totalSupply()", "totalMints()", "MAX_MINTS()", "mintOpen()"]),
 "Pacture": ("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SHARES()", "freeSharesRemaining()"]),
 "960E-sale": ("0x960E7e4126b97679053B8416fA59f13508be88bf", ["freeMinted()", "FREE_CAP()", "freeClaimed()", "totalShares()"]),
 "Tampesta": ("0x6aA51bd62C0c6B0bA206e25952F4063a7e0CCE79", ["totalSupply()", "freeMinted()", "FREE_SUPPLY()"]),
 "GLPX": ("0xba5cde0ceea8704b8944deb51228ca59a7bd9cf0", ["sharesSold()", "MAX_SHARES()"]),
 "PLNK": ("0xec266bdd979b19d8a2f1266ef0610b4791dbd24b", ["sharesSold()", "MAX_SHARES()"]),
 "CRBK": ("0x38066aF063b6Eb0fBdF56e2D38eC265D9A79D996", ["sharesSold()", "MAX_SHARES()"]),
 "MZWK": ("0x892E438425b3A41BC75b25C22Fd878b3fa2e308d", ["sharesSold()", "MAX_SHARES()"]),
 "KZMB": ("0xBd6e4c6DEF0065007Bd163e4223Ae4f3aa3b6f09", ["sharesSold()", "MAX_SHARES()"]),
}
def read_one(args):
    name, (addr, views) = args
    d = {}
    for sig in views:
        if time.time() - T0 > DEADLINE:
            d[sig.split("(")[0]] = "deadline"; continue
        d[sig.split("(")[0]] = call(addr, sel(sig))
    if time.time() - T0 <= DEADLINE:
        d["freeClaimed_user"] = call(addr, sel("freeClaimed(address)") + USER_PAD[2:])
    return name, d
reread = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(read_one, it): it[0] for it in ITEMS.items()}
    for f in as_completed(futs):
        try:
            n, d = f.result(); reread[n] = d
        except Exception as e:
            reread[futs[f]] = {"error": str(e)}
out["leg4"] = reread
for n, d in reread.items(): print(n, d, flush=True)
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-{TS}.json", "w"), indent=1)
print("DONE duration", out["duration_s"], flush=True)
