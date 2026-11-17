#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 07:04 WIB - lean pattern (same as 0629 run).
Legs: (1) Sourcify feed fresh fetch (limit 20) + shape-check new contracts;
(2) Boltbook EN+ZH boltbook.fun fresh fetch; (3) leg 4 priority re-read vs
0659-prio baseline; (4) scan-bridge.json read-only.
Read-only except own hot-leg state files. No preview/mint, no chain scan."""
import json, time, urllib.request, concurrent.futures, subprocess, re
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 07:04 WIB"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}

# ---- Leg 1: Sourcify feed ----
feed_addrs, feed_note = [], ""
try:
    st, body = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 15)
    feed = json.loads(body.decode())
    items = feed.get("results", feed if isinstance(feed, list) else [])
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
    json.dump(feed, open(BASE + "hot-leg-2026-11-11-0704-feed.json", "w"))
    feed_note = f"feed HTTP {st}, {len(feed_addrs)} contracts"
except Exception as e:
    feed_note = f"feed fetch FAILED: {type(e).__name__}: {str(e)[:80]} - leg skipped, retried next run"
NEW = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
ALREADY = [a for a in feed_addrs if a.lower() in seen_l]
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(fetch_abi, NEW))
s1_pass = [s["address"] for s in shapes if s.get("S1")]
s2_pass = [s["address"] for s in shapes if s.get("S2")]
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
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 2: Boltbook EN + ZH ----
def curl_get(url, timeout=20):
    p = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError(f"curl rc={p.returncode} bytes={len(p.stdout)} err={p.stderr[:80]!r}")
    return 200, p.stdout

bb_note = ""
try:
    st_en, en = curl_get("https://boltbook.fun/", 20)
    st_zh, zh = curl_get("https://boltbook.fun/?lang=zh", 20)
    open(BASE + "hot-leg-2026-11-11-0704-boltbook-en.html", "wb").write(en)
    open(BASE + "hot-leg-2026-11-11-0704-boltbook-zh.html", "wb").write(zh)
    addrs = set(ADDR_RE.findall(en.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh.decode("utf-8", "ignore")))
    fresh = sorted(a for a in addrs if a.lower() not in {k.lower() for k in seen})
    bb_note += (f"EN HTTP {st_en} ({len(en)}B) + ZH HTTP {st_zh} ({len(zh)}B) boltbook.fun; "
               f"{len(addrs)} unique addresses, {len(fresh)} not in hot-leg-seen.json: {fresh or 'none'}")
    _txhash = set()
    for _pg in (en.decode("utf-8", "ignore"), zh.decode("utf-8", "ignore")):
        for _m in re.finditer(r"0x[0-9a-fA-F]{64}", _pg):
            _txhash.add("0x" + _m.group(0)[2:42].lower())
    for a in fresh:
        if a.lower() in _txhash:
            seen[a] = {"first_seen_wib": NOW_ISO,
                       "note": "First 40 hex chars of a 64-hex TX HASH inside a Boltbook post text, not a contract address - no shape-check, never a lead.",
                       "source": "boltbook-frontpage", "status": "checked-not-contract"}
        else:
            _s = fetch_abi(a)
            if _s.get("error"):
                seen[a] = {"first_seen_wib": NOW_ISO,
                           "note": f"Boltbook front-page mention; Sourcify ABI fetch error: {_s['error']} - no sale-shape evidence; recorded, not a lead, never previewed/minted.",
                           "source": "boltbook-frontpage", "status": "checked-abi-unavailable"}
            else:
                seen[a] = {"first_seen_wib": NOW_ISO,
                           "note": f"Boltbook front-page mention; shape-check in-run: S1={_s['S1']} S2={_s['S2']} mint={_s['has_mint']} quote={_s['has_quote']} free={_s['free_views']} agent={_s['agent_ref']} token={_s['is_token']}",
                           "source": "boltbook-frontpage", "status": "checked-not-sale-shape" if not (_s['S1'] or _s['S2']) else "sale-shape-pass"}
                if _s['S1'] or _s['S2']:
                    bb_note += f" SALE-SHAPE PASS from Boltbook: {a} (S1={_s['S1']} S2={_s['S2']})."
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    bb_note = f"Boltbook fetch FAILED: {type(e).__name__}: {str(e)[:80]} - leg skipped, retried next run"

# ---- Leg 4: priority re-read vs 0659-prio baseline ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("agentFreeUsed", "agentFreeUsed()"), ("freeLeft", "freeLeft()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "NIGHTFORGE_B": ("0x051f04ff7b095793613b9caac197cc1051c24e2b", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)")]),
 "SOLDERCATS": ("0x3D972EBbF7488f21b95250B867e2406c723C9DDC", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("freePhaseStart", "freePhaseStart()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("balanceOf_user", "balanceOf(address)")]),
 "sale-11-11": ("0x64767b1a39441e72046c2162065a2896e154b341", [
    ("freeMinted", "freeMinted()"), ("freeClaimed_user", "freeClaimed(address)")]),
 "PESI": ("0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD", [
    ("freeMinted", "freeMinted()"), ("totalFreeShares", "totalFreeShares()"),
    ("totalShares", "totalShares()")]),
 "ORYN-sale": ("0x96135a41FA155752dc7154CDcaA480f2fBEC1493", [
    ("paused", "paused()"), ("freePoolRemaining", "freePoolRemaining()")]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened", "opened()"), ("totalFreeMinted", "totalFreeMinted()"),
    ("totalMinted", "totalMinted()")]),
 "BOME-50CD": ("0x50CDd91b31cED977D2776825BBaD72e99FF0830E", [
    ("mintOpen", "mintOpen()"), ("freeLotsMinted", "freeLotsMinted()")]),
 "YAMA": ("0x86D779fc4d83044cCECCb53639f9a98E367D6E46", [
    ("totalFreeShares", "totalFreeShares()"), ("totalShares", "totalShares()")]),
 "binanceai-sale": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()")]),
}

jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        data = sel(sig) + enc_addr(USER) if sig.endswith("(address)") else sel(sig)
        jobs.append((name, fname, addr, data))

p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                   capture_output=True, text=True)
try:
    block = int(json.loads(p.stdout)["result"], 16)
except Exception:
    block = None

out = {}
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i+25]
    payload = json.dumps([{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for j, (_, _, to, data) in enumerate(chunk)])
    pr = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                         "-H", "Content-Type: application/json", "--data", payload],
                        capture_output=True, text=True)
    try:
        resps = json.loads(pr.stdout)
    except Exception:
        resps = []
    if isinstance(resps, dict):
        resps = [resps]
    for (name, fname, addr, _), r in zip(chunk, resps):
        raw = r.get("result") if isinstance(r, dict) else None
        val = None
        if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
            try:
                val = int(raw[:66], 16)
            except Exception:
                val = None
        out.setdefault(name, {})[fname] = val

json.dump({"block": block, "values": out},
          open(BASE + "hot-leg-run-2026-11-11-0704-prio.json", "w"), indent=1)

prev = json.load(open(BASE + "hot-leg-run-2026-11-11-0659-prio.json"))
prev_vals = prev.get("values", {})
diffs = []
for name, vals in out.items():
    for f, v in vals.items():
        old = prev_vals.get(name, {}).get(f)
        if old != v:
            diffs.append({"item": name, "field": f, "old": old, "new": v})

# ---- Bridge (read-only) + discards check ----
bridge_note = ""
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    in_bridge_new = [a for a in NEW if a.lower() in {k.lower() for k in bcontracts}]
    discarded_n = sum(1 for v in bcontracts.values() if v.get("same_owner_discarded"))
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, last written "
                   f"{br.get('last_written', br.get('written', 'n/a'))}); {discarded_n} same_owner_discarded; "
                   f"new feed contracts in bridge: {in_bridge_new or 'none'}")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    in_discards = [a for a in NEW if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts in same-owner-discards.json: {in_discards or 'none'}"

s1s2_note = f"S1_PASS={s1_pass} S2_PASS={s2_pass}"
report_items = []
if s1_pass or s2_pass:
    report_items.append(f"new sale-shape pass needs lead evaluation: S1={s1_pass} S2={s2_pass}")
report_str = ("REPORT: " + "; ".join(report_items)) if report_items else "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat."
result = {"run": RUN, "legs": {
  "sourcify_feed": f"{feed_note}; {len(ALREADY)} already seen, {len(NEW)} new shape-checked, {len(EXCL_HIT)} excluded hit. {s1s2_note}. Recorded in hot-leg-seen.json.",
  "boltbook": bb_note,
  "leg4_priority_reread": f"block {block} vs 0659-prio baseline block {prev.get('block')}; {len(diffs)} diffs: {diffs}",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": report_str,
 "duration_sec": round(time.time() - T0, 1)}
json.dump(result, open(BASE + "hot-leg-run-2026-11-11-0704.json", "w"), indent=1)
print(json.dumps(result, indent=1))
print("PRIO VALUES:", json.dumps(out))
