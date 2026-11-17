#!/usr/bin/env python3
"""Fast ABI-only S1/S2 shape-check for the 8 remaining new addresses (run 1101).
The full feedshape job was killed at ~430s (egress too slow for 6 RPC calls/addr);
ABI shape is the discriminator; on-chain confirmation only for any S1/S2 hit.
Read-only; writes run-2026-11-14-1101-feedshape-fast.json."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed"}
REMAIN = [("0x2Bb3c30BEDe53c44E18805BBffeB51BAD0BAf7BF","2026-11-14T03:56:00Z"),
 ("0x7d5F7f323db3050AF92E9aa1584E883B3b24d680","2026-11-14T03:55:52Z"),
 ("0x98cf202BC682a0009EB2f5517fA3d7B825845142","2026-11-14T03:54:55Z"),
 ("0xeD06B4df81Ebd6832D4A3cE2D1166A3084802022","2026-11-14T03:54:41Z"),
 ("0xE4D5449c08D720040d894D383afB73027aFfab2e","2026-11-14T03:53:36Z"),
 ("0x2786b9F84f42eB61d93172455E00CcD7C47577Cc","2026-11-14T03:52:44Z"),
 ("0xA40A972de2075Ea6d2Aa47B91f2487AC411fA5AD","2026-11-14T03:50:06Z"),
 ("0x86012E976c060BD83CAd2F02491f60e4eEb44D0B","2026-11-14T03:43:48Z"),
 ("0xd91ff38e382AF4085A6be5380eF3adBfAA52A79A","2026-11-14T03:43:31Z"),
 ("0x89a95A7b413Ee91569DF68FdDa5967F7580012AF","2026-11-14T03:43:13Z"),
 ("0xb3e68A75bb06084990030c20d6e4aC8dd74676d8","2026-11-14T03:42:55Z"),
 ("0x9a44d29Fbf44f58E27FAAA6F4C7D6fEf9E0a989A","2026-11-14T03:42:39Z"),
 ("0x9329CF4132c299F4bbc0E2d5AE1247bDDDD0f47e","2026-11-14T03:42:20Z"),
 ("0xCb3fdE98288B1AbE7046db8f570F50ac7F1b812a","2026-11-14T03:42:03Z"),
 ("0x06A8Fc0E8FCdF58529355F9591273eB515CF38BA","2026-11-14T03:41:46Z"),
 ("0x26620bAe9cbBF59B99938f0B966A6A9060876B32","2026-11-14T03:41:29Z"),
 ("0x066bb55e7a4c4e6567ec7eA0700E571aaCDc4390","2026-11-14T03:41:11Z"),
 ("0x89e7BC22f37B6B2D973416Ab075b5F7CebDA4C26","2026-11-14T03:40:55Z")]
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
out={"started_wib":"2026-11-14T11:01+07:00","shapes":results,"elapsed_s":round(time.time()-t0,1)}
json.dump(out,open("run-2026-11-14-1101-feedshape-fast.json","w"),indent=1)
print("DONE elapsed",out["elapsed_s"])
