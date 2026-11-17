#!/usr/bin/env python3
"""Leg-3 verification for Ninetailix 0x809215729bcbff2ef31dea5efd6c12a6b788ba9a (S1, found via Boltbook 0244 run)."""
import json, sys, time, urllib.request, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

ADDR = "0x809215729bcbff2ef31dea5efd6c12a6b788ba9a"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def raw_call(addr, data):
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0)
        except Exception:
            continue
    return None
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def dec_string(hexstr):
    try:
        b = bytes.fromhex(hexstr[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big"); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"<decode err {e}>"
def dec_addr(hexstr):
    try: return "0x" + hexstr[-40:]
    except Exception: return None

out = {}
def uint(name, sig, arg=""):
    out[name] = to_int(raw_call(ADDR, sel(sig) + arg))
def string(name, sig, arg=""):
    out[name] = dec_string(raw_call(ADDR, sel(sig) + arg))
def addr(name, sig, arg=""):
    out[name] = dec_addr(raw_call(ADDR, sel(sig) + arg))

string("name", "name()"); string("symbol", "symbol()")
uint("totalSupply", "totalSupply()")
uint("FREE_SUPPLY", "FREE_SUPPLY()"); uint("FREE_PER_WALLET", "FREE_PER_WALLET()")
uint("MAX_SUPPLY", "MAX_SUPPLY()"); uint("MAX_PER_WALLET", "MAX_PER_WALLET()")
uint("PRICE", "PRICE()")
uint("freeClaimed_total", "freeClaimed()")
uint("freeLeft_user", "freeLeft(address)", enc(USER))
uint("freeUsed_user", "freeUsed(address)", enc(USER))
uint("freeFor_user1", "freeFor(address,uint256)", enc(USER) + enc_uint(1)[2:])
uint("mintedBy_user", "mintedBy(address)", enc(USER))
uint("balanceOf_user", "balanceOf(address)", enc(USER))
uint("quote_user1", "quote(address,uint256)", enc(USER) + enc_uint(1)[2:])
addr("AGENT_ID", "AGENT_ID()"); addr("owner", "owner()")
raw_mo = raw_call(ADDR, sel("mintOpen()"))
out["mintOpen"] = to_int(raw_mo)
string("contractURI", "contractURI()")
print(json.dumps(out, indent=1))

# First mint via getLogs Transfer from zero address (Ankr for logs; dataseed for block ts - Ankr ts is FAKE per AGENTS.md)
def post(rpc, method, params, timeout=25):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.load(r)

blk = None
try:
    blk = int(post(EPS[0], "eth_blockNumber", [], 10)["result"], 16)
except Exception as e:
    print("blockNumber fail:", e)
print("current block:", blk)
fm = {}
if blk:
    from_blk = hex(blk - 60000)
    TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
    for rpc in ["https://rpc.ankr.com/bsc", EPS[0], EPS[1]]:
        try:
            o = post(rpc, "eth_getLogs", [{"fromBlock": from_blk, "toBlock": "latest", "address": ADDR, "topics": [TOPIC0, ZERO]}], 30)
            if "error" in o:
                print(rpc, "getLogs error:", o["error"]); continue
            logs = o.get("result", [])
            print(rpc, "zero-address Transfer logs:", len(logs))
            if logs:
                first = logs[0]
                fblk = int(first["blockNumber"], 16)
                ts = None
                try:
                    b = post(EPS[0], "eth_getBlockByNumber", [first["blockNumber"], False], 10)
                    ts = int(b["result"]["timestamp"], 16)
                except Exception as e:
                    print("block ts fail:", e)
                wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None
                fm = {"first_mint_block": fblk, "first_mint_ts": ts, "first_mint_wib": wib,
                      "first_mint_tx": first["transactionHash"], "first_tokenId": int(first["topics"][3], 16),
                      "logs_total": len(logs), "logs_via": rpc, "from_block": from_blk, "current_block": blk}
                print(json.dumps(fm, indent=1))
                break
            else:
                print("no logs in window", from_blk, "- contract may predate window")
                fm = {"logs_total": 0, "from_block": from_blk, "current_block": blk}
                break
        except Exception as e:
            print(rpc, "EXC:", type(e).__name__, e)
json.dump({"onchain": out, "first_mint": fm, "run_wib": "2026-11-08T02:44:38+07:00"},
          open("hot-leg-2026-11-08-0244-leg3-ninetailix.json", "w"), indent=1)
