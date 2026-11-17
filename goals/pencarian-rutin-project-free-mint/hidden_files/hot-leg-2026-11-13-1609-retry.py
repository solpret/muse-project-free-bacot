#!/usr/bin/env python3
"""Retry 1609 followup: chunked (<=24) single-batch re-read of the 2 probe-possible-sale contracts."""
import json, subprocess
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
TARGETS = ["0x6430594F2C40A4374f2EfEdF034C77065DC4CC7D",
           "0xEa98b2065d43c0DE0Ad8629F5D0A08fDABcc708A"]
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def curl(url, data=None, timeout=25):
    cmd = ["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0"]
    if data is not None: cmd += ["-H","Content-Type: application/json","-d",data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
VIEWS = ["freeMinted","FREE_SLOTS","FREE_SUPPLY","freeClaimed","mintOpen","saleOpen","saleStart","totalSupply","name"]
calls, keys = [], []
for a in TARGETS:
    for fn in VIEWS:
        uarg = fn=="freeClaimed"
        calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_call",
                      "params":[{"to":a,"data":sel(fn+"(address)" if uarg else fn+"()")+(USER_PAD if uarg else "")},"latest"]})
        keys.append((a, fn+("_user" if uarg else "")))
assert len(calls) <= 24, len(calls)
body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(calls), timeout=25)
reads, errs = {}, {}
if body:
    try:
        resp = json.loads(body); items = resp if isinstance(resp,list) else [resp]
        by_id = {it.get("id"): it for it in items if isinstance(it,dict)}
        for cid,(a,fn) in enumerate(keys):
            it = by_id.get(cid,{})
            r = it.get("result"); v=None
            if r and r!="0x":
                try: v=int(r[-64:],16)
                except Exception:
                    try: v=bytes.fromhex(r[2:]).decode(errors="ignore").strip("\x00")
                    except Exception: v="unparsed"
            reads.setdefault(a,{})[fn]=v
            if it.get("error"): errs[f"{a}:{fn}"]=it["error"]
    except Exception as e: errs["parse"]=str(e)
else: errs["fetch"]="fetch-failed"
out={"run":"retry-1609","reads":reads,"errors":errs}
for a in TARGETS:
    r=reads.get(a,{}) or {}
    fm,fs,fsup=r.get("freeMinted"),r.get("FREE_SLOTS"),r.get("FREE_SUPPLY")
    pool=None
    if fm is not None and fs is not None: pool=fs-fm
    elif fm is not None and fsup is not None: pool=fsup-fm
    out.setdefault("derived",{})[a]={"free_pool_remaining":pool,"freeMinted":fm,
        "FREE_SLOTS":fs,"FREE_SUPPLY":fsup,"slot_user_freeClaimed":r.get("freeClaimed_user"),
        "mintOpen":r.get("mintOpen"),"saleOpen":r.get("saleOpen"),"saleStart":r.get("saleStart"),
        "totalSupply":r.get("totalSupply"),"name":r.get("name")}
seen=json.load(open(f"{HF}/hot-leg-seen.json"))
for a in TARGETS:
    e=seen.get(a,{})
    e["retry_1609"]=out["derived"][a]
    # age still unverified (no saleStart/mintStart readable + no first-mint corroboration)
    e["status"]="watchlist-only-age-unverified"
    e["note"]="probe-possible-sale (freeMinted+AGENT_ID_REGISTRY+mintOpen); pool/slot/age NOT verified this run (RPC reads NULL in followup+retry) - watchlist-only, never lead, never preview/mint"
    seen[a]=e
json.dump(seen, open(f"{HF}/hot-leg-seen.json","w"), indent=1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1609-retry.json","w"), indent=1)
print(json.dumps(out, indent=1))
