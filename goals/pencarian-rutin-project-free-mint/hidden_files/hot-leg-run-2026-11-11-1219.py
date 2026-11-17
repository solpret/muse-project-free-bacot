#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 12:19 WIB. Legs: (1) Sourcify feed (limit 20) +
shape-check new contracts; (2) Boltbook EN+ZH boltbook.fun; (3) on-chain verify
any new S1/S2; (4) leg4 re-read of prio set vs 1214 baseline; bridge read-only.
Read-only except own hot-leg state files. No preview/mint, no chain scan."""
import json, time, urllib.request, concurrent.futures, subprocess, re, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EP = "https://bsc.nodereal.io/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 12:19 WIB"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)
def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(EP, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.loads(r.read().decode())
        if "error" in j: return {"error": str(j["error"])[:120]}
        raw = j["result"]
        if raw in (None, "0x"): return {"error": "empty-return"}
        if len(raw) >= 66:
            v = raw[2:66]
            if set(v) <= set("0123456789abcdef"):
                try: return int(v, 16)
                except Exception: return raw
        return raw
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:90]}"}

def call_str(addr, sig):
    r = call(addr, sig)
    if isinstance(r, dict): return r
    return r  # raw hex (bytes32/string) - caller interprets

def get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}

# ---- Leg 1: Sourcify feed ----
feed_addrs, feed_times, feed_note = [], {}, ""
try:
    st, body = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 15)
    feed = json.loads(body.decode())
    items = feed.get("results", feed if isinstance(feed, list) else [])
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
            feed_times[a] = it.get("verifiedAt") or it.get("matchDate") or ""
    json.dump(feed, open(BASE + "hot-leg-2026-11-11-1219-feed.json", "w"))
    feed_note = f"feed HTTP {st}, {len(feed_addrs)} contracts"
except Exception as e:
    feed_note = f"feed fetch FAILED: {type(e).__name__}: {str(e)[:80]} - leg skipped, retried next run"
NEW = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
EXCL_HIT = [a for a in feed_addrs if a.lower() in EXCLUDED]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:100]}"}

shapes = []
if NEW:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        shapes = list(ex.map(fetch_abi, NEW))
for s in shapes:
    a = s["address"]
    if s.get("error"):
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"Sourcify ABI fetch error: {s['error']} - no sale-shape evidence; recorded, not a lead, never previewed/minted.",
                   "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    else:
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"S1={s['S1']} S2={s['S2']} mint={s['has_mint']} quote={s['has_quote']} free={s['free_views']} agent={s['agent_ref']} token={s['is_token']}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape"}
s1_pass = [s["address"] for s in shapes if s.get("S1")]
s2_pass = [s["address"] for s in shapes if s.get("S2")]
feed_detail = f"{feed_note}; {len(NEW)} new vs seen; S1={s1_pass or []} S2={s2_pass or []}; shapes={ {s['address'][-6:]: (s.get('S1'), s.get('S2'), s.get('error','')) for s in shapes} }; excluded-hit={EXCL_HIT or []}"

# ---- Leg 2: Boltbook EN + ZH ----
def curl_get(url, timeout=20):
    p = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError(f"curl rc={p.returncode} bytes={len(p.stdout)} err={p.stderr[:80]!r}")
    return 200, p.stdout

bb_note = ""
bb_fresh = []
try:
    st_en, en = curl_get("https://boltbook.fun/", 20)
    st_zh, zh = curl_get("https://boltbook.fun/?lang=zh", 20)
    open(BASE + "hot-leg-2026-11-11-1219-boltbook-en.html", "wb").write(en)
    open(BASE + "hot-leg-2026-11-11-1219-boltbook-zh.html", "wb").write(zh)
    addrs = set(ADDR_RE.findall(en.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh.decode("utf-8", "ignore")))
    bb_fresh = sorted(a for a in addrs if a.lower() not in {k.lower() for k in seen})
    bb_note = (f"EN HTTP {st_en} ({len(en)}B) + ZH HTTP {st_zh} ({len(zh)}B) boltbook.fun; "
               f"{len(addrs)} unique addresses, {len(bb_fresh)} not in hot-leg-seen.json: {bb_fresh or 'none'}")
    txhash = set()
    for _pg in (en.decode("utf-8", "ignore"), zh.decode("utf-8", "ignore")):
        for _m in re.finditer(r"0x[0-9a-fA-F]{64}", _pg):
            txhash.add("0x" + _m.group(0)[2:42].lower())
    for a in bb_fresh:
        if a.lower() in txhash:
            seen[a] = {"first_seen_wib": NOW_ISO,
                       "note": "First 40 hex chars of a 64-hex TX HASH inside a Boltbook post text, not a contract address - no shape-check, never a lead.",
                       "source": "boltbook-frontpage", "status": "checked-not-contract"}
        else:
            seen[a] = {"first_seen_wib": NOW_ISO,
                       "note": "Boltbook front-page address, Sourcify/shape check pending next run (feed leg covers shape-check for verified contracts).",
                       "source": "boltbook-frontpage", "status": "checked-seen-only"}
except Exception as e:
    bb_note = f"Boltbook fetch FAILED: {type(e).__name__}: {str(e)[:100]} - leg skipped, retried next run"
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: prio re-read (single eth_calls) ----
U = enc_addr(USER)
def views(addr, spec):
    out = {}
    for key, sig, args in spec:
        out[key] = call(addr, sig, args)
    return out

PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply", "totalSupply()", ""), ("mintOpen", "mintOpen()", ""),
    ("agentFreeUsed", "agentFreeUsed()", ""), ("freeLeft", "freeLeft()", ""),
    ("balanceOf_user", "balanceOf(address)", U), ("agentFreeByWallet_user", "agentFreeByWallet(address)", U)]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply", "totalSupply()", ""), ("agentFreeUsed", "agentFreeUsed()", ""),
    ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
    ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened", "opened()", ""), ("totalFreeMinted", "totalFreeMinted()", ""),
    ("totalMinted", "totalMinted()", "")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("startTime", "startTime()", ""), ("freeClaimed", "freeClaimed()", ""),
    ("launched", "launched()", "")]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES", "FREE_SHARES()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "CAP7": ("0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", [
    ("freeMinted", "freeMinted()", ""), ("sharesMinted", "sharesMinted()", ""),
    ("soldOut", "soldOut()", ""), ("phase", "phase()", ""),
    ("balanceOf_user", "balanceOf(address)", U),
    ("freeClaimed_agentId", "freeClaimed(uint256)", enc_u(AGENTID))]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("SALE_START", "SALE_START()", ""), ("FREE_SHARES", "FREE_SHARES()", ""),
    ("freeSharesLeft", "freeSharesLeft()", ""), ("openedAt", "openedAt()", ""),
    ("freeTaken_agentId", "freeTaken(uint256)", enc_u(AGENTID))]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [
    ("FREE_CAP", "FREE_CAP()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "CopperNook": ("0xb5b121e1CEC5aDD53708DB93D8997a837918f89e", [
    ("PRICE", "PRICE()", ""), ("spotsLeft", "spotsLeft()", ""),
    ("totalSpotsMinted", "totalSpotsMinted()", ""), ("MAX_SPOTS", "MAX_SPOTS()", ""),
    ("isAgent_user", "isAgent(address)", U)]),
 "EmberFord": ("0x6d02F55f4d21220d3F60498C963A4e882a564A7f", [
    ("PRICE", "PRICE()", ""), ("spotsLeft", "spotsLeft()", ""),
    ("totalSpotsMinted", "totalSpotsMinted()", ""), ("MAX_SPOTS", "MAX_SPOTS()", ""),
    ("isAgent_user", "isAgent(address)", U)]),
}
prio = {"block": None, "values": {}}
try:
    blk = call("0x0000000000000000000000000000000000000000", "blockNumber()", "")
    prio["block"] = blk if isinstance(blk, int) else None
except Exception:
    pass
# blockNumber via raw rpc
try:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    req = urllib.request.Request(EP, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        prio["block"] = int(json.loads(r.read().decode())["result"], 16)
except Exception as e:
    prio["block"] = f"error {e}"
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    futs = {name: ex.submit(views, addr, spec) for name, (addr, spec) in PRIO.items()}
    for name, f in futs.items():
        try: prio["values"][name] = f.result(timeout=60)
        except Exception as e: prio["values"][name] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
json.dump(prio, open(BASE + "hot-leg-2026-11-11-1219-prio.json", "w"), indent=1)

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    cons = b.get("contracts", {})
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    new_in_bridge = [a for a in feed_addrs + bb_fresh if a.lower() in {k.lower() for k in cons}]
    disc = None
    dp = BASE + "same-owner-discards.json"
    if os.path.exists(dp):
        disc = json.load(open(dp))
        disc_l = {k.lower() for k in disc} if isinstance(disc, dict) else set()
        hits = [a for a in feed_addrs + bb_fresh if a.lower() in disc_l]
    else:
        hits = "discards file not found"
    bridge_note = (f"scan-bridge.json read ({len(cons)} contracts, mtime {mtime}); "
                   f"new feed/Boltbook contracts in bridge: {new_in_bridge or 'none'}; "
                   f"same-owner-discards hits among new: {hits}")
except Exception as e:
    bridge_note = f"bridge read FAILED: {type(e).__name__}: {str(e)[:100]} - skipped, run continues"

# ---- Compare vs 1214 baseline ----
base = json.load(open(BASE + "hot-leg-2026-11-11-1214-prio.json"))
bv = base.get("values", {})
def cmp(name, key):
    old = bv.get(name, {}).get(key) if isinstance(bv.get(name), dict) else None
    new = prio["values"].get(name, {}).get(key) if isinstance(prio["values"].get(name), dict) else None
    return old, new
changes = []
for name in PRIO:
    for key in prio["values"].get(name, {}):
        o, n = cmp(name, key)
        if o != n:
            changes.append(f"{name}.{key}: {o} -> {n}")
run = {
 "run": RUN, "block": prio["block"], "duration_s": round(time.time() - T0, 1),
 "legs": {
  "sourcify_feed": feed_detail,
  "boltbook": bb_note,
  "leg4_priority_reread": ("changes vs 1214 baseline: " + ("; ".join(changes) if changes else "NONE") +
     " | fresh: " + json.dumps(prio["values"])),
  "bridge": bridge_note,
  "execution": "NONE - no new strong lead / track-C lead; no preview/mint/claim (to be decided after reading fresh values).",
 },
 "report": "TBD",
}
json.dump(run, open(BASE + "hot-leg-run-2026-11-11-1219.json", "w"), indent=1)
print(json.dumps(run, indent=1)[:6000])
print("DURATION", round(time.time() - T0, 1))
