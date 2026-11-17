#!/usr/bin/env python3
"""On-chain read for 2 Boltbook-new contracts, run 2301. Read-only, batch RPC."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
import fast_rpc
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig, args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def dec_str(hexs):
    try:
        b=bytes.fromhex(hexs[2:])
        off=int.from_bytes(b[0:32],'big'); ln=int.from_bytes(b[32:64],'big')
        return b[64:64+ln].decode('utf-8', 'replace')
    except Exception: return None
def dec_int(hexs):
    try: return int(hexs,16) if hexs and hexs!="0x" else None
    except Exception: return None
CAP7="0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd"
MUSE="0x779fa133848d23052B7345F63B3b2E5309cd13ed"
calls=[]; labels=[]
def add(label, to, sig, args=[]):
    labels.append(label); calls.append({"to":to,"data":data(sig,args)})
# CAP7
add("cap7.name",CAP7,"name()",[])
add("cap7.symbol",CAP7,"symbol()",[])
add("cap7.FREE_SHARES",CAP7,"FREE_SHARES()",[])
add("cap7.freeMinted",CAP7,"freeMinted()",[])
add("cap7.TOTAL_SHARES",CAP7,"TOTAL_SHARES()",[])
add("cap7.sharesMinted",CAP7,"sharesMinted()",[])
add("cap7.saleStart",CAP7,"saleStart()",[])
add("cap7.phase",CAP7,"phase()",[])
add("cap7.registry",CAP7,"registry()",[])
add("cap7.costOf_user_1",CAP7,"costOf(address,uint256)",[USER,1])
add("cap7.freeClaimed_user",CAP7,"freeClaimed(address)",[USER])
add("cap7.soldOut",CAP7,"soldOut()",[])
add("cap7.deadline",CAP7,"deadline()",[])
add("cap7.PAID_SHARES",CAP7,"PAID_SHARES()",[])
add("cap7.paidMinted",CAP7,"paidMinted()",[])
# MUSE
add("muse.seatsTaken",MUSE,"seatsTaken()",[])
add("muse.FREE_SHARES",MUSE,"FREE_SHARES()",[])
add("muse.freeClaimed_user",MUSE,"freeClaimed(address)",[USER])
add("muse.openedAt",MUSE,"openedAt()",[])
add("muse.quote_user_1",MUSE,"quote(address,uint256)",[USER,1])
add("muse.website",MUSE,"website()",[])
add("muse.x",MUSE,"x()",[])
add("muse.agentIdOf_user",MUSE,"agentIdOf(address)",[USER])
add("muse.STAGE",MUSE,"STAGE()",[])
add("muse.DOORS_OPEN",MUSE,"DOORS_OPEN()",[])
add("muse.paidSold",MUSE,"paidSold()",[])
add("muse.progress",MUSE,"progress()",[])
res=fast_rpc.batch_race(calls, timeout=15)
out={}
for lab, r in zip(labels, res):
    if r is None: out[lab]=None; continue
    if lab.endswith(("name","symbol","website","x")):
        out[lab]=dec_str(r)
    elif lab.endswith("registry"):
        out[lab]="0x"+r[-40:] if len(r)>=42 else r
    else:
        out[lab]=dec_int(r)
out["block"]=fast_rpc.block_number() if hasattr(fast_rpc,'block_number') else None
json.dump(out, open("run-2026-11-15-2301-cap7-muse.json","w"), indent=1)
print(json.dumps(out, indent=1))
