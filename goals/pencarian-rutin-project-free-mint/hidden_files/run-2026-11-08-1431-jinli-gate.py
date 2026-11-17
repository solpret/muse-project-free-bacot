import json, urllib.request, sys, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            if not isinstance(out,dict): continue
            if out.get("error"): return "ERR"
            r=out.get("result")
            if r is None: return None
            return r
        except Exception: continue
    return "ERR:all-fail"
def dec_str(r):
    if not isinstance(r,str) or not r.startswith("0x") or len(r)<130: return r
    try:
        ln=int(r[66:130],16)
        b=bytes.fromhex(r[130:130+ln*2])
        return b.decode('utf-8', 'replace')
    except Exception as e: return f"decode-err {e} raw={r[:200]}"
J='0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496'
print("Jinli contractURI:", dec_str(single(J, sel('contractURI()'))))
print("Jinli tokenURI(1):", dec_str(single(J, sel('tokenURI(uint256)')+enc_u(1)))[:800])
print("Jinli name:", dec_str(single(J, sel('name()'))))
print("Jinli symbol:", dec_str(single(J, sel('symbol()'))))
# Sourcify ABI + metadata
url=f"https://sourcify.dev/server/v2/contract/56/{J}?fields=abi"
req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
try:
    d=json.load(urllib.request.urlopen(req, timeout=20))
    abi=d.get("abi")
    if isinstance(abi,list):
        fns=[e.get("name","") for e in abi if e.get("type")=="function"]
        print("Jinli Sourcify verified, fns:", fns)
        for e in abi:
            if e.get("type")=="function" and e.get("name") in ("mint","freeMint","mintFree","claimFree","quote","cost","price","mintPrice"):
                print("  ABI", e.get("name"), "inputs:", [(i.get("type"),i.get("name")) for i in e.get("inputs",[])], "mutability:", e.get("stateMutability"))
    else:
        print("Jinli Sourcify no-abi")
    src=json.dumps(d).lower()
    import re
    urls=sorted(set(re.findall(r'https?://[a-z0-9.\-_/]+', src)))
    print("Jinli Sourcify URLs in metadata:", urls[:20])
except Exception as e:
    print("Jinli Sourcify ERROR", e)
# mint price check
print("Jinli mintPrice():", single(J, sel('mintPrice()')))
print("Jinli PRICE():", single(J, sel('PRICE()')))
print("Jinli quote(1):", single(J, sel('quote(uint256)')+enc_u(1)))
print("Jinli cost(1):", single(J, sel('cost(uint256)')+enc_u(1)))
print("Jinli MAX_SUPPLY:", single(J, sel('MAX_SUPPLY()')))
print("Jinli FREE_SUPPLY:", single(J, sel('FREE_SUPPLY()')))
print("Jinli totalSupply:", single(J, sel('totalSupply()')))
print("Jinli freeClaimed:", single(J, sel('freeClaimed()')))
print("Jinli mintOpen:", single(J, sel('mintOpen()')))
