import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=8) as r: j=json.load(r)
            v=j.get("result"); return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
feed=['0x5725d0CeD0A0dd52dCc7f111dA5c2489c5a14F13','0x9f1C960c382B693e654e4B99aA89267DBbf926c6','0xe24137c9BDB32dEacC1f1194FF5576fa82ac4a4F','0xc0a948429d503De19e5251D9Dbe7e1888072263f','0x44c62EE029c07eD736CA4cFCc1223D687309fc4E','0x349A7622466e408D437b455e21a0dA34916b57Dc','0x0620888500cf5BAD56326716a0eB9f53167bBf59','0xbb57297595aEf7e65Ef300081c7bE9bfe2FABE59','0x76d6dCacdc8caB2832d2060C351974F2aBE54DeD','0x4388fcCFBfCC4D2A48C2e59c5C5aFdD9e26c7C89','0xAc86Edbe3ebE5012502B80E64cbB7d0465723034','0x19544bfE93BF9709E50A5Cd5c99a2482288d644a','0xF19A66e4643C5D11D1522A2352331688F8a2f324','0x8D3e00DF5B942239569acfa35Cd7274d2D454c80','0x79E573112aab540F80DC6FCeE342D6eb4EBC7EbF','0x883aF1BD8eF7b3e84e0Ece8562F3e5C488a27777','0x4ab7d5b5f32D6e42d27141a724C0E72331392200','0xfdf24705a48f08558a6eed9B72d24cF3Bbce07e5','0xb5980Eb0b21a1CE6393E3641a9e4729106e08616','0x0Fa28b44F9D4417d5cAbB232688Bd01aBEeD69b5']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    o['freeMinted']=iv(call(a,sel("freeMinted()"))); o['FREE_SLOTS']=iv(call(a,sel("FREE_SLOTS()"))); o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()")))
    o['freeClaimed_user']=iv(call(a,sel("freeClaimed(address)")+u))
    o['freeSharesRemaining']=iv(call(a,sel("freeSharesRemaining()"))); o['freeLeft']=iv(call(a,sel("freeLeft()"))); o['freeAvailable_user']=iv(call(a,sel("freeAvailable(address)")+u))
    o['quote_user1']=iv(call(a,sel("quote(address,uint256)")+u+one))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()")); o['agentId']=call(a,sel("agentId()"))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0409-sourcify-shape.json","w"),indent=1)
print("DONE")
