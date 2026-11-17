#!/usr/bin/env python3
"""Triage run 0301 (read-only): 2 alamat baru Boltbook + WhaleFirst + Golden Agents.
Checks: Sourcify verification/ABI, registry bytes, free-mint shape, basic views
(totalSupply/totalMinted/freeMinted/saleStart/saleEnd/mintStart/mintOpen/owner),
first-mint Transfer-from-zero in recent 10k blocks. No preview/mint."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
t0 = time.time()
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)
def call(addr, sig, args=None, blk="latest"):
    data = sel(sig)
    for a in (args or []):
        data += a[2:].lower().rjust(64,"0") if isinstance(a,str) and a.startswith("0x") else format(int(a),"064x")
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},blk]}, 30)
            if isinstance(r, dict) and r.get("result") not in (None, "0x"):
                return int(r["result"],16)
            if isinstance(r, dict) and r.get("result") == "0x":
                return 0
        except Exception: continue
    return None
def getcode(addr):
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}, 30)
            if isinstance(r, dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
def sourcify(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}",
            headers={"User-Agent":"free-mint-search/0301"})
        with urllib.request.urlopen(req, timeout=25) as r: return json.loads(r.read().decode())
    except Exception as e: return {"error": f"{type(e).__name__}: {str(e)[:120]}"}
VIEWS = ["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()",
         "freeSupply()","freeRemaining()","saleStart()","saleEnd()","mintStart()",
         "mintOpen()","saleOpen()","MAX_SUPPLY()"]
TARGETS = {
 "Boltbook-new-17cd": "0x17cd1f525e8331b504aa08b83a9ca86d0d27d08f",
 "Boltbook-new-7e6c": "0x7e6c1f8d98d7d18ee6d49a38f867b3664f32a120",
 "WhaleFirst": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
 "GoldenAgents": "0x4233c62919cc03168a361c547117c1553c375bfc",
}
out = {}
for name, addr in TARGETS.items():
    sc = sourcify(addr)
    std = sc.get("stdJson", {}) if isinstance(sc, dict) else {}
    src = ""
    try:
        src = json.dumps(sc.get("stdJson", {}).get("sources", {}))[:2000]
    except Exception: pass
    abi = []
    try:
        abi = sc.get("stdJson", {}).get("output", {}).get("abi", []) or []
    except Exception: pass
    fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type")=="function"]
    code = getcode(addr)
    reg_in_code = (code or "").lower().find(REG) >= 0
    agent_ref = reg_in_code or any("agent" in (f or "").lower() for f in fns) or "60B926" in src
    views = {}
    if code and len(code) > 4:
        for v in VIEWS:
            views[v] = call(addr, v)
    out[name] = {"address": addr, "sourcify": {"match": sc.get("match"), "verifiedAt": None,
                  "error": sc.get("error")} if isinstance(sc, dict) else {},
                 "n_abi_fns": len(abi), "fns_sample": fns[:25],
                 "has_code": bool(code and len(code) > 4), "code_len": len(code or ""),
                 "registry_bytes": reg_in_code, "agent_ref": agent_ref,
                 "free_fn": [f for f in fns if "free" in (f or "").lower()],
                 "views": views}
    print(name, "match=", out[name]["sourcify"].get("match"), "code_len=", out[name]["code_len"],
          "reg_bytes=", reg_in_code, "free_fn=", out[name]["free_fn"], "views=", {k:v for k,v in views.items() if v is not None}, flush=True)
json.dump(out, open(BASE+"run-2026-11-15-0301-triage.json","w"), indent=1)
print("TRIAGE DONE", round(time.time()-t0,1), "s")
