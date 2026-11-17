import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
targets = [
 ("Syntaxia","0xA9b060551764f3213a64a449fD3D06db3b8CbCff"),
 ("Noesyn","0x69e2B3df4ecedBf7FC89085707a8cb9163F5e1BC"),
 ("Robogent","0x5eA7E757dfc4654f7478841BD30175bd7F186e24"),
 ("Synaptik","0xE5523bf6AA0F92aCC7d2898F65596a0A088a8f0F"),
 ("Yydsgent","0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61"),
 ("Lumenhold","0x9701980b0afd825134390ee46fb3bd675a2f356f"),
 ("Vertexa","0x7e00856e5bbc2795ad545592ba547336133fd244"),
 ("Omegrid","0x4095f575f1aec7068ec0e542aaf20e44cd62e5d1"),
 ("Auditrix","0x13eEa6a99720e2C9dDEda9B28d7eF5306B7322F4"),
 ("bridge-FAMULI","0x95ce945bef11643a8c7a97148b36f9a52c48d0f0"),
 ("bridge-AgentOnyx","0xf9a314e76855cab1f676ddbe77a5a91fa163da53"),
 ("IMARS-sale","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"),
]
views = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("totalMinted()",""),("freeMinted()",""),("mintedBy(address)",pad),("freeUsed(address)",pad),("balanceOf(address)",pad),("owner()",""),("mintOpen()",""),("quote(address,uint256)",pad+"0"*63+"1")]
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
    print(name, d, d["name"], d["symbol"], flush=True)
for name,addr,sigs in [("IMARS-extra","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",["opened()","freeMinted()","FREE_SHARES()","totalMinted()"])]:
    d={sig:one(addr,sig,"") for sig in sigs}; out[name]=d; print(name, d, flush=True)
json.dump(out,open(f"{H}/run-2026-11-03-1631-reread.json","w"),indent=1)
print("DONE",len(targets),"block",out["block"])
