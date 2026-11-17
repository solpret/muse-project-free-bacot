#!/usr/bin/env python3
"""Hot-leg 16:09 leg4 RETRY: re-read the 36 live items (+ ONI) vs 16:01 baseline
with SMALL batches (10 calls) - the 60-call chunks in the main run failed at
the node (only the final 10-call chunk returned values). Merges into
hot-leg-run-2026-11-15-1609.json. Read-only except that run log."""
import json, time, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
NOARG = {"totalSupply", "totalMinted", "freeMinted", "freeClaimed", "FREE_SUPPLY",
         "FREE_CAP", "FREE_MAX", "FREE_MINT_CAP", "MAX_SUPPLY", "maxSupply", "mintOpen",
         "launched", "failed", "isRefundPhase", "totalShares", "remainingSupply",
         "standardRemaining", "legendaryRemaining", "paused", "TOKEN_PRICE", "claimOpen",
         "mintStartTime", "AGENT_ID", "freeSharesLeft", "openedAt", "freeBlock",
         "mintOpenTimestamp", "mintPaused", "price", "PRICE", "mintPrice", "paidMinted",
         "totalSpecimens", "currentExperiment", "genesisStart", "genesisOpen",
         "mintsLeft", "freeMintsLeft", "freeRemaining", "owner"}
ADDRARG = {"balanceOf", "freeClaimedOf", "freeUsed", "mintedBy", "mintedByWallet",
           "freeMintedPerWallet", "mintedPerWallet", "mintCountOf", "mintsBy",
           "holdsAgentId", "hasAgentId", "isEligible", "tokenClaimed", "freeBooked",
           "hasFreeClaimed"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

base = json.load(open(BASE + "run-2026-11-15-1601-reread.json"))
base_reads = base["reads"]
base_reads["ONI"] = {"address": "0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",
                     "views": {"totalMinted": 3, "freeClaimed_user": 0,
                               "freeClaimedOf_user": 0, "balanceOf_user": 0}}
calls = []
for name, it in base_reads.items():
    for vn, bv in it["views"].items():
        if bv is None or vn.startswith("freeClaimedByAgent"):
            continue
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

reads, block, errors = {}, None, []
CH = 10
for s in range(0, len(calls), CH):
    chunk = calls[s:s + CH]
    payload = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                "params": [{"to": base_reads[c[0]]["address"], "data": c[2]}, "latest"]}
               for i, c in enumerate(chunk)]
    payload.append({"jsonrpc": "2.0", "id": len(chunk), "method": "eth_blockNumber", "params": []})
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST",
                              "https://bsc-dataseed.binance.org/",
                              "-H", "Content-Type: application/json",
                              "-d", json.dumps(payload)],
                             capture_output=True, text=True, timeout=40).stdout
        resp = json.loads(out)
        if not isinstance(resp, list):
            errors.append({"chunk": s, "resp": str(resp)[:200]})
            continue
        by_id = {r.get("id"): r for r in resp}
        for i, (name, vn, _d) in enumerate(chunk):
            r = by_id.get(i, {})
            val = to_int(r.get("result")) if r.get("result") else None
            reads.setdefault(name, {"address": base_reads[name]["address"], "views": {}})["views"][vn] = val
        blk = by_id.get(len(chunk), {}).get("result")
        if blk:
            block = int(blk, 16)
    except Exception as ex:
        errors.append({"chunk": s, "error": f"{type(ex).__name__}: {str(ex)[:120]}"})

diffs = {}
for name, it in base_reads.items():
    now_views = reads.get(name, {}).get("views", {})
    for vn, bv in it["views"].items():
        if bv is None or vn.startswith("freeClaimedByAgent"):
            continue
        nv = now_views.get(vn)
        if nv is None:
            diffs.setdefault(name, {})[vn] = {"1601": bv, "now": None, "note": "read-failed-now"}
        elif nv != bv:
            diffs.setdefault(name, {})[vn] = {"1601": bv, "now": nv}

n_ok = sum(1 for it in reads.values() for v in it["views"].values() if v is not None)
run = json.load(open(BASE + "hot-leg-run-2026-11-15-1609.json"))
run["leg4_reread_retry"] = {"reads": reads, "block": block, "errors": errors,
                            "n_calls": len(calls), "n_ok": n_ok,
                            "chunk_size": CH, "elapsed_s": round(time.time() - t0, 1)}
run["leg4_diffs_vs_1601"] = diffs
run["elapsed_s"] = round(run.get("elapsed_s", 0) + (time.time() - t0), 1)
json.dump(run, open(BASE + "hot-leg-run-2026-11-15-1609.json", "w"), indent=1)
print(json.dumps({"block": block, "n_calls": len(calls), "n_ok": n_ok,
                  "errors": errors, "diffs": diffs,
                  "elapsed_s": round(time.time() - t0, 1)}, indent=1))
