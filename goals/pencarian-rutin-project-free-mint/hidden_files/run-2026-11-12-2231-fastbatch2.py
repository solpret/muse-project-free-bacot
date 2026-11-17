#!/usr/bin/env python3
"""Fast-batch retry v2 run 2231: per-contract batches (small), reverts -> None.
One curl per contract; bsc-dataseed then dataseed1 fallback."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
t0 = time.time()
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
TARGETS = {
 "SolNFT": ("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
   ["totalSupply()","totalMinted()","freeMinted()","FREE_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","mintOpensAt()","saleStart()","freeAvailable(address)"]),
 "AgcNFT": ("0xdAc222886b887fC5b6262889B189B8eb57e99794",
   ["totalMinted()","freeMinted()","FREE_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","mintOpensAt()","saleStart()","freeAvailable(address)"]),
 "AgentGenesis-fa22": ("0xfa22065BEc8aebfA2789CFb7F6F1799c1ecf395e",
   ["totalMinted()","freeMinted()","FREE_SUPPLY()","FREE_CAP()","mintOpen()","balanceOf(address)","freeClaimed(address)","mintOpensAt()","saleStart()"]),
 "NOTV-0415": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
   ["totalMinted()","totalSupply()","mintOpen()","mintOpensAt()","saleStart()"]),
 "0x4919-S1": ("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
   ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeUsed(address)","mintedBy(address)","mintStart()","saleStart()","mintOpensAt()","freeAvailable(address)","freeClaimed(address)"]),
}
def one_batch(ep, calls):
    out = subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,
                          "-H","Content-Type: application/json","-d",json.dumps(calls)],
                         capture_output=True,text=True,timeout=30).stdout
    res = json.loads(out)
    if isinstance(res, list) and len(res) == len(calls):
        return res
    return None
out = {"block": None, "reads": {}}
for name, (addr, views) in TARGETS.items():
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call",
                      "params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    res = None
    for ep in EPS:
        try:
            res = one_batch(ep, calls)
            if res is not None: break
        except Exception:
            continue
    if res is None:
        out["reads"][name] = {"error": "BATCH-FAIL"}
        print(name, "BATCH-FAIL", flush=True)
        continue
    d = {}
    for it, key in zip(res, keys):
        d[key] = None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)
    out["reads"][name] = d
    print(name, {k: v for k, v in d.items() if v is not None}, flush=True)
for ep in EPS:
    try:
        r = subprocess.run(["curl","-sL","--max-time","10","-X","POST",ep,
                            "-H","Content-Type: application/json",
                            "-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],
                           capture_output=True,text=True,timeout=15).stdout
        out["block"] = int(json.loads(r)["result"], 16); break
    except Exception:
        continue
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-12-2231-fastbatch.json", "w"), indent=1)
print("BLOCK", out["block"], "ELAPSED", out["elapsed_s"])
