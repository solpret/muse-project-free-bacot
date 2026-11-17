#!/usr/bin/env python3
"""Follow-up 1609: verify the 2 probe-possible-sale contracts from the Sourcify feed.
Reads: free pool views, user slot, saleStart/mintOpen, name/symbol; Sourcify ABI+metadata
for shape (S1/S2) and verifiedAt. Read-only except hot-leg-seen.json status update."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
TARGETS = ["0x6430594F2C40A4374f2EfEdF034C77065DC4CC7D",
           "0xEa98b2065d43c0DE0Ad8629F5D0A08fDABcc708A"]
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def curl(url, data=None, timeout=20):
    cmd = ["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0"]
    if data is not None: cmd += ["-H","Content-Type: application/json","-d",data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
VIEWS = ["freeMinted","FREE_SLOTS","FREE_SUPPLY","FREE_AMOUNT","freeClaimed",
         "mintOpen","saleOpen","saleStart","mintStart","freeLeft","freeSharesRemaining",
         "name","symbol","totalSupply","agentRegistry","contractURI"]
calls, keys = [], []
for a in TARGETS:
    for fn in VIEWS:
        uarg = fn in ("freeClaimed",)
        data = sel(fn+"(address)" if uarg else fn+"()") + (USER_PAD if uarg else "")
        calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_call",
                      "params":[{"to":a,"data":data},"latest"]})
        keys.append((a, fn+("_user" if uarg else "")))
body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(calls), timeout=30)
reads = {}
if body:
    try:
        resp = json.loads(body); items = resp if isinstance(resp,list) else [resp]
        by_id = {it.get("id"): it for it in items if isinstance(it,dict)}
        for cid,(a,fn) in enumerate(keys):
            r = by_id.get(cid,{}).get("result")
            v = None
            if r and r!="0x":
                try: v = int(r[-64:],16)
                except Exception:
                    try: v = bytes.fromhex(r[2:]).decode(errors="ignore").strip("\x00")
                    except Exception: v = "unparsed"
            reads.setdefault(a,{})[fn]=v
    except Exception as e: reads["error"]=str(e)
else: reads["error"]="rpc-fetch-failed"
out = {"run":"followup-1609","reads":reads}
# Sourcify ABI + metadata per contract
for a in TARGETS:
    meta = curl(f"https://sourcify.dev/server/v2/contract/56/{a}", timeout=20)
    info = {}
    if meta:
        try:
            m = json.loads(meta)
            info["verifiedAt"] = m.get("stdJson",{}).get("creationMatch") or m.get("creationMatch")
            src = m.get("stdJson",{}) or {}
            info["contractName"] = src.get("settings",{}).get("compilationTarget") if isinstance(src,dict) else None
            abi = []
            try:
                abi = json.loads(m.get("metadata",{}).get("output",{}).get("abi","[]")) if isinstance(m.get("metadata"),dict) else []
            except Exception: pass
            # simpler: fetch files tree for abi
            info["has_abi_in_meta"] = bool(abi)
        except Exception as e: info["meta_error"]=str(e)
    else: info["meta_error"]="fetch-failed"
    # ABI via sourcify files endpoint
    ab = curl(f"https://sourcify.dev/server/v2/contract/56/{a}/files/abi.json", timeout=20)
    fns = []
    if ab:
        try:
            abj = json.loads(ab)
            fl = abj if isinstance(abj,list) else abj.get("abi",[])
            fns = sorted({f.get("name") for f in fl if isinstance(f,dict) and f.get("type")=="function"})
        except Exception as e: info["abi_error"]=str(e)
    else: info["abi_error"]="fetch-failed"
    info["functions"]=fns
    out.setdefault("sourcify",{})[a]=info
# derived
for a in TARGETS:
    r = reads.get(a,{}) or {}
    fm, fs, fsup = r.get("freeMinted"), r.get("FREE_SLOTS"), r.get("FREE_SUPPLY")
    pool = None
    if fm is not None and fs is not None: pool = fs - fm
    elif fm is not None and fsup is not None: pool = fsup - fm
    out.setdefault("derived",{})[a]={
        "free_pool_remaining": pool,
        "freeMinted": fm, "FREE_SLOTS": fs, "FREE_SUPPLY": fsup,
        "FREE_AMOUNT": r.get("FREE_AMOUNT"), "freeLeft": r.get("freeLeft"),
        "freeSharesRemaining": r.get("freeSharesRemaining"),
        "slot_user_freeClaimed": r.get("freeClaimed_user"),
        "mintOpen": r.get("mintOpen"), "saleOpen": r.get("saleOpen"),
        "saleStart": r.get("saleStart"), "mintStart": r.get("mintStart"),
        "name": r.get("name"), "symbol": r.get("symbol"),
        "totalSupply": r.get("totalSupply")}
    # update seen entry with verification note (watchlist-only until age verified)
    seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    e = seen.get(a, {})
    e["followup_1609"] = out["derived"][a]
    e["status"] = "watchlist-only-age-unverified" if pool is None or pool is not None else e.get("status")
    seen[a]=e
    json.dump(seen, open(f"{HF}/hot-leg-seen.json","w"), indent=1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1609-followup.json","w"), indent=1)
print(json.dumps(out, indent=1))
