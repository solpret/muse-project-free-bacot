#!/usr/bin/env python3
"""Leg 3 for 4 S1 contracts found in 0024 feed (identical 104-fn NFT template).
Reads name/symbol/supply/free counters/price/slot/owner/registry via eth_call."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/"]
ADDRS = ["0x030C38417FCB34714E3124c61EAb22Bc539D7e4C",
         "0x309fc27Eb11634716EaB23BCa97d614Ebc923E21",
         "0x98DcfdeB5e015bbB3c9ACa2a90Ba0EE80E35315b",
         "0x09a713Bd5b2c76ff3cE15b653f4f80645B3c93b5"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
VIEWS = [("name","name()","str"),("symbol","symbol()","str"),
 ("totalSupply","totalSupply()","u"),("freeMinted","freeMinted()","u"),
 ("FREE_MINT_BONUS","FREE_MINT_BONUS()","u"),
 ("MAX_MINT_BONUS","MAX_MINT_BONUS()","u"),
 ("MAX_MINT_EMISSION","MAX_MINT_EMISSION()","u"),
 ("MAX_SUPPLY","MAX_SUPPLY()","u"),
 ("mintActive","mintActive()","u"),
 ("currentPrice","currentPrice()","u"),
 ("priceFor_user","priceFor(address)","u","addr"),
 ("freeUsed_user","freeUsed(address)","u","addr"),
 ("holdsAgentId_user","holdsAgentId(address)","u","addr"),
 ("mintCount_user","mintCount(address)","u","addr"),
 ("balanceOf_user","balanceOf(address)","u","addr"),
 ("owner","owner()","addr"),
 ("agentIdRegistry","agentIdRegistry()","addr"),
 ("baseURI","baseURI()","str"),
 ("divineMinted","divineMinted()","u"),
 ("deckRemaining","deckRemaining()","u"),
 ("commonsRemaining","commonsRemaining()","u"),
 ("MAX_PER_WALLET","MAX_PER_WALLET()","u")]
def dec_str(h):
    if not h or not h.startswith("0x"): return None
    try:
        b = bytes.fromhex(h[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception: return None
def dec_u(h):
    if not h or not h.startswith("0x"): return None
    try: return int(h, 16)
    except Exception: return None
out = {}
for a in ADDRS:
    calls = []
    for v in VIEWS:
        arg = enc_addr(USER) if len(v) > 3 and v[3] == "addr" else ""
        calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_call",
                      "params":[{"to":a,"data":sel(v[1])+arg},"latest"]})
    res = None
    for rpc in RPCS:
        p = subprocess.run(["curl","-s","--max-time","25","-X","POST",rpc,
            "-H","Content-Type: application/json","--data",json.dumps(calls)],
            capture_output=True, text=True)
        try:
            r = json.loads(p.stdout)
            if isinstance(r, list) and len(r) == len(calls): res = r; break
        except Exception: pass
    d = {"address": a}
    if res is None:
        d["_err"] = "all-rpc-fail"; out[a] = d; continue
    for v, resp in zip(VIEWS, res):
        raw = resp.get("result") if isinstance(resp, dict) else None
        if raw is None: d[v[0]] = None; continue
        if v[2] == "str": d[v[0]] = dec_str(raw)
        elif v[2] == "addr":
            d[v[0]] = "0x" + raw[-40:] if len(raw) >= 42 else raw
        else: d[v[0]] = dec_u(raw)
    out[a] = d
    print(json.dumps(d, indent=1), flush=True)
json.dump(out, open("hot-leg-2026-11-11-0024-leg3.json","w"), indent=1)
