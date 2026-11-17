#!/usr/bin/env python3
"""One targeted retry of failed leg4 chunk 40 (calls 40-49) from run 17:04.
Patches run-hot-leg-2026-11-15-1704.json reads + diffs if it succeeds."""
import json, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
base = json.load(open(BASE + "run-hot-leg-2026-11-15-1659.json"))
base_reads = base["leg4"]["reads"]
NAMES11 = ["AGCLUB","Ledgera","RAVE","REOPIR","Matrix Agents","ORBIT",
           "BinanceAI-mint","RigForge","RaceAgents","Pengu","Zephyra"]
base11 = {n: base_reads[n] for n in NAMES11 if n in base_reads}
NOARG = {"totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP",
         "FREE_MAX","FREE_MINT_CAP","MAX_SUPPLY","maxSupply","mintOpen","launched","failed",
         "isRefundPhase","totalShares","remainingSupply","standardRemaining","legendaryRemaining",
         "paused","TOKEN_PRICE","claimOpen","mintStartTime","AGENT_ID","freeSharesLeft",
         "openedAt","freeBlock","mintOpenTimestamp","mintPaused","price","PRICE","mintPrice",
         "paidMinted","totalSpecimens","currentExperiment","genesisStart","genesisOpen",
         "mintsLeft","freeMintsLeft","freeRemaining","owner"}
ADDRARG = {"balanceOf","freeClaimedOf","freeUsed","mintedBy","mintedByWallet",
           "freeMintedPerWallet","mintedPerWallet","mintCountOf","mintsBy","holdsAgentId",
           "hasAgentId","isEligible","tokenClaimed","freeBooked","hasFreeClaimed"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
calls = []
for name, it in base11.items():
    for vn, bv in it["views"].items():
        if bv is None or vn.startswith("freeClaimedByAgent"): continue
        if vn == "priceFor_user_1":
            calls.append((name, vn, sel("priceFor(address,uint256)") + enc_addr(USER) + enc_u(1)))
        elif vn.endswith("_user"):
            fn = vn[:-5]
            if fn in ADDRARG or fn == "freeClaimed":
                calls.append((name, vn, sel(f"{fn}(address)") + enc_addr(USER)))
        elif vn in NOARG:
            calls.append((name, vn, sel(f"{vn}()")))
        elif vn in ADDRARG:
            calls.append((name, vn, sel(f"{vn}(address)") + enc_addr(USER)))
chunk = calls[40:50]
print("retrying chunk:", [(c[0], c[1]) for c in chunk])
payload = [{"jsonrpc":"2.0","id":i,"method":"eth_call",
            "params":[{"to": base11[c[0]]["address"], "data": c[2]}, "latest"]} for i,c in enumerate(chunk)]
payload.append({"jsonrpc":"2.0","id":len(chunk),"method":"eth_blockNumber","params":[]})
out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",
                      "https://bsc-dataseed.binance.org/",
                      "-H","Content-Type: application/json",
                      "-d", json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
print("raw len:", len(out), "head:", out[:200])
resp = json.loads(out)
by_id = {r.get("id"): r for r in resp}
run = json.load(open(BASE + "run-hot-leg-2026-11-15-1704.json"))
ok = 0
for i,(name,vn,_d) in enumerate(chunk):
    r = by_id.get(i, {})
    val = to_int(r.get("result")) if r.get("result") else None
    if val is not None: ok += 1
    run["leg4"]["reads"].setdefault(name, {"address": base11[name]["address"], "views": {}})["views"][vn] = val
    # recompute diff vs 1659 baseline
    bv = base11[name]["views"].get(vn)
    d = run["leg4"]["diffs_vs_1659"].setdefault(name, {})
    if val is None:
        d[vn] = {"1659": bv, "now": None, "note": "read-failed-now"}
    elif val != bv:
        d[vn] = {"1659": bv, "now": val}
    else:
        d.pop(vn, None)
    if not d: run["leg4"]["diffs_vs_1659"].pop(name, None)
blk = by_id.get(len(chunk), {}).get("result")
if blk: run["leg4"]["block"] = int(blk, 16)
run["leg4"]["retry_chunk40"] = {"ok": ok, "of": len(chunk), "block": run["leg4"].get("block")}
run["leg4"]["n_ok"] = sum(1 for it in run["leg4"]["reads"].values() for v in it["views"].values() if v is not None)
run["leg4"]["errors"] = [e for e in run["leg4"]["errors"] if e.get("chunk") != 40]
json.dump(run, open(BASE + "run-hot-leg-2026-11-15-1704.json", "w"), indent=1)
print("retry ok:", ok, "of", len(chunk))
print("diffs now:", json.dumps(run["leg4"]["diffs_vs_1659"]))
