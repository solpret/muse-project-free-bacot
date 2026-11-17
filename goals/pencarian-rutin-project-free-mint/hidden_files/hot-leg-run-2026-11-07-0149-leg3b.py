#!/usr/bin/env python3
"""Hot-leg 2026-11-07 01:49 leg-3b: retry mintStart/mintEnd/remaining + first-mint corroboration for JourneyWest."""
import json, urllib.request, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3"
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
def call(sig, args=""):
    v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel(sig) + args}, "latest"])
    if v is None or v == "0x": return None, rpc
    try: return int(v, 16), rpc
    except Exception: return v, rpc
out = {}
for sig in ("mintStart()", "mintEnd()", "remaining()"):
    v, rpc = call(sig)
    out[sig.split("(")[0]] = v
    out[sig.split("(")[0] + "_via"] = rpc
out["name_retry"] = None
# name/symbol with proper decode
v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel("name()")}, "latest"])
if v and v != "0x":
    b = bytes.fromhex(v[2:])
    try:
        ln = int.from_bytes(b[64:96], "big")
        out["name"] = b[96:96+ln].decode()
    except Exception as e:
        out["name_raw"] = v[:200]
v, rpc = rpc_call("eth_call", [{"to": ADDR, "data": sel("symbol()")}, "latest"])
if v and v != "0x":
    b = bytes.fromhex(v[2:])
    try:
        ln = int.from_bytes(b[64:96], "big")
        out["symbol"] = b[96:96+ln].decode()
    except Exception:
        out["symbol_raw"] = v[:200]
now = int(time.time())
out["now_unix"] = now
ms = out.get("mintStart")
if isinstance(ms, int):
    import datetime
    out["mintStart_wib"] = datetime.datetime.fromtimestamp(ms, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    out["mintEnd_wib"] = datetime.datetime.fromtimestamp(out["mintEnd"], datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if isinstance(out.get("mintEnd"), int) else None
    out["age_h"] = round((now - ms)/3600, 3)
    # binary search block number for mintStart timestamp
    lo, hi = 132000000, 132061000
    def blk_ts(n):
        v, _ = rpc_call("eth_getBlockByNumber", [hex(n), False])
        return int(v["timestamp"], 16) if v else None
    for _ in range(18):
        mid = (lo + hi)//2
        t = blk_ts(mid)
        if t is None: break
        if t < ms: lo = mid
        else: hi = mid
    out["block_at_mintStart"] = hi
    # first Transfer (mint) logs from block_at_mintStart-200 to latest
    transfer_topic = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
    zero_topic = "0x" + "00"*31 + "00"
    from_topic = "0x0000000000000000000000000000000000000000000000000000000000000000"
    logs, rpc = rpc_call("eth_getLogs", [{"fromBlock": hex(max(0, hi-500)), "toBlock": "latest",
        "address": ADDR, "topics": [transfer_topic, from_topic]}])
    out["first_mint_logs_rpc"] = rpc
    if isinstance(logs, list):
        out["first_mint_count"] = len(logs)
        if logs:
            first = logs[0]
            bn = int(first["blockNumber"], 16)
            out["first_mint_block"] = bn
            out["first_mint_tx"] = first["transactionHash"]
            out["first_mint_tokenId"] = int(first["topics"][3], 16)
            bv, _ = rpc_call("eth_getBlockByNumber", [hex(bn), False])
            if bv:
                ts = int(bv["timestamp"], 16)
                out["first_mint_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                out["first_mint_age_h"] = round((now - ts)/3600, 3)
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-0149-leg3b.json", "w"), indent=1)
print(json.dumps(out, indent=1))
