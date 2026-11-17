import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
SALE="0x796387D8106a2edb83e00c4f877e4358Ec721d49"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16)
    except Exception: return None
views=["startTime()","endTime()","freeSharesRemaining()","totalShares()","sharesMinted()","freeAvailableFor(address)","freeClaimed(address)","quote(address,uint256)"]
for sig in views:
    data=sel(sig)+(enc(USER) if "(address)" in sig else ("0"*64 if "(address,uint256)" in sig else ""))
    if "(address,uint256)" in sig:
        data=sel(sig)+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
    ok=False
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/"]:
        try:
            res=batch([("eth_call",[{"to":SALE,"data":data},"latest"])], endpoint=ep, timeout=10)
            r=res[0]
            if isinstance(r,dict) and "result" in r:
                print(sig, "->", ti(r["result"])); ok=True; break
            else:
                print(sig, "-> ERR", r); ok=True; break
        except Exception as e:
            print(sig, "ep fail", e); break
    if not ok: print(sig, "-> no result")
