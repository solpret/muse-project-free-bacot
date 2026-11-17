#!/usr/bin/env python3
"""Hot-leg 2026-11-07 01:49 leg-3: on-chain verify new S1 sale-shape JourneyWest 0xB0d58925..."""
import json, urllib.request, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def call(to, data, tag="latest", timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, tag]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o: continue
            v = o.get("result")
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return "transport-fail"
def u(v):
    if v is None or v == "transport-fail": return v
    try: return int(v, 16)
    except Exception: return v
def s(v):
    # decode string return
    if v is None or v == "transport-fail": return v
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64+off-32:64+off], "big") if False else int.from_bytes(b[32+off:64+off], "big")
        return b[64+off:64+off+ln].decode()
    except Exception:
        return v
out = {"contract": ADDR}
blk = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as r:
            o = json.load(r)
        blk = int(o["result"], 16); out["block"] = blk; out["via"] = rpc; break
    except Exception:
        continue
out["name"] = s(call(ADDR, sel("name()")))
out["symbol"] = s(call(ADDR, sel("symbol()")))
out["AGENT_ID"] = call(ADDR, sel("AGENT_ID()"))
out["owner"] = call(ADDR, sel("owner()"))
out["creator"] = call(ADDR, sel("creator()"))
out["mintOpen"] = u(call(ADDR, sel("mintOpen()")))
out["mintStart"] = u(call(ADDR, sel("mintStart()")))
out["mintEnd"] = u(call(ADDR, sel("mintEnd()")))
out["remaining"] = u(call(ADDR, sel("remaining()")))
out["totalSupply"] = u(call(ADDR, sel("totalSupply()")))
out["MAX_SUPPLY"] = u(call(ADDR, sel("MAX_SUPPLY()")))
out["PRICE"] = u(call(ADDR, sel("PRICE()")))
out["MINT_DURATION"] = u(call(ADDR, sel("MINT_DURATION()")))
out["LORD"] = u(call(ADDR, sel("LORD()")))
q = call(ADDR, sel("quote(address,uint256)") + enc(USER) + enc_uint(0))
if q and q not in (None, "transport-fail"):
    b = bytes.fromhex(q[2:])
    out["quote_user_paid0"] = [int.from_bytes(b[i:i+32], "big") for i in (0, 32)]
else:
    out["quote_user_paid0"] = q
out["freeClaimed_user"] = u(call(ADDR, sel("freeClaimed(address)") + enc(USER)))
out["balanceOf_user"] = u(call(ADDR, sel("balanceOf(address)") + enc(USER)))
out["paidCount_user"] = u(call(ADDR, sel("paidCount(address)") + enc(USER)))
# tokenURI(1) if any minted
if isinstance(out.get("totalSupply"), int) and out["totalSupply"] > 0:
    out["tokenURI_1"] = s(call(ADDR, sel("tokenURI(uint256)") + enc_uint(1)))
now = int(time.time())
out["now_unix"] = now
ms = out.get("mintStart")
if isinstance(ms, int):
    out["age_from_mintStart_s"] = now - ms
    out["age_from_mintStart_h"] = round((now - ms)/3600, 2)
me = out.get("mintEnd")
if isinstance(me, int):
    out["mintEnd_in_h"] = round((me - now)/3600, 2)
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-0149-leg3.json", "w"), indent=1)
print(json.dumps(out, indent=1))
