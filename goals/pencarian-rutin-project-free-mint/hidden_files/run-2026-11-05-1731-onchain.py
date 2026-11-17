import json, urllib.request, time
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.binance.org","https://bsc-dataseed1.defibit.io"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def call(addr, data, rpc):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}).encode()
    req=urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r: return json.load(r).get("result")
def read(addr, sig, args=""):
    data=sel(sig)+args
    last=None
    for rpc in RPCS:
        try:
            res=call(addr,data,rpc)
            if res is None: last="null-result"; continue
            if res=="0x": return {"revert": True}
            return {"raw": res}
        except Exception as e:
            last=str(e)
    return {"error": last}
def u(raw):
    try: return int(raw,16)
    except: return None
def b(raw):
    v=u(raw); return None if v is None else bool(v)
def s(raw):
    # decode string return (offset,len,bytes)
    try:
        h=raw[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode()
    except Exception: return None
OUT={}
def R(contract, label, sig, args="", kind="uint"):
    res=read(contract, sig, args)
    if "raw" in res:
        v = u(res["raw"]) if kind=="uint" else (b(res["raw"]) if kind=="bool" else (s(res["raw"]) if kind=="str" else res["raw"]))
        OUT.setdefault(contract,{})[label]=v
    else:
        OUT.setdefault(contract,{})[label]=res
    print(contract[:10], label, OUT[contract][label])
BNB="0x0cbc2c5f9c5bdac24d98e71bf173192692050946"
BAG="0xE3baAd369B4C30E6c6bfB0ffc6658C4a66062D81"
SUB="0x65DDB3E337c12E5964ead6Cb9b6469203EF4caf1"
MOCHI="0x2c1608fef2ccc5b1ffd134047f2c4767ff3bc483"
print("== BNB Bull =="); 
for lab,sig,k in [("startTime","startTime()","uint"),("endTime","endTime()","uint"),("freeMinted","freeMinted()","uint"),("FREE_SHARES","FREE_SHARES()","uint"),("paidSold","paidSold()","uint"),("TOTAL_SHARES","TOTAL_SHARES()","uint"),("isMintLive","isMintLive()","bool"),("launched","launched()","bool"),("outcome","outcome()","uint"),("freeOpensAt","freeOpensAt()","uint"),("totalSupply","totalSupply()","uint"),("agentId","agentId()","addr"),("name","name()","str"),("symbol","symbol()","str")]:
    R(BNB,lab,sig,kind=k)
print("== BAGENT ==")
for lab,sig,k in [("startTime","startTime()","uint"),("freeCount","freeCount()","uint"),("FREE_UNITS","FREE_UNITS()","uint"),("freeWindowActive","freeWindowActive()","bool"),("freeWindowEnd","freeWindowEnd()","uint"),("TOTAL_UNITS","TOTAL_UNITS()","uint"),("totalUnits","totalUnits()","uint"),("phase","phase()","uint"),("registry","registry()","addr"),("token","token()","addr"),("freeClaimed_user","freeClaimed(address)","uint")]:
    args=enc_addr(USER) if "address" in sig else ""
    R(BAG,lab,sig,args=args,kind=("bool" if k=="bool" else "uint"))
print("== Subsonic ==")
for lab,sig,k in [("totalSupply","totalSupply()","uint"),("FREE_SUPPLY","FREE_SUPPLY()","uint"),("MAX_SUPPLY","MAX_SUPPLY()","uint"),("freeClaimed","freeClaimed()","uint"),("mintOpen","mintOpen()","bool"),("PRICE","PRICE()","uint"),("AGENT_ID","AGENT_ID()","addr"),("name","name()","str"),("symbol","symbol()","str"),("hasFreeMint_user","hasFreeMint(address)","uint"),("mintedBy_user","mintedBy(address)","uint"),("quote_user_1","quote(address,uint256)","uint")]:
    args=""
    if sig.startswith("hasFreeMint") or sig.startswith("mintedBy"): args=enc_addr(USER)
    if sig.startswith("quote"): args=enc_addr(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
    R(SUB,lab,sig,args=args,kind=("bool" if k=="bool" else "uint"))
print("== MOCHI probes (selector guesses, unverified) ==")
for lab,sig in [("totalSupply","totalSupply()"),("sharesMinted","sharesMinted()"),("freeMinted","freeMinted()"),("mintedCount","mintedCount()")]:
    R(MOCHI,lab,sig,kind="uint")
# block number
for rpc in RPCS:
    try:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
        req=urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r: print("block", rpc, int(json.load(r)["result"],16)); break
    except Exception as e: print("block ERR", rpc, e)
json.dump(OUT, open("run-2026-11-05-1731-onchain.json","w"), indent=1)
print("saved")
