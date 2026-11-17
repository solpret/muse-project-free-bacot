#!/usr/bin/env python3
"""Verify the 2 new S1 passes from feed shape-check (run 2331): free pool,
user slot/quote, launch-time views. Read-only; no preview/mint."""
import json, subprocess, datetime
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr, data, timeout=25):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout)
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data, key = sel(sig)+enc(USER), base+"_user"
        else: data, key = sel(sig), base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {k: (None if isinstance(it, dict) and "error" in it else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(res, keys)}
        except Exception: continue
    return None
VIEWS = ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","freeLeft()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)","mintedBy(address)","mintStart()","saleStart()","saleEnd()","mintOpenedAt()","freePoolSize()","totalFreeCount()","paidMinted()","PRICE()","price()","freeSharesRemaining()","freeRemaining()"]
TARGETS = {"S1-Ff65": "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
           "S1-4367": "0x4367b86F889014e6fD57fE812B86A581b913C645"}
out = {}
for name, addr in TARGETS.items():
    d = {"address": addr}
    # ABI fn list (for quote signature + name/symbol)
    try:
        r = subprocess.run(["curl","-sL","--max-time","30",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=35)
        meta = json.loads(r.stdout)
        fns = [(f.get("name"), ",".join(i.get("type","") for i in f.get("inputs",[]))) for f in meta.get("abi",[]) if f.get("type")=="function"]
        d["fns"] = fns
        d["name_fns"] = [f for f in fns if f[0] in ("name","symbol","decimals","quote","mint","mintFree","freeMint","claimFreeShare","freeSharesRemaining","freeRemaining")]
    except Exception as e:
        d["abi_error"] = str(e)[:120]
    got = batch(addr, VIEWS)
    d.update(got or {"_batch_fail": True})
    # quote attempts: quote(uint256) and quote(address,uint256)
    for sig, data in (("quote(uint256)", sel("quote(uint256)")+enc_u(1)),
                      ("quote(address,uint256)", sel("quote(address,uint256)")+enc(USER)+enc_u(1))):
        raw = call(addr, data)
        d[sig] = raw
    # name/symbol via eth_call (string decode)
    for fn in ("name()","symbol()"):
        raw = call(addr, sel(fn))
        if raw and len(raw) > 130:
            try:
                ln = int(raw[130:194], 16)
                d[fn] = bytes.fromhex(raw[194:194+ln*2]).decode(errors="replace")
            except Exception: d[fn] = raw[:66]
        else: d[fn] = raw
    out[name] = d
    print(name, json.dumps(d, indent=None)[:1500], flush=True)
json.dump(out, open(BASE+"run-2026-11-11-2331-verify-s1new.json","w"), indent=1)
print("VERIFY-S1NEW DONE")
