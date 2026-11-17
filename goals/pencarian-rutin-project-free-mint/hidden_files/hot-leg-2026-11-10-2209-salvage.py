#!/usr/bin/env python3
"""Salvage for hot-leg run 2026-11-10 22:09 WIB.
Leg 3: on-chain verify 2 new S1 sale-shape contracts from feed
(0xE405...2728 verified 22:06:52 WIB; 0x6729...93A4 verified 22:03:14 WIB).
Leg 4 retry: BYTEBLOOM only (near 25% strong-lead), small batches
(the 38-call batch in the main script failed wholesale on all RPCs).
Read-only.
"""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-10-2209-salvage"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return hex(n)[2:].rjust(64, "0")

def words(hexstr):
    if not isinstance(hexstr, str) or not hexstr.startswith("0x"): return None
    h = hexstr[2:]
    if not h or len(h) % 64: return None
    return [int(h[i:i+64], 16) for i in range(0, len(h), 64)]

def batch(rpc, calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try:
        r = json.loads(p.stdout)
        return r if isinstance(r, list) else {"_err": str(r)[:200]}
    except Exception:
        return {"_err": (p.stdout + p.stderr)[:200]}

def run_batch(jobs):
    """jobs: list of (name, field, addr, data). Returns dict name->field->value."""
    out = {}
    for rpc in RPCS:
        r = batch(rpc, [(a, d) for (_, _, a, d) in jobs])
        if isinstance(r, list) and len(r) == len(jobs):
            ok = 0
            for (name, field, addr, _), resp in zip(jobs, r):
                val = resp.get("result") if isinstance(resp, dict) else None
                if val:
                    w = words(val)
                    if w is not None:
                        out.setdefault(name, {})[field] = w if len(w) > 1 else w[0]
                        ok += 1
            print(f"  batch via {rpc}: {ok}/{len(jobs)} ok")
            if ok:
                return out, rpc
        else:
            print(f"  batch via {rpc}: bad response {str(r)[:150]}")
    return out, None

def block_number(rpc):
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json",
                        "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                       capture_output=True, text=True)
    try: return int(json.loads(p.stdout)["result"], 16)
    except Exception: return None

A = "0xE4059eA596392AcA14100af6CDC9481c330E2728"
B = "0x67299f979508CeDBb1Fb04226c3846D2b82c93A4"
BB = "0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"

# Contract A views (12 calls)
jobsA = []
for f, d in [("name", sel("name()")), ("symbol", sel("symbol()")),
             ("saleStart", sel("saleStart()")), ("saleEnd", sel("saleEnd()")),
             ("saleOpen", sel("saleOpen()")),
             ("FREE_SHARES", sel("FREE_SHARES()")),
             ("MAX_SHARES", sel("MAX_SHARES()")),
             ("totalFreeShares", sel("totalFreeShares()")),
             ("totalPaidShares", sel("totalPaidShares()")),
             ("totalShares", sel("totalShares()")),
             ("freeUsed_user", sel("freeUsed(address)") + enc_addr(USER)),
             ("sharesOf_user", sel("sharesOf(address)") + enc_addr(USER)),
             ("isAgent_user", sel("isAgent(address)") + enc_addr(USER)),
             ("registry", sel("registry()")),
             ("quote_1", sel("quote(uint256)") + enc_uint(1)),
             ("PRICE", sel("PRICE()")),
             ("TOKENS_PER_SHARE", sel("TOKENS_PER_SHARE()"))]:
    jobsA.append(("A", f, A, d))
print("== Contract A", A)
outA, rpcA = run_batch(jobsA)
print(json.dumps(outA, indent=1))

# Contract B views (12 calls)
jobsB = []
for f, d in [("token", sel("token()")), ("pair", sel("pair()")),
             ("launched", sel("launched()")), ("opensAt", sel("opensAt()")),
             ("deadline", sel("deadline()")),
             ("maxShares", sel("maxShares()")),
             ("targetShares", sel("targetShares()")),
             ("totalShares", sel("totalShares()")),
             ("totalPaid", sel("totalPaid()")),
             ("pricePerShare", sel("pricePerShare()")),
             ("tokensPerShare", sel("tokensPerShare()")),
             ("quotaOf_user", sel("quotaOf(address)") + enc_addr(USER)),
             ("remainingOf_user", sel("remainingOf(address)") + enc_addr(USER)),
             ("quote_1", sel("quote(uint256)") + enc_uint(1)),
             ("currentStage", sel("currentStage()")),
             ("freeFor_0", sel("freeFor(uint256)") + enc_uint(0))]:
    jobsB.append(("B", f, B, d))
print("== Contract B", B)
outB, rpcB = run_batch(jobsB)
print(json.dumps(outB, indent=1))

# BYTEBLOOM re-read (7 calls)
jobsBB = []
for f, d in [("totalSupply", sel("totalSupply()")),
             ("agentFreeUsed", sel("agentFreeUsed()")),
             ("agentFreeLeft", sel("agentFreeLeft()")),
             ("mintOpen", sel("mintOpen()")),
             ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
             ("walletInfo_user", sel("walletInfo(address)") + enc_addr(USER)),
             ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER))]:
    jobsBB.append(("BYTEBLOOM", f, BB, d))
print("== BYTEBLOOM", BB)
outBB, rpcBB = run_batch(jobsBB)
print(json.dumps(outBB, indent=1))

block = block_number(rpcA or rpcB or rpcBB or RPCS[0])
res = {"block": block, "A": outA, "B": outB, "BYTEBLOOM": outBB,
       "rpcs": {"A": rpcA, "B": rpcB, "BYTEBLOOM": rpcBB}}
json.dump(res, open(BASE + TAG + ".json", "w"), indent=1)

# Token name/symbol for B if token address known
tok = None
try:
    tok = "0x" + format(outB["B"]["token"], "040x")
except Exception:
    pass
if tok:
    jobsT = [("Btoken", "name", tok, sel("name()")),
             ("Btoken", "symbol", tok, sel("symbol()"))]
    outT, rpcT = run_batch(jobsT)
    print("== B token", tok, json.dumps(outT))
    res["Btoken"] = outT
    json.dump(res, open(BASE + TAG + ".json", "w"), indent=1)

print("DURATION sec:", round(time.time() - T0, 1))
