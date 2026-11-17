import json, subprocess
from Crypto.Hash import keccak
ADDR="0xBb9bA68C8E99651450F099C431eb530a71C712bE"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-rpc.publicnode.com/","https://bsc-dataseed1.bnbchain.org/"]
def rpc(ep,method, params, timeout=60):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",p],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
ZERO="0x"+"0"*64
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
for ep in EPS:
    try:
        head=int(rpc(ep,"eth_blockNumber",[]).get("result","0x0"),16)
        print(ep,"head",head,flush=True)
        r=rpc(ep,"eth_getLogs",[{"fromBlock":hex(head-2000),"toBlock":hex(head),"address":ADDR,"topics":[TRANSFER,ZERO]}],timeout=60)
        logs=r.get("result")
        print(" mint logs last 2000:", len(logs) if isinstance(logs,list) else r,flush=True)
        if isinstance(logs,list) and logs:
            first=min(logs,key=lambda l:int(l["blockNumber"],16))
            print(" earliest in window block",int(first["blockNumber"],16),flush=True)
            break
        # also unfiltered count
        r2=rpc(ep,"eth_getLogs",[{"fromBlock":hex(head-2000),"toBlock":hex(head),"address":ADDR}],timeout=60)
        l2=r2.get("result")
        print(" all logs last 2000:", len(l2) if isinstance(l2,list) else r2,flush=True)
        if isinstance(l2,list) and l2:
            from collections import Counter
            print(" topics:", Counter([x.get("topics",[None])[0] for x in l2]),flush=True)
            break
    except Exception as e:
        print(ep,"ERR",str(e)[:120],flush=True)
# user-slot views on first working endpoint
for sig in ["freeClaimed(address)","hasFreeMint(address)","freeMintedFor(address)","claimedFree(address)","hasMintedFree(address)","freeMintsClaimed(address)"]:
    try:
        d=sel(sig)+enc_addr(USER)
        r=rpc(EPS[0],"eth_call",[{"to":ADDR,"data":d},"latest"],timeout=45)
        res=r.get("result")
        print(sig,"=",int(res,16) if res and res!="0x" else r,flush=True)
    except Exception as e:
        print(sig,"ERR",str(e)[:80],flush=True)
