import sys, json, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def rpc(m,p,timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,timeout,retries=0)
        except Exception as e: last=e
    raise last
def keccak_sel(sig):
    from Crypto.Hash import keccak
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def call(addr,sig,args=""):
    try: return rpc("eth_call",[{"to":addr,"data":keccak_sel(sig)+args},"latest"])
    except Exception as e: return f"ERR:{e}"
def di(h):
    try:
        if isinstance(h,str) and h.startswith("0x") and len(h)>=66: return int(h[2:66],16)
    except Exception: pass
    return None
def da(h):
    try:
        if isinstance(h,str) and h.startswith("0x") and len(h)>=66: return "0x"+h[-40:]
    except Exception: pass
    return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
user_arg="0"*24+USER[2:].lower()
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def mints_before(addr, first_block, from_block):
    """Ankr getLogs address-filtered Transfer mints in [from_block, first_block-1]."""
    logs=[]; tok=None; pages=0
    while True:
        params={"blockchain":"bsc","address":addr,"fromBlock":hex(from_block),"toBlock":hex(first_block-1),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}
        if tok: params["pageToken"]=tok
        body=ankr_post("ankr_getLogs",params,timeout=30)
        r=body.get("result",{}) if isinstance(body,dict) else {}
        logs.extend(r.get("logs",[])); tok=r.get("nextPageToken"); pages+=1
        if not tok or pages>=20: break
        time.sleep(2.2)
    return logs
def block_ts(blk):
    b=rpc("eth_getBlockByNumber",[hex(blk),False])
    return int(b["timestamp"],16)
def wib(ts): return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts+7*3600))
out={}
for addr,first_block in [("0x3BF121dC4c5a1Ba567F3eE801d0e447601726207",131975982),("0x71f86082C3b32601f865c63980a9B686e887EAB1",131976627)]:
    print("="*90,flush=True); print(addr,"first_block",first_block,flush=True)
    # full ABI for signatures
    r=subprocess.run(["curl","-sS","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=40)
    abi=json.loads(r.stdout).get("abi",[])
    def sig_of(name):
        for f in abi:
            if f.get("type")=="function" and f.get("name")==name:
                ins=",".join(i.get("type","") for i in f.get("inputs",[]))
                return f"{name}({ins})"
        return None
    for nm in ["mintStartsAt","mintEndsAt","freeAllocated","freeUsed","freeClaimed","mintedBy","freeMintedBy","freeCapPerWallet","freeClaimFeeWei","paidPriceWei","mintOpen","totalMinted","totalSupply","quote","claimFree","mintFree","claimableBy","nextFreeAt","agentRegistry"]:
        s=sig_of(nm)
        if s: print("  ABI:",s,flush=True)
    # zero-mint check: wide range back to block 131900000 (~Nov 6 ~04:00 WIB, >11h before)
    logs=mints_before(addr,first_block,131900000)
    print(f"  mints in [131900000, {first_block-1}]: {len(logs)}",flush=True)
    for lg in logs[:10]:
        print("   prior mint block",int(lg["blockNumber"],16),"tx",lg.get("transactionHash"),flush=True)
    first_ts=block_ts(first_block)
    print(f"  first-mint block {first_block} ts {first_ts} = {wib(first_ts)} WIB",flush=True)
    out[addr]={"prior_mints_from_131900000":len(logs),"prior_mint_blocks":[int(l["blockNumber"],16) for l in logs],"first_block_ts":first_ts,"first_block_wib":wib(first_ts)}
    # free-pool / slot reads
    if addr.lower().startswith("0x3bf1"):
        for sig,lbl in [("mintStartsAt()","mintStartsAt"),("mintEndsAt()","mintEndsAt"),("freeAllocated()","freeAllocated"),("freeUsed()","freeUsed"),("totalMinted()","totalMinted"),("FREE_SUPPLY()","FREE_SUPPLY"),("MAX_SUPPLY()","MAX_SUPPLY")]:
            print(" ",lbl,di(call(addr,sig)),flush=True)
        print("  quote(uint256,1):",di(call(addr,"quote(uint256)","0"*63+"1")),flush=True)
        print("  quote(address,uint256) user,1:",di(call(addr,"quote(address,uint256)",user_arg+"0"*63+"1")),flush=True)
        print("  mintedBy(user):",di(call(addr,"mintedBy(address)",user_arg)),flush=True)
        print("  freeClaimed(user)?:",call(addr,"freeClaimed(address)",user_arg),flush=True)
    else:
        for sig,lbl in [("freeCapPerWallet()","freeCapPerWallet"),("freeClaimFeeWei()","freeClaimFeeWei"),("paidPriceWei()","paidPriceWei"),("totalMinted()","totalMinted"),("MAX_SUPPLY()","MAX_SUPPLY"),("mintOpen()","mintOpen"),("nextFreeAt()","nextFreeAt")]:
            v=call(addr,sig); print(" ",lbl,di(v),flush=True)
        print("  freeMintedBy(user):",di(call(addr,"freeMintedBy(address)",user_arg)),flush=True)
        print("  claimableBy(user):",di(call(addr,"claimableBy(address)",user_arg)),flush=True)
        print("  mintFree sig:",sig_of("mintFree"),"claimFree sig:",sig_of("claimFree"),flush=True)
json.dump(out,open('run-2026-11-06-1501-verify.json','w'),indent=1)
print("WROTE verify",flush=True)
