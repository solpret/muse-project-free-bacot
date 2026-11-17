import json, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0xe15e68C9198ee0A5780fba96016e1780204aF3B4"
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=f"{type(e).__name__}: {str(e)[:160]}"
    return None,err
def show(name,arg=""):
    v,err=call(SALE, sel(name)+arg)
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    print(name, "int=",iv,"raw=",v,"err=",err if v is None else None)
    return v
for n,a in [("registry()",""),("token()",""),("totalCards()",""),("cardsSold()",""),("cardsRemaining()",""),("freeCardCap()",""),("freeCardsRemaining()",""),("freeGiven()",""),("gateOn()",""),("paused()",""),("tokensPerShare()",""),("pricePerShare()",""),("freeClaimed(address)",enc_addr(USER)[2:]),("quotaLeft(address)",enc_addr(USER)[2:]),("quotaUsed(address)",enc_addr(USER)[2:]),("collected(address)",enc_addr(USER)[2:])]:
    show(n,a)
# quote: try quote(uint256) and quote(address,uint256)
for sig,arg in [("quote(uint256)",enc_uint(1)[2:]),("quote(address,uint256)",enc_addr(USER)[2:]+enc_uint(1)[2:])]:
    show(sig,arg)
# block
for ep in EPS:
    try: print("block",int(_single(ep,"eth_blockNumber",[],8,retries=0),16)); break
    except Exception: pass
# ABI mint signature
req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{SALE}?fields=abi", headers={"User-Agent":"hot-leg/1.0"})
with urllib.request.urlopen(req, timeout=15) as r: abi=json.loads(r.read().decode()).get("abi",[])
for e in abi:
    if e.get("type")=="function" and e["name"] in ("mint","quote","registry","freeClaimed"):
        print("ABI",e["name"],[(i.get("name"),i.get("type")) for i in e.get("inputs",[])],"->",[o.get("type") for o in e.get("outputs",[])])
