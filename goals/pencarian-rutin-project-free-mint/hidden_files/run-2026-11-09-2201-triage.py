#!/usr/bin/env python3
"""Run 2201 triage: AGENT CORE 0xf4bacf30, Agent Miner 0x8670e990, Eon Agent 0x9d619eb8,
Riddle Run 0x92473d34, Gryphlume 0x8ea465ab. Read-only; never previews/mints."""
import json, subprocess
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def ti(v):
    try:
        return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_call(addr, data):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    return ti(raw_call(addr, data))
def call2(addr, sig, a1, a2):
    data = sel(sig) + enc(a1) + enc_u(a2)
    return ti(raw_call(addr, data))
def call_str(addr, sig):
    r = raw_call(addr, sel(sig))
    if not r or r == "0x": return None
    try:
        b = bytes.fromhex(r[2:])
        off = int.from_bytes(b[0:32],"big"); ln = int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="ignore")
    except Exception: return None
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
VIEWS = ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeSupply()","freeLeft()","mintPrice()","price()","MAX_PER_WALLET()","balanceOf(address)","freeClaimed(address)","freeMinted(address)","hasMinted(address)","mintedBy(address)"]
EXTRA = ["owner()","mintStart()","startTime()","SALE_START()","launchTime()","freeSharesRemaining()","saleActive()","opened()"]
out = {"block": block(), "items": {}}
ITEMS = [("AGENT-CORE-f4ba","0xf4bacf30fb8f69373f63d99c657f53dd7774af1d"),
         ("AgentMiner-8670","0x8670e99062ead2ce5402754aede769602fdf38b8"),
         ("EonAgent-9d61","0x9d619eb8d97a746c962ff8defbe3a85d6804b0cf"),
         ("RiddleRun-9247","0x92473d34f017a342ccbc4119b6ef0ef00daa4ee8"),
         ("Gryphlume-8ea4","0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c")]
for name, addr in ITEMS:
    d = {}
    for v in VIEWS:
        base = v.split("(")[0]
        key = base + ("_user" if "(address)" in v else "")
        d[key] = call(addr, v, USER if "(address)" in v else None)
    for v in EXTRA:
        d[v.split("(")[0]] = call(addr, v)
    d["freeOf_user_1"] = call2(addr, "freeOf(address,uint256)", USER, 1)
    d["costOf_user_1"] = call2(addr, "costOf(address,uint256)", USER, 1)
    d["mintsLeft_user"] = call(addr, "mintsLeft(address)", USER)
    d["freeLeft_user"] = call(addr, "freeLeft(address)", USER)
    d["freeUsed_user"] = call(addr, "freeUsed(address)", USER)
    d["owner_addr"] = raw_call(addr, sel("owner()"))
    if d["owner_addr"]:
        try: d["owner_addr"] = "0x" + d["owner_addr"][-40:]
        except Exception: pass
    c = code(addr)
    d["code_len"] = len(c)-2 if c else None
    d["registry_bytes"] = (REG in (c or "").lower()) if c else None
    d["name_str"] = call_str(addr, "name()")
    d["symbol_str"] = call_str(addr, "symbol()")
    out["items"][name] = d
    print(name, json.dumps(d), flush=True)
print("BLOCK", out["block"])
json.dump(out, open("run-2026-11-09-2201-triage.json","w"), indent=1)
print("TRIAGE DONE", flush=True)
