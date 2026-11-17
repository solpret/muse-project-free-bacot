import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch as _batch
from Crypto.Hash import keccak
def sel(s): return "0x"+keccak.new(digest_bits=256, data=s.encode()).hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.publicnode.com/"]
def single(addr, data):
    for ep in EPS:
        try:
            r=_batch([("eth_call",[{"to":addr,"data":data},"latest"])],endpoint=ep,timeout=12)[0]
            if isinstance(r,str) and r.startswith("0x"):
                try: return int(r,16)
                except: return r
            return r
        except Exception as e:
            last=str(e)[:90]
    return "ERR:"+last
VIEWS=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","freeLeft()","mintOpen()"]
for name, addr in [("AURISLE","0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D"),("InkKoi","0xbd4B4e7189ae9356514664146b0eD683601200A9")]:
    print("==",name,addr)
    for v in VIEWS:
        print("  ",v, single(addr, sel(v)))
    print("   freeClaimed(user):", single(addr, sel("freeClaimed(address)")+enc(USER)))
    print("   freeMintedBy(user):", single(addr, sel("freeMintedBy(address)")+enc(USER)))
    print("   balanceOf(user):", single(addr, sel("balanceOf(address)")+enc(USER)))
