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
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=str(e)[:120]
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
for addr in ["0x61C360b0fA3fef5c61728756e0fb574c66D73663","0x06aB825D14454174819E1c08a6E72C4b5bBF78fE"]:
    # address-filtered getLogs from 131060000 to latest, chunked
    head=int(_single(EPS[0],"eth_blockNumber",[],8,retries=0),16)
    logs=[]; frm=131060000
    while frm<=head:
        to=min(frm+1999,head)
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":frm,"toBlock":to,"address":addr.lower(),"topics":[TRANSFER,ZERO]},timeout=30)
        logs+=body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
        frm=to+1
    logs_sorted=sorted(logs,key=lambda l:int(l["blockNumber"],16))
    first=logs_sorted[0] if logs_sorted else None
    first_ts=None
    if first:
        blk=_single(EPS[0],"eth_getBlockByNumber",[first["blockNumber"],False],8,retries=0)
        first_ts=int(blk["timestamp"],16)
    import datetime
    fw=None
    if first_ts: fw=datetime.datetime.fromtimestamp(first_ts,datetime.timezone(datetime.timedelta(hours=7))).isoformat()
    tests=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:]),("name()",""),("symbol()","")]
    d={}
    for name,arg in tests:
        v,e=call(addr,sel(name)+arg); d[name]={"int":iv(v),"raw":v,"error":e}
    v,e=call(addr,sel("quote(address,uint256)")+enc_addr(USER)[2:]+enc_uint(1)[2:]); d["quote_user_1"]={"words":words(v),"raw":v,"error":e}
    v,e=call(addr,sel("AGENT_ID()")); d["AGENT_ID"]={"int":iv(v),"raw":v,"error":e}
    out[addr]={"head":head,"logs_count":len(logs_sorted),"distinct_minters":len({l["topics"][2] for l in logs_sorted}),"first_block":int(first["blockNumber"],16) if first else None,"first_wib":fw,"state":d}
    print(addr, "logs",len(logs_sorted),"minters",out[addr]["distinct_minters"],"first",out[addr]["first_block"],fw)
    print("  totalSupply",d["totalSupply()"]["int"],"freeClaimed",d["freeClaimed()"]["int"],"FREE_SUPPLY",d["FREE_SUPPLY()"]["int"],"MAX",d["MAX_SUPPLY()"]["int"],"mintOpen",d["mintOpen()"]["int"],"mintedBy",d["mintedBy(address)"]["int"],"freeUsed",d["freeUsed(address)"]["int"],"bal",d["balanceOf(address)"]["int"],"quote",d["quote_user_1"]["words"],"AGENT_ID",d["AGENT_ID"]["raw"])
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0931-verify-new.json","w"),indent=1)
