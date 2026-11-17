#!/usr/bin/env python3
"""ELSY user-slot reads + deployment-block binary search (read-only)."""
import json, subprocess, time
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc.nodereal.io/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def rpc(method, params, block="latest", timeout=25):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    for ep in EPS:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                                  "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                                 capture_output=True, text=True, timeout=timeout + 5).stdout
            r = json.loads(out)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def call(data, block="latest"):
    return rpc("eth_call", [{"to": ADDR, "data": data}, block])
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
res = {}
res["AGENT_ID"] = call(sel("AGENT_ID()"))
res["hasAgentId_user"] = to_int(call(sel("hasAgentId(address)") + enc(USER)))
res["freeMintedByWallet_user"] = to_int(call(sel("freeMintedByWallet(address)") + enc(USER)))
res["mintedByWallet_user"] = to_int(call(sel("mintedByWallet(address)") + enc(USER)))
res["freeQtyFor_user_2"] = to_int(call(sel("freeQtyFor(address,uint256)") + enc(USER) + enc_u(2)))
res["freeQtyFor_user_1"] = to_int(call(sel("freeQtyFor(address,uint256)") + enc(USER) + enc_u(1)))
res["quote_user_2"] = to_int(call(sel("quote(address,uint256)") + enc(USER) + enc_u(2)))
res["quote_user_1"] = to_int(call(sel("quote(address,uint256)") + enc(USER) + enc_u(1)))
res["mintPrice"] = to_int(call(sel("mintPrice()")))
res["totalSupply"] = to_int(call(sel("totalSupply()")))
res["freeLeft"] = to_int(call(sel("freeLeft()")))
if res["AGENT_ID"]:
    res["AGENT_ID_addr"] = "0x" + res["AGENT_ID"][-40:]
print(json.dumps(res, indent=1), flush=True)
# --- deployment binary search via eth_getCode ---
head = to_int(rpc("eth_blockNumber", []))
print("head:", head, flush=True)
lo, hi = 132715000, head
# invariant: code empty at lo-1 (assumed), non-empty at hi
def has_code(b):
    r = rpc("eth_getCode", [ADDR, hex(b)])
    return r is not None and r != "0x" and len(r) > 2
t0 = time.time()
while hi - lo > 1:
    mid = (lo + hi) // 2
    if has_code(mid): hi = mid
    else: lo = mid
    print(f"  bisect lo={lo} hi={hi} ({time.time()-t0:.0f}s)", flush=True)
blk = rpc("eth_getBlockByNumber", [hex(hi), False])
ts = int(blk["timestamp"], 16) if blk else None
print(json.dumps({"deploy_block": hi, "deploy_ts": ts}), flush=True)
json.dump({"slot": res, "deploy_block": hi, "deploy_ts": ts, "head": head},
          open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-1401-elsy-slot.json", "w"), indent=1)
print("DONE")
