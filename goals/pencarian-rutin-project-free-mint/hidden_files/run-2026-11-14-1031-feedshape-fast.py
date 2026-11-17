#!/usr/bin/env python3
"""Fast ABI-only S1/S2 shape-check for the 8 remaining new addresses (run 1031).
The full feedshape job was killed at ~430s (egress too slow for 6 RPC calls/addr);
ABI shape is the discriminator; on-chain confirmation only for any S1/S2 hit.
Read-only; writes run-2026-11-14-1031-feedshape-fast.json."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed"}
REMAIN = [("0x50A4ffAF7A1Fc22f648895924f7525eF32A54cF4","2026-11-14T03:19:07Z"),
 ("0x7143467fd3Bc5e4358cfaf1Da71833aDB15657CC","2026-11-14T03:17:37Z"),
 ("0x3ee8689F5566d079Ed068823471e034A470bAC63","2026-11-14T03:15:23Z"),
 ("0x2296367f74b2ec266cf4667d98501ae7110f5a58","boltbook-1031 Pickhash"),
 ("0x4bfc32d8ea0981739f328ce8e16bb7398bafa4e0","boltbook-1031 BAGENT-miner-12Nov"),
 ("0xc755f66b7873e53bb4f006956e49a1c8daf66930","boltbook-1031 BAGENT-miner-13Nov"),
 ("0xdb7257dbf18ca1539159c64534ffd68ef14c2f32","boltbook-1031 ARCADEWARDEN"),
 ("0xe4eE5375910C692a0316D800063250ad0db69359","boltbook-1031 BAGENT-miner-today")]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl","-sS","-m","30","-A","Mozilla/5.0",url],
                           capture_output=True, text=True, timeout=40)
        if p.returncode != 0 or not p.stdout:
            return addr, None, f"curl rc={p.returncode}"
        return addr, json.loads(p.stdout).get("abi", []), None
    except Exception as e:
        return addr, None, f"{type(e).__name__}: {str(e)[:100]}"
t0=time.time(); results=[]
with ThreadPoolExecutor(max_workers=8) as ex:
    for addr, abi, err in ex.map(lambda t: fetch(t[0]), REMAIN):
        vat = dict(REMAIN)[addr]
        if abi is None:
            results.append({"address":addr,"verifiedAt":vat,"S1":None,"S2":None,"error":err,"status":"abi-fetch-failed"})
            print(addr,"ABI FAILED",err,flush=True); continue
        names=set(); fns={}
        for e in abi:
            if e.get("type")=="function":
                names.add(e["name"]); fns.setdefault(e["name"],[]).append(e)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID_REGISTRY","agentIdRegistry","AGENT_ID"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1=bool(has_mint and has_quote and free_views and agent_ref)
        s2=bool(is_token and mintfree and (names & {"freeClaimed","freeMinted"}) and (names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref)
        results.append({"address":addr,"verifiedAt":vat,"S1":s1,"S2":s2,"has_mint":has_mint,
                        "has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,
                        "is_token":is_token,"n_fns":len(names),"status":"checked"})
        print(addr,"S1",s1,"S2",s2,"mint",has_mint,"quote",has_quote,"free",free_views,"agent",agent_ref,"n",len(names),flush=True)
out={"started_wib":"2026-11-14T10:31+07:00","shapes":results,"elapsed_s":round(time.time()-t0,1)}
json.dump(out,open("run-2026-11-14-1031-feedshape-fast.json","w"),indent=1)
print("DONE elapsed",out["elapsed_s"])
