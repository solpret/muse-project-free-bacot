#!/usr/bin/env python3
"""Run 0301 web leg — Sourcify ABI shape-check (S1/S2), curl-based, read-only."""
import json, subprocess, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-07-0301"
MINT=["mint","mintfree","claimfree","claim","mintagent","buyshare","buyshares","purchase"]
QUOTE=["quote","quotefor","cost","costfor","getcost","price","mintprice","feefor"]
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount","freetokens","freeperwallet"]
GATE=["agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"]
def curl_json(url, timeout=20):
    try:
        r=subprocess.run(["curl","-sS","--max-time",str(timeout),"-A","free-mint-web/1.0",url],capture_output=True,text=True,timeout=timeout+10)
        if r.returncode!=0: return None,f"curl rc={r.returncode} {r.stderr.strip()[:120]}"
        if not r.stdout.strip(): return None,"empty response"
        return json.loads(r.stdout),None
    except Exception as e: return None,f"{type(e).__name__}: {e}"[:120]
def fetch_abi(addr):
    last=""
    for att in (1,2):
        d,err=curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",20)
        if d is not None:
            abi=d.get("abi")
            if isinstance(abi,list): return abi,"verified",f"attempt {att}"
            return None,"not_verified",f"attempt {att}: no abi field (keys={list(d.keys())})"
        last=err or "unknown"
        if "404" in last: return None,"not_verified",last
        time.sleep(1)
    return None,"transport-failed",last
def classify(abi):
    ns=[e.get("name","").lower() for e in abi if isinstance(e,dict) and e.get("type")=="function"]
    fn=[e.get("name","") for e in abi if isinstance(e,dict) and e.get("type")=="function"]
    has_mint=any(any(m in n for m in MINT) for n in ns)
    has_quote=any(any(q in n for q in QUOTE) for n in ns)
    has_free=any(any(fv in n for fv in FREE_VIEWS) for n in ns)
    has_gate=any(any(g in n for g in GATE) for n in ns)
    has_token=any(x in ns for x in ("name","symbol","decimals","totalsupply")) and any(x in ns for x in ("name","symbol"))
    noarg_free=any(f.lower() in ("mintfree","claimfree") for f in fn)
    return {"mint":has_mint,"quote":has_quote,"free_view":has_free,"agent_gate":has_gate,
      "is_token":has_token,"noarg_free":noarg_free,
      "S1":bool(has_mint and has_quote and has_free and has_gate),
      "S2":bool(has_token and noarg_free and has_free and has_gate),
      "mint_fns":[f for f in fn if "mint" in f.lower() or "claim" in f.lower()],
      "quote_fns":[f for f in fn if any(q in f.lower() for q in QUOTE)],
      "free_views":[f for f in fn if any(fv in f.lower() for fv in FREE_VIEWS)],
      "gate_fns":[f for f in fn if any(g in f.lower() for g in GATE)],
      "fn_count":len(fn)}
def shape_check(addr,label):
    abi,status,detail=fetch_abi(addr)
    rec={"address":addr,"label":label,"sourcify":status,"detail":detail}
    if status=="verified":
        rec.update(classify(abi)); rec["verdict"]="SALE-SHAPE-HIT" if (rec["S1"] or rec["S2"]) else "not-sale-shape"
    elif status=="not_verified":
        rec.update({"S1":False,"S2":False,"verdict":"not-sale-shape"})
    else:
        rec.update({"S1":None,"S2":None,"verdict":"shape-check-failed-transport"})
    print(label,addr,status,rec.get("verdict"),"S1=",rec.get("S1"),"S2=",rec.get("S2"))
    return rec
targets=[
 ("0x79cd174ca3eC25C06FF5fdDAE365643f73d77777","sourcify-feed-new-2026-11-06T20:06:36Z"),
 ("0x6288DFe86f22B53eEB6886aE2D78941de7483743","boltbook-en-AGCC-minter"),
 ("0xFe1Bbe79A6Ea942e01722E626097741971c6cf82","SYNTHIA-NFT"),
 ("0xE9F55641e71b026871849955e8181B3A01929685","SYNTHIA-token-SYNTH"),
 ("0x7A3cD992e6aeA95C684d71d1f33511ff1206d9E6","JOLT-token"),
 ("0x63C9d73f09bb7CCD8E363510676Bd9ecD563f8e4","JOLT-claim"),
 ("0xce79Ef82426A72d44C4306e73B06e9e44e7E407B","CHASTLE"),
]
out=[shape_check(a,l) for a,l in targets]
json.dump(out,open(f"{BASE}/run-{TS}-sourcify-shape.json","w"),indent=1)
print("wrote run-%s-sourcify-shape.json"%TS)
