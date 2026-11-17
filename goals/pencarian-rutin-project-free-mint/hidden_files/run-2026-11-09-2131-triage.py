#!/usr/bin/env python3
"""Run 2131 triage: Nova 0x232816a2, Flare 0xe2deb475, CHIPS 0xb2625d56. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try:
        return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(r, dict) and "result" in r: return ti(r["result"])
        except Exception: continue
    return None
def code(addr):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
VIEWS = ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeSupply()","freeLeft()","mintCount()","MAX_MINTS()","mintPrice()","balanceOf(address)","freeClaimed(address)","freeMinted(address)","hasMinted(address)","quote(address,uint256)","cost(address,uint256)"]
out = {"block": block(), "items": {}}
for name, addr in [("Nova-2328","0x232816a2f556b9448f15f3baa3bf9a988922033d"),
                    ("Flare-e2de","0xe2deb47514bbfd19550866c8820bce04e8a8d416"),
                    ("CHIPS-b262","0xb2625d56a7fc855bf7432b5584b390a4b4d9c7fd")]:
    d = {}
    for v in VIEWS:
        base = v.split("(")[0]
        key = base + ("_user" if "(address)" in v and "uint256" not in v else ("_quote" if "quote" in v or "cost" in v else ""))
        d[key] = call(addr, v, USER if "(address)" in v else None) if "(address)" in v else call(addr, v)
    c = code(addr)
    d["code_len"] = len(c)-2 if c else None
    d["registry_bytes"] = (REG in (c or "").lower()) if c else None
    d["name"] = call(addr, "name()")
    out["items"][name] = d
    print(name, json.dumps(d), flush=True)
print("BLOCK", out["block"])
json.dump(out, open("run-2026-11-09-2131-triage.json","w"), indent=1)
