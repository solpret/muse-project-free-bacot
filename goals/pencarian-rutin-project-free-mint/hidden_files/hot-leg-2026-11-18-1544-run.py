#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-18 15:44 WIB. Legs 1-4 + bridge, read-only.
Writes hot-leg-run-2026-11-18-1544.json + -reread.json; updates hot-leg-seen.json ONLY.
Leg4 targeted re-read (same 4 items as 1539 run): DGF totalMinted, BinanceAI launched,
AlphaPulse V1 totalSupply, FABE freeSharesRemaining + user share + launched."""
import json, re, subprocess, time
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
assert len(REGISTRY[2:]) == 40, "registry literal wrong length"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
RPC_URL = "https://bsc-dataseed.binance.org/"

def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    elif arg == "one": d += "%064x" % 1
    elif arg == "user1": d += enc_addr(USER) + "%064x" % 1
    return d
def curl_json(url, payload, timeout=20):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),url,
                        "-H","Content-Type: application/json","-d",json.dumps(payload)],
                       capture_output=True, timeout=timeout+5)
    if r.returncode != 0 or not r.stdout: raise IOError(f"curl rc={r.returncode}")
    return json.loads(r.stdout.decode())
def rpc_batch(calls, timeout=12):
    payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call",
              "params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)]
    resp=curl_json(RPC_URL,payload,timeout=timeout)
    if not isinstance(resp,list): raise IOError(f"non-list: {str(resp)[:150]}")
    by={it["id"]:it for it in resp if isinstance(it,dict)}
    out=[]
    for i in range(len(calls)):
        it=by.get(i+1,{})
        if "result" in it and it["result"] not in (None,"0x"):
            try: out.append(int(it["result"],16))
            except Exception: out.append(it["result"])
        elif "error" in it: out.append(f"err:{it['error']}")
        else: out.append(None)
    return out
def rpc_chunked(calls, chunk=5):
    out=[]; errs=[]
    for i in range(0,len(calls),chunk):
        try: out+=rpc_batch(calls[i:i+chunk])
        except Exception as e:
            errs.append(f"calls {i}-{i+len(calls[i:i+chunk])-1}: {type(e).__name__}: {str(e)[:150]}")
            out+=[None]*len(calls[i:i+chunk])
    return out,errs

seen=json.load(open(f"{HF}/hot-leg-seen.json")); seen_l={k.lower() for k in seen}
out={"run":"free-mint-hot-leg 2026-11-18 15:44 WIB","started_wib":now_wib}

# Leg 1 Sourcify feed
try:
    r=subprocess.run(["curl","-s","-L","--max-time","15",
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
        capture_output=True, timeout=25)
    feed=json.loads(r.stdout.decode())
    items=feed if isinstance(feed,list) else feed.get("results",feed.get("contracts",[]))
    addrs=[]
    for it in items:
        a=it.get("address") or (it.get("contract") or {}).get("address")
        if a: addrs.append((a,it.get("verifiedAt")))
    new1=[(a,v) for a,v in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    out["leg1_sourcify"]={"total":len(addrs),"new":len(new1),
        "new_contracts":[a for a,_ in new1],
        "verified_window":[addrs[-1][1] if addrs else None, addrs[0][1] if addrs else None]}
except Exception as e:
    out["leg1_sourcify"]={"error":f"{type(e).__name__}: {e}"}; new1=[]

# Leg 2 Boltbook EN+ZH
def boltbook(lang):
    url="https://boltbook.fun/"+("?lang=zh" if lang=="zh" else "")
    path=f"{HF}/hot-leg-2026-11-18-1544-boltbook-{lang}.html"
    for _try in range(2):
        r=subprocess.run(["curl","-s","-L","-A","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "--max-time","12",url,"-o",path,"-w","%{http_code}"],capture_output=True,text=True,timeout=20)
        code=r.stdout.strip()
        try:
            html=open(path,encoding="utf-8",errors="replace").read()
            if len(html)>1000: break
        except Exception: html=""
    addrs=sorted(set(re.findall(r"0x[0-9a-fA-F]{40}",html)))
    new=[a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED and a.lower()!=REGISTRY.lower()]
    return {"bytes":len(html),"http_code":code,"addresses":len(addrs),
            "new":len(new),"new_contracts":new,
            "free_kw":len(re.findall(r"free",html,re.I)),
            "zh_free_kw":len(re.findall("免费",html))}
for lang in ("en","zh"):
    try: out[f"leg2_boltbook_{lang}"]=boltbook(lang)
    except Exception as e: out[f"leg2_boltbook_{lang}"]={"error":f"{type(e).__name__}: {e}"}

# Leg 3 shape-check new contracts
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
            "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape_check(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r=subprocess.run(["curl","-s","-L","--max-time","20",url],capture_output=True,timeout=25)
        meta=json.loads(r.stdout.decode()); abi=meta.get("abi",[])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address":addr,"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,
                "free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,
                "n_fns":len(names),"status":"checked","verifiedAt":meta.get("verifiedAt")}
    except Exception as e:
        return {"address":addr,"status":"shape-check-failed","error":f"{type(e).__name__}: {str(e)[:120]}"}
targets=[a for a,_ in new1]
for lang in ("en","zh"):
    targets+=[a for a in out.get(f"leg2_boltbook_{lang}",{}).get("new_contracts",[])]
targets=list(dict.fromkeys(targets))
sc=[shape_check(a) for a in targets]
out["leg3_shape_check"]=sc
out["leg3_sale_shape"]=[s for s in sc if s.get("S1") or s.get("S2")]
seen_added=[]
for s in sc:
    if s.get("status")!="checked": continue
    seen[s["address"]]={"first_seen_wib":now_wib,"source":"sourcify-feed",
        "status":"sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
        "note":json.dumps(s)[:600],"verifiedAt":s.get("verifiedAt")}
    seen_added.append(s["address"])
for a,v in new1:
    if a not in seen:
        seen[a]={"first_seen_wib":now_wib,"source":"sourcify-feed","status":"checked-not-sale-shape",
                 "note":"no shape-check result","verifiedAt":v}; seen_added.append(a)
out["seen_added"]=seen_added; out["seen_n"]=len(seen)
json.dump(seen,open(f"{HF}/hot-leg-seen.json","w"),indent=1)

# Leg 4 targeted re-read
PLAN=[
 ("DGF CARD","0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",
  [("totalMinted","totalMinted()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("BinanceAI","0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched","launched()",None),("failed","failed()",None),
   ("tokenClaimed_user","tokenClaimed(address)","user")]),
 ("AlphaPulse V1","0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",
  [("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None),
   ("balanceOf_user","balanceOf(address)","user")]),
 ("FABE","0xFabE022a5943462fee1Bd221791945DA57510BE8",
  [("freeSharesRemaining","freeSharesRemaining()",None),("launched","launched()",None),
   ("freeSharesClaimed_user","freeSharesClaimed(address)","user"),
   ("totalShares","totalShares()",None)]),
]
calls=[]; meta=[]
for name,addr,views in PLAN:
    for label,sig,arg in views:
        calls.append((addr,encode(sig,arg))); meta.append((name,addr,label))
res,errs=rpc_chunked(calls,chunk=5)
reads={}
for (name,addr,label),val in zip(meta,res):
    reads.setdefault(name,{"address":addr,"views":{}})["views"][label]=val
try:
    blk=curl_json(RPC_URL,[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
    block=int(blk[0]["result"],16)
except Exception as e: block=f"error: {str(e)[:120]}"
reread={"reads":reads,"errors":errs,"n_calls":len(calls),
        "elapsed_s":round(time.time()-T0,1),"block":block,"started_wib":now_wib}
json.dump(reread,open(f"{HF}/hot-leg-run-2026-11-18-1544-reread.json","w"),indent=1)
out["leg4_reread"]={"block":block,"reads":{k:v["views"] for k,v in reads.items()},"errors":errs}
prev={"DGF CARD totalMinted":1639,"BinanceAI launched()":0,"AlphaPulse V1 totalSupply":34,
      "FABE freeSharesRemaining":2821}
cur={"DGF CARD totalMinted":reads["DGF CARD"]["views"].get("totalMinted"),
     "BinanceAI launched()":reads["BinanceAI"]["views"].get("launched"),
     "AlphaPulse V1 totalSupply":reads["AlphaPulse V1"]["views"].get("totalSupply"),
     "FABE freeSharesRemaining":reads["FABE"]["views"].get("freeSharesRemaining")}
out["leg4_changes_vs_1539"]={k:{"prev":prev[k],"now":cur[k]} for k in prev if prev[k]!=cur[k]}
out["leg4_note"]=("DGF age+free% still unverified (no promotion); BinanceAI still not launched; "
  "AlphaPulse V1 age/free% unverified; FABE user already holds 1 share. No sellout, slot loss, "
  "age-exclusion, claim opening, or tier promotion unless changes above show otherwise.")

# Bridge read-only
try:
    bridge=json.load(open(f"{HF}/scan-bridge.json")); contracts=bridge.get("contracts",{})
    snap=json.load(open(f"{HF}/onchain-snapshot.json")); snap_addrs=set()
    for coll in ("contracts","track_c"):
        for k,v in snap.get(coll,{}).items():
            if isinstance(v,dict):
                for f in ("address","sale","token","mint"):
                    if v.get(f): snap_addrs.add(str(v[f]).lower())
    for k,v in snap.get("pending_claims",{}).items():
        if isinstance(v,dict):
            for f in ("mint","token"):
                if v.get(f): snap_addrs.add(str(v[f]).lower())
    not_in=[a for a in contracts if a.lower() not in snap_addrs]
    disc=sum(1 for v in contracts.values() if isinstance(v,dict) and v.get("same_owner_discarded"))
    out["bridge"]={"total":len(contracts),"not_in_snapshot":len(not_in),
                   "same_owner_discarded":disc,
                   "note":"bridge contracts not in snapshot are not reported as new; no bridge promotion/change unless leg4 shows one."}
except Exception as e:
    out["bridge"]={"error":f"{type(e).__name__}: {str(e)[:150]}","note":"bridge skip - run continues"}

out["elapsed_s"]=round(time.time()-T0,1)
out["executions"]="none - no preview, no mint, no claim (read-only run)"
out["result"]=("SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim."
  if not out["leg3_sale_shape"] and not out["leg4_changes_vs_1539"] else "CHANGES FOUND - see leg3/leg4")
json.dump(out,open(f"{HF}/hot-leg-run-2026-11-18-1544.json","w"),indent=1)
print(json.dumps(out,indent=1)[:12000])
