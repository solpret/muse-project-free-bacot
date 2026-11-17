#!/usr/bin/env python3
"""Run 2026-11-08 19:31 WIB: verify strong-lead legs for the 5 velocity-passing
FREE_SUPPLY-7000 siblings (Keyforge/Pixpad/Coralume/Candlewick/Compasso).
Reads: freeLeft(user), freeUsed(user), mintedBy(user), quote(user,1), FREE_PER_WALLET,
PRICE, mintOpen, AGENT_ID, owner, contractURI (method H). Read-only."""
import json, sys, time, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u256(n): return "%064x" % n
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out:
                return out["result"]
            if isinstance(out, dict) and "error" in out:
                return None
        except Exception:
            continue
    return None

def dec_str(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64: return b.decode(errors="replace")
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None

def dec_addr(h):
    if not isinstance(h, str) or len(h) < 42: return None
    return "0x" + h[-40:]

SIBS = {
    "Keyforge": "0xd9D4466342c993b43f02AE2e21D6F125a1Bd937F",
    "Pixpad": "0x7b601C3D2050B021B3bd9d650D421f3F98436ab3",
    "Coralume": "0xF10C1E17ae65e88e34253b951dD8EC274fa3AfEB",
    "Candlewick": "0x9A67E1FD6409B91BD9751206c81fDf37Fc467aE6",
    "Compasso": "0x6551529eC146020ee59B41265614b7a00A166A3f",
}
discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}

out = {}
for name, addr in SIBS.items():
    r = {"address": addr}
    r["totalSupply"] = to_int(call(addr, sel("totalSupply()")))
    r["freeClaimed"] = to_int(call(addr, sel("freeClaimed()")))
    r["FREE_SUPPLY"] = to_int(call(addr, sel("FREE_SUPPLY()")))
    r["FREE_PER_WALLET"] = to_int(call(addr, sel("FREE_PER_WALLET()")))
    r["MAX_SUPPLY"] = to_int(call(addr, sel("MAX_SUPPLY()")))
    r["PRICE"] = to_int(call(addr, sel("PRICE()")))
    r["mintOpen"] = to_int(call(addr, sel("mintOpen()")))
    r["AGENT_ID"] = dec_addr(call(addr, sel("AGENT_ID()")))
    r["owner"] = dec_addr(call(addr, sel("owner()")))
    r["owner_in_discards"] = (r["owner"] or "").lower() in disc_owners if r["owner"] else None
    r["freeLeft_user"] = to_int(call(addr, sel("freeLeft(address)") + enc_addr(USER)))
    r["freeUsed_user"] = to_int(call(addr, sel("freeUsed(address)") + enc_addr(USER)))
    r["mintedBy_user"] = to_int(call(addr, sel("mintedBy(address)") + enc_addr(USER)))
    r["quote_user_1"] = to_int(call(addr, sel("quote(address,uint256)") + enc_addr(USER) + enc_u256(1)))
    r["freeFor_user_1"] = to_int(call(addr, sel("freeFor(address,uint256)") + enc_addr(USER) + enc_u256(1)))
    r["balanceOf_user"] = to_int(call(addr, sel("balanceOf(address)") + enc_addr(USER)))
    uri_raw = call(addr, sel("contractURI()"))
    r["contractURI_raw"] = dec_str(uri_raw)
    if r["contractURI_raw"]:
        s = r["contractURI_raw"]
        try:
            if s.startswith("data:application/json;base64,"):
                r["contractURI_json"] = json.loads(base64.b64decode(s.split(",", 1)[1]).decode())
            else:
                r["contractURI_json"] = None
        except Exception as e:
            r["contractURI_json"] = {"decode_error": str(e)[:100]}
    if r["freeClaimed"] is not None and r["FREE_SUPPLY"]:
        r["freePct"] = round(100.0 * r["freeClaimed"] / r["FREE_SUPPLY"], 2)
    out[name] = r
    print(name, json.dumps(r), flush=True)

json.dump(out, open(BASE + "/run-2026-11-08-1931-stronglead-verify.json", "w"), indent=1)
print("DONE")
