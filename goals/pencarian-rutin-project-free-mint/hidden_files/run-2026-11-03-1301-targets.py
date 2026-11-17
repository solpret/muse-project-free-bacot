import sys
sys.path.insert(0,"/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from onchain_nft_scan import rpc_call
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad=USER[2:].rjust(64,'0')
def call(addr,sig,args=""):
    try:
        r=rpc_call("eth_call",[{"to":addr,"data":"0x"+sel(sig)+args},"latest"])
        if isinstance(r,str) and len(r)==66: return int(r,16)
        if isinstance(r,str) and len(r)==130: return "0x"+r[-40:]
        return r
    except Exception as e: return f"ERR:{type(e).__name__}"
T={
 "Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24",
 "Whale Agent":"0xcA9f56eC4BB32753245d3a0a77912e76240185fb",
 "Zach Xbt":"0x6C39Ba54897Fb36B017A52eDA70A4A4D348D77De",
 "Deepvane":"0x0000000000000000000000000000000000000000",
 "Neuroveil":"0x0000000000000000000000000000000000000000",
}
import json
s=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
for k in ("Deepvane","Neuroveil"):
    if k in s['contracts']: T[k]=s['contracts'][k]['address']
for name,addr in T.items():
    vals={}
    for sig,args in [("totalSupply()",""),("freeClaimed()",""),("freeMinted()",""),("totalMinted()",""),("FREE_SUPPLY()",""),("mintedBy(address)",pad),("freeUsed(address)",pad),("balanceOf(address)",pad),("owner()","")]:
        vals[sig]=call(addr,sig,args)
    print(name,addr,vals,flush=True)
