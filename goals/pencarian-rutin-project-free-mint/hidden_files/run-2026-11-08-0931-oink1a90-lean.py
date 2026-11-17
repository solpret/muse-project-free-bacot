import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as single
from Crypto.Hash import keccak
ADDR="0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(sig, arg=False):
    data=sel(sig)+(enc(USER) if arg else "")
    last=None
    for ep in EPS:
        try:
            r=single(ep, "eth_call", [{"to":ADDR,"data":data},"latest"], 8, retries=0)
            if r is None or r=="0x": return None
            return int(r,16)
        except Exception as e:
            last=str(e)[:90]
    return {"error": last}
VIEWS=["totalSupply()","totalMinted()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintPrice()","balanceOf(address)","freeClaimed(address)","isFree()","freeMinted(address)","mintedBy(address)","freeLeft()","FREE_HASH()"]
out={}
for v in VIEWS:
    out[v]=call(v, "(address)" in v)
    print(v, "=", out[v])
json.dump(out, open("run-2026-11-08-0931-oink1a90-lean.json","w"), indent=1)
