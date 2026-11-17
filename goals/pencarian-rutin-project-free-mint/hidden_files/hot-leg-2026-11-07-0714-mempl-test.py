#!/usr/bin/env python3
"""MEMPL first-mint disambiguation: verify Minted topic + raw eth_getLogs on small ranges."""
import json, urllib.request
from Crypto.Hash import keccak
MEMPL = "0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
minted_topic = "0x" + keccak.new(digest_bits=256, data=b"Minted(address,uint256,uint256,uint256,string)").hexdigest()
transfer_topic = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
print("minted topic:", minted_topic)
print("transfer topic:", transfer_topic)

def post(url, payload, timeout=15):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {e}"}

# current block
s, blk = post("https://bsc-dataseed1.bnbchain.org", {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
print("blockNumber:", s, blk)
cur = int(blk["result"], 16) if isinstance(blk, dict) and blk.get("result") else None
print("current block:", cur)

if cur:
    # Test A: Minted logs, last 1000 blocks, dataseed1
    for name, url in [("dataseed1", "https://bsc-dataseed1.bnbchain.org"),
                      ("publicnode", "https://bsc.publicnode.com"),
                      ("binance", "https://bsc-dataseed.binance.org")]:
        s, o = post(url, {"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[
            {"fromBlock": hex(cur-1000), "toBlock": hex(cur), "address": MEMPL, "topics": [minted_topic]}]}, 15)
        res = o.get("result") if isinstance(o, dict) else None
        print(f"A Minted 1000blk {name}: status={s} n={len(res) if isinstance(res, list) else res} err={o.get('error') if isinstance(o, dict) else o}")
        if isinstance(res, list) and res:
            print("  first log block:", int(res[0]["blockNumber"], 16), "tx:", res[0]["transactionHash"])
    # Test B: Transfer-from-zero, last 1000 blocks, dataseed1
    s, o = post("https://bsc-dataseed1.bnbchain.org", {"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[
        {"fromBlock": hex(cur-1000), "toBlock": hex(cur), "address": MEMPL,
         "topics": [transfer_topic, "0x"+"0"*64]}]}, 15)
    res = o.get("result") if isinstance(o, dict) else None
    print(f"B Transfer0 1000blk dataseed1: n={len(res) if isinstance(res, list) else res} err={o.get('error') if isinstance(o, dict) else o}")
    if isinstance(res, list) and res:
        print("  first log block:", int(res[0]["blockNumber"], 16), "tx:", res[0]["transactionHash"])
        # get that block's timestamp
        s2, b = post("https://bsc-dataseed1.bnbchain.org", {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[res[0]["blockNumber"], False]}, 10)
        print("  block ts:", b.get("result", {}).get("timestamp") if isinstance(b, dict) else b)
