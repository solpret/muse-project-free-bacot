"""Salvage for hot-leg 2026-11-13 09:49 WIB: legs 3+4 returned views NULL for ALL 20
targets (leg34_ok=0) - total RPC batch failure in the main run, NOT on-chain state.
Likely cause: 10-worker parallel race overloaded flaky egress (single OBFG quote call
in the same run DID succeed). This salvage re-reads SEQUENTIALLY, one small chunk per
contract, max 2 attempts each, total budget ~90s. If it fails again: stop, record, retry
next run. Updates hot-leg-run-2026-11-13-0939.json with salvage results + seen notes.
"""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-13-0949"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "hot-leg 0949 salvage (sequential re-read)", "started_wib": now_wib}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)

def batch_sequential(addr, views):
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
    for ep in EPS:
        try:
            res = post_one(ep, calls, timeout=12)
            if isinstance(res, list) and len(res) == len(calls):
                return {key: (None if (isinstance(it, dict) and "error" in it)
                              else (to_int(it.get("result")) if isinstance(it, dict) else None))
                        for it, key in zip(res, keys)}
        except Exception:
            continue
    return None

TARGETS = [
    ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
     ["totalMinted()", "freeMinted()", "FREE_SUPPLY()", "saleStart()", "saleOpen()",
      "freeAvailable(address)", "totalSupply()"]),
    ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
     ["freeClaimed()", "freeLeft()", "FREE_LOTS_CAP()", "totalMinted()", "paidMinted()",
      "mintStart()", "opened()", "freeSharesRemaining()"]),
    ("Agentx", "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
     ["freeMinted()", "FREE_CAP()", "mintOpen()", "freeClaimed(address)",
      "balanceOf(address)", "totalMinted()", "mintOpensAt()"]),
    ("BC1B", "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
     ["freeCount()", "FREE_CAP()", "totalSupply()", "saleStart()", "refundOpen()",
      "freeMinted(address)", "balanceOf(address)"]),
    ("NOTV", "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
     ["totalMinted()", "FREE_SHARES()", "freeStart()", "mintOpen()", "freeClaimed(address)",
      "balanceOf(address)"]),
]
reads = {}
for name, addr, views in TARGETS:
    if time.time() > T0 + 85:
        reads[name] = {"address": addr, "error": "deadline-skipped"}; continue
    r = None
    for _a in range(2):
        r = batch_sequential(addr, views)
        if r is not None and any(v is not None for v in r.values()):
            break
        time.sleep(2)
    e = {"address": addr, "views": r}
    if r: e["summary"] = {k: v for k, v in r.items() if v is not None}
    reads[name] = e
    time.sleep(1)
out["reads"] = reads
out["ok"] = sum(1 for e in reads.values()
                if e.get("views") and any(v is not None for v in e["views"].values()))
def pct(n, d):
    return round(100 * n / d, 1) if n is not None and d else None
ob = reads.get("OBFG", {}).get("summary") or {}
jn = reads.get("JNTM", {}).get("summary") or {}
ax = reads.get("Agentx", {}).get("summary") or {}
bc = reads.get("BC1B", {}).get("summary") or {}
out["pct"] = {"OBFG_free": pct(ob.get("freeMinted"), ob.get("FREE_SUPPLY")),
              "JNTM_free": pct(jn.get("freeClaimed"), jn.get("FREE_LOTS_CAP")),
              "Agentx_free": pct(ax.get("freeMinted"), ax.get("FREE_CAP")),
              "BC1B_free": pct(bc.get("freeCount"), bc.get("FREE_CAP"))}

# compare vs baselines 09:31 main + 09:39 salvage
changes = []
try:
    base = {}
    d = json.load(open(BASE + "run-2026-11-13-0931-verify.json"))
    for _n, _e in (d.get("reads") or {}).items():
        _v = _e.get("views") or {}
        base[_n] = {k: v for k, v in _v.items() if isinstance(v, (int, float))}
    lite = json.load(open(BASE + "hot-leg-2026-11-13-0924-leg4lite.json"))
    if lite.get("agentx"):
        base["Agentx"] = {k: v for k, v in lite["agentx"].items() if isinstance(v, (int, float))}
    if lite.get("resume"):
        base["BC1B"] = {k: v for k, v in lite["resume"].items() if isinstance(v, (int, float))}
    if lite.get("jntm_views"):
        base["JNTM"] = {k: v for k, v in lite["jntm_views"].items() if isinstance(v, (int, float))}
    try:
        salv = json.load(open(BASE + "hot-leg-run-2026-11-13-0939.json"))
        for _n, _e in (salv.get("salvage", {}).get("reads") or {}).items():
            _v = _e.get("views") or {}
            base[_n] = {k: v for k, v in _v.items() if isinstance(v, (int, float))}
    except Exception:
        pass
    KEY = {"freeMinted", "freeClaimed", "totalMinted", "mintOpen", "freeClaimed_user",
           "balanceOf_user", "launched", "finalized", "refunding", "FREE_CAP", "FREE_SUPPLY",
           "freeCount", "freeLeft"}
    for name, e in reads.items():
        v = e.get("views") or {}
        pv = base.get(name, {})
        for k, val in v.items():
            if val is None: continue
            if k in pv and pv[k] is not None and pv[k] != val:
                changes.append(f"{name}.{k}: {pv[k]} -> {val}")
            elif (k not in pv or pv.get(k) is None) and k in KEY:
                changes.append(f"{name}.{k}: (new read) {val}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["changes_vs_0931_0939salvage"] = changes

# merge into main run file + seen notes
run = json.load(open(BASE + f"hot-leg-run-{TAG}.json"))
run["salvage"] = out
json.dump(run, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
seen = json.load(open(BASE + "hot-leg-seen.json"))
for nm, ad in (("OBFG", TARGETS[0][1]), ("JNTM", TARGETS[1][1]), ("Agentx", TARGETS[2][1]),
               ("BC1B", TARGETS[3][1]), ("NOTV", TARGETS[4][1])):
    e = reads.get(nm, {})
    ssum = e.get("summary") or {}
    if isinstance(seen.get(ad), dict):
        _old = seen[ad].get("note", "")
        _old = _old[-400:] if len(_old) > 400 else _old
        if ssum:
            seen[ad]["note"] = (_old + f" | SALVAGE-0949 {now_wib}: " +
                                ", ".join(f"{k}={v}" for k, v in ssum.items())[:300]).strip()[:900]
        else:
            seen[ad]["note"] = (_old + f" | SALVAGE-0949 {now_wib}: views STILL null (RPC batch failure persists, not on-chain state) - retry next run.").strip()[:900]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-salvage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
