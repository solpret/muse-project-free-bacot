import json, subprocess, urllib.request
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x9404e09389a893cb718d36d2e81f51882cb7535f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        else: d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
views = [("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
 ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
 ("mintOpen","mintOpen()",[]),("FREE_PER_WALLET","FREE_PER_WALLET()",[]),
 ("PRICE","PRICE()",[]),("freeLeft_user","freeLeft(address)",[USER]),
 ("freeFor_user_1","freeFor(address,uint256)",[USER,1]),
 ("quote_user_1","quote(address,uint256)",[USER,1]),
 ("balanceOf_user","balanceOf(address)",[USER]),
 ("mintedBy_user","mintedBy(address)",[USER]),
 ("freeUsed_user","freeUsed(address)",[USER])]
calls = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":build(s,a)},"latest"]} for i,(k,s,a) in enumerate(views)]
for ep in EPS:
    try:
        o = subprocess.run(["curl","-sL","--max-time","60","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=70).stdout
        res = json.loads(o)
        if isinstance(res,list) and len(res)==len(calls):
            out = {}
            for it,(k,s,a) in zip(res,views):
                out[k] = to_int(it["result"][:66]) if isinstance(it,dict) and it.get("result") not in (None,"0x") and len(it["result"])>=66 else None
            print("RONIN via", ep); print(json.dumps(out,indent=1)); break
    except Exception as e:
        print("ep fail", ep, str(e)[:80])
# retry Sourcify for 0xC02ab311 (404 in shape-check)
try:
    req = urllib.request.Request("https://sourcify.dev/server/v2/contract/56/0xC02ab311Fd987ba1c380031DA338e56a580B175B?fields=abi", headers={"User-Agent":"hot-leg/1.0"})
    d = json.loads(urllib.request.urlopen(req, timeout=15).read())
    print("C02AB311 retry: OK, abi len", len(d.get("abi") or []))
except Exception as e:
    print("C02AB311 retry:", type(e).__name__, e)
# bridge entry for Roninagent
br = json.load(open("scan-bridge.json"))
print("bridge 0x9404:", json.dumps(br.get("contracts",{}).get("0x9404e09389a893cb718d36d2e81f51882cb7535f"))[:500])
