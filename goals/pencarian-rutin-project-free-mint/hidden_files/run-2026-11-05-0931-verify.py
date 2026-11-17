import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,sig,args=""):
    data=sel(sig)+args; last=None
    for rpc in RPCS:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
            break
        except Exception as e: last=e; continue
    else: return {"error":str(last)}
    if "error" in out: return {"error":out["error"]}
    v=out["result"]
    if not v or v=="0x": return None
    try: return int(v,16)
    except Exception: return v
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
def block():
    for rpc in RPCS:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_SLOTS()","FREE_CAP()","MAX_SUPPLY()","mintOpen()","opened()","launched()","name()","symbol()","decimals()","owner()","agentRegistry()","registry()","freeSharesRemaining()","freeAvailable()"]
res={"block":block()}
NFT={"LIMITLESS":"0xc7aa008c2369ff00322c49d526f33529bb692a86","Cogito":"0x5ae2be6BbA1BD4f561Dc13158c7f5B95992e045B","SEAT":"0xf11e9405b23ca0f53e6135162a85545d780a3737","PixelLaptop":"0x273fc2c7705b23eb129e35ac8da26348e6fc498",
     "V74":"0xC8Bb757247ca3D440677950f04bb000360f88138","DYOR":"0x86956Bc830EB62110820Ae79164BeF61c7E31936","Maverick":"0x5bF37927Ea62b0aB11C64E20D215e39A38c21193"}
for n,a in NFT.items():
    d={}
    for sig in VIEWS:
        v=call(a,sig)
        if sig in ("name()","symbol()") and isinstance(v,str): v=dec_str(v)
        d[sig]=v
    d["balanceOf(user)"]=call(a,"balanceOf(address)",enc(USER))
    d["mintedBy(user)"]=call(a,"mintedBy(address)",enc(USER))
    d["freeClaimed(user)"]=call(a,"freeClaimed(address)",enc(USER))
    d["claimedFree(user)"]=call(a,"claimedFree(address)",enc(USER))
    d["canFreeMint(user)"]=call(a,"canFreeMint(address)",enc(USER))
    d["freeMinted(user)"]=call(a,"freeMinted(address)",enc(USER))
    d["quote(user,1)"]=call(a,"quote(address,uint256)",enc(USER)+"0"*63+"1")
    res[n]=d
    print(n, json.dumps(d), flush=True)
ERC20=['0x3e613baCd4A9b7E5398FA8fFe856AA1e27a3A66A','0x7233a7c50dfD20758223451a1e7b496B7E2Fd639','0xe073791b476728A85899f2A9626A906fd7c32cc1','0xfC310CFC3827920A006C9Ca1E98b5090A203fbb4','0x0c84aED253EaaB9b7263665D7e213B7aEC718f23','0x832cc56b564663045609423a063a3d7dEbDCfEdc','0x9E575b649C63cbAE4994aD51D27Aa97f76bD404F','0x0607A5a7F0D0965b89826700756fD6B44284972d','0x37CC60790a649820752973FA661fef9badaDDeE1']
res["erc20_shape"]={}
for a in ERC20:
    d={}
    for sig in VIEWS:
        v=call(a,sig)
        if sig in ("name()","symbol()") and isinstance(v,str): v=dec_str(v)
        d[sig]=v
    d["freeClaimed(user)"]=call(a,"freeClaimed(address)",enc(USER))
    d["quote(user,1)"]=call(a,"quote(address,uint256)",enc(USER)+"0"*63+"1")
    d["freeSharesClaimed(user)"]=call(a,"freeSharesClaimed(address)",enc(USER))
    res["erc20_shape"][a]=d
    print("ERC20",a,json.dumps(d),flush=True)
def abi_check(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{a}",headers={"Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=15) as r: j=json.load(r)
        std=j.get("stdJson",{}); src=json.dumps(std)
        names=[f.get("name","") for f in std.get("output",{}).get("abi",[])]
        return {"match":j.get("match"),"registry_bytes":"60b9262456de011f7d15a54cdd8c48baa8b022f" in src.lower(),"agent_word":("agentgate" in src.lower() or "agentid" in src.lower()),"abi_names":names}
    except Exception as e: return {"error":str(e)[:150]}
res["abi"]={}
for n,a in list(NFT.items())+[(f"ERC20-{a}",a) for a in ERC20]:
    res["abi"][n]=abi_check(a); print("ABI",n,json.dumps(res["abi"][n])[:800],flush=True)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0931-verify.json","w"),indent=1)
print("DONE block",res["block"])
