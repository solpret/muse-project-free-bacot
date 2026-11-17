import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch as _batch
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
A="0xb8164afefc53910D7A74cEcE15A60a9e0C86089e"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            r=_batch([("eth_call",[{"to":addr,"data":data},"latest"])], endpoint=ep, timeout=15)[0]
            return r
        except Exception: continue
    return None
def vint(sig, arg=None):
    data=sel(sig)+(enc(arg) if arg else "")
    r=single(A,data)
    try: return int(r,16) if r not in (None,"0x") else None
    except Exception: return None
def vaddr(sig):
    r=single(A, sel(sig))
    try: return "0x"+r[-40:] if r and len(r)>=66 else None
    except Exception: return None
def vstr(sig):
    r=single(A, sel(sig))
    if not r or len(r)<130: return None
    try:
        ln=int(r[66:130],16); raw=bytes.fromhex(r[130:130+ln*2]); return raw.decode()
    except Exception: return None
out={"address":A,"name":vstr("name()"),"symbol":vstr("symbol()"),
 "totalSupply":vint("totalSupply()"),"totalMinted":vint("totalMinted()"),"totalCards":vint("totalCards()"),
 "remaining":vint("remaining()"),"cardMinted":vint("cardMinted()"),"cumulativeSupply":vint("cumulativeSupply()"),
 "nextTokenId":vint("nextTokenId()"),"MAX_SUPPLY":vint("MAX_SUPPLY()"),"MAX_PER_WALLET":vint("MAX_PER_WALLET()"),
 "firstFreeUsed_user":vint("firstFreeUsed(address)",USER),"mintedByWallet_user":vint("mintedByWallet(address)",USER),
 "balanceOf_user":vint("balanceOf(address)",USER),"owner":vaddr("owner()"),"agentRegistry":vaddr("agentRegistry()"),
 "priceOf_1":vint("priceOf(uint256)", "0x0000000000000000000000000000000000000000000000000000000000000001")}
print(json.dumps(out, indent=1), flush=True)
# first mint: Ankr address-filtered Transfer from zero, walk back in 1000-block chunks from head
head=int(_batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=15)[0],16)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
first=None; chunks=0
to_block=head
while to_block>head-20000 and first is None:
    frm=max(head-20000, to_block-999)
    try:
        body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to_block),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":A}, timeout=30)
        logs=body.get("result",{}).get("logs",[])
    except Exception as e:
        print("walkback err", frm, to_block, e, flush=True); break
    chunks+=1
    if logs:
        first=min(int(l.get("blockNumber","0x0"),16) for l in logs)
        out["first_mint_block"]=first; out["first_mint_logs_in_chunk"]=len(logs)
        print("FIRST MINT BLOCK", first, "chunk", frm, to_block, "logs", len(logs), flush=True)
        break
    to_block=frm-1
    time.sleep(1)
out["walkback_chunks"]=chunks; out["head"]=head
print("walkback chunks:", chunks, "first:", first, flush=True)
# block timestamp via dataseed for first mint block
if first:
    for ep in EPS:
        try:
            b=_batch([("eth_getBlockByNumber",[hex(first),False])], endpoint=ep, timeout=15)[0]
            ts=int(b["timestamp"],16); out["first_mint_ts"]=ts
            import datetime; out["first_mint_wib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
            print("FIRST MINT WIB:", out["first_mint_wib"], flush=True)
            break
        except Exception as e: print("ts fail", ep, e, flush=True)
json.dump(out, open("run-2026-11-09-0231-b816.json","w"), indent=1)
print("DONE")
