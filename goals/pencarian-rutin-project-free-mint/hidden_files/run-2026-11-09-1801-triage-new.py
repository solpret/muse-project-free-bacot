#!/usr/bin/env python3
"""Triage new contracts run 1801 (Boltbook + sweep finds). Read-only.
Writes run-2026-11-09-1801-triage-new.json."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return None if v in (None, "0x") else int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data = sel(sig) + enc(USER); key = base + "_user"
        else: data = sel(sig); key = base
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
def code(addr):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}, timeout=25)
            c = r.get("result")
            if isinstance(c, str): return c
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
def sourcify(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                     headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r: d = json.load(r)
        abi = d.get("abi") or []
        fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type")=="function"]
        return {"match": d.get("match"), "verifiedAt": d.get("verifiedAt"), "fns": fns}
    except Exception as e:
        return {"error": str(e)[:150]}
VIEWS = ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()",
         "MAX_SUPPLY()","mintOpen()","mintStart()","mintEnd()","balanceOf(address)",
         "freeClaimed(address)","owner()","name()","symbol()"]
TARGETS = {
 "Onyx Agent": "0x23ff20cd84d16d7c1ce53a29c7d2c726de8cbb3d",
 "TIME CARDS Genesis": "0xc5624B61beE1971E6Aa3AB5f403236Ab32C2B6cd",
 "Neon District": "0x796958fa68fc760b70adba01d082d73e4478c042",
 "ALL ACCESS": "0xc3ce00677dad113f5d466d46c8c7b3a227855a5b",
 "Swarm Agent": "0xD612Ded8F2b4818c0A9d2465f06eBf1B745f0E17",
 "ENIGMAAGENT": "0x213A879D11a85b54483CEA2cdEC5D9026958Add3",
}
out = {"block": block(), "targets": {}}
print("BLOCK", out["block"], flush=True)
for name, addr in TARGETS.items():
    t0 = time.time()
    got = batch(addr, VIEWS)
    c = code(addr)
    reg = (REG in (c or "").lower()) if c else None
    sf = sourcify(addr)
    d = {"address": addr, "views": got, "code_len": (len(c)-2)//2 if c else None,
         "registry_bytes": reg, "sourcify": sf}
    out["targets"][name] = d
    print(name, "ts=", (got or {}).get("totalSupply"), "free=", (got or {}).get("freeClaimed"),
          "FREE_SUPPLY=", (got or {}).get("FREE_SUPPLY"), "mintOpen=", (got or {}).get("mintOpen"),
          "mintStart=", (got or {}).get("mintStart"), "reg=", reg,
          "sf=", sf.get("match") or sf.get("error"), f"({time.time()-t0:.1f}s)", flush=True)
# ORDIagent sale (track-C): free pool read
ORDI = "0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8"
got = batch(ORDI, ["freeClaimed()","freeMinted()","FREE_SHARES()","totalSupply()","mintOpen()","freeSharesRemaining()","balanceOf(address)"])
out["targets"]["ORDIagent-sale"] = {"address": ORDI, "views": got,
    "sourcify": sourcify(ORDI)}
print("ORDIagent-sale", got, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1801-triage-new.json","w"), indent=1)
print("TRIAGE NEW DONE")
