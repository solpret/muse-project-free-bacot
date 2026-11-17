#!/usr/bin/env python3
"""Leg 3: Orchidia 0x09bc... on-chain verification (read-only)."""
import json, urllib.request, time
from Crypto.Hash import keccak
ADDR = "0x09bcdd97186f6f37521bd1b281d329e48ac54b89"
RPCS = ["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def rpc(method, params, timeout=8):
    for r in RPCS:
        try:
            body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req = urllib.request.Request(r, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp: out = json.load(resp)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
def call(sig, args=""):
    v = rpc("eth_call", [{"to":ADDR,"data":sel(sig)+args},"latest"])
    if not v or v=="0x": return None
    try: return int(v,16)
    except Exception: return v
def call_str(sig):
    v = rpc("eth_call", [{"to":ADDR,"data":sel(sig)},"latest"])
    if not v or v=="0x" or len(v)<130: return None
    try:
        ln = int(v[66:130],16)
        return bytes.fromhex(v[130:130+ln*2]).decode("utf-8","ignore")
    except Exception: return v
blk = rpc("eth_blockNumber", [])
print("BLOCK", int(blk,16) if blk else None)
out = {"address":ADDR, "block": int(blk,16) if blk else None}
out["name"] = call_str("name()")
out["symbol"] = call_str("symbol()")
for sig in ["totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","freeClaimed()","freeMinted()","PRICE()","mintOpen()","owner()","AGENT_ID()"]:
    out[sig.split("(")[0]] = call(sig)
out["quote_user1"] = call("quote(address,uint256)", enc(USER)+enc_uint(1))
out["freeFor_user1"] = call("freeFor(address,uint256)", enc(USER)+enc_uint(1))
out["freeLeft_user"] = call("freeLeft(address)", enc(USER))
out["freeUsed_user"] = call("freeUsed(address)", enc(USER))
out["mintedBy_user"] = call("mintedBy(address)", enc(USER))
out["balanceOf_user"] = call("balanceOf(address)", enc(USER))
out["contractURI"] = call_str("contractURI()")
print(json.dumps(out, indent=1))
# first mint: Transfer from 0x0, earliest log
topic0 = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
logs = rpc("eth_getLogs", [{"fromBlock":"0x0","toBlock":"latest","address":ADDR,
      "topics":[topic0, zero]}])
print("transfer-from-zero logs:", len(logs) if logs is not None else None)
if logs:
    first = logs[0]; last = logs[-1]
    print("first mint block:", int(first["blockNumber"],16), "tx:", first["transactionHash"])
    print("last mint block:", int(last["blockNumber"],16))
    b = rpc("eth_getBlockByNumber", [first["blockNumber"], False])
    if b: 
        import datetime
        print("first mint time UTC:", datetime.datetime.utcfromtimestamp(int(b["timestamp"],16)).isoformat())
        print("first mint time WIB:", datetime.datetime.utcfromtimestamp(int(b["timestamp"],16)+7*3600).isoformat())
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-07-0409-orchidia.json","w"), indent=1)
print("DONE")
