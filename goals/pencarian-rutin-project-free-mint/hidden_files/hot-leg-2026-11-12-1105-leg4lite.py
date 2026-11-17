#!/usr/bin/env python3
"""Hot-leg 1105 leg4-lite: bounded re-read of 6 highest-signal targets after the
main 1105 script was killed by the 280s timeout (legs 1+retry done, leg4 not run).
Single eth_calls, 6s each, total deadline 75s. Read-only except own output file."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1105"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
DEADLINE = T0 + 75
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def call(addr, sig, timeout=6):
    data = sel(sig) + (enc(USER) if "(address)" in sig else "")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": addr, "data": data}, "latest"]}
    for ep in EPS:
        if time.time() > DEADLINE: return None
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=timeout + 3)
            j = json.loads(r.stdout)
            res = j.get("result")
            if res is None: continue
            return int(res, 16) if res != "0x" else 0
        except Exception:
            continue
    return None
TARGETS = {
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459",
               ["freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "freeUsed(address)",
                "freeAvailable(address)", "balanceOf(address)", "freeLeft()"]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
              ["freeClaimed()", "totalFreeMinted()", "FREE_SHARES()", "openedAt()",
               "freeSharesLeft()", "currentState()", "finalized()", "refunding()"]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
           ["totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
            "freeAvailable(address)", "freeLeft()"]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                    ["launched()", "totalMinted()", "freeClaimed()", "freeMinted()"]),
 "AGCR": ("0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
          ["totalMinted()", "freeClaimed()", "freeMinted()"]),
 "0x016b9CE7": ("0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7",
               ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
                "freeLeft()", "freeAvailable(address)", "mintStart()"]),
}
out = {"run": "free-mint-hot-leg 2026-11-12 11:05 WIB leg4-lite", "started_wib": now_wib, "reads": {}}
for name, (addr, views) in TARGETS.items():
    if time.time() > DEADLINE:
        out["reads"][name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    vals = {}
    for sig in views:
        v = call(addr, sig)
        vals[sig.split("(")[0] + ("_user" if "(address)" in sig else "")] = v
        if time.time() > DEADLINE: break
    out["reads"][name] = {"address": addr, "views": vals}
# compare vs 1034 verify2
try:
    prev = json.load(open(BASE + "run-2026-11-12-1034-verify2.json"))["reads"]
    ch = []
    for name, e in out["reads"].items():
        if "views" not in e: continue
        pv = (prev.get(name, {}) or {}).get("views") or {}
        for k, v in e["views"].items():
            if v is None: continue
            if k in pv and pv[k] is not None and pv[k] != v:
                ch.append(f"{name}.{k}: {pv[k]} -> {v}")
            elif k not in pv or pv.get(k) is None:
                ch.append(f"{name}.{k}: (new read) {v}")
    out["changes_vs_1034"] = ch
except Exception as ex:
    out["changes_vs_1034"] = [f"compare-error: {ex}"]
# Stampooor site
try:
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "10", "-w", "%{http_code} %{size_download}",
                        "https://stampooor.com/"], capture_output=True, timeout=15)
    out["stampooor_site"] = r.stdout.decode(errors="replace").strip()
except Exception as e:
    out["stampooor_site"] = f"error {e}"
# Bridge read-only
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
    out["bridge"] = {"total": len(contracts),
                     "not_in_snapshot": [a for a in contracts if a.lower() not in snap_addrs],
                     "same_owner_discarded": [a for a, v in contracts.items()
                                              if isinstance(v, dict) and v.get("same_owner_discarded")]}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"run-{TAG}-leg4lite.json", "w"), indent=1)
print(json.dumps(out, indent=1))
