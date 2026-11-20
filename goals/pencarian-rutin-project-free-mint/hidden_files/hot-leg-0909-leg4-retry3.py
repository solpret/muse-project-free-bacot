#!/usr/bin/env python3
"""Hot-leg 0909 leg4 retry #3 (micro): single small nodereal batch for the
threshold-critical fields only (STOCKAGENT + PunchCard supply/free views).
Merge into the 0909 reread + run JSON. Read-only."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    return keccak(s.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

calls, keys = [], []

def add(name, addr, fn, arg=None):
    data = "0x" + sel(fn)
    suffix = ""
    if arg == "user":
        data += enc_addr(USER)
        suffix = "_user"
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
        suffix = "_user_1"
    calls.append({"jsonrpc": "2.0", "method": "eth_call",
                  "params": [{"to": addr, "data": data}, "latest"], "id": len(calls)})
    keys.append((name, fn.split("(")[0] + suffix))

SA = "0xba7068233da805bdebcc167be361c219002e6b7f"
PC = "0x5877d2bb9f226cc3e438f4d656caeb27deafc576"
for fn in ["totalSupply()", "freeLeft()", "FREE_SUPPLY()", "MAX_SUPPLY()"]:
    add("STOCKAGENT", SA, fn)
add("STOCKAGENT", SA, "quote(address,uint256)", "user1")
add("STOCKAGENT", SA, "freeMintedByWallet(address)", "user")
for fn in ["totalSupply()", "totalMinted()", "freeMinted()", "paidMinted()", "MAX_SUPPLY()"]:
    add("PunchCard", PC, fn)

r = subprocess.run(["curl", "-s", "-m", "25", "-A", "Mozilla/5.0",
                    "-H", "Content-Type: application/json", "-X", "POST",
                    "https://bsc.nodereal.io/", "-d", json.dumps(calls)],
                   capture_output=True, text=True)
resp = json.loads(r.stdout)
vals = {}
for it in resp:
    k = keys[it["id"]]
    vals[k] = int(it["result"], 16) if isinstance(it, dict) and "result" in it and it["result"] not in (None, "0x") else None
print(json.dumps({f"{a}:{b}": v for (a, b), v in vals.items()}, indent=1))

rr = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0909-reread.json"))
fixed = 0
for (name, field), v in vals.items():
    if v is not None:
        rr["reads"][name]["views"][field] = v
        fixed += 1
rr["retry3"] = {"endpoint": "nodereal", "fields": len(vals), "fixed": fixed}
rr["reads_ok"] = (sum(1 for it in rr["reads"].values() for v in it["views"].values() if v is not None)
                  + sum(1 for v in rr["bsccat"]["views"].values() if v is not None)
                  + sum(1 for v in rr["pepe"].values() if v is not None))
json.dump(rr, open(f"{HF}/hot-leg-run-2026-11-19-0909-reread.json", "w"), indent=1)

run = json.load(open(f"{HF}/hot-leg-2026-11-19-0909.json"))
sa = rr["reads"]["STOCKAGENT"]["views"]
pc = rr["reads"]["PunchCard"]["views"]
run["threshold_check"]["STOCKAGENT_free_pct"] = round(100 * (1111 - sa["freeLeft"]) / 1111, 1) if isinstance(sa.get("freeLeft"), int) else None
run["threshold_check"]["STOCKAGENT"] = {k: sa.get(k) for k in ("totalSupply", "freeLeft", "FREE_SUPPLY", "mintOpen", "quote_user_1", "freeMintedByWallet_user", "balanceOf_user")}
run["threshold_check"]["PunchCard_free_pct"] = round(100 * pc["freeMinted"] / 5555, 1) if isinstance(pc.get("freeMinted"), int) else None
run["threshold_check"]["PunchCard"] = {k: pc.get(k) for k in ("totalSupply", "freeMinted", "totalMinted", "mintOpen", "mintPriceFor_user_1", "mintedCount_user", "balanceOf_user")}
run["leg4_retry3"] = {"endpoint": "nodereal", "fixed": fixed, "fields": len(vals)}
prev = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0854-reread.json"))
changes = []
for name, pv in prev["reads"].items():
    cv = rr["reads"].get(name, {}).get("views", {})
    diff = {}
    for label, pval in pv["views"].items():
        nval = cv.get(label)
        if pval != nval:
            diff[label] = {"prev": pval, "now": nval}
    if diff:
        changes.append({"item": name, "type": "value-change", "diff": diff})
run["leg4_changes_vs_0854"] = changes
json.dump(run, open(f"{HF}/hot-leg-2026-11-19-0909.json", "w"), indent=1)
print("reads_ok now:", rr["reads_ok"])
print("STOCKAGENT pct:", run["threshold_check"]["STOCKAGENT_free_pct"],
      "PunchCard pct:", run["threshold_check"]["PunchCard_free_pct"])
print("n_changes:", len(changes))
print("CHANGES:", json.dumps(changes, indent=1))
