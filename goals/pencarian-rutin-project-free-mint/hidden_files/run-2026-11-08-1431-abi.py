import json, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            r=out.get("result")
            if r is None: return None
            if out.get("error"): return "ERR:"+str(out["error"].get("message",""))
            return int(r,16) if r.startswith("0x") and len(r)<=66 else r
        except Exception as e:
            continue
    return "ERR:all-endpoints-fail"
# owners decode
for n,v in [("Alchemister",1322753689635082000788515507271940711601539421090),
            ("0x1a904Da7/0xbd4B4e71",555830023021011055551544091950786256662119557417),
            ("Zigzoo",13623742849624351287028540571884565964388122775),
            ("Jinli",205296289098938073264598461855055657361476746154),
            ("Undead",409677946206013052515363714067240544535493139149)]:
    print(n, "owner=0x"+format(v,'040x'))
# Jinli slot retry
J='0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496'
print("Jinli quote(1):", single(J, sel('quote(uint256)')+enc_u(1)))
print("Jinli freeClaimed(user):", single(J, sel('freeClaimed(address)')+enc_addr(USER)))
print("Jinli freeUsed(user):", single(J, sel('freeUsed(address)')+enc_addr(USER)))
print("Jinli freeLeft(user):", single(J, sel('freeLeft(address)')+enc_addr(USER)))
print("Jinli freeFor(user):", single(J, sel('freeFor(address)')+enc_addr(USER)))
# Sourcify ABI for the 4 free-shape-unknown contracts
for name,addr in [("Alchemister-0xCafEEDDF","0xCafEEDDF3C15C5CD9A63D97021efDe845e1781Bc"),
                  ("0x1a904Da7","0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B"),
                  ("Zigzoo","0x09ada5a12293c30d75b97c56e34967e8a4326a3c"),
                  ("Undead","0xC92bEc9160506065E515b225721a749Fad7664E9")]:
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: d=json.load(r)
    except Exception as e:
        print(name, "Sourcify ERROR", e); continue
    abi=d.get("abi")
    if not isinstance(abi,list):
        print(name, "Sourcify no-abi", str(d)[:200]); continue
    fns=[e.get("name","") for e in abi if e.get("type")=="function"]
    print(name, "Sourcify verified, fns:", fns)
    # also try alternate free counters via single calls
    for fn in ["freeSupply()","freeLeft()","totalMinted()","MAX_SUPPLY()","FREE_SUPPLY()","freeMinted()","freeClaimed()","mintedFree()","freeMints()"]:
        v=single(addr, sel(fn))
        print("   ", fn, "=", v)
