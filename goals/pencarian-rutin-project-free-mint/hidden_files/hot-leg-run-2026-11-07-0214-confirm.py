#!/usr/bin/env python3
"""Targeted confirm for 5 near-sellout early leads that hit the 90s leg4 deadline in run 02:14.
Read-only eth_call, single RPC, short timeout. One freeClaimed + totalSupply + balanceOf(user) each."""
import json, urllib.request
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
ITEMS = {
 "Qilingentle-423d": ("0x423d25764E4D3D792C08e04C759cE3b0FcDE8596", 499, 500),
 "Hivejupiter-8DF7": ("0x8DF74cBe998F8d447E7c77dD5117aFB940605400", 499, 500),
 "Saturnswarm-238c": ("0x238C995A1376e08395b970870A546C57aE184434", 887, 888),
 "Boohiveling-c1da": ("0xC1dAf114e377242eEB76d180B24b491758Acb4f7", 499, 500),
 "Neidroidjuan-758c": ("0x758c9665747466Ff4CBa2a3714CC4e9F7C9324b6", 407, 408),
}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(to, sig, args=""):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": sel(sig) + args}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r:
                o = json.load(r)
            v = o.get("result")
            if not v or v == "0x" or "error" in o:
                return None
            return int(v, 16)
        except Exception:
            continue
    return None
blk = None; blk_rpc = None
for rpc in RPCS:
    try:
        blk_body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=blk_body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as r:
            blk = int(json.load(r)["result"], 16); blk_rpc = rpc; break
    except Exception:
        continue
out = {"block": blk, "via": blk_rpc, "items": {}}
enc = USER[2:].lower().rjust(64, "0")
for name, (addr, prev_fc, prev_ts) in ITEMS.items():
    fc = call(addr, "freeClaimed()")
    ts = call(addr, "totalSupply()")
    bal = call(addr, "balanceOf(address)", enc)
    mb = call(addr, "mintedBy(address)", enc)
    sold = (fc is not None and ts is not None and fc >= ts) or (fc is not None and fc >= prev_ts)
    out["items"][name] = {"address": addr, "freeClaimed": fc, "totalSupply": ts,
                          "balanceOf_user": bal, "mintedBy_user": mb,
                          "prev_freeClaimed_0204": prev_fc, "prev_totalSupply_0204": prev_ts,
                          "sold_out_now": sold if fc is not None else None}
print(json.dumps(out, indent=1))
json.dump(out, open("hot-leg-run-2026-11-07-0214-confirm.json", "w"), indent=1)
