import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x03c63ecadf8e0da8377a13aacb28a2a2301181ae"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def build(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        elif isinstance(a,str) and a.startswith("0x"): d+=enc_u(int(a,16))
        else: d+=enc_u(int(a))
    return d
def post(ep,payload,timeout=120):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
U=[USER]
VIEWS=[("name","name()",[]),("symbol","symbol()",[]),("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),("freeLeft","freeLeft()",[]),
("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CAP","FREE_CAP()",[]),("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
("mintOpen","mintOpen()",[]),("mintStart","mintStart() ",[]),("mintStartTime","mintStartTime() ",[]),
("priceFor_user_1","priceFor(address,uint256)",[USER,1]),("costOf_user_1","costOf(address,uint256)",[USER,1]),
("quote_user_1","quote(address,uint256)",[USER,1]),("mintPrice","mintPrice()",[]),("price","price()",[]),
("mintedBy_user","mintedBy(address)",U),("freeUsed_user","freeUsed(address)",U),("freeClaimed_user","freeClaimed(address)",U),
("freeMintedBy_user","freeMintedBy(address)",U),("mintedPerWallet_user","mintedPerWallet(address)",U),
("balanceOf_user","balanceOf(address)",U),("owner","owner()",[]),("AGENT_ID","AGENT_ID()",[]),
("agentRegistry","agentRegistry()",[]),("hasAgentId_user","hasAgentId(address)",U),("paused","paused()",[])]
calls=[]; meta=[]
for key,sig,args in VIEWS:
    sig=sig.strip()
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":ADDR,"data":build(sig,args)},"latest"]})
    meta.append((key,sig))
out={}; ok_ep=None
for ep in EPS:
    try:
        res=post(ep,calls,timeout=120)
        if not isinstance(res,list) or len(res)!=len(calls): print("bad shape",ep,str(res)[:120],flush=True); continue
        for it,(key,sig) in zip(res,meta):
            if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"): out[key]=None
            else:
                r=it["result"]
                if sig in ("name()","symbol()"):
                    try:
                        raw=bytes.fromhex(r[2:])
                        ln=int.from_bytes(raw[32:64],'big'); out[key]=raw[64:64+ln].decode(errors='ignore')
                    except Exception: out[key]=r
                elif len(r)>=66 and key not in ("owner","AGENT_ID","agentRegistry"):
                    out[key]=to_int(r[:66])
                else: out[key]=r
        ok_ep=ep; break
    except Exception as e:
        print("ep fail",ep,str(e)[:100],flush=True); continue
blk=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=60)
        if isinstance(r,dict) and r.get("result"): blk=int(r["result"],16); break
    except Exception: continue
json.dump({"address":ADDR,"via":ok_ep,"block":blk,"views":out},open(BASE+"nero-1331-probe.json","w"),indent=1)
print("via",ok_ep,"block",blk); print(json.dumps(out,indent=1))
