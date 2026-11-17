#!/usr/bin/env python3
"""Hot-leg 2026-11-07 01:49 leg-3c: name/symbol fix, first-mint log retry, deployer-group check."""
import json, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3"
DEPLOYER = "45e2c8a09022914ce00cfce9a93dd3fda54d8686"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def rpc_call(method, params, timeout=10):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o: continue
            return o.get("result"), rpc
        except Exception:
            continue
    return None, None
out = {}
def dec_str(sig):
    v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel(sig)}, "latest"])
    if not v or v == "0x": return None
    b = bytes.fromhex(v[2:])
    ln = int.from_bytes(b[32:64], "big")
    return b[64:64+ln].decode(errors="replace")
out["name"] = dec_str("name()")
out["symbol"] = dec_str("symbol()")
# tokenURI(1) proper decode
v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel("tokenURI(uint256)") + format(1, "064x")}, "latest"])
if v and v != "0x":
    b = bytes.fromhex(v[2:])
    ln = int.from_bytes(b[32:64], "big")
    out["tokenURI_1"] = b[64:64+ln].decode(errors="replace")
# first mint: Transfer from zero, narrow window around launch (blocks ~132060500-latest)
transfer_topic = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
for frm in (132060500, 132060900):
    logs, rpc = rpc_call("eth_getLogs", [{"fromBlock": hex(frm), "toBlock": "latest",
        "address": ADDR, "topics": [transfer_topic, zero]}], timeout=15)
    out[f"getLogs_from_{frm}"] = {"rpc": rpc, "n": len(logs) if isinstance(logs, list) else logs}
    if isinstance(logs, list) and logs:
        import datetime
        first = logs[0]
        bn = int(first["blockNumber"], 16)
        out["first_mint_block"] = bn
        out["first_mint_tx"] = first["transactionHash"]
        out["first_mint_to"] = "0x" + first["topics"][2][26:]
        out["first_mint_tokenId"] = int(first["topics"][3], 16)
        bv, _ = rpc_call("eth_getBlockByNumber", [hex(bn), False])
        if bv:
            ts = int(bv["timestamp"], 16)
            out["first_mint_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        break
# deployer group: any other snapshot contract with same creator/owner?
snap_text = open(f"{BASE}/onchain-snapshot.json").read().lower()
out["deployer_in_snapshot_text"] = DEPLOYER in snap_text
# current totalSupply/remaining re-read
v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel("totalSupply()")}, "latest"])
out["totalSupply_now"] = int(v, 16) if v and v != "0x" else v
v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel("remaining()")}, "latest"])
out["remaining_now"] = int(v, 16) if v and v != "0x" else v
blk, rpc = rpc_call("eth_blockNumber", [])
out["block_now"] = int(blk, 16) if blk else None
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-0149-leg3c.json", "w"), indent=1)
print(json.dumps(out, indent=1))
