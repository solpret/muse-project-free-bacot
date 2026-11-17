#!/usr/bin/env python3
"""Run 2201 triage-batched: Agent Miner 0x8670e990, Eon Agent 0x9d619eb8,
Riddle Run 0x92473d34, Gryphlume 0x8ea465ab. Batched eth_call (reread pattern).
Read-only; never previews/mints."""
import json, time, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
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
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch_call(addr, datas):
    """datas: list of (key, data). Chunked in 9s (dataseed batch limit)."""
    outd = {}
    for ci in range(0, len(datas), 9):
        chunk = datas[ci:ci+9]
        calls = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":d},"latest"]} for i,(_,d) in enumerate(chunk)]
        got = None
        for ep in EPS:
            try:
                res = post_rpc(ep, calls, timeout=25)
                if isinstance(res, list) and len(res) == len(calls):
                    got = res; break
            except Exception: continue
        for (key,_) in chunk:
            outd[key] = None
        if got:
            for item,(key,_) in zip(got, chunk):
                r = item.get("result") if isinstance(item,dict) else None
                outd[key] = r if key.endswith("_raw") else (ti(r) if r else None)
    return outd
def code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})
            if isinstance(r,dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
def decode_str(hexstr):
    if not hexstr or hexstr=="0x": return None
    try:
        b=bytes.fromhex(hexstr[2:])
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="ignore")
    except Exception: return None
VIEWS = ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeSupply()","freeLeft()","mintPrice()","price()","MAX_PER_WALLET()","owner()","mintStart()","startTime()","SALE_START()","launchTime()","freeSharesRemaining()","saleActive()","opened()","soldOut()"]
ADDR_VIEWS = ["balanceOf(address)","freeClaimed(address)","freeMinted(address)","hasMinted(address)","mintedBy(address)","mintsLeft(address)","freeLeft(address)","freeUsed(address)"]
ITEMS = [("AgentMiner-8670","0x8670e99062ead2ce5402754aede769602fdf38b8"),
         ("EonAgent-9d61","0x9d619eb8d97a746c962ff8defbe3a85d6804b0cf"),
         ("RiddleRun-9247","0x92473d34f017a342ccbc4119b6ef0ef00daa4ee8"),
         ("Gryphlume-8ea4","0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c")]
out = {"block": block(), "items": {}}
def triage(item):
    name, addr = item
    t=time.time()
    datas=[]
    for v in VIEWS:
        datas.append((v.split("(")[0], sel(v)))
    for v in ADDR_VIEWS:
        datas.append((v.split("(")[0]+"_user", sel(v)+enc(USER)))
    datas.append(("freeOf_user_1", sel("freeOf(address,uint256)")+enc(USER)+enc_u(1)))
    datas.append(("costOf_user_1", sel("costOf(address,uint256)")+enc(USER)+enc_u(1)))
    datas.append(("owner_raw", sel("owner()")))
    datas.append(("name_raw", sel("name()")))
    datas.append(("symbol_raw", sel("symbol()")))
    d = batch_call(addr, datas)
    d["owner_addr"] = ("0x"+d["owner_raw"][-40:]) if d.get("owner_raw") else None
    d["name_str"] = decode_str(d.get("name_raw"))
    d["symbol_str"] = decode_str(d.get("symbol_raw"))
    c = code(addr)
    d["code_len"] = len(c)-2 if c else None
    d["registry_bytes"] = (REG in (c or "").lower()) if c else None
    print(name, json.dumps(d), f"({time.time()-t:.1f}s)", flush=True)
    return name, d
with ThreadPoolExecutor(max_workers=4) as ex:
    for name, d in ex.map(triage, ITEMS):
        out["items"][name] = d
print("BLOCK", out["block"])
json.dump(out, open(f"{BASE}/run-2026-11-09-2201-triage2.json","w"), indent=1)
print("TRIAGE2 DONE", flush=True)
