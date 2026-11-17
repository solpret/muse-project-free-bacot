import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch as _batch
from ankr import ankr_post
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    return "0x"+keccak.new(digest_bits=256, data=s.encode()).hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x5bc4fb61270c2628c93bf507c4ba125b868d34ff"
def call(data, frm=None):
    for ep in EPS:
        try:
            tx={"to":ADDR,"data":data}
            if frm: tx["from"]=frm
            return _batch([("eth_call",[tx,"latest"])],endpoint=ep,timeout=15)[0]
        except Exception as e:
            last=e
    return "ERR:"+str(last)
def ti(v):
    try: return int(v,16)
    except: return None
def dec_str(h):
    if not isinstance(h,str) or not h.startswith("0x"): return None
    raw=bytes.fromhex(h[2:])
    if len(raw)>=64:
        try:
            ln=int.from_bytes(raw[32:64],"big")
            if 0<ln<=len(raw)-64: return raw[64:64+ln].decode("utf-8","replace")
        except: pass
    if len(raw)==32: return raw.rstrip(b"\x00").decode("utf-8","replace") or None
    return None
out={}
out['name']=dec_str(call(sel("name()")))
out['symbol']=dec_str(call(sel("symbol()")))
out['totalMinted']=ti(call(sel("totalMinted()")))
out['totalSupply']=ti(call(sel("totalSupply()")))
out['mintOpen']=ti(call(sel("mintOpen()")))
out['MAX_SUPPLY']=ti(call(sel("MAX_SUPPLY()")))
out['FREE_PER_WALLET']=ti(call(sel("FREE_PER_WALLET()")))
out['MAX_PER_WALLET']=ti(call(sel("MAX_PER_WALLET()")))
out['MINT_PRICE']=ti(call(sel("MINT_PRICE()")))
out['mintedBy_user']=ti(call(sel("mintedBy(address)"), )) if False else ti(call(sel("mintedBy(address)")+enc(USER)))
out['owner']=call(sel("owner()"))
# quote(address,uint256) -> try
qdata=sel("quote(address,uint256)")+enc(USER)+(1).to_bytes(32,"big").hex()
out['quote_user_1']=call(qdata)
# first mint: address-filtered Transfer from zero, search back in 1000-block chunks from head
head=int(_batch([("eth_blockNumber",[])],endpoint=EPS[0],timeout=15)[0],16)
out['head']=head
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
found=None
# probe last 5000 blocks in 5 chunks of 1000
for i in range(5):
    to_b=head-i*1000; from_b=to_b-999
    body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(from_b),"toBlock":hex(to_b),"pageSize":1000,"decodeLogs":False,"address":ADDR,"topics":[TRANSFER,ZERO]},timeout=30)
    logs=body.get("result",{}).get("logs",[])
    if logs:
        blk=min(int(l.get("blockNumber","0x0"),16) for l in logs)
        out[f'mints_in_{from_b}-{to_b}']=len(logs)
        if found is None or blk<found: found=blk
    else:
        out[f'mints_in_{from_b}-{to_b}']=0
out['earliest_mint_block_last_5000']=found
print(json.dumps(out,indent=1))
json.dump(out,open('run-2026-11-08-1101-verify-5bc4.json','w'),indent=1)
