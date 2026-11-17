#!/usr/bin/env python3
"""Hot-leg 0059 salvage (2026-11-14): full run killed by 280s timeout (EXIT=124,
no output JSON). Lightweight salvage only: Sourcify feed + Boltbook EN/ZH
(short 10s timeouts) + ONE 24-call batch re-read of decision-relevant items.
Baselines: 0039 (Agentx 792/1111 71.3% gate-blocked/override declined/age-expired;
OBFG 721/1230 58.6% age-excluded; Zero 315/500 63.0%; 2e34 921/1000 92.1%;
NEW5893 90/480 18.8%; binanceai/NOTV/JNTM not opened). Read-only except run output."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=10):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-14 00:59 WIB SALVAGE", "started_wib": now_wib(),
       "note": "full 0059 run killed by 280s timeout (EXIT=124, no output); salvage = feed+boltbook+1 batch only"}

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

# Leg 1: Sourcify feed
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=10)
    parsed = json.loads(body) if body else {}
    feed = parsed.get("results", []) if isinstance(parsed, dict) else parsed
    out["feed"] = {"n": len(feed),
                   "newest_verifiedAt": feed[0].get("verifiedAt") if feed else None,
                   "oldest_verifiedAt": feed[-1].get("verifiedAt") if feed else None}
    out["feed_new"] = [i.get("address", "") for i in feed
                       if i.get("address", "").lower() not in seen_lower]
except Exception as e:
    out["feed"] = {"error": str(e)}
    out["feed_new"] = []

# Leg 2: Boltbook EN+ZH
bb = {}
for lang, url in (("en", "https://boltbook.fun/?lang=en"), ("zh", "https://boltbook.fun/?lang=zh")):
    body = curl(url, timeout=10)
    bb[lang] = ({"bytes": len(body),
                 "addrs": sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))} if body
                else {"error": "fetch-failed"})
out["boltbook"] = bb
out["boltbook_new"] = [a for lang in ("en", "zh") for a in bb.get(lang, {}).get("addrs", [])
                       if a.lower() not in seen_lower]

# One batch re-read (24 calls max): Agentx, OBFG, Zero, 2e34, NEW5893, VIOLET, binanceai, NOTV, JNTM
PLAN = [
 ("Agentx", "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
  [("freeMinted", False), ("FREE_CAP", False), ("freeClaimed", True)]),
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("freeAvailable", True)]),
 ("Zero", "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
  [("freeMinted", False), ("FREE_CAP", False), ("freeClaimed", True)]),
 ("2e34", "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",
  [("freeMinted", False), ("FREE_MAX", False)]),
 ("NEW5893", "0x5893199322A5300775912ebD236d8f1fEFC700Db",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False)]),
 ("VIOLET", "0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d",
  [("freeMinted", False), ("FREE_SUPPLY", False)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False)]),
 ("NOTV", "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
  [("totalMinted", False)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("opened", False), ("freeLeft", False)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
reads = {}
body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(reqs), timeout=15)
if not body:
    body = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(reqs), timeout=15)
if body:
    try:
        resp = json.loads(body)
        items = resp if isinstance(resp, list) else [resp]
        by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
        for cid, (name, fn) in enumerate(keys):
            r = by_id.get(cid, {}).get("result")
            v = None
            if r and r != "0x" and len(r) >= 66:
                try:
                    v = int(r[-64:], 16)
                except Exception:
                    v = None
            reads.setdefault(name, {})[fn] = v
    except Exception as e:
        out["reads_error"] = str(e)[:200]
else:
    out["reads_error"] = "both RPC endpoints failed"
out["reads"] = reads
out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))

flags = {}
ax = reads.get("Agentx", {})
if ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    flags["Agentx_pct"] = round(ax["freeMinted"] / ax["FREE_CAP"] * 100, 1)
    flags["Agentx_delta_vs_0039_792"] = ax["freeMinted"] - 792
    flags["Agentx_note"] = "gate website_failed; user declined override 13 Nov ~20:31; age deadline 23:11 WIB 13 Nov EXPIRED - NO re-check, NO report, NEVER preview/mint"
ob = reads.get("OBFG", {})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    flags["OBFG_pct"] = round(ob["freeMinted"] / ob["FREE_SUPPLY"] * 100, 1)
    flags["OBFG_delta_vs_0039_721"] = ob["freeMinted"] - 721
    flags["OBFG_soldout"] = bool(ob["freeMinted"] >= ob["FREE_SUPPLY"])
    flags["OBFG_slot_lost"] = bool(ob.get("freeAvailable_user") == 0)
ze = reads.get("Zero", {})
if ze.get("freeMinted") is not None and ze.get("FREE_CAP"):
    flags["Zero_pct"] = round(ze["freeMinted"] / ze["FREE_CAP"] * 100, 1)
    flags["Zero_delta_vs_0039_315"] = ze["freeMinted"] - 315
    flags["Zero_slot_open"] = bool(ze.get("freeClaimed_user") == 0)
te = reads.get("2e34", {})
if te.get("freeMinted") is not None and te.get("FREE_MAX"):
    flags["2e34_pct"] = round(te["freeMinted"] / te["FREE_MAX"] * 100, 1)
    flags["2e34_delta_vs_0039_921"] = te["freeMinted"] - 921
n5 = reads.get("NEW5893", {})
if n5.get("freeMinted") is not None and n5.get("FREE_SUPPLY"):
    flags["NEW5893_pct"] = round(n5["freeMinted"] / n5["FREE_SUPPLY"] * 100, 1)
    flags["NEW5893_opened"] = bool(n5.get("saleOpen") == 1 or n5.get("mintOpen") == 1)
vl = reads.get("VIOLET", {})
if vl.get("freeMinted") is not None and vl.get("FREE_SUPPLY"):
    flags["VIOLET_pct"] = round(vl["freeMinted"] / vl["FREE_SUPPLY"] * 100, 1)
flags["binanceai_opened"] = bool(reads.get("binanceai-mint", {}).get("launched") == 1)
flags["NOTV_opened"] = bool((reads.get("NOTV", {}).get("totalMinted") or 0) > 0)
flags["JNTM_opened"] = bool(reads.get("JNTM", {}).get("opened") == 1)
out["flags"] = flags
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0059-salvage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
