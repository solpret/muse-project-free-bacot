#!/usr/bin/env python3
"""Subagent B run 2031 read-only probes: Sourcify-feed agent-shaped contracts
+ Galaxy Agents (Boltbook ZH new). No signing, no preview, no tx."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return ("%064x" % n)
def rpc(method, params):
    for r in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(r, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp: out = json.load(resp)
            if "error" in out: continue
            return out.get("result")
        except Exception:
            continue
    return None
def raw(to, data):
    v = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    if not v or v == "0x": return None
    return v
def call_int(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v
def call_str(to, sig):
    v = raw(to, sel(sig))
    if v is None: return None
    try:
        b = bytes.fromhex(v[2:])
        # abi string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return v
def addr_of(v):
    if v and len(v) >= 42: return "0x" + v[-40:]
    return v
def wei_str(n):
    if n is None: return None
    return n / 1e18

out = {}
out["head"] = rpc("eth_blockNumber", [])
if out["head"]: out["head"] = int(out["head"], 16)

TARGETS = {
 "SALE-32cc": "0x32cc8c5036943Dc0DbC3E238F86cF365390AC4FF",
 "NFT-3C5C": "0x3C5CD8F1AD75f80F94509eE4D5A7C6EDf7405e9C",
 "NFT-3D1F": "0x3D1F1DAd36DFe781ee813B8d7fe8aF69f332f620",
 "NFT-8d22": "0x8d22b007b404EF49bDCdB9819e0981D9eD514E8D",
 "SALE-4731": "0x4731f2816290168f6b894D4c391527fFB767ffB9",
 "SALE-bC8b": "0xbC8b1b791C81EC97024632Ac05ED27a71F5392Aa",
 "MEME-Fe8F": "0xFe8FEAb233Bed23818C5Aa86B7ab9d3Ef4BD7777",
 "GALAXY": "0xa388bba8e4ed07043bae8cc68a00e9aec42f72f4",
}
for label, a in TARGETS.items():
    d = {}
    d["name"] = call_str(a, "name()")
    d["symbol"] = call_str(a, "symbol()")
    d["totalSupply"] = call_int(a, "totalSupply()")
    d["totalMinted"] = call_int(a, "totalMinted()")
    d["spotsLeft"] = call_int(a, "spotsLeft()")
    d["MAX_SUPPLY"] = call_int(a, "MAX_SUPPLY()")
    d["CAP"] = call_int(a, "CAP()")
    d["PRICE"] = call_int(a, "PRICE()")
    d["FREE_SHARES"] = call_int(a, "FREE_SHARES()")
    d["TOKENS_PER_SHARE"] = call_int(a, "TOKENS_PER_SHARE()")
    d["launched"] = call_int(a, "launched()")
    d["decimals"] = call_int(a, "decimals()")
    reg = raw(a, sel("AGENT_REGISTRY()"))
    d["AGENT_REGISTRY"] = addr_of(reg)
    reg2 = raw(a, sel("AGENT_ID()"))
    d["AGENT_ID"] = addr_of(reg2)
    d["mintedBy_user"] = call_int(a, "mintedBy(address)", enc(USER))
    d["balanceOf_user"] = call_int(a, "balanceOf(address)", enc(USER))
    # quote variants: quote(uint256) then quote(address,uint256)
    d["quote_1"] = call_int(a, "quote(uint256)", enc_u(1))
    d["quote_user_1"] = call_int(a, "quote(address,uint256)", enc(USER) + enc_u(1))
    d["bnbQuote_user_1"] = call_int(a, "bnbQuote(address,uint256)", enc(USER) + enc_u(1))
    d["pair"] = addr_of(raw(a, sel("pair()")))
    if label == "SALE-32cc":
        d["WEBSITE"] = call_str(a, "WEBSITE()")
        d["TWITTER"] = call_str(a, "TWITTER()")
        d["PER_SPOT"] = call_int(a, "PER_SPOT()")
        d["totalSpotsMinted"] = call_int(a, "totalSpotsMinted()")
        d["MAX_SPOTS"] = call_int(a, "MAX_SPOTS()")
    if label == "GALAXY":
        code = rpc("eth_getCode", [a, "latest"])
        d["code_len"] = len(code) - 2 if code else None
        d["code_has_registry_bytes"] = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower())
        d["code_has_zero_addr_bytes"] = ("0000000000000000000000000000000000000000" in (code or "").lower())
    out[label] = d
    print(label, json.dumps(d), flush=True)

json.dump(out, open("run-2026-11-05-2031-probe.json", "w"), indent=1)
print("saved run-2026-11-05-2031-probe.json head=", out["head"])
