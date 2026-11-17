#!/usr/bin/env python3
"""Run 0331 web leg — Sourcify ABI shape-check (S1/S2), curl-based, read-only."""
import json, subprocess, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-07-0331"
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
targets=[ ("0x31e43b72F14FEA00A576e84c4e3605d98A317777","sourcify-feed-new-0331"),
 ("0x5a152B632513D2603575D6209f44d3ecf28EF791","sourcify-feed-new-0331"),
 ("0x8f784A767407A5C9E48b175E0E7393498e074847","sourcify-feed-new-0331"),
 ("0xe5839480727788c41c1Be7D8DdC08532Efe53259","sourcify-feed-new-0331"),
 ("0x30CB761ef3B1Ac13037597a940D4261a64910b42","sourcify-feed-new-0331"),
 ("0xB8b0E6933A31C80b86772E2149dfF5D2405E506C","sourcify-feed-new-0331"),
 ("0xdD811804A59BdA07f394f5d6Ecd1947E07fD22F3","sourcify-feed-new-0331"),
 ("0x79cd174ca3eC25C06FF5fdDAE365643f73d77777","sourcify-feed-new-0331"),
 ("0x1b1d8625E0Ef7B1759cCA3A333329A208Ffb96Ea","sourcify-feed-new-0331"),
 ("0xF88BCD4e76ce5eF677D5F4B42bDe1Dd7C9771071","sourcify-feed-new-0331"),
 ("0x8A4b7e255A1afba925A4c8378e410763a17d18a7","sourcify-feed-new-0331"),
 ("0xb35606f225Ed6a207a6afE0d61Dcf37D7CeAa5c1","sourcify-feed-new-0331"),
 ("0xAe9230F154F7fC38edeFe6404cE1e37478DAa6AE","sourcify-feed-new-0331"),
 ("0xBe6bf0c9CbBF487BF3fAe80bEc31B3A5f8229BcA","sourcify-feed-new-0331"),
 ("0x4d2A0e951D5C640950D28E8f6e8b5c4271948B33","sourcify-feed-new-0331"),
 ("0x8dc4Cf3546339a1Ba93A2C1670207E6D40B1e63f","sourcify-feed-new-0331"),
 ("0xB7C251A232d3Fb483071A37E56A3cDD6a2Ec4cf5","sourcify-feed-new-0331"),
 ("0x43C8f55B12391671d1F00b04BA1Ef6D1842E7777","sourcify-feed-new-0331"),
 ("0x35A59e7bb346e5f379b0AE84dE1c4A00bd65e164","sourcify-feed-new-0331"),
 ("0xbbFFF07D306D68bed1FD39CA823dB2b703a4bC9C","sourcify-feed-new-0331"),
 ("0x4E92A02a99D8e2Cff4e784db4766ea9b32d635A2","sourcify-feed-new-0331"),
 ("0xcb68E9e97e60eEE7F83265738f038caa70Ab8047","sourcify-feed-new-0331"),
 ("0x33Ff545cCdFa316EF08EA724E7551301AD9e0443","sourcify-feed-new-0331"),
 ("0x62F356a488c93a2047C09CaEAD71Cf7cC91E2b1C","sourcify-feed-new-0331"),
 ("0x8b952DBeb7Ca9c31917645b249f48bab2798ed21","sourcify-feed-new-0331"),
 ("0x7a3A47683715A3932faCe168d6Df23989f47276f","sourcify-feed-new-0331"),
 ("0x3d1201EA0d559E7071bc42d24E1494c6D7547777","sourcify-feed-new-0331"),
 ("0x1efc924004f0D8674f9707825dA9d57bf0Cc0Dd3","sourcify-feed-new-0331"),
 ("0x77F4C608B2B1961DC6eF1fCE0751388bc93D3673","sourcify-feed-new-0331"),
 ("0xCBFF2895eCCd21AA0DBc07BBF911897049D25555","sourcify-feed-new-0331"),
 ("0xEAE0936E2f9ECb0a1Acac8C5B9E43f86D3d37777","sourcify-feed-new-0331"),
 ("0xbdB9D4815408c06A23A1AA027d3307850AA8450c","sourcify-feed-new-0331"),
 ("0xca6d3F2fEcD9B496a79dd8778b4619c81cB71418","sourcify-feed-new-0331"),
 ("0xf8146A045b42BA9ee5DEE64437B5b5fd261c6E9b","sourcify-feed-new-0331"),
 ("0x42a643230d82F5C7a42377870F95a1Cd0bB58616","sourcify-feed-new-0331"),
 ("0xA3e315A8C60366b8291391602CC8f408f364EE90","sourcify-feed-new-0331"),
 ("0xDE00b1A492F5c747725DAb78E1D95c15484b08E5","sourcify-feed-new-0331"),
 ("0x889A76E4D48169d0398828A36c57B64298577777","sourcify-feed-new-0331"),
 ("0xC0cbd55a50f2362C3a1C2FA9702d395B0Ab1A7d2","sourcify-feed-new-0331"),
 ("0x003618FD629EeEb37e55647C2bACEA7e5F13E9a8","sourcify-feed-new-0331"),
 ("0xe78fD25696220Cc066206Fb1389a069208960a40","sourcify-feed-new-0331"),
 ("0xCB5F006e61770B07f810aa04F201aaCB8e499a86","sourcify-feed-new-0331"),
 ("0xAE421450a9755972B6ff71C00416F0f537875687","sourcify-feed-new-0331"),
 ("0x42491EFdffe0aEa61799D12b79CFe6aD2A977777","sourcify-feed-new-0331")
]
out=[shape_check(a,l) for a,l in targets]
json.dump(out,open(f"{BASE}/run-{TS}-sourcify-shape.json","w"),indent=1)
print("wrote run-%s-sourcify-shape.json"%TS)
