#!/usr/bin/env python3
"""AGCE fresh on-chain verification run 1901 (parent). Read-only."""
import json, urllib.request, datetime
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE = "0x5AD10026B4233aC004043DBB9291CFad19b1B3C3"
TOKEN = "0x942c19A87a77b062D94C452ED8FaC6162aff45aD"
POE = "0xaa890A3B658eCFa56f0d0486665F0D4e77f3Fa0F"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None
def call(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v
def call_addr(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return "0x" + v[-40:]
    except Exception: return v
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
def decode_str(v):
    if not v or len(v) < 130: return None
    try:
        off = int(v[2:66], 16); ln = int(v[2+off*2:2+off*2+64], 16)
        return bytes.fromhex(v[2+off*2+64:2+off*2+64+ln*2]).decode("utf-8", "replace")
    except Exception: return None
blk = block()
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
out = {"block": blk, "now_wib": now.strftime("%Y-%m-%d %H:%M:%S")}
out["sale"] = {
 "AGENT_REGISTRY": call_addr(SALE, "AGENT_REGISTRY()"),
 "token": call_addr(SALE, "token()"),
 "saleStart": call(SALE, "saleStart()"),
 "isLive": call(SALE, "isLive()"),
 "pair": call_addr(SALE, "pair()"),
 "PRICE": call(SALE, "PRICE()"),
 "totalPaidShares": call(SALE, "totalPaidShares()"),
 "FREE_AMOUNT": call(SALE, "FREE_AMOUNT()"),
 "TOKENS_PER_SHARE": call(SALE, "TOKENS_PER_SHARE()"),
 "freeRemaining": call(SALE, "freeRemaining()"),
 "freeSharesClaimed": call(SALE, "freeSharesClaimed()"),
 "freeClaimed_user": call(SALE, "freeClaimed(address)", enc(USER)),
}
out["token"] = {
 "saleContract": call_addr(TOKEN, "saleContract()"),
 "pair": call_addr(TOKEN, "pair()"),
 "totalSupply": call(TOKEN, "totalSupply()"),
 "balanceOf_user": call(TOKEN, "balanceOf(address)", enc(USER)),
}
out["poe"] = {
 "EXTERNAL_URL": decode_str(raw(POE, sel("EXTERNAL_URL()"))),
 "minter": call_addr(POE, "minter()"),
 "nextId": call(POE, "nextId()"),
}
ss = out["sale"]["saleStart"]
if isinstance(ss, int):
    out["saleStart_wib"] = datetime.datetime.fromtimestamp(ss, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    out["age_minutes"] = round((now.timestamp() - ss) / 60, 1)
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1901-agce-verify.json", "w"), indent=1)
