#!/usr/bin/env python3
"""Focused track-C re-checks run 1801: opened/launched + S2 free views.
Read-only; writes run-2026-11-09-1831-trackc-focus.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return None if v in (None, "0x") else int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    # views: list of (key, sig, argkind) argkind: None | 'user' | ('uint', n) | ('bytes32user',)
    calls, keys = [], []
    for i,(key,sig,arg) in enumerate(views):
        data = sel(sig)
        if arg == 'user': data += enc_addr(USER)
        elif isinstance(arg, tuple) and arg[0]=='uint': data += enc_u(arg[1])
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
OUT = {"block": block(), "items": {}}
print("BLOCK", OUT["block"], flush=True)
CHECKS = {
 "DROID": ("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", [
    ("opened","opened()",None),("freeMinted","freeMinted()",None),
    ("FREE_SHARES","FREE_SHARES()",None),("totalMinted","totalMinted()",None),
    ("paused","paused()",None)]),
 "OSK": ("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", [
    ("opened","opened()",None),("totalMinted","totalMinted()",None),
    ("FREE_SHARES","FREE_SHARES()",None),("freeMinted","freeMinted()",None),
    ("saleStart","saleStart()",None),("saleEnd","saleEnd()",None)]),
 "IMARS": ("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", [
    ("opened","opened()",None),("freeMinted","freeMinted()",None),
    ("FREE_SHARES","FREE_SHARES()",None),("totalMinted","totalMinted()",None)]),
 "NIULAI": ("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", [
    ("launched","launched()",None),("freeClaimed","freeClaimed()",None),
    ("freeShares","freeShares()",None),("phase","phase()",None)]),
 "KillZero": ("0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97", [
    ("launched","launched()",None),("totalFreeClaimed","totalFreeClaimed()",None),
    ("FREE_SHARES","FREE_SHARES()",None),("totalMintCount","totalMintCount()",None)]),
 "0x260bf39a": ("0x260bf39a6f3aB5E459856297178CC0DF6003374a", [
    ("launched","launched()",None),("launchTime","launchTime()",None),
    ("FREE_SLOTS","FREE_SLOTS()",None),("freeClaimed","freeClaimed()",None),
    ("freeClaimed_user","freeClaimed(address)",'user')]),
 "BoxBigem": ("0x3Ee92296D663378D42521273aAA4779BDa8e25dD", [
    ("freeMinted","freeMinted()",None),("freeRemaining","freeRemaining()",None),
    ("FREE_POOL","FREE_POOL()",None),("mintStart","mintStart()",None),("mintEnd","mintEnd()",None)]),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", [
    ("freeCount","freeCount()",None),("FREE_SLOTS","FREE_SLOTS()",None),
    ("FREE_SUPPLY","FREE_SUPPLY()",None),("freeByAddress_user","freeByAddress(address)",'user')]),
 "FANBEIMAO": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", [
    ("freeCap","freeCap()",None),("freeSold","freeSold()",None),
    ("isFreeOpen","isFreeOpen()",None)]),
}
for name,(addr,views) in CHECKS.items():
    t0=time.time()
    got = batch(addr, views)
    OUT["items"][name] = {"address": addr, "views": got}
    print(name, got, f"({time.time()-t0:.1f}s)", flush=True)
json.dump(OUT, open(f"{BASE}/run-2026-11-09-1831-trackc-focus.json","w"), indent=1)
print("TRACKC FOCUS DONE")
