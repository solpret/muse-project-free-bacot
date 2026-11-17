import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,frm=None):
    tx={"to":to,"data":data}
    if frm: tx["from"]=frm
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict): return v
    return int(v,16) if v and v!="0x" else 0
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception as e: return {"decode_error":str(e)}
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
jobs={}
def add(k,addr,fn,frm=None): jobs[k]=(addr,sel(fn),frm)
STAR="0x7d390e37ed41a359f276d8764ca15432704b99b7"
add("STAR_totalSupply",STAR,"totalSupply()"); add("STAR_balance_user",STAR,"balanceOf(address)",USER); add("STAR_freeClaimed_user",STAR,"freeClaimed(address)",USER)
PACT="0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"
add("PACT_sharesMinted",PACT,"sharesMinted()"); add("PACT_freeMinted",PACT,"freeMinted()"); add("PACT_paidShares",PACT,"paidShares()"); add("PACT_freeClaimed_user",PACT,"freeClaimed(address)",USER)
M="0x7a38395ad7317594a8eb6c658f3f073a693dfaab"
add("MEOW_totalSupply",M,"totalSupply()"); add("MEOW_balance_user",M,"balanceOf(address)",USER); add("MEOW_launched",M,"launched()")
add("OSK_opened","0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37","opened()"); add("OSK_totalMinted","0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37","totalMinted()")
add("NIULAI_launched","0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF","launched()"); add("NIULAI_phase","0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF","phase()")
add("KillZero_launched","0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97","launched()")
add("DROID_opened","0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","opened()"); add("DROID_freeMinted","0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","freeMinted()"); add("DROID_totalMinted","0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","totalMinted()")
add("IMARS_opened","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","opened()"); add("IMARS_freeMinted","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","freeMinted()"); add("IMARS_totalMinted","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","totalMinted()")
add("ASOC_freeClaimed_user","0x43cEef9313CB8c4ca3757bA841C44DF40A223205","freeClaimed(address)",USER); add("ASOC_saleEnded","0x43cEef9313CB8c4ca3757bA841C44DF40A223205","saleEnded()")
def run(item):
    k,(a,s,frm)=item
    v=raw(a, s+enc(frm) if frm else s, frm=frm)
    return k, (cint(v) if not isinstance(v,dict) else v)
blk=block()
with ThreadPoolExecutor(max_workers=12) as ex:
    res=dict(ex.map(run, jobs.items()))
out={"block":blk,"values":res}
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1304-reread.json","w"),indent=1)
