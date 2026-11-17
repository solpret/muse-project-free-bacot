import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.defibit.io","https://bsc-dataseed1.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def raw(to,data):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    last=None
    for rpc in RPCS:
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            if "error" in out: return {"error":out["error"]}
            return out["result"]
        except Exception as e: last=str(e); continue
    return {"error":last}
def callint(to,data):
    v=raw(to,data)
    if isinstance(v,dict): return v
    return int(v,16) if v and v!="0x" else 0
def callstr(to,fn):
    v=raw(to,sel(fn+"()"))
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception as e: return {"decode_error":str(e)}
def block():
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    for rpc in RPCS:
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
blk=block(); res={"block":blk}
STAR="0x7d390e37ed41a359f276d8764ca15432704b99b7"
res["STAR"]={"name":callstr(STAR,"name"),"symbol":callstr(STAR,"symbol"),"totalSupply":callint(STAR,sel("totalSupply()")),"freeMinted":callint(STAR,sel("freeMinted()")),"FREE_SLOTS":callint(STAR,sel("FREE_SLOTS()")),"FREE_SUPPLY":callint(STAR,sel("FREE_SUPPLY()")),"freeClaimed_user":callint(STAR,sel("freeClaimed(address)")+enc_addr(USER)[2:]),"claimed_user":callint(STAR,sel("claimed(address)")+enc_addr(USER)[2:]),"mintFree_noarg":raw(STAR,sel("mintFree()")),"balanceOf_user":callint(STAR,sel("balanceOf(address)")+enc_addr(USER)[2:]),"agentRegistry":raw(STAR,sel("agentRegistry()"))}
PACT="0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"
res["PACTURE"]={"sharesMinted":callint(PACT,sel("sharesMinted()")),"freeMinted":callint(PACT,sel("freeMinted()")),"paidShares":callint(PACT,sel("paidShares()")),"soldOut":callint(PACT,sel("soldOut()")),"freeClaimed_user":callint(PACT,sel("freeClaimed(address)")+enc_addr(USER)[2:])}
res["MEOWBARK"]={"name":callstr("0x7a38395ad7317594a8eb6c658f3f073a693dfaab","name"),"symbol":callstr("0x7a38395ad7317594a8eb6c658f3f073a693dfaab","symbol"),"decimals":callint("0x7a38395ad7317594a8eb6c658f3f073a693dfaab",sel("decimals()")),"totalSupply":callint("0x7a38395ad7317594a8eb6c658f3f073a693dfaab",sel("totalSupply()")),"balanceOf_user":callint("0x7a38395ad7317594a8eb6c658f3f073a693dfaab",sel("balanceOf(address)")+enc_addr(USER)[2:]),"launched":callint("0x7a38395ad7317594a8eb6c658f3f073a693dfaab",sel("launched()")),"pair":raw("0x7a38395ad7317594a8eb6c658f3f073a693dfaab",sel("pair()")),"freeClaimed_user":callint("0x7a38395ad7317594a8eb6c658f3f073a693dfaab",sel("freeClaimed(address)")+enc_addr(USER)[2:])}
res["OSK"]={"opened()":callint("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",sel("opened()")),"totalMinted()":callint("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",sel("totalMinted()"))}
res["NIULAI"]={"launched()":callint("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",sel("launched()")),"phase()":callint("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",sel("phase()"))}
res["KillZero"]={"launched()":callint("0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",sel("launched()"))}
res["DROID"]={"opened()":callint("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("opened()")),"freeMinted()":callint("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("freeMinted()")),"totalMinted()":callint("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("totalMinted()"))}
res["IMARS"]={"opened()":callint("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("opened()")),"freeMinted()":callint("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("freeMinted()")),"totalMinted()":callint("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("totalMinted()"))}
res["ASOC"]={"freeClaimed(address)":callint("0x43cEef9313CB8c4ca3757bA841C44DF40A223205",sel("freeClaimed(address)")+enc_addr(USER)[2:]),"saleEnded()":callint("0x43cEef9313CB8c4ca3757bA841C44DF40A223205",sel("saleEnded()"))}
print(json.dumps(res,indent=1))
with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1034-reread.json","w") as f: json.dump(res,f,indent=1)
