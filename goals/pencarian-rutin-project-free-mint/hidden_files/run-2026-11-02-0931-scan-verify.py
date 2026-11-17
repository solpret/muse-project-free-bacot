import sys, json
sys.path.insert(0,"/home/hatch/workspace/fast_exec")
sys.path.insert(0,"/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=str(e)[:100]
    return None,err
def iv(v):
    try: return int(v,16) if v else None
    except: return None
def words(v):
    if not v: return None
    b=bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
ZERO="0x"+"0"*64
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
out={}
for addr in ["0x74798228c7D4223029e3be6e44Dd06b925b6154D","0x6F0BBF213593244F2904Bbd89D3405eD5B3acF9F","0x3D03bd74e0Aaf3ee160315a13805236E55b9A973"]:
    logs=[]; frm=131060000; to_end=131161793
    while frm<=to_end:
        to=min(frm+1999,to_end)
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":frm,"toBlock":to,"address":addr.lower(),"topics":[TRANSFER,ZERO]},timeout=30)
        logs+=body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
        frm=to+1
    d={}
    for name,arg in [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:]),("name()",""),("symbol()","")]:
        v,e=call(addr,sel(name)+arg); d[name]=iv(v)
    v,e=call(addr,sel("quote(address,uint256)")+enc_addr(USER)[2:]+enc_uint(1)[2:]); d["quote"]=words(v)
    v,e=call(addr,sel("AGENT_ID()")); d["AGENT_ID_raw"]=v
    v,e=call(addr,sel("agentRegistry()")); d["agentRegistry_raw"]=v
    out[addr]={"pre_window_mint_logs":len(logs),"pre_window_first_block":int(sorted(logs,key=lambda l:int(l["blockNumber"],16))[0]["blockNumber"],16) if logs else None,"state":d}
    print(addr,"pre-window mints:",len(logs),"first:",out[addr]["pre_window_first_block"],"state:",d)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0931-scan-verify.json","w"),indent=1)
