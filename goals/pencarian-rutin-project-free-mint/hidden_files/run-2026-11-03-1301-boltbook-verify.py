import json,sys,subprocess
sys.path.insert(0,"/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad=USER[2:].rjust(64,'0')
def call(addr,sig,args=""):
    try:
        r=race("eth_call",[{"to":addr,"data":"0x"+sel(sig)+args},"latest"])
        if isinstance(r,str) and len(r)==66: return int(r,16)
        if isinstance(r,str) and len(r)==130: return r[-40:]
        return r
    except Exception as e: return f"ERR:{type(e).__name__}"
def abi(addr):
    try:
        raw=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True).stdout
        return json.loads(raw).get('abi',[])
    except Exception as e: return []
out={}
MARS="0xc4059d2f9f6f86695896e68f3e73e1e6cc3791c8"
print("MARS block", int(race("eth_blockNumber",[]),16), flush=True)
for sig in ["name()","symbol()","totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintedBy(address)","freeUsed(address)","balanceOf(address)","owner()"]:
    args=pad if "(address)" in sig else ""
    print("MARS",sig,call(MARS,sig,args),flush=True)
ab=abi(MARS); print("MARS abi fns", sorted({f['name'] for f in ab if f.get('type')=='function'}) if ab else "UNVERIFIED", flush=True)
SALE="0xbd6087fc30f2395344020cb190255c56cbc517bd"; TOK="0x2b96fc99cb3edc8e3a907b63d19a06db5ad894ab"
for label,addr in [("SALE",SALE),("TOK",TOK)]:
    ab=abi(addr); fns=sorted({f['name'] for f in ab if f.get('type')=='function'}) if ab else []
    print(label, "abi", fns if fns else "UNVERIFIED", flush=True)
    out[label]=fns
for sig in ["totalSupply()","name()","symbol()"]:
    print("TOK",sig,call(TOK,sig),flush=True)
for sig,args in [("sharesMinted()", ""),("freeMinted()",""),("freeClaimed(address)",pad),("quote(address,uint256)",pad+"0"*63+"1"),("quote(uint256)","0"*63+"1"),("freeSharesRemaining()",""),("MAX_FREE()",""),("MAX_SHARES()",""),("owner()","")]:
    print("SALE",sig,call(SALE,sig,args),flush=True)
