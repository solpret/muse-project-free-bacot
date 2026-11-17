import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
targets = [
 ("Kitsuneon","0x2b5c0d44878279501aa111e353a2b493e0823b57"),
 ("Anonymous-NFT","0x2eB3f13aDb66Ef9D0eCdF890D3BA94cb0a8913FE"),
 ("Anonymous-Token","0x38cB550C1909daBD80a2C6aC6E9E0B107D02052F"),
 ("Oathbots-Pass","0x1bb3701da38d1572984cd200821d1162d6783435"),
 ("Fireball","0xB594b29360BD45975608C92dBDBA764c508B5c99"),
 ("BOLT","0xBbDd8C7720d1EEB1d63738eaABB584a4b72C7777"),
 ("Ptah","0xd87adb2e47979d6cb323896b1a9320e0dd132213"),
]
views = [("totalSupply()",""),("totalMinted()",""),("freeClaimed()",""),("freeMinted()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("paused()",""),("decimals()",""),("mintedBy(address)",pad),("freeUsed(address)",pad),("balanceOf(address)",pad),("owner()",""),("quote(address,uint256)",pad+"0"*63+"1"),("freeLeft(address)",pad),("AGENT_ID()",""),("agentRegistry()","")]
out={"block":None}
try: out["block"]=int(race("eth_blockNumber",[]),16)
except Exception as e: out["block_error"]=str(e)[:120]
def one(addr,sig,args):
    try:
        r=race("eth_call",[{"to":addr,"data":"0x"+sel(sig)+args},"latest"])
        if isinstance(r,str) and r.startswith("0x") and len(r)==66: return int(r,16)
        if isinstance(r,str) and r.startswith("0x") and len(r)==130: return r[-40:]
        return None
    except Exception as e: return f"ERR:{type(e).__name__}"
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
json.dump(out,open(f"{H}/run-2026-11-03-1431-verify-new.json","w"),indent=1)
print("DONE block",out["block"])
