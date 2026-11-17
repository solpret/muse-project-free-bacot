import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v, 16) if v else None
def words(v):
    if not v: return None
    b = bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
out={"block": blk()}
# Bd14 PIXEL FROGS extra views
C="0xBd144C91F0bcA43Ee86a47a07488710D33281E8b"
r={}
for fn,arg in [("freeClaimed(address)",enc_addr(USER)[2:]),("mintedByType(address)",enc_addr(USER)[2:]),("bonusFor(address)",enc_addr(USER)[2:]),("walletInfo(address)",enc_addr(USER)[2:]),("mintInfo()", ""),("remaining()", ""),("freeSupply()", ""),("totalFreeClaimed()", ""),("freeMinted()", ""),("mintedBy(address)",enc_addr(USER)[2:])]:
    v=call(C,sel(fn)+arg); r[fn]=words(v)
out["Bd14_extra"]=r; print("Bd14", json.dumps(r))
# C48c Hachiko extra views
C="0x48c977d13ef156475F086F907D8da9583E1E072E"
r={}
for fn,arg in [("mintedByAgent(address)",enc_addr(USER)[2:]),("freeUsedByAgent(bytes32)", "0"*64),("agentIdOf(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])]:
    v=call(C,sel(fn)+arg); r[fn]=words(v) if v else None
aid=r.get("agentIdOf(address)")
if aid and aid[0]:
    hx=format(aid[0],'064x')
    for fn in ["freeUsedByAgent(bytes32)","freeClaimed(bytes32)","mintedByAgent(bytes32)"]:
        v=call(C,sel(fn)+hx); r[fn+"_agentid"]=words(v) if v else None
out["C48c_extra"]=r; print("C48c", json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0731-verify4.json","w"), indent=1)
