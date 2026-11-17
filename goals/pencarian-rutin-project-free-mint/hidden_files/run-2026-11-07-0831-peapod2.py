import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
A="0x25f3efb465685692ef3ddc47ed040baf216b5d38"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
VIEWS=["FREE_PODS_TOTAL()","PAID_PODS_TOTAL()","TOTAL_PODS()","totalPodsMinted()","freePodsClaimed()","paidPodsSold()","paidPodsRemaining()","freeWindowOpen()","freeWindowClosesAt()","gateStart()","podSeasonEndsAt()","freeClaimedBy(address)","podsMintedBy(address)","registry()","devWallet()","peaToken()","windowOpen()","paidSalesOpen()","MAX_PODS_PER_WALLET()"]
out={}
for sig in VIEWS:
    if "(address)" in sig: data=sel(sig)+enc(USER)
    else: data=sel(sig)
    val=None
    for ep in EPS:
        try:
            r=batch([("eth_call",[{"to":A,"data":data},"latest"])], endpoint=ep, timeout=12)
            val=r[0]; break
        except Exception as e:
            val=f"ERR:{str(e)[:80]}"; time.sleep(1)
    try: iv=int(val,16) if isinstance(val,str) and val.startswith("0x") else val
    except Exception: iv=val
    print(sig,"->",val,"=",iv,flush=True); out[sig]=(val,iv)
import datetime
for k in ("freeWindowClosesAt()","gateStart()","podSeasonEndsAt()"):
    v=out.get(k,(None,None))[1]
    if isinstance(v,int) and v>0:
        print(k,"WIB:",datetime.datetime.fromtimestamp(v,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB"),flush=True)
json.dump(out, open("run-2026-11-07-0831-peapod2.json","w"), indent=1, default=str)
