#!/usr/bin/env python3
"""Hot-leg 2026-11-11 23:19 WIB — legs 1+2+4 in one fast script.
Leg 1: Sourcify feed limit 20, shape-check new vs hot-leg-seen.json +
      retry 5 most-recent shape-check-failed ABIs.
Leg 2: Boltbook EN+ZH front pages, extract addresses.
Leg 4: prio re-read via 5-call batched eth_call (salvage2 pattern).
Bridge: read-only counts.
Read-only except hot-leg-seen.json (own file) + own run files."""
import json, re, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2319"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-11 23:19 WIB", "started_wib": now_wib}

def curl(url, timeout=12, data=None, headers=None):
    cmd = ["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-d", data]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

def curl_json(url, timeout=12):
    raw = curl(url, timeout)
    try:
        return json.loads(raw.decode(errors="replace"))
    except Exception:
        return None

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}

# ---- Leg 1: Sourcify feed ----
feed = curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 12)
feed_addrs, feed_meta = [], {}
if isinstance(feed, dict):
    items = feed.get("results") or feed.get("contracts") or []
    for it in items:
        a = (it.get("address") or "").strip()
        if a:
            feed_addrs.append(a)
            feed_meta[a] = it.get("verifiedAt") or ""
elif isinstance(feed, list):
    for it in feed:
        a = (it.get("address") or "").strip()
        if a:
            feed_addrs.append(a)
            feed_meta[a] = it.get("verifiedAt") or ""
out["leg1_feed"] = {"returned": len(feed_addrs),
                    "verified_range": (min(feed_meta.values()), max(feed_meta.values())) if feed_meta else None,
                    "ok": bool(feed_addrs)}
json.dump({"addrs": feed_addrs, "meta": feed_meta}, open(BASE + f"hot-leg-{TAG}-feed.json", "w"), indent=1)

FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeamount", "free_supply", "freeslots", "free_slots",
              "freeminted", "freemint", "freesupply"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def shape_check(a):
    al = a.lower()
    if al in EXCLUDED or al == REGISTRY:
        return {"status": "excluded-or-registry"}
    abi_j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 8)
    abi = None
    if isinstance(abi_j, dict):
        abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
    if not abi:
        return {"status": "shape-check-failed", "note": "ABI unfetchable"}
    names = set()
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") in ("function", None):
            names.add((fn.get("name") or "").lower())
    has_mint = any("mint" in n for n in names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice", "getprice")) for n in names)
    free_views = sorted(n for n in names if n in FREE_VIEWS or "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) or n in
                ("agentregistry", "agentgate", "agent_id_registry", "registry") for n in names)
    src = json.dumps(abi).lower()
    agent = agent or ("agent_id_registry" in src) or ("agentgate" in src) or (REGISTRY[2:].lower() in src)
    is_token = all(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    has_mintfree = "mintfree" in names
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = is_token and has_mintfree and bool(free_views) and agent
    return {"status": "checked", "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_views, "agent": agent, "n_fns": len(names)}

new = [a for a in feed_addrs if a.lower() not in seen_lc]
out["leg1_new"] = new
shape = {}
for a in new:
    shape[a] = shape_check(a)
    time.sleep(0.15)
out["leg1_shape"] = shape
out["leg1_s1_pass"] = [a for a, s in shape.items() if s.get("S1")]
out["leg1_s2_pass"] = [a for a, s in shape.items() if s.get("S2")]

# retry 5 most-recent shape-check-failed
RETRY = ["0xffb755653b9638beeb23d8a451b9ddcf003b7777",
         "0x0EafFB8F2A3aAFBB7Fb60e5Fa902286E09Ca0f01",
         "0x83aC0c3E0cdFBcdEAA58278FAc504B1fbF2Ff08F"]
retry = {}
for a in RETRY:
    retry[a] = shape_check(a)
    time.sleep(0.15)
out["leg1_retry"] = retry
for a, s in retry.items():
    key = seen_lc.get(a.lower(), a)
    seen[key] = {"first_seen_wib": seen.get(key, {}).get("first_seen_wib", now_wib) if isinstance(seen.get(key), dict) else now_wib,
                 "source": "sourcify-feed-retry",
                 "status": s.get("status", "checked"),
                 "note": f"retry run 2319: S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
for a in new:
    key = seen_lc.get(a.lower())
    if key is None:
        s = shape.get(a, {})
        seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
                   "status": s.get("status", "checked"),
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
        seen_lc[a.lower()] = a
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_count"] = len(seen)
out["legs12_elapsed_s"] = round(time.time() - T0, 1)

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = curl(url, 12)
    open(BASE + f"hot-leg-{TAG}-boltbook-{lang}.html", "wb").write(raw)
    return raw.decode(errors="replace")

addrs = set()
kw = {}
for lang in ("en", "zh"):
    html = boltbook(lang)
    found = set(re.findall(r"0x[a-fA-F0-9]{40}", html))
    addrs |= found
    kw[lang] = {"bytes": len(html),
                "free-share": html.lower().count("free share"),
                "first-share-free": html.lower().count("first share free"),
                "free-mint-share": html.lower().count("free mint share"),
                "free-mint": html.lower().count("free mint"),
                "zh-free-share": html.count("免费份额"),
                "zh-first-free": html.count("首个免费"),
                "zh-free-mint": html.count("免费铸造") + html.count("免费mint")}
    time.sleep(0.3)
bb_new = sorted(a for a in addrs if a.lower() not in seen_lc)
out["leg2_boltbook"] = {"unique_addrs": len(addrs), "new_vs_seen": bb_new, "keywords": kw}
for a in bb_new:
    if a.lower() not in seen_lc:
        seen[a] = {"first_seen_wib": now_wib, "source": "boltbook",
                   "status": "boltbook-mention-unchecked", "note": "Boltbook mention run 2244, shape-check pending"}
        seen_lc[a.lower()] = a
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_count_after_bb"] = len(seen)

# ---- Leg 4: prio re-read, 5-call batches ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
U = enc_addr(USER)

CALLS = [
 ("Stampooor.freeMinted", "0x467696af8c2206B977B24081445104632dc1D459", "freeMinted()", ""),
 ("Stampooor.freeAvailable", "0x467696af8c2206B977B24081445104632dc1D459", "freeAvailable(address)", U),
 ("Stampooor.balanceOf", "0x467696af8c2206B977B24081445104632dc1D459", "balanceOf(address)", U),
 ("AgentPals.freeMinted", "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", "freeMinted()", ""),
 ("MECHA.totalMinted", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "totalMinted()", ""),
 ("MECHA.freeClaimed", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "freeClaimed()", ""),
 ("MECHA.freeAvailable", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "freeAvailable(address)", U),
 ("MECHA.balanceOf", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "balanceOf(address)", U),
 ("BUCKET.totalSupply", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "totalSupply()", ""),
 ("BUCKET.totalFreeCount", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "totalFreeCount()", ""),
 ("BUCKET.freeAvailable", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "freeAvailable(address)", U),
 ("BUCKET.balanceOf", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "balanceOf(address)", U),
 ("MOONDRILL.totalSupply", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "totalSupply()", ""),
 ("MOONDRILL.firstFreeUsed", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "firstFreeUsed()", ""),
 ("MOONDRILL.freeMinted", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "freeMinted()", ""),
 ("MOONDRILL.balanceOf", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "balanceOf(address)", U),
 ("0x2e50.totalSupply", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "totalSupply()", ""),
 ("0x2e50.firstFreeUsed", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "firstFreeUsed()", ""),
 ("0x2e50.freeMinted", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "freeMinted()", ""),
 ("0x2e50.balanceOf", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "balanceOf(address)", U),
 ("CRTSAINTS.totalSupply", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "totalSupply()", ""),
 ("CRTSAINTS.firstFreeUsed", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "firstFreeUsed()", ""),
 ("CRTSAINTS.freeMinted", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "freeMinted()", ""),
 ("CRTSAINTS.balanceOf", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "balanceOf(address)", U),
 ("WFPASS.mintOpen", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", "mintOpen()", ""),
 ("WFPASS.freeMinted", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", "freeMinted()", ""),
 ("WFPASS.totalMinted", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", "totalMinted()", ""),
 ("ORIGAMIX.totalSupply", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "totalSupply()", ""),
 ("ORIGAMIX.firstFreeUsed", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "firstFreeUsed()", ""),
 ("ORIGAMIX.freeMinted", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "freeMinted()", ""),
 ("ORIGAMIX.balanceOf", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "balanceOf(address)", U),
 ("AGCR.freeMinted", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "freeMinted()", ""),
 ("AGCR.FREE_SUPPLY", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "FREE_SUPPLY()", ""),
 ("AGCR.balanceOf", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "balanceOf(address)", U),
 ("BINANCEAI.launched", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "launched()", ""),
 ("BINANCEAI.claimable", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "claimable(address)", U),
 ("S1-0x6C50.mintStart", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "mintStart()", ""),
 ("S1-0x6C50.totalMinted", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "totalMinted()", ""),
 ("S1-0x6C50.freeMinted", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "freeMinted()", ""),
 ("S1-0x6C50.freeAvailable", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "freeAvailable(address)", U),
 ("NAOMI.freeMinted", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9", "freeMinted()", ""),
 ("NAOMI.totalMinted", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9", "totalMinted()", ""),
 ("NAOMI.freeAvailable", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9", "freeAvailable(address)", U),
 ("NAOMI.balanceOf", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9", "balanceOf(address)", U),
 ("RIGFORGE.freeSharesLeft", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "freeSharesLeft()", ""),
 ("RIGFORGE.openedAt", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "openedAt()", ""),
 ("RIGFORGE.freeClaimed", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "freeClaimed()", ""),
]

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/",
       "https://bsc.nodereal.io/")
block = None
for ep in EPS:
    try:
        r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                            "-d", json.dumps({"jsonrpc": "2.0", "id": 0, "method": "eth_blockNumber", "params": []}), ep],
                           capture_output=True, timeout=15)
        j = json.loads(r.stdout.decode(errors="replace"))
        if j.get("result"):
            block = int(j["result"], 16)
            out["block"] = block
            out["block_endpoint"] = ep
            break
    except Exception:
        continue

results = {}
notes = []
CHUNK = 5
for ci in range(0, len(CALLS), CHUNK):
    chunk = CALLS[ci:ci + CHUNK]
    batch = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
              "params": [{"to": addr, "data": sel(sig) + args}, "latest"]}
             for i, (key, addr, sig, args) in enumerate(chunk)]
    done = False
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", "20", "-H", "Content-Type: application/json",
                                "-d", json.dumps(batch), ep],
                               capture_output=True, timeout=25)
            arr = json.loads(r.stdout.decode(errors="replace"))
            if isinstance(arr, list) and arr and all("result" in it or "error" in it for it in arr):
                for item in arr:
                    i = item.get("id")
                    if i is None or i >= len(chunk):
                        continue
                    key = chunk[i][0]
                    if "error" in item:
                        results[key] = {"error": str(item["error"])[:80]}
                    else:
                        res = item.get("result")
                        if res in (None, "0x"):
                            results[key] = {"error": "empty-return"}
                        elif len(res) >= 66:
                            try:
                                results[key] = int(res[2:66], 16)
                            except Exception:
                                results[key] = res
                        else:
                            results[key] = res
                done = True
                break
        except Exception:
            continue
    if not done:
        for key, _, _, _ in chunk:
            results[key] = {"error": "all-endpoints-failed"}
        notes.append(f"chunk@{ci} failed all endpoints")
    time.sleep(0.4)

out["leg4_reread"] = {"n_calls": len(CALLS),
                      "n_ok": sum(1 for v in results.values() if not isinstance(v, dict)),
                      "n_error": sum(1 for v in results.values() if isinstance(v, dict)),
                      "notes": notes, "results": results}

# ---- Bridge (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
    not_in = [a for a in contracts if a.lower() not in snap_addrs]
    disc = [a for a, v in contracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": len(not_in),
                     "same_owner_discarded": len(disc), "not_in_list": not_in}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
