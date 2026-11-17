#!/usr/bin/env python3
"""Triage run 2026-11-13 10:31: 0x2e34 (Sourcify feed-new, agent-shaped NFT
candidate: mintFree + free views + agent). Read NFT views in one batch +
first-mint Transfer-from-zero via bsc-dataseed eth_getLogs (direct, read-only;
Ankr is down, this is a per-contract log read, not the chain-wide scan)."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
ADDR = "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def words(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception:
        return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
VIEWS = [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
 ("freeMinted","freeMinted()"),("freeRemaining","freeRemaining()"),
 ("FREE_MAX","FREE_MAX()"),("FREE_TOKEN_REWARD","FREE_TOKEN_REWARD()"),
 ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintStart","mintStart()"),
 ("mintOpensAt","mintOpensAt()"),("agentIdRegistry","agentIdRegistry()"),
 ("registry","registry()"),("owner","owner()"),("price","price()"),
 ("mintPrice","mintPrice()"),("name","name()"),("symbol","symbol()"),
 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
 ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
 ("freeClaimedByAgent_user","freeClaimedByAgent(uint256)",enc_u(AGENT_ID)),
 ("holdsAgentId_user","holdsAgentId(address)",enc_addr(USER))]
def main():
    t0=time.time(); out={"address":ADDR,"started_wib":"2026-11-13T10:31+07:00","views":{}}
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call",
            "params":[{"to":ADDR,"data":sel(sig)+(rest[0] if rest else "")},"latest"]}
           for i,(key,sig,*rest) in enumerate(VIEWS)]
    for ep in EPS:
        try:
            r=post_rpc(ep,calls)
            if not isinstance(r,list) or len(r)!=len(calls): continue
            for it,(key,sig,*rest) in zip(r,VIEWS):
                if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x":
                    out["views"][key]=None; continue
                w=words(it["result"])
                out["views"][key]=w[0] if w is not None and len(w)==1 else w
            out["endpoint"]=ep; break
        except Exception as e:
            out.setdefault("errors",[]).append(str(e)[:80])
    # first-mint logs via dataseed eth_getLogs, chunked 1000 blocks back to 4000
    TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ZERO="0x"+"00"*32
    try:
        hb=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
        head=int(hb.get("result"),16); out["head"]=head
    except Exception as e:
        out["head_error"]=str(e)[:100]; head=None
    logs=[]; out["log_chunks"]=[]
    if head:
        for start in range(head-4000, head, 1000):
            p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
                "fromBlock":hex(start),"toBlock":hex(min(start+999,head)),
                "address":ADDR,"topics":[TRANSFER,ZERO]}]}
            try:
                r=post_rpc(EPS[0],p,timeout=25)
                res=r.get("result")
                if isinstance(res,list):
                    out["log_chunks"].append({"from":start,"to":min(start+999,head),"n":len(res)})
                    logs.extend(res)
                else:
                    out["log_chunks"].append({"from":start,"to":min(start+999,head),"error":str(r)[:120]})
            except Exception as e:
                out["log_chunks"].append({"from":start,"to":min(start+999,head),"error":str(e)[:120]})
    if logs:
        logs.sort(key=lambda l:int(l["blockNumber"],16))
        first=logs[0]; out["first_mint"]={"block":int(first["blockNumber"],16),
            "tx":first.get("transactionHash"),"count_in_window":len(logs)}
        try:
            b=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                "params":[first["blockNumber"],False]},timeout=15)
            ts=int((b.get("result") or {}).get("timestamp","0x0"),16)
            out["first_mint"]["timestamp"]=ts
            import datetime
            out["first_mint"]["wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception as e:
            out["first_mint"]["ts_error"]=str(e)[:100]
    else:
        out["first_mint"]=None
    out["elapsed_s"]=round(time.time()-t0,1)
    print(json.dumps(out,indent=1))
    json.dump(out,open(BASE+"run-2026-11-13-1031-triage.json","w"),indent=1)
if __name__=="__main__":
    main()
