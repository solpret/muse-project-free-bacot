import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v,16)
    except Exception: return None
try:
    head=int(_single(EPS[0],"eth_blockNumber",[],8,retries=0),16)
except Exception:
    head=None
print("head", head)
# (name, addr, prev ts, prev fc, prev FREE_SUPPLY, prev bal)
items=[
 ("Orchidia","0x09bcdd97186f6f37521bd1b281d329e48ac54b89",2894,2893,None,0),
 ("Agent Goats","0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6",560,560,None,0),
 ("Tacotron","0x05debe4445232205ae7e79d02cb5de5aa0641eff",6933,6932,None,0),
 ("Agent Frogs","0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",539,539,1111,0),
 ("Wuyuhive","0x250e800025a9a7861970e253bab6975a57f80567",1532,1526,3000,0),
 ("Thronemind","0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",829,None,None,0),
]
out={}
for name,addr,pts,pfc,pfs,pbal in items:
    d={"address":addr,
       "totalSupply":iv(call(addr,sel("totalSupply()"))),
       "freeClaimed":iv(call(addr,sel("freeClaimed()"))),
       "freeMinted":iv(call(addr,sel("freeMinted()"))),
       "FREE_SUPPLY":iv(call(addr,sel("FREE_SUPPLY()"))),
       "mintOpen":iv(call(addr,sel("mintOpen()"))),
       "balanceOf_user":iv(call(addr,sel("balanceOf(address)")+enc(USER))),
       "freeClaimed_user":iv(call(addr,sel("freeClaimed(address)")+enc(USER)))}
    out[name]=d
    print(f"{name} ts={d['totalSupply']} (prev {pts}) fc={d['freeClaimed']} (prev {pfc}) FREE_SUPPLY={d['FREE_SUPPLY']} mintOpen={d['mintOpen']} bal={d['balanceOf_user']} fcU={d['freeClaimed_user']}",flush=True)
leads={"CipherAgent":"0x158b5e25015758a94703A27c152889451E5d52E5","MarsAgent":"0x2231FdAe405c33dc4993f8C577c453802FF1AcE9"}
prev_leads={"CipherAgent":47,"MarsAgent":99}
for name,addr in leads.items():
    tm=iv(call(addr,sel("totalMints()")))
    fl=iv(call(addr,sel("freeLeft(address)")+enc(USER)))
    q=call(addr,sel("quote(address,uint256)")+enc(USER)+enc_u(1))
    mb=iv(call(addr,sel("mintedBy(address)")+enc(USER)))
    bal=iv(call(addr,sel("balanceOf(address)")+enc(USER)))
    mo=iv(call(addr,sel("mintOpen()")))
    print(f"{name} totalMints={tm} (prev {prev_leads[name]}) freeLeft={fl} quote={iv(q)} mintedBy={mb} bal={bal} mintOpen={mo}",flush=True)
    out[name]={"address":addr,"totalMints":tm,"freeLeft_user":fl,"quote_user":iv(q),"mintedBy_user":mb,"balanceOf_user":bal,"mintOpen":mo}
json.dump({"block":head,"items":out},open("hot-leg-2026-11-07-1804-reread.json","w"),indent=1)
