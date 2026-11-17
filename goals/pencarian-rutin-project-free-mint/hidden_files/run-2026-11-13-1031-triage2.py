#!/usr/bin/env python3
"""Triage2 run 2026-11-13 10:31: Royal Rush Agents 0x2e34 follow-up.
Read AGENT_ID_REGISTRY(), token(), tokenURI(1), freeClaimedByAgent(agentId),
paidMinted, mintedCount; retry first-mint getLogs in 100-block chunks."""
import json, subprocess, time, base64
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
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
def call(ep, data):
    r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call",
                      "params":[{"to":ADDR,"data":data},"latest"]}, timeout=20)
    return r.get("result")
VIEWS = [("AGENT_ID_REGISTRY","AGENT_ID_REGISTRY()"),("token","token()"),
 ("paidMinted","paidMinted()"),("mintedCount","mintedCount()"),
 ("freeClaimedByAgent_user","freeClaimedByAgent(uint256)",enc_u(AGENT_ID)),
 ("tokenURI_1","tokenURI(uint256)",enc_u(1))]
def main():
    t0=time.time(); out={"address":ADDR,"views":{},"raw":{}}
    for key,sig,*rest in VIEWS:
        data=sel(sig)+(rest[0] if rest else "")
        res=None; err=None
        for ep in EPS:
            try:
                res=call(ep,data); break
            except Exception as e:
                err=str(e)[:80]
        out["raw"][key]=res
        if res and res!="0x":
            w=words(res)
            if key=="tokenURI_1":
                try:
                    b=bytes.fromhex(res[2:])
                    ln=int.from_bytes(b[32:64],"big")
                    out["views"][key]=b[64:64+ln].decode("utf-8","replace")
                except Exception as e:
                    out["views"][key]="decode-error "+str(e)[:60]
            elif key in ("AGENT_ID_REGISTRY","token"):
                out["views"][key]="0x"+res[-40:]
            else:
                out["views"][key]=w[0] if w and len(w)==1 else w
        else:
            out["views"][key]=None
            if err: out.setdefault("errors",{})[key]=err
    # tokenURI may be base64 JSON - decode
    tu=out["views"].get("tokenURI_1") or ""
    if tu.startswith("data:application/json;base64,"):
        try:
            out["tokenURI_json"]=json.loads(base64.b64decode(tu.split(",",1)[1]))
        except Exception as e:
            out["tokenURI_decode_error"]=str(e)[:100]
    # first-mint logs, 100-block chunks over last 1000 blocks
    TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ZERO="0x"+"00"*32
    try:
        hb=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
        head=int(hb.get("result"),16); out["head"]=head
    except Exception as e:
        out["head_error"]=str(e)[:100]; head=None
    logs=[]; out["log_chunks"]=[]
    if head:
        for start in range(head-999, head, 100):
            p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
                "fromBlock":hex(start),"toBlock":hex(min(start+99,head)),
                "address":ADDR,"topics":[TRANSFER,ZERO]}]}
            try:
                r=post_rpc(EPS[0],p,timeout=20)
                res=r.get("result")
                if isinstance(res,list):
                    out["log_chunks"].append({"from":start,"to":min(start+99,head),"n":len(res)})
                    logs.extend(res)
                else:
                    out["log_chunks"].append({"from":start,"to":min(start+99,head),"error":str(r)[:100]})
            except Exception as e:
                out["log_chunks"].append({"from":start,"to":min(start+99,head),"error":str(e)[:100]})
    if logs:
        logs.sort(key=lambda l:int(l["blockNumber"],16))
        first=logs[0]
        out["first_mint"]={"block":int(first["blockNumber"],16),"tx":first.get("transactionHash"),
                           "count_in_window":len(logs)}
        try:
            b=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                "params":[first["blockNumber"],False]},timeout=15)
            ts=int((b.get("result") or {}).get("timestamp","0x0"),16)
            import datetime
            out["first_mint"]["wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception as e:
            out["first_mint"]["ts_error"]=str(e)[:100]
    else:
        out["first_mint"]=None
    out["elapsed_s"]=round(time.time()-t0,1)
    print(json.dumps(out,indent=1))
    json.dump(out,open(BASE+"run-2026-11-13-1031-triage2.json","w"),indent=1)
if __name__=="__main__":
    main()
