import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
targets = [
 ("Dronegent","0xF6Ab7131b01F0a94e8860C284fC904D09ED0373b"),
 ("Syntaxia","0xA9b060551764f3213a64a449fD3D06db3b8CbCff"),
 ("Robogent","0x5eA7E757dfc4654f7478841BD30175bd7F186e24"),
 ("AgentisVox","0xe7b329fC7F8294f75bAa40dD438940Ba83b6168c"),
 ("Autonym","0x7Fa142C23805387c94fbc4AdEbf1168A7145f528"),
 ("Noesyn","0x69e2B3df4ecedBf7FC89085707a8cb9163F5e1BC"),
 ("Synaptik","0xE5523bf6AA0F92aCC7d2898F65596a0A088a8f0F"),
 ("Logiphon","0x14Fb2182311dEBfA3fa6EdbE17278cd4ddBDB619"),
 ("Yydsgent","0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61"),
 ("Terragent","0x508468BAD31de925a533b88B17a233EC377C641d"),
 ("Hackagent","0xc13f995d7e2ab6B4267Dec8eeB2761464056d07b"),
 ("Mechfarm","0xde536232c09ea778b6cb8409328362F7e9182bc9"),
 ("bridge-Agent Harvest Land-2","0xacf150d9ec909e3d339bf4c6d090b18495674e66"),
 ("Gondolux","0xD37aF310F2Da74c8baBe301F2A8F8494f40e0C14"),
 ("Gachagent","0xE23d1DC8F47f6a56F436d73c52862f40F26e9D39"),
 ("Cryptlichor","0xb792Bf600DF37EB7638fb16434e813fc0c90C3C8"),
 ("bridge-new-8831","0x88313a88836783dcc4008fee2b8c743bb1029ef7"),
 ("bridge-new-c060","0xc06091bc9a1d1b8e7d79ed238727b28ac52b996e"),
 ("IMARS-sale","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"),
 ("hive-pollen-mint","0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"),
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
json.dump(out,open(f"{H}/run-2026-11-03-1531-reread.json","w"),indent=1)
print("DONE",len(targets),"block",out["block"])

# pollen + IMARS extra views
for name,addr,sigs in [("pollen-extra","0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f",["launched()","phase()","pollenAgents()","paidSold()"]),
 ("IMARS-extra","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",["opened()","freeMinted()","FREE_SHARES()","totalMinted()","OPEN_AT()"])]:
    d={sig:one(addr,sig,"") for sig in sigs}
    out[name]=d; print(name, d, flush=True)
json.dump(out,open(f"{H}/run-2026-11-03-1531-reread.json","w"),indent=1)
print("DONE2")
