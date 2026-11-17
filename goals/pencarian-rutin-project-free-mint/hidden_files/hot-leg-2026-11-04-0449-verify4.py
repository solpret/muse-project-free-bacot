import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def enc_addr(a): return a[2:].lower().rjust(64,"0")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception: pass
    return None
def dec_str(raw):
    try:
        b=bytes.fromhex(raw[2:])
        # ABI string: offset, len
        ln=int.from_bytes(b[32:64],'big')
        return b[64:64+ln].decode(errors='replace')
    except Exception as e: return f"<decode err {e}> rawlen={len(raw) if raw else 0}"
def dec_int(raw):
    try: return int(raw,16) if raw else None
    except Exception: return None
FEED=["0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","0x9c60E147f10fF790A293889DDee1e2C4063e096d","0xd1E75De8e6B46E09a90126A122373Fac79578300"]
out={}
for a in FEED:
    d={}
    d['name']=dec_str(call(a, sel("name()")))
    d['symbol']=dec_str(call(a, sel("symbol()")))
    d['contractURI']=dec_str(call(a, sel("contractURI()")))
    for fn in ["mintedBy(address)","freeUsed(address)","balanceOf(address)","hasAgentId(address)","freeLeft(address)","freeClaimed(address)"]:
        d[fn]=dec_int(call(a, sel(fn)+enc_addr(USER)))
    d['totalSupply']=dec_int(call(a, sel("totalSupply()")))
    d['FREE_SUPPLY']=dec_int(call(a, sel("FREE_SUPPLY()")))
    d['freeClaimed_total']=dec_int(call(a, sel("freeClaimed()")))
    out[a]=d; print(a, json.dumps(d)[:800], flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-04-0449-verify4.json","w"), indent=1)
