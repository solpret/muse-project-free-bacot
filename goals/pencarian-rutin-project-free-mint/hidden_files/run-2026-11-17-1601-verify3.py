#!/usr/bin/env python3
"""Run 1601 triage: Abyssora 0x4785, Mine Card 0xf8a7, $BTCB-ish 0x75f1.
Sourcify shape check + on-chain reads. Read-only."""
import json, subprocess, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    return (to, d)
def curl_batch(calls, timeout=15):
    out=[]
    for i in range(0, len(calls), 5):
        chunk=calls[i:i+5]
        payload=[{"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for j,(t,d) in enumerate(chunk)]
        r=subprocess.run(["curl","-s","--max-time",str(timeout),"https://bsc-dataseed.binance.org/","-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
        resp=json.loads(r.stdout.decode()); by={it["id"]:it for it in resp if isinstance(it,dict)}
        for j in range(len(chunk)):
            it=by.get(j+1,{})
            if "result" in it and it["result"] not in (None,"0x"):
                try: out.append(int(it["result"],16))
                except Exception: out.append(it["result"])
            else: out.append(None)
    return out
TARGETS = {
 "Abyssora": "0x4785e7b396d13fb23b50bd66a6f828797c862770",
 "Mine Card": "0xf8a72c4538cd9d570b2c771f01a0d561a90a64eb",
 "BTCB-scan": "0x75f1756ACD90153fF624F44fDc24a86d0e6DB793",
}
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
out={}
for name, addr in TARGETS.items():
    # Sourcify
    try:
        try: raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        except Exception:
            r=subprocess.run(["curl","-s","-L","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,timeout=25)
            raw=r.stdout
        meta=json.loads(raw.decode()); abi=meta.get("abi",[])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns)
        out[name]={"address":addr,"sourcify":"verified","verifiedAt":meta.get("verifiedAt"),
            "n_fns":len(names),
            "has_mint":any(n.lower().startswith("mint") for n in names),
            "mint_fns":sorted(n for n in names if n.lower().startswith("mint")),
            "has_quote":bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"}),
            "free_views":sorted(names & FREE_VIEWS),
            "agent_ref":bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"}),
            "is_token":bool(names & {"name","symbol","decimals","totalSupply"}),
            "name_fn":None}
    except Exception as e:
        out[name]={"address":addr,"sourcify":"UNVERIFIED/failed","error":f"{type(e).__name__}: {str(e)[:120]}"}
    # on-chain reads
    views=[("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
           ("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),
           ("freeLeft","freeLeft()",None),("freeRemaining","freeRemaining()",None),
           ("MAX_SUPPLY","MAX_SUPPLY()",None),("FREE_SUPPLY","FREE_SUPPLY()",None),
           ("mintOpen","mintOpen()",None),("mintActive","mintActive()",None),
           ("name","name()",None),("symbol","symbol()",None),
           ("balanceOf_user","balanceOf(address)","user"),
           ("freeClaimed_user","freeClaimed(address)","user"),
           ("mintedBy_user","mintedBy(address)","user")]
    calls=[call(addr,sig,arg) for _,sig,arg in views]
    try:
        res=curl_batch(calls)
    except Exception as e:
        res=[None]*len(calls); out[name]["read_error"]=str(e)[:150]
    rd={}
    for (label,_,_),v in zip(views,res):
        if label in ("name","symbol") and isinstance(v,str):
            try:
                b=bytes.fromhex(v[2:] if v.startswith("0x") else v)
                # ABI string decode
                if len(b)>=64:
                    off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[32:64],"big")
                    rd[label]=b[off:off+ln].decode(errors="replace")
                else: rd[label]=v
            except Exception: rd[label]=v
        else: rd[label]=v
    out[name]["reads"]=rd
    # head block
    try:
        r=subprocess.run(["curl","-s","--max-time","10","https://bsc-dataseed.binance.org/","-H","Content-Type: application/json","-d",'[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}]'],capture_output=True,timeout=15)
        out[name]["block"]=int(json.loads(r.stdout.decode())[0]["result"],16)
    except Exception: pass
json.dump(out, open(f"{HF}/run-2026-11-17-1601-verify3.json","w"), indent=1)
print(json.dumps(out, indent=1))
