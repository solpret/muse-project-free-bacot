import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from ankr import ankr_post
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
# Part A: Kitsuneon any from-zero log before 48h cutoff block 131014404 (wide range, paged)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def logs(addr,frm,to):
    out=[]; token=None
    for _ in range(10):
        p={"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"address":addr,"topics":[TRANSFER,ZERO]}
        if token: p["pageToken"]=token
        body=ankr_post("ankr_getLogs",p,timeout=30)
        r=body.get("result",{}) if isinstance(body,dict) else {}
        out.extend(r.get("logs",[])); token=r.get("nextPageToken")
        if not token: break
    return out
try:
    lg=logs("0x2b5c0d44878279501aa111e353a2b493e0823b57",129000000,131014404)
    blocks=sorted({int(x.get("blockNumber"),16) if isinstance(x.get("blockNumber"),str) else x.get("blockNumber") for x in lg})
    print("KITSUNEON pre-cutoff logs:",len(lg),"earliest block:",blocks[0] if blocks else None,"latest:",blocks[-1] if blocks else None,flush=True)
except Exception as e:
    print("KITSUNEON pre-cutoff ERR:",type(e).__name__,str(e)[:200],flush=True)
# Part B: 14 factory first-seen
targets=[
 ("Plugvale","0x5d01D13A1814c2Bc673b4c73e8A93d2deAa941f1"),
 ("Sandbarr","0x120E6D75604eEE73FA5EbE43FE9A8d4552b4a67b"),
 ("Hookwyrd","0xF7BBf38dAeCaDb00537d2d5490C429aE0b0BE877"),
 ("Endpoynt","0x9Ca287f325070bc7978Ee121EFfEdB9BD18C72F2"),
 ("Apivora","0xB385E16a454F76Cd11CD2797300cdeBe5D30fE24"),
 ("Contexa","0xD0Cec431BFb88dFf8a3B940f8a4f9c81C68BdbcB"),
 ("Toolsmyth","0x42aC74C35d09c20E5dda06D1e65322f5e3C2cB60"),
 ("Memorind","0xCc674040C93Bf40403Ce4f4b2683A376c97dB177"),
 ("Tokenwick","0x3Fd85Ca8d7F250Ef821353F521c0eb1E117f1b15"),
 ("Parsewick","0x3b899116B0D6D1171223dc5fEC861b9a912a3F91"),
 ("Funcvix","0xBFbDE67707D00a759E55Ee158aBfcb3b33F375FD"),
 ("Vectorine","0x9B89Bbfe355Cd3313817276A55c513FbBAFb3063"),
 ("Embedrune","0x2925CF06b4E657f9d5301478b1BE2E62Cf863D11"),
 ("NightshadeClub","0x2C027F14d36a080E5e058CF39407EAc2503B90Cc"),
]
views=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintedBy(address)",pad),("balanceOf(address)",pad),("owner()",""),("quote(address,uint256)",pad+"0"*63+"1"),("mintOpen()","")]
out={"block":None}
try: out["block"]=int(race("eth_blockNumber",[]),16)
except Exception as e: out["block_error"]=str(e)[:120]
def one(addr,sig,args):
    try:
        r=race("eth_call",[{"to":addr,"data":"0x"+sel(sig)+args},"latest"])
        if isinstance(r,str) and r.startswith("0x") and len(r)==66: return int(r,16)
        if isinstance(r,str) and r.startswith("0x") and len(r)==130: return r[-40:]
        return None
    except Exception: return None
def txt(addr,sig):
    try:
        r=race("eth_call",[{"to":addr,"data":"0x"+sel(sig)},"latest"])
        if isinstance(r,str) and len(r)>130:
            raw=bytes.fromhex(r[2:]); ln=int(raw[32:64].hex(),16); return raw[64:64+ln].decode(errors="ignore")
        return None
    except Exception: return None
for name,addr in targets:
    d={sig:one(addr,sig,args) for sig,args in views}
    d["name"]=txt(addr,"name()"); d["symbol"]=txt(addr,"symbol()")
    out[name]={"address":addr,**d}
    print(name,d,d["name"],d["symbol"],flush=True)
# Part C: pollen pending claim
POLLEN="0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"
pd={sig:one(POLLEN,sig,"") for sig in ["launched()","phase()","pollenAgents()","paidSold()"]}
out["Pollen"]={"address":POLLEN,**pd}
print("Pollen",pd,flush=True)
json.dump(out,open(f"{H}/run-2026-11-03-1431-scanverify.json","w"),indent=1)
print("DONE block",out["block"])
