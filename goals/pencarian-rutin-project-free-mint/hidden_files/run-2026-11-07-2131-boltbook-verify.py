#!/usr/bin/env python3
"""Run 2131: on-chain verify of 3 NEW Boltbook addresses + ETERNAL.
Read-only eth_call via fast_rpc singles (batch-revert safe).
Sora 0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d
Frost Agent 0x09f893bab23d14ad296a17092c6611aac5a0932b
Paw Gang 0x587c303982187ec578df309d27670327b13202f8
ETERNAL 0xc66afa72a36ddb03e5c1360b9a64c1d08f312845
"""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

ADDRS = {
    "Sora": "0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d",
    "Frost": "0x09f893bab23d14ad296a17092c6611aac5a0932b",
    "PawGang": "0x587c303982187ec578df309d27670327b13202f8",
    "ETERNAL": "0xc66afa72a36ddb03e5c1360b9a64c1d08f312845",
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode())
    return "0x" + k.hexdigest()[:8]

def enc(a):
    return a[2:].lower().rjust(64, "0")

def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None

def dec_addr(v):
    try: return "0x" + v[-40:]
    except Exception: return None

def single(ep, addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])],
              endpoint=ep, timeout=12)
    return r[0]

out = {}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
out["endpoint"] = ep

VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "mintActive()",
         "agentRegistry()", "owner()", "contractURI()", "minter()", "FREE_CAP()",
         "freeSupply()", "freeLeft()", "PRICE()", "startTime()", "START_TIME()"]
for name, addr in ADDRS.items():
    e = {"address": addr}
    for sig in VIEWS:
        base = sig.split("(")[0]
        try:
            v = single(ep, addr, sig)
            if base in ("name", "symbol", "contractURI"):
                e[base] = dec_str(v)
            elif base in ("agentRegistry", "owner", "minter"):
                e[base] = dec_addr(v)
            else:
                e[base] = to_int(v)
        except Exception as ex:
            e[base] = None
            e[base + "_err"] = str(ex)[:100]
    for sig, key in [("balanceOf(address)", "balanceOf_user"),
                     ("freeClaimed(address)", "freeClaimed_user"),
                     ("freeMintedBy(address)", "freeMintedBy_user"),
                     ("mintedBy(address)", "mintedBy_user")]:
        try:
            e[key] = to_int(single(ep, addr, sig, USER))
        except Exception as ex:
            e[key] = None
            e[key + "_err"] = str(ex)[:100]
    # user quote(1) if quote(address,uint256) exists — try quote(user,1)
    try:
        data = sel("quote(address,uint256)") + enc(USER) + (1).to_bytes(32, "big").hex()
        r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])],
                  endpoint=ep, timeout=12)
        e["quote_user1_raw"] = r[0]
    except Exception as ex:
        e["quote_user1_raw"] = None
        e["quote_user1_err"] = str(ex)[:100]
    e["registry_match"] = (e.get("agentRegistry") is not None and
                           e.get("agentRegistry", "").lower() == REG.lower())
    out[name] = e
    print(name, json.dumps(e), flush=True)

json.dump(out, open("run-2026-11-07-2131-boltbook-verify.json", "w"), indent=1)
print("saved run-2026-11-07-2131-boltbook-verify.json block", out["block"])
