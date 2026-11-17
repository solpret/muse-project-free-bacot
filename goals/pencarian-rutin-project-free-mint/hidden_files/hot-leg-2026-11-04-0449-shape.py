import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception: pass
    return None
def code_len(to):
    for ep in EPS:
        try:
            c=_single(ep,"eth_getCode",[to,"latest"],8,retries=0); return (len(c)-2)//2 if c else None
        except Exception: pass
    return None
VIEWS=["totalSupply()","decimals()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_SLOTS()","mintOpen()","mintingOpen()","poolOpen()","freeSharesRemaining()","freeCardsRemaining()","contractURI()","agentRegistry()","owner()"]
FEED=["0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","0x9f08F4Db569F83401e21C0f981E0f7270FFF81f6","0xaF88B24720262433897b9b5C10f8eD107A0d730A","0xaE7E59E6E8c2030ec2a658558e71453ECa6526eA","0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","0xea52b68f6Ab589df1F57CFdfcbAfa20aCa1dF14f","0x14A606B4e14892667bb46a0F1cfCbfB7452860Ad","0x9c60E147f10fF790A293889DDee1e2C4063e096d","0xd1E75De8e6B46E09a90126A122373Fac79578300","0xe9818845C7834fEd64F403e2F5Dd3630272beC4C","0x4AfeBAB78424F1eE0250d208ed2b207312cDd1BE","0xAfe9fc3b24A27Cf20878FC929b1b1fbab5364Dd2","0xA67d1de61a05697f730C4dE1e6dDfed1a4a510bF","0xbcCbf4D476e75Ed055f446D5fBBDb29f119f0312","0xf437576C77212E5d3Dc98CE64749A2E815dB950F","0xC10520b4D965Ed123B3fFc56938d031c31De3CDd","0xAFd02Bdc773f69Df8E393dFaCB51ddafbb136ab9"]
out={}
for a in FEED:
    d={"code_len":code_len(a)}
    for v in VIEWS:
        r=call(a, sel(v))
        try: iv=int(r,16) if r else None
        except Exception: iv=None
        d[v]=iv if iv is not None else ("nonempty" if r and r!="0x" else None)
    out[a]=d
    print(a, d, flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-04-0449-sourcify-shape.json","w"), indent=1)
