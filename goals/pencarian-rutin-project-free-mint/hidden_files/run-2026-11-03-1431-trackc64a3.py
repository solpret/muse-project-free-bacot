import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
A = "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"
def one(sig,args=""):
    try:
        r=race("eth_call",[{"to":A,"data":"0x"+sel(sig)+args},"latest"])
        if isinstance(r,str) and len(r)==66: return int(r,16)
        if isinstance(r,str) and len(r)==130: return r[-40:]
        return None
    except Exception as e: return f"ERR:{type(e).__name__}"
def txt(sig):
    try:
        r=race("eth_call",[{"to":A,"data":"0x"+sel(sig)},"latest"])
        if isinstance(r,str) and len(r)>130:
            raw=bytes.fromhex(r[2:]); ln=int(raw[32:64].hex(),16); return raw[64:64+ln].decode(errors="ignore")
        return None
    except Exception: return None
out={}
for sig in ["idCollection()","FREE_SHARES()","freeMinted()","opened()","OPEN_AT()","decimals()","totalSupply()","totalMinted()","pair()","MAX_SHARES()","BASE_QUOTA()"]:
    out[sig]=one(sig)
out["name"]=txt("name()"); out["symbol"]=txt("symbol()")
print(json.dumps(out,indent=1),flush=True)
json.dump(out,open(f"{H}/run-2026-11-03-1431-trackc64a3.json","w"),indent=1)
print("DONE")
