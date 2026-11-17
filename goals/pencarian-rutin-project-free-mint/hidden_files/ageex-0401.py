import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,sig):
    try:
        r=race("eth_call",[{"to":to,"data":sel(sig)},"latest"],timeout=10)
        if not r or r=="0x": return None
        return int(r,16)
    except Exception: return None
T={
 "Soarm-sale 0x7ba14e1119d31E876Cc4aa52a0bcB9E43C841799":["freeSharesLeft()","sharesSold()","finalized()"],
 "Hongbao-sale 0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97":["totalSharesSold()","mintOpen()","freeClaimed()"],
 "Nvagent-7Eb3 0x7Eb3a26F895d4D1b8FcD38A67E9689cB2693661f":["totalMints()","mintOpen()"],
 "Nvagent-28Fe 0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2":["totalMints()","mintOpen()"],
}
out={}
for name,views in T.items():
    addr=name.split()[-1]
    res={v:call(addr,v) for v in views}
    out[name]=res
    print(name,res,flush=True)
json.dump(out,open("ageex-0401.json","w"),indent=1)
print("DONE")
