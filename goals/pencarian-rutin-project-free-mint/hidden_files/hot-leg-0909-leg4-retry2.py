#!/usr/bin/env python3
"""Hot-leg 0909 leg4 retry #2: nodereal-only re-read of the still-null fields
of the 0909 reread. publicnode rate-limited (-32005) during retry #1 and the
error-list counted as 'got a list', so nodereal was never tried; dataseed
returned empty bodies. Merge results into the 0909 reread + run JSON.
Read-only on-chain. No preview/mint/claim."""
import json, subprocess, sys, time
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB).isoformat(timespec="seconds")
PEPE_ADDR = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
BSCCAT_ADDR = "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A"

def curl_post(url, payload, timeout=25):
    r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", UA, "-H",
                        "Content-Type: application/json", "-X", "POST", url,
                        "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def sig_for(label):
    if label.endswith("_user_1"):
        return label[:-7] + "(address,uint256)", "user1"
    if label.endswith("_user"):
        return label[:-5] + "(address)", "user"
    if label.endswith("_1"):
        return label[:-2] + "(uint256)", "one"
    return label + "()", None

def encode(label):
    sig, arg = sig_for(label)
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def decode(h):
    if not h or not isinstance(h, str) or len(h) < 3:
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

reread = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0909-reread.json"))
plan = []
for name, item in reread["reads"].items():
    for field, val in item["views"].items():
        if val is None:
            plan.append(("reads", name, item["address"], field))
for field, val in reread["bsccat"]["views"].items():
    if val is None:
        plan.append(("bsccat", "bsccat", BSCCAT_ADDR, field))
for field, val in reread["pepe"].items():
    if val is None:
        plan.append(("pepe", "pepe", PEPE_ADDR, field))
print(f"retry2 targets: {len(plan)} null fields")
by_contract = {}
for sec, name, addr, field in plan:
    by_contract.setdefault((sec, name, addr), []).append(field)
contracts = list(by_contract.items())
results = {}
chunk_errors = []
for ci in range(0, len(contracts), 4):
    chunk = contracts[ci:ci+4]
    batch, keys = [], []
    for (sec, name, addr), fields in chunk:
        for field in fields:
            batch.append({"jsonrpc": "2.0", "method": "eth_call",
                          "params": [{"to": addr, "data": encode(field)}, "latest"],
                          "id": len(batch)})
            keys.append((sec, name, field))
    try:
        got = json.loads(curl_post(EP, batch))
    except Exception as e:
        chunk_errors.append(f"chunk@{ci} err:{type(e).__name__}")
        got = None
    if not isinstance(got, list):
        chunk_errors.append(f"chunk@{ci} non-list response")
        for k in keys:
            results[k] = None
        continue
    by_id = {r.get("id"): r for r in got if isinstance(r, dict)}
    for i, k in enumerate(keys):
        r = by_id.get(i, {})
        results[k] = decode(r.get("result")) if not r.get("error") else None

fixed = 0
for (sec, name, field), val in results.items():
    if sec == "reads":
        reread["reads"][name]["views"][field] = val
    elif sec == "bsccat":
        reread["bsccat"]["views"][field] = val
    else:
        reread["pepe"][field] = val
    if val is not None:
        fixed += 1
reread["retry2"] = {"started_wib": NOW, "endpoint": EP, "fixed": fixed,
                    "targets": len(plan), "chunk_errors": chunk_errors,
                    "elapsed_s": round(time.time() - T0, 1)}
reread["reads_ok"] = sum(1 for it in reread["reads"].values() for v in it["views"].values() if v is not None) \
    + sum(1 for v in reread["bsccat"]["views"].values() if v is not None) \
    + sum(1 for v in reread["pepe"].values() if v is not None)
json.dump(reread, open(f"{HF}/hot-leg-run-2026-11-19-0909-reread.json", "w"), indent=1)

prev = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0854-reread.json"))
cur = reread
changes = []
for name, pv in prev["reads"].items():
    cv = cur["reads"].get(name, {}).get("views", {})
    diff = {}
    for label, pval in pv["views"].items():
        nval = cv.get(label)
        if pval != nval:
            diff[label] = {"prev": pval, "now": nval}
    if diff:
        changes.append({"item": name, "type": "value-change", "diff": diff})
bdiff = {}
for label, pval in prev["bsccat"]["views"].items():
    nval = cur["bsccat"]["views"].get(label)
    if pval != nval:
        bdiff[label] = {"prev": pval, "now": nval}
pdiff = {}
for label, pval in prev["pepe"].items():
    nval = cur["pepe"].get(label)
    if pval != nval:
        pdiff[label] = {"prev": pval, "now": nval}
run = json.load(open(f"{HF}/hot-leg-2026-11-19-0909.json"))
run["leg4_retry2"] = {"endpoint": EP, "fixed": fixed, "targets": len(plan),
                      "chunk_errors": chunk_errors, "reads_ok_after": reread["reads_ok"]}
run["leg4_changes_vs_0854"] = changes
run["bsccat_changes_vs_0854"] = bdiff
run["pepe_changes_vs_0854"] = pdiff
def rd(name):
    return cur["reads"].get(name, {}).get("views", {})
sa, lh, al, pc = rd("STOCKAGENT"), rd("Lumenhold"), rd("ALIEN"), rd("PunchCard")
ag, mx = rd("AGCLUB"), rd("Matrix")
run["threshold_check"] = {
    "STOCKAGENT_free_pct": round(100*(1111-sa["freeLeft"])/1111, 1) if isinstance(sa.get("freeLeft"), int) else None,
    "STOCKAGENT": {k: sa.get(k) for k in ("totalSupply","freeLeft","FREE_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user")},
    "Lumenhold_free_pct": round(100*lh["freeClaimed"]/1500, 1) if isinstance(lh.get("freeClaimed"), int) else None,
    "Lumenhold": {k: lh.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","mintOpen","balanceOf_user","mintedBy_user")},
    "ALIEN_free_pct": round(100*al["totalSupply"]/1000, 1) if isinstance(al.get("totalSupply"), int) else None,
    "ALIEN": {k: al.get(k) for k in ("totalSupply","FREE_SUPPLY","mintOpen","isFreePhase","balanceOf_user")},
    "PunchCard_free_pct": round(100*pc["freeMinted"]/5555, 1) if isinstance(pc.get("freeMinted"), int) else None,
    "PunchCard": {k: pc.get(k) for k in ("totalSupply","freeMinted","totalMinted","mintOpen","mintPriceFor_user_1","mintedCount_user","balanceOf_user")},
    "AGCLUB_free_pct": round(100*ag["freeMinted"]/888, 1) if isinstance(ag.get("freeMinted"), int) else None,
    "Matrix_free_pct": round(100*mx["freeMinted"]/1000, 1) if isinstance(mx.get("freeMinted"), int) else None,
    "AgentBubble": {k: rd("AgentBubble").get(k) for k in ("totalMinted","totalSupply","MAX_SUPPLY","freeMinted","mintOpen","balanceOf_user")},
    "AgentEcho": {k: rd("AgentEcho").get(k) for k in ("totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user")},
    "binanceai_pending": {k: rd("binanceai-mint").get(k) for k in ("launched","failed","isRefundPhase","totalShares","tokenClaimed_user")},
    "notes": "Strong-lead bar >70% + age <24h + slot open + verified website. STOCKAGENT + Lumenhold: age + website still UNVERIFIED per snapshot (early-lead-reported-2026-11-18-0031 / watchlist-only-age-unverified-2026-11-17) -> no promotion regardless of %. AgentBubble: age-excluded 2026-11-18 -> no promotion.",
}
run["boltbook_en_note"] = "EN fetch 0 bytes twice (initial + retry): boltbook.fun/ 302 -> /?lang=en (Cloudflare). ZH /?lang=zh OK (200, 42992 bytes, 7 addresses, 0 new). Future runs: fetch EN via /?lang=en or curl -L."
json.dump(run, open(f"{HF}/hot-leg-2026-11-19-0909.json", "w"), indent=1)
print(json.dumps({"fixed": fixed, "targets": len(plan), "chunk_errors": chunk_errors,
                  "reads_ok": reread["reads_ok"], "n_changes": len(changes),
                  "threshold": run["threshold_check"]}, indent=1, default=str))
print("CHANGES:", json.dumps(changes, indent=1))
print("BSCCAT:", json.dumps(bdiff))
print("PEPE:", json.dumps(pdiff))
