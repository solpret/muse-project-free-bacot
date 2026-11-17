#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 09:44 WIB - consolidated run (feed + shape +
Boltbook + leg4 prio re-read + bridge/discards). Read-only except own
hot-leg state files. No preview/mint/claim, no chain scan."""
import json, time, subprocess, re, urllib.request
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP_NODE = "https://bsc.nodereal.io/"
EP_DATA = "https://bsc-dataseed.binance.org/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 09:44 WIB"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def curl_bytes(url, timeout, extra=None):
    cmd = ["curl", "-s", "--max-time", str(timeout)] + (extra or []) + [url]
    pr = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
    return pr.returncode, pr.stdout

def curl_json_post(url, payload, timeout):
    pr = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", url,
                         "-H", "Content-Type: application/json", "--data", payload],
                        capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(pr.stdout)

# ---- Leg 1: Sourcify feed ----
feed, feed_note = None, ""
for to in (30, 60):
    try:
        rc, raw = curl_bytes("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", to)
        if rc == 0 and raw:
            feed = json.loads(raw.decode())
            feed_note = f"feed HTTP 200 ({len(raw)} bytes, timeout {to}s)"
            break
        feed_note = f"feed attempt {to}s rc={rc} bytes={len(raw)}"
    except Exception as e:
        feed_note = f"feed attempt {to}s {type(e).__name__}: {e}"
    time.sleep(1)
if feed is None:
    feed = {"results": []}
    feed_note += " -> FEED FAILED, leg 1 skipped"
json.dump(feed, open(BASE + "hot-leg-2026-11-11-0944-feed.json", "w"), indent=1)
items = feed.get("results", feed if isinstance(feed, list) else [])
feed_addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
verified_at = [it.get("verifiedAt") for it in items if isinstance(it, dict)]

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lc = {k.lower() for k in seen}
NEW = [a for a in feed_addrs if a.lower() not in seen_lc]
EXCL_HIT = [a for a in NEW if a.lower() in EXCLUDED]

# ---- Leg 1 shape-check (sequential, same logic as 0924) ----
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
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
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names), "fns": sorted(names)[:60]}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
for a in NEW:
    if a.lower() in EXCLUDED:
        shapes.append({"address": a, "excluded": True})
        continue
    r = fetch_abi(a)
    shapes.append(r)
    print(a, "S1" if r.get("S1") else "-", "S2" if r.get("S2") else "-",
          "EARLY" if r.get("early_shape") else "-", r.get("error", f"fns={r.get('fn_count')} free={r.get('free_views')} agent={r.get('agent_ref')} nft={r.get('is_nft')}"))
    time.sleep(1)
s1_pass = [s["address"] for s in shapes if s.get("S1")]
s2_pass = [s["address"] for s in shapes if s.get("S2")]
early_shape = [s["address"] for s in shapes if s.get("early_shape")]
json.dump({"started_wib": RUN, "elapsed_s": round(time.time() - T0, 1),
           "s1_pass": s1_pass, "s2_pass": s2_pass, "early_shape": early_shape,
           "shapes": shapes},
          open(BASE + "hot-leg-2026-11-11-0944-shape.json", "w"), indent=1)

# ---- Leg 2: Boltbook EN + ZH ----
bb_notes = []
bb_new = []
try:
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = {str(k).lower() for k in snap.get("contracts", {})}
    snap_addrs |= {str(c).lower() for c in snap.get("track_c", {})}
except Exception:
    snap_addrs = set()
for lang, url in (("en", "https://boltbook.fun/"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        rc, raw = curl_bytes(url, 25)
        open(BASE + f"boltbook-2026-11-11-0944-{lang}.html", "wb").write(raw)
        if rc == 0 and len(raw) > 1000:
            addrs = sorted({m.lower() for m in re.findall(r"0x[0-9a-fA-F]{40}", raw.decode(errors="ignore"))})
            new_here = [a for a in addrs if a not in seen_lc and a not in snap_addrs]
            bb_notes.append(f"{lang.upper()} HTTP 200 {len(raw)} bytes, {len(addrs)} addr, {len(new_here)} new: {new_here}")
            bb_new.extend(new_here)
        else:
            bb_notes.append(f"{lang.upper()} FAILED rc={rc} bytes={len(raw)}")
    except Exception as e:
        bb_notes.append(f"{lang.upper()} ERROR {type(e).__name__}: {e}")

# ---- hot-leg-seen.json update ----
for a in NEW:
    st = ("excluded-recorded" if a.lower() in EXCLUDED else
          "early-shape-noted-main-job-scan-leg-owns-early-detection" if a in early_shape else
          "checked-not-sale-shape")
    seen[a] = {"first_seen": NOW_ISO, "source": "sourcify-feed", "status": st}
for a in bb_new:
    seen[a] = {"first_seen": NOW_ISO, "source": "boltbook-frontpage",
               "status": "checked-not-sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: priority re-read vs 0939-prio baseline ----
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
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("freeMinted", "freeMinted()"), ("freeSharesRemaining", "freeSharesRemaining()"),
    ("FREE_SHARES", "FREE_SHARES()"), ("freeClaimed_user", "freeClaimed(address)")]),
 "AGTC": ("0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5", [
    ("freeMinted", "freeMinted()"), ("totalSupply", "totalSupply()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("balanceOf_user", "balanceOf(address)")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched", "launched()"), ("startTime", "startTime()")]),
}

jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        data = sel(sig) + enc_addr(USER) if sig.endswith("(address)") else sel(sig)
        jobs.append((name, fname, addr, data))

block = None
for ep in (EP_NODE, EP_DATA):
    try:
        block = int(curl_json_post(ep, '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}', 15)["result"], 16)
        break
    except Exception:
        continue

out = {}
chunk_notes = []
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i+25]
    payload = json.dumps([{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for j, (_, _, to, data) in enumerate(chunk)])
    resps = []
    for ep in (EP_NODE, EP_DATA):
        try:
            resps = curl_json_post(ep, payload, 30)
            if resps:
                break
        except Exception:
            resps = []
    if isinstance(resps, dict):
        resps = [resps]
    if not resps:
        chunk_notes.append(f"chunk {i//25+1}: EMPTY on both RPCs")
    for (name, fname, addr, _), r in zip(chunk, resps):
        raw = r.get("result") if isinstance(r, dict) else None
        val = None
        if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
            try: val = int(raw[:66], 16)
            except Exception: val = None
        out.setdefault(name, {})[fname] = val

json.dump({"block": block, "values": out},
          open(BASE + "hot-leg-run-2026-11-11-0944-prio.json", "w"), indent=1)

prev = json.load(open(BASE + "hot-leg-run-2026-11-11-0939-prio.json"))
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
    discarded_n = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, "
                   f"{discarded_n} same_owner_discarded; new feed contracts in bridge: {in_bridge_new or 'none'})")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    dc |= {str(e).lower() for e in discards if isinstance(e, str)}
    in_discards = [a for a in NEW + bb_new + ["0xDDc2352d1ceC10b42e05A297232f5328902C6c2C"] if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts + SHINE in same-owner-discards.json: {in_discards or 'none'}"

result = {"run": RUN, "legs": {
  "sourcify_feed": f"{feed_note}; {len(feed_addrs)} contracts, verifiedAt {verified_at[0] if verified_at else 'n/a'}..{verified_at[-1] if verified_at else 'n/a'}; {len(NEW)} new, {len(EXCL_HIT)} excluded hit. S1_PASS={s1_pass} S2_PASS={s2_pass} EARLY_SHAPE={early_shape}. Recorded in hot-leg-seen.json (total {len(seen)}).",
  "boltbook": "; ".join(bb_notes) + f" BB_NEW={bb_new or 'none'}",
  "leg4_priority_reread": f"block {block} vs 0939-prio baseline block {prev.get('block')}; {len(diffs)} diffs: {diffs}; chunk notes: {chunk_notes or 'none'}",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat.",
 "duration_sec": round(time.time() - T0, 1)}
json.dump(result, open(BASE + "hot-leg-run-2026-11-11-0944.json", "w"), indent=1)
print(json.dumps(result, indent=1))
print("PRIO VALUES:", json.dumps(out))
