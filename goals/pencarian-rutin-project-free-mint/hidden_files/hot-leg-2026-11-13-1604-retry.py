#!/usr/bin/env python3
"""Hot-leg 1604 retry: re-read chunk-1 failures (OBFG/Mossbound/Ochre/JNTM head).
bsc-dataseed single chunk of 24 calls."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
PLAN = [
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("freeAvailable", True)]),
 ("Mossbound", "0xe589A94316C68d4A4f008f841Deb7e9612445244",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("saleStart", False), ("isFreeOpen", False), ("freeRemaining", False), ("freeAvailable", True)]),
 ("Ochre", "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("isFreeOpen", False), ("saleStart", False), ("totalSupply", False),
   ("freeClaimed", True), ("freeAvailable", True)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("freeClaimed", False), ("FREE_LOTS_CAP", False), ("opened", False)]),
]
calls, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
body = subprocess.run(["curl", "-sS", "-m", "30", "-H", "Content-Type: application/json",
                       "-d", json.dumps(calls), "https://bsc-dataseed.binance.org/"],
                      capture_output=True, text=True, timeout=40).stdout
reads = {}
try:
    resp = json.loads(body)
    items = resp if isinstance(resp, list) else [resp]
    by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
    for cid, (name, fn) in enumerate(keys):
        it = by_id.get(cid, {})
        r = it.get("result")
        v = None
        if r and r != "0x" and len(r) >= 66:
            try: v = int(r[-64:], 16)
            except Exception: v = None
        reads.setdefault(name, {})[fn] = {"v": v, "err": it.get("error")}
except Exception as e:
    reads = {"parse_error": str(e), "raw_head": body[:300]}
out = {"run": "hot-leg 1604 retry (chunk-1)", "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600)), "reads": reads}
flags = {}
ob = {k: v["v"] for k, v in reads.get("OBFG", {}).items()} if isinstance(reads.get("OBFG"), dict) else {}
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    flags["OBFG_pct"] = round(ob["freeMinted"]/ob["FREE_SUPPLY"]*100, 1)
    flags["OBFG_soldout"] = bool(ob["freeMinted"] >= ob["FREE_SUPPLY"])
    flags["OBFG_slot_lost"] = bool(ob.get("freeAvailable_user") == 0)
mb = {k: v["v"] for k, v in reads.get("Mossbound", {}).items()} if isinstance(reads.get("Mossbound"), dict) else {}
if mb.get("freeMinted") is not None and mb.get("FREE_SUPPLY"):
    flags["Mossbound_pct"] = round(mb["freeMinted"]/mb["FREE_SUPPLY"]*100, 1)
    flags["Mossbound_soldout"] = bool(mb["freeMinted"] >= mb["FREE_SUPPLY"])
    flags["Mossbound_freeRemaining"] = mb.get("freeRemaining")
oc = {k: v["v"] for k, v in reads.get("Ochre", {}).items()} if isinstance(reads.get("Ochre"), dict) else {}
if oc.get("freeMinted") is not None and oc.get("FREE_SUPPLY"):
    flags["Ochre_pct"] = round(oc["freeMinted"]/oc["FREE_SUPPLY"]*100, 1)
    flags["Ochre_soldout"] = bool(oc["freeMinted"] >= oc["FREE_SUPPLY"])
jn = {k: v["v"] for k, v in reads.get("JNTM", {}).items()} if isinstance(reads.get("JNTM"), dict) else {}
if jn.get("freeClaimed") is not None:
    flags["JNTM_freeClaimed"] = jn["freeClaimed"]
    flags["JNTM_soldout"] = bool(jn.get("FREE_LOTS_CAP") and jn["freeClaimed"] >= jn["FREE_LOTS_CAP"])
out["flags"] = flags
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1604-retry.json", "w"), indent=1)
print(json.dumps(out, indent=1))
