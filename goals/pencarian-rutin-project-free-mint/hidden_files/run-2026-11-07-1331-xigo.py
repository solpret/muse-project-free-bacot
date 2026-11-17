import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
SALE="0x796387D8106a2edb83e00c4f877e4358Ec721d49"
TOKEN="0xbB30a6C4bafA060C586Eb13128F2250B6285F823"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16)
    except Exception: return None
views=["startTime()","endTime()","freeSharesRemaining()","freeClaimed(address)","freeAvailableFor(address)","totalShares()","sharesMinted()"]
calls=[]; keys=[]
for sig in views:
    base=sig.split("(")[0]
    data=sel(sig)+(enc(USER) if "(address)" in sig else "")
    calls.append(("eth_call",[{"to":SALE,"data":data},"latest"])); keys.append(base)
for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]:
    try:
        res=batch(calls, endpoint=ep, timeout=10)
        out={}
        for k,r in zip(keys,res):
            out[k]=ti(r.get("result")) if isinstance(r,dict) else None
        print(json.dumps(out, indent=1)); break
    except Exception as e:
        print("ep fail", ep, e)
