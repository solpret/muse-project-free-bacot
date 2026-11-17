#!/usr/bin/env python3
"""Hot-leg 2026-11-12 18:39 WIB — focused follow-up after resume run was killed by timeout.
Runic Key (near-sellout 321/325) + Stampooor + THONK small raced batches (3 endpoints),
then Stampooor site check, bridge (read-only), compare, final run JSON + runlog.
Writes hot-leg-run-2026-11-12-1839.json (final) — does NOT touch main snapshot."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1839"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 18:39 WIB (focused follow-up)", "started_wib": now_wib}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def post_one(ep, payload, timeout=20):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def race(payload, timeout=20):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(post_one, ep, payload, timeout): ep for ep in EPS}
        for f in as_completed(futs):
            try:
                res = f.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
def get_block(timeout=10):
    try:
        r = race([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=timeout)
        if isinstance(r, list) and r:
            return int(r[0]["result"], 16)
    except Exception:
        pass
    return None
def read_views(addr, views, attempts=2, timeout=20):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for att in range(attempts):
        res = race(calls, timeout=timeout)
        if res is not None:
            views_d = {k: (None if (isinstance(it, dict) and "error" in it)
                           else (int(it["result"], 16) if isinstance(it, dict) and it.get("result") not in (None, "0x") else None))
                       for it, k in zip(res, keys)}
            return {"views": views_d, "summary": {k: v for k, v in views_d.items() if v is not None},
                    "attempt": att + 1}
    return {"views": None, "summary": None, "attempt": attempts}

SMALL = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "freeRemaining()", "mintOpen()", "isFreeOpen()", "saleStart()",
         "saleEnd()", "balanceOf(address)", "freeAvailable(address)", "freeMintedBy(address)",
         "freeLeft()"]

block = get_block()
out["block"] = block

RUNIC = "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
runic = read_views(RUNIC, SMALL, attempts=2)
runic["block"] = block
out["runic_retry"] = runic
json.dump(runic, open(BASE + f"hot-leg-{TAG}-runic-retry.json", "w"), indent=1)

STAMP = "0x467696af8c2206B977B24081445104632dc1D459"
stamp = read_views(STAMP, SMALL, attempts=2)
stamp["block"] = block
out["stampooor_retry"] = stamp
json.dump(stamp, open(BASE + f"hot-leg-{TAG}-stampooor-retry.json", "w"), indent=1)

THONK = "0x22e69F9a7BeC3D991C0ceB5a103E509319E42B2A"
thonk = read_views(THONK, SMALL, attempts=1)
thonk["block"] = block
out["thonk_retry"] = thonk

# ---- Stampooor site check ----
def curl(url, timeout=10):
    try:
        r = subprocess.run(["curl", "-sL", "-m", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""
def site_check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "8", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, timeout=12)
        return r.stdout.decode(errors="replace").strip()
    except Exception: return "000 0"
packs_raw = curl("https://stampooor.pages.dev/packs/", 10)
out["stampooor_site"] = {"root_com": site_check("https://stampooor.com/"),
                         "pages_dev_packs": site_check("https://stampooor.pages.dev/packs/"),
                         "packs_contract_prints": packs_raw.decode(errors="replace").lower().count(
                             "0x467696af8c2206b977b24081445104632dc1d459")}

# ---- Bridge (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict):
                a = v.get("address") or v.get("sale") or v.get("contract")
                if a: snap_addrs.add(str(a).lower())
    not_in = [a for a in contracts if a.lower() not in snap_addrs]
    disc = [a for a, v in contracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": not_in,
                     "same_owner_discarded": disc}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}

# ---- Compare focused reads vs baselines ----
changes = []
try:
    prev_runic = json.load(open(BASE + "hot-leg-2026-11-12-1834-runic-retry.json"))
    pv = prev_runic.get("views") or {}
    if runic.get("views"):
        for k, v in runic["views"].items():
            if v is None: continue
            if k in pv and pv[k] is not None and pv[k] != v:
                changes.append(f"RunicKey.{k}: {pv[k]} -> {v}")
    prev_stamp = None
    for f in ("hot-leg-run-2026-11-12-1834.json", "run-2026-11-12-1834-verify2.json",
              "hot-leg-run-2026-11-12-1814.json", "run-2026-11-12-1814-verify2.json"):
        try:
            d = json.load(open(BASE + f))
            r = (d.get("leg4_reads") or d.get("reads") or {}).get("Stampooor", {})
            if r.get("views"):
                prev_stamp = r["views"]; break
        except Exception:
            continue
    if prev_stamp and stamp.get("views"):
        for k, v in stamp["views"].items():
            if v is None: continue
            if k in prev_stamp and prev_stamp[k] is not None and prev_stamp[k] != v:
                changes.append(f"Stampooor.{k}: {prev_stamp[k]} -> {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["focused_changes"] = changes

# ---- Leg1+Leg2 summary (from checkpointed files) ----
try:
    feed = json.load(open(BASE + f"hot-leg-{TAG}-feed.json"))
    out["feed_summary"] = {"n": len(feed.get("addrs", [])),
                           "newest_verifiedAt": max(feed["meta"].values()) if feed.get("meta") else None,
                           "oldest_verifiedAt": min(feed["meta"].values()) if feed.get("meta") else None}
except Exception as e:
    out["feed_summary"] = {"error": str(e)[:100]}
out["boltbook_en_bytes"] = len(open(BASE + f"hot-leg-{TAG}-boltbook-en.html", "rb").read())
out["boltbook_zh_bytes"] = len(open(BASE + f"hot-leg-{TAG}-boltbook-zh.html", "rb").read())

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
