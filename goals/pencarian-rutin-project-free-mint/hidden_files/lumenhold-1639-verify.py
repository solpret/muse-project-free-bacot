#!/usr/bin/env python3
"""Hot-leg 1639 follow-up: on-chain verify Lumenhold 0x9701980b0afd825134390ee46fb3bd675a2f356f (Boltbook S1, already snapshot-excluded)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as single
from Crypto.Hash import keccak

ADDR = "0x9701980b0afd825134390ee46fb3bd675a2f356f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc", "https://bsc.publicnode.com"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def call(to, data, frm=None):
    params = {"to": to, "data": data}
    if frm: params["from"] = frm
    for ep in EPS:
        try:
            v = single(ep, "eth_call", [params, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            return v
        except Exception:
            continue
    return "transport-fail"

def u256(v):
    if v is None or v == "transport-fail": return v
    try: return int(v, 16)
    except Exception: return v

def dyn_str(v):
    # decode ABI string return
    if v is None or v == "transport-fail" or len(v) < 130: return v
    try:
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"decode-err {e}"

out = {}
views = ["FREE_SUPPLY()", "freeClaimed()", "FREE_PER_WALLET()", "MAX_PER_WALLET()",
         "MAX_SUPPLY()", "totalSupply()", "mintOpen()", "PRICE()", "agentIdRequired()",
         "AGENT_ID()", "owner()"]
for sig in views:
    key = sig.split("(")[0]
    v = call(ADDR, sel(sig))
    out[key] = u256(v) if sig not in ("AGENT_ID()", "owner()") else (("0x" + v[-40:]) if isinstance(v, str) and len(v) >= 42 else v)
for sig in ["freeLeft(address)", "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]:
    key = sig.split("(")[0] + "_user"
    out[key] = u256(call(ADDR, sel(sig) + enc(USER)))
# quote(user,1) and freeFor(user,1) with from=USER (freeFor reverts for non-Agent wallets per Boltbook)
out["quote_user1"] = u256(call(ADDR, sel("quote(address,uint256)") + enc(USER) + enc_uint(1), frm=USER))
out["freeFor_user1"] = call(ADDR, sel("freeFor(address,uint256)") + enc(USER) + enc_uint(1), frm=USER)
out["freeFor_user1_dec"] = u256(out["freeFor_user1"])
for sig in ["name()", "symbol()", "contractURI()"]:
    key = sig.split("(")[0]
    out[key] = dyn_str(call(ADDR, sel(sig)))
# current head + launch-block timestamp via dataseed (NOT ankr: fake timestamps)
blk = None
for ep in EPS[:4]:
    try:
        blk = single(ep, "eth_blockNumber", [], 8, retries=0)
        if blk: break
    except Exception:
        continue
out["head_block"] = int(blk, 16) if blk else None
for b in (132101090, 132177886):
    ts = None
    for ep in EPS[:4]:
        try:
            r = single(ep, "eth_getBlockByNumber", [hex(b), False], 8, retries=0)
            if r and r.get("timestamp"):
                ts = int(r["timestamp"], 16); break
        except Exception:
            continue
    out[f"block_{b}_ts"] = ts
# first Transfer-from-zero via getLogs (publicnode, chunked)
import urllib.request
def get_logs(frm, to, topic0):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                       "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                                   "topics": [topic0]}]}).encode()
    req = urllib.request.Request("https://bsc.publicnode.com", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r).get("result")
    except Exception as e:
        return f"ERR {e}"
TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
ZERO_TOPIC = "0x" + "0"*64
logs = get_logs(132090000, 132178672, TRANSFER)
if isinstance(logs, list):
    mint_logs = [l for l in logs if l["topics"][1] == ZERO_TOPIC]
    out["getLogs_total_transfers_132090000_132178672"] = len(logs)
    out["getLogs_mint_from_zero"] = len(mint_logs)
    if mint_logs:
        out["first_mint_block"] = int(mint_logs[0]["blockNumber"], 16)
        out["last_mint_block"] = int(mint_logs[-1]["blockNumber"], 16)
        minters = {l["topics"][2] for l in mint_logs}
        out["unique_minters_in_window"] = len(minters)
else:
    out["getLogs_error"] = logs
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/lumenhold-1639-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
