import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
RPC="https://bsc.publicnode.com"
RPC2="https://bsc-dataseed1.bnbchain.org"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,frm=None):
    tx={"to":to,"data":data}
    if frm: tx["from"]=frm
    for rpc in (RPC,RPC2):
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=12) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:120]}
            return out["result"]
        except Exception as e: continue
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
    for rpc in (RPC,RPC2):
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=12) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
NEW=["0x908DbB0b613696860829434b45ac78810483Bd2A","0x7497538C3195bC4E32Dd5cE70cf4bcA5573F6eA6","0xCA28f64A4F2C6f3Ec34024cC8D2ecC36fCf0bc4F","0x3b8204db7c1cd16f6d50Df9D0F1C78a2Dda5931D","0x4430550fe146199aE404fCeD849Dfb6565D67798","0xeF7861fA2009BfCE26b73f07055A5fB0A769048B","0x397a913A3EaD02018bCBb82b67b1b70B1d9EB0A3","0x6F61c7467eABe2139598CE49B6Fd2022880478f9","0x119Fa3BF44A32692aBC06D2c7E9b8059C81FCC6e","0xc9D3F29dA84FC3F7cd6F2e91269c575d31F695aa","0xF8A50Bd217687664b186Bf2439a23Ef24e8C2432","0xE2ad0bc87CCaFf4cA66509C73dcA011AFF922a25","0xED0bE7FF00953B9c5dc31aB0D1be46c2Bf237368","0x36bCF1C8b626d29D2dDEc38df8d9033d05B66e0C"]
def probe_new(a):
    d={"name":cstr(raw(a,sel("name()"))),"symbol":cstr(raw(a,sel("symbol()"))),
       "decimals":cint(raw(a,sel("decimals()"))),"totalSupply":cint(raw(a,sel("totalSupply()"))),
       "agentRegistry":raw(a,sel("agentRegistry()")),"registry":raw(a,sel("registry()")),
       "freeMinted":cint(raw(a,sel("freeMinted()"))),"FREE_SLOTS":cint(raw(a,sel("FREE_SLOTS()"))),
       "FREE_SUPPLY":cint(raw(a,sel("FREE_SUPPLY()"))),"FREE_AMOUNT":cint(raw(a,sel("FREE_AMOUNT()"))),
       "freeClaimed_user":cint(raw(a,sel("freeClaimed(address)")+enc(USER))),
       "freeSharesRemaining":cint(raw(a,sel("freeSharesRemaining()"))),
       "mintFree_noarg_from_user":raw(a,sel("mintFree()"),frm=USER)}
    return d
def probe_reread():
    r={}
    STAR="0x7d390e37ed41a359f276d8764ca15432704b99b7"
    r["STAR"]={"name":cstr(raw(STAR,sel("name()"))),"symbol":cstr(raw(STAR,sel("symbol()"))),"totalSupply":cint(raw(STAR,sel("totalSupply()"))),
      "freeMinted":cint(raw(STAR,sel("freeMinted()"))),"FREE_SLOTS":cint(raw(STAR,sel("FREE_SLOTS()"))),"FREE_SUPPLY":cint(raw(STAR,sel("FREE_SUPPLY()"))),
      "freeClaimed_user":cint(raw(STAR,sel("freeClaimed(address)")+enc(USER))),"claimed_user":cint(raw(STAR,sel("claimed(address)")+enc(USER))),
      "mintFree_from_user":raw(STAR,sel("mintFree()"),frm=USER),"balanceOf_user":cint(raw(STAR,sel("balanceOf(address)")+enc(USER))),"agentRegistry":raw(STAR,sel("agentRegistry()"))}
    PACT="0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"
    r["PACTURE"]={"sharesMinted":cint(raw(PACT,sel("sharesMinted()"))),"freeMinted":cint(raw(PACT,sel("freeMinted()"))),"paidShares":cint(raw(PACT,sel("paidShares()"))),"soldOut":cint(raw(PACT,sel("soldOut()"))),"freeClaimed_user":cint(raw(PACT,sel("freeClaimed(address)")+enc(USER)))}
    M="0x7a38395ad7317594a8eb6c658f3f073a693dfaab"
    r["MEOWBARK"]={"name":cstr(raw(M,sel("name()"))),"symbol":cstr(raw(M,sel("symbol()"))),"decimals":cint(raw(M,sel("decimals()"))),"totalSupply":cint(raw(M,sel("totalSupply()"))),"balanceOf_user":cint(raw(M,sel("balanceOf(address)")+enc(USER))),"launched":cint(raw(M,sel("launched()"))),"pair":raw(M,sel("pair()")),"freeClaimed_user":cint(raw(M,sel("freeClaimed(address)")+enc(USER)))}
    r["OSK"]={"opened":cint(raw("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",sel("opened()"))),"totalMinted":cint(raw("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",sel("totalMinted()")))}
    r["NIULAI"]={"launched":cint(raw("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",sel("launched()"))),"phase":cint(raw("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",sel("phase()")))}
    r["KillZero"]={"launched":cint(raw("0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",sel("launched()")))}
    r["DROID"]={"opened":cint(raw("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("opened()"))),"freeMinted":cint(raw("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("freeMinted()"))),"totalMinted":cint(raw("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("totalMinted()")))}
    r["IMARS"]={"opened":cint(raw("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("opened()"))),"freeMinted":cint(raw("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("freeMinted()"))),"totalMinted":cint(raw("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("totalMinted()")))}
    r["ASOC"]={"freeClaimed_user":cint(raw("0x43cEef9313CB8c4ca3757bA841C44DF40A223205",sel("freeClaimed(address)")+enc(USER))),"saleEnded":cint(raw("0x43cEef9313CB8c4ca3757bA841C44DF40A223205",sel("saleEnded()")))}
    return r

def probe_extra(a):
    d={"name":cstr(raw(a,sel("name()"))),"symbol":cstr(raw(a,sel("symbol()"))),
       "totalSupply":cint(raw(a,sel("totalSupply()"))),
       "freeMinted":cint(raw(a,sel("freeMinted()"))),"FREE_SLOTS":cint(raw(a,sel("FREE_SLOTS()"))),
       "freeClaimed_user":cint(raw(a,sel("freeClaimed(address)")+enc(USER))),
       "agentRegistry":raw(a,sel("agentRegistry()")),
       "mintFree_from_user":raw(a,sel("mintFree()"),frm=USER),
       "claimFree_from_user":raw(a,sel("claimFree()"),frm=USER),
       "mintOpen":cint(raw(a,sel("mintOpen()"))),"launched":cint(raw(a,sel("launched()")))}
    return d
EXTRA=["0x78573ab46e5436e126d3ea1fdef8766cce4efd2b","0x640ddbf8c62c393a0852eb2e48d71c74a20eb228","0xb34105002B19EF0ce43B59011fE848df5c8B174f"]
blk=block()
news=[]
res={"block":blk,"new":{},"reread":probe_reread(),"boltbook_zh_new":dict(zip(EXTRA,[probe_extra(a) for a in EXTRA])),"fragment":probe_extra("0xadEC4072dAAb830017d82189734696A9cCe834dD")}
print(json.dumps(res,indent=1))
base="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
json.dump(res,open(f"{base}/hot-leg-2026-11-05-1129-reread.json","w"),indent=1)
