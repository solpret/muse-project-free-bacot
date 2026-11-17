#!/usr/bin/env python3
"""Run 0331 Boltbook-leg verification: Bearlambo RLAM + Wezards MAGES distributor.
Read-only. Sourcify ABI shape-check (S1/S2) + key on-chain views via fast_rpc."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race, call_many
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT=["mint","mintfree","claimfree","claim","mintagent","buyshare","buyshares","purchase"]
QUOTE=["quote","quotefor","cost","costfor","getcost","price","mintprice","feefor"]
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount","freetokens","freeperwallet"]
GATE=["agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"]
def curl_json(url, timeout=20):
    try:
        r=subprocess.run(["curl","-sS","--max-time",str(timeout),"-A","free-mint-web/1.0",url],capture_output=True,text=True,timeout=timeout+10)
        if r.returncode!=0: return None,f"curl rc={r.returncode}"
        if not r.stdout.strip(): return None,"empty"
        return json.loads(r.stdout),None
    except Exception as e: return None,f"{type(e).__name__}: {e}"[:120]
def fetch_abi(addr):
    for att in (1,2):
        d,err=curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",20)
        if d is not None:
            abi=d.get("abi")
            if isinstance(abi,list): return abi,"verified"
            return None,"not_verified"
        time.sleep(1)
    return None,"transport-failed"
def classify(abi):
    ns=[e.get("name","").lower() for e in abi if isinstance(e,dict) and e.get("type")=="function"]
    fn=[e.get("name","") for e in abi if isinstance(e,dict) and e.get("type")=="function"]
    has_mint=any(any(m in n for m in MINT) for n in ns)
    has_quote=any(any(q in n for q in QUOTE) for n in ns)
    has_free=any(any(fv in n for fv in FREE_VIEWS) for n in ns)
    has_gate=any(any(g in n for g in GATE) for n in ns)
    has_token=any(x in ns for x in ("name","symbol","decimals","totalsupply"))
    noarg_free=any(f.lower() in ("mintfree","claimfree") for f in fn)
    return {"mint":has_mint,"quote":has_quote,"free_view":has_free,"agent_gate":has_gate,
      "is_token":has_token,"noarg_free":noarg_free,
      "S1":bool(has_mint and has_quote and has_free and has_gate),
      "S2":bool(has_token and noarg_free and has_free and has_gate),
      "mint_fns":[f for f in fn if "mint" in f.lower() or "claim" in f.lower()],
      "quote_fns":[f for f in fn if any(q in f.lower() for q in QUOTE)],
      "free_views":[f for f in fn if any(fv in f.lower() for fv in FREE_VIEWS)],
      "gate_fns":[f for f in fn if any(g in f.lower() for g in GATE)],
      "fn_count":len(fn),
      "all_fns":fn}
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def call(addr, sig, args=""):
    try:
        r=race("eth_call",[{"to":addr,"data":sel(sig)+args},"latest"],timeout=15)
        return r
    except Exception as e:
        return f"ERROR: {e}"
out={}
for label,addr in [("Bearlambo-RLAM","0xcb43cd9ac0a157820a44a49465494f300f37f1da"),
                   ("Wezards-MAGES-distributor","0xbD709301473aC208f1bc4be598aE53295d311459")]:
    abi,status=fetch_abi(addr)
    rec={"address":addr,"sourcify":status}
    if status=="verified":
        rec.update(classify(abi))
    out[label]=rec
    print(label,addr,status,"S1=",rec.get("S1"),"S2=",rec.get("S2"),flush=True)
    if status=="verified":
        print("  fns:",rec.get("all_fns"),flush=True)
# on-chain views
head=int(race("eth_blockNumber",[]),16)
out["_block"]=head
print("head",head,flush=True)
RLAM="0xcb43cd9ac0a157820a44a49465494f300f37f1da"
views={
 "name()":call(RLAM,"name()"),"symbol()":call(RLAM,"symbol()"),"decimals()":call(RLAM,"decimals()"),
 "totalSupply()":call(RLAM,"totalSupply()"),"balanceOf(user)":call(RLAM,"balanceOf(address)",enc(USER)),
 "agentRegistry()":call(RLAM,"agentRegistry()"),"AGENT_ID()":call(RLAM,"AGENT_ID()"),
 "freeMinted()":call(RLAM,"freeMinted()"),"FREE_SUPPLY()":call(RLAM,"FREE_SUPPLY()"),
 "freeClaimed(address)":call(RLAM,"freeClaimed(address)",enc(USER)),
 "mintOpen()":call(RLAM,"mintOpen()"),
}
for k,v in views.items():
    iv=to_int(v) if isinstance(v,str) and v.startswith("0x") else v
    print("RLAM",k,"=",iv if iv is not None else v,flush=True)
out["Bearlambo-RLAM"]["views"]={k:(to_int(v) if isinstance(v,str) and v.startswith("0x") and len(v)<=66 else v) for k,v in views.items()}
MAGES="0xbD709301473aC208f1bc4be598aE53295d311459"
mviews={
 "name()":call(MAGES,"name()"),"nftContract()":call(MAGES,"nftContract()"),"token()":call(MAGES,"token()"),
 "nft()":call(MAGES,"nft()"),"mageToken()":call(MAGES,"mageToken()"),"rewardToken()":call(MAGES,"rewardToken()"),
 "totalSupply()":call(MAGES,"totalSupply()"),"balanceOf(user)":call(MAGES,"balanceOf(address)",enc(USER)),
 "agentRegistry()":call(MAGES,"agentRegistry()"),"claimFree(uint256)":None,
}
for k,v in mviews.items():
    if v is None: continue
    iv=to_int(v) if isinstance(v,str) and v.startswith("0x") else v
    print("MAGES",k,"=",iv if iv is not None else (v[:80] if isinstance(v,str) else v),flush=True)
out["Wezards-MAGES-distributor"]["views"]={k:v for k,v in mviews.items() if v is not None}
json.dump(out,open(f"{BASE}/run-2026-11-07-0331-bearlambo-wezards.json","w"),indent=1)
print("wrote run-2026-11-07-0331-bearlambo-wezards.json",flush=True)
