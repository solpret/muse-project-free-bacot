#!/usr/bin/env python3
"""Subagent B run 2031 LEAN probes (read-only): threaded eth_call, 6s timeout,
one RPC at a time. Replaces the slow sequential probe (killed)."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return "%064x" % n
def rpc_call(rpc, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        out = json.load(resp)
    if "error" in out: raise Exception(str(out["error"])[:80])
    return out.get("result")
def raw(to, data):
    for r in RPCS:
        try:
            v = rpc_call(r, "eth_call", [{"to": to, "data": data}, "latest"])
            if v and v != "0x": return v
        except Exception:
            continue
    return None
def code(to):
    for r in RPCS:
        try:
            v = rpc_call(r, "eth_getCode", [to, "latest"])
            if v: return v
        except Exception:
            continue
    return None
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
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return v
def addr_of(v):
    if v and len(v) >= 42: return "0x" + v[-40:]
    return v

TARGETS = {
 "SALE-32cc": "0x32cc8c5036943Dc0DbC3E238F86cF365390AC4FF",
 "NFT-3C5C": "0x3C5CD8F1AD75f80F94509eE4D5A7C6EDf7405e9C",
 "NFT-3D1F": "0x3D1F1DAd36DFe781ee813B8d7fe8aF69f332f620",
 "NFT-8d22": "0x8d22b007b404EF49bDCdB9819e0981D9eD514E8D",
 "SALE-4731": "0x4731f2816290168f6b894D4c391527fFB767ffB9",
 "SALE-bC8b": "0xbC8b1b791C81EC97024632Ac05ED27a71F5392Aa",
 "GALAXY": "0xa388bba8e4ed07043bae8cc68a00e9aec42f72f4",
}
def probe(item):
    label, a = item
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
    d["mintedBy_user"] = call_int(a, "mintedBy(address)", enc(USER))
    d["balanceOf_user"] = call_int(a, "balanceOf(address)", enc(USER))
    d["quote_1"] = call_int(a, "quote(uint256)", enc_u(1))
    d["quote_user_1"] = call_int(a, "quote(address,uint256)", enc(USER) + enc_u(1))
    d["AGENT_REGISTRY"] = addr_of(raw(a, sel("AGENT_REGISTRY()")))
    d["AGENT_ID"] = addr_of(raw(a, sel("AGENT_ID()")))
    if label == "SALE-32cc":
        d["WEBSITE"] = call_str(a, "WEBSITE()")
        d["TWITTER"] = call_str(a, "TWITTER()")
        d["PER_SPOT"] = call_int(a, "PER_SPOT()")
        d["totalSpotsMinted"] = call_int(a, "totalSpotsMinted()")
        d["MAX_SPOTS"] = call_int(a, "MAX_SPOTS()")
    if label == "GALAXY":
        c = code(a)
        d["code_len"] = (len(c) - 2) // 2 if c else None
        d["code_has_registry_bytes"] = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in (c or "").lower())
    print(label, json.dumps(d), flush=True)
    return label, d

out = {}
try:
    head = None
    for r in RPCS:
        try:
            head = rpc_call(r, "eth_blockNumber", []); break
        except Exception:
            continue
    out["head"] = int(head, 16) if head else None
except Exception as e:
    out["head"] = None
print("head:", out["head"], flush=True)
with ThreadPoolExecutor(max_workers=7) as ex:
    for label, d in ex.map(probe, list(TARGETS.items())):
        out[label] = d
json.dump(out, open("run-2026-11-05-2031-probe.json", "w"), indent=1)
print("saved run-2026-11-05-2031-probe.json")
