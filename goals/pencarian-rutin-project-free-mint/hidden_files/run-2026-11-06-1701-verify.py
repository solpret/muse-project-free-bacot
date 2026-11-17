#!/usr/bin/env python3
"""Verify run 2026-11-06 1701 WIB. Read-only.
Boltbook front-page leads (EN 17:07 WIB): WHALE NFT (new, in seen file,
NOT in snapshot), Driftnauts/M3MO/Pixel Laptop/AgentX (already early leads,
promotion/sellout re-check), Ghostbot (reported CLOSED 666/666 -> sellout
verify), Mindvolt (638/700 progress). Also WHALE first-mint timestamp check.
"""
import json, urllib.request, time, sys
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1701"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def raw_hex(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return None

def decode_str(hx):
    if not hx or hx == "0x": return None
    try:
        b = bytes.fromhex(hx[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "ignore")
    except Exception:
        return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

ITEMS = {
 "WHALE": ("0xf81b542c41f982a7d7a8e2ee8cab5feee6203218",
           ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
            "priceFor()", "freeMintAvailable()", "MINT_PRICE()", "MAX_SUPPLY()",
            "mintOpen()", "mintedBy(address)", "freeUsed(address)",
            "balanceOf(address)", "quote(address,uint256)", "hasAgentId(address)"]),
 "Ghostbot": ("0x0c654bef00dad6925f64b72151c4a504f1c00bcd",
              ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "freeMinted()",
               "freeClaimed()", "balanceOf(address)"]),
 "Mindvolt": ("0x2f47305baedc1b1f28461cd6b488404a908b1bea",
              ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "freeMinted()",
               "freeClaimed()", "balanceOf(address)"]),
 "Driftnauts": ("0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b",
                 ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
                  "FREE_CAP()", "MAX_SUPPLY()", "PAID_CAP()", "paidMinted()",
                  "mintedBy(address)", "canFreeMint(address)", "claimedFree(address)",
                  "balanceOf(address)", "quote(address,uint256)"]),
 "Pixel Laptop": ("0x273fc2c7705b23eb129e35ac8da26348e6fc4980",
                  ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
                   "FREE_SUPPLY()", "MAX_SUPPLY()", "mintedBy(address)",
                   "balanceOf(address)", "quote(address,uint256)"]),
 "AgentX": ("0x59d96d8b4b82abb350868e897f25f8e021360823",
            ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
             "MAX_SUPPLY()", "mintedBy(address)", "balanceOf(address)",
             "quote(address,uint256)"]),
 "M3MO": ("0x08be8a0727b6fc801171c1f4f4dd547ea44ca339",
          ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
           "FREE_SUPPLY()", "MAX_SUPPLY()", "mintedBy(address)",
           "balanceOf(address)", "quote(address,uint256)"]),
}

def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    d["name"] = decode_str(raw_hex(addr, sel("name()")) or "")
    d["symbol"] = decode_str(raw_hex(addr, sel("symbol()")) or "")
    d["contractURI"] = decode_str(raw_hex(addr, sel("contractURI()")) or "")
    print(name, json.dumps(d, default=str), flush=True)
    return name, d

out = {}
with ThreadPoolExecutor(max_workers=7) as ex:
    for name, d in ex.map(read_item, ITEMS.items()):
        out[name] = d

# WHALE first-mint timestamp: backwards Ankr search from seen first_block 131064620
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
WHALE = "0xf81b542c41f982a7d7a8e2ee8cab5feee6203218"
def ankr_logs(frm, to, addr):
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
            "toBlock": hex(to), "pageSize": 1000, "decodeLogs": False,
            "topics": [TRANSFER, ZERO_TOPIC],
            "address": [addr]}, timeout=30)
        return body.get("result", {}).get("logs", [])
    except Exception as e:
        return f"error:{e}"

def block_ts(blk):
    sys.path.insert(0, "/home/hatch/workspace/fast_exec")
    from fast_rpc import _single
    for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com"]:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(blk), False], 8, retries=0)
            return int(b["timestamp"], 16)
        except Exception:
            continue
    return None

import datetime
def wib(ts):
    if ts is None: return None
    return (datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
            + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S WIB")

first_blk = None
to_blk = 131064620
chunks = 0
while chunks < 60 and to_blk > 131000000:
    frm = max(131000000, to_blk - 999)
    logs = ankr_logs(frm, to_blk, WHALE)
    chunks += 1
    if isinstance(logs, str):
        print("WHALE ankr error chunk", frm, to_blk, logs, flush=True)
        break
    if not logs:
        break
    first_blk = min(int(l["blockNumber"], 16) for l in logs)
    to_blk = frm - 1
ts = block_ts(first_blk) if first_blk else block_ts(131064620)
print("WHALE firstMintBlock", first_blk, "wib", wib(ts), "chunks", chunks, flush=True)
out["whale_firstMint"] = {"firstMintBlock": first_blk, "firstMintWib": wib(ts),
                          "seenFirstBlock": 131064620, "seenFirstWib": wib(block_ts(131064620)),
                          "chunks": chunks}
json.dump(out, open(f"{BASE}/run-{TS}-verify.json", "w"), indent=1, ensure_ascii=False)
print("VERIFY DONE", flush=True)
