import sys, json
sys.path.insert(0,"/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=str(e)[:120]
    return None,err
def iv(v):
    try: return int(v,16) if v else None
    except: return None
def words(v):
    if not v: return None
    b=bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
out={"block":int(_single(EPS[0],"eth_blockNumber",[],8,retries=0),16)}
BIAO="0x16469C174cd827A5e21f4bf3eE3711f2bB42e275"
tests=[("phase()",""),("freeClaimed()",""),("sold()",""),("tradingOpen()",""),("poolCreated()",""),("startedAt()","")]
d={}
for n,a in tests:
    v,e=call(BIAO,sel(n)+a); d[n]=iv(v)
out["BIAO"]=d
print("BIAO",d)
# BNBbaby: address from snapshot? track_c BNBbaby address None in snapshot print; get from previous run files
import glob
for f in glob.glob("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0801-trackc-read.py"):
    print(open(f).read()[:2000])
