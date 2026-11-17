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
# BHACK mintFree(uint256) is the free lane
C="0x072154bD66Ac9D65Fd29fabCEe1ca1dD52342c5c"
r={}
for fn in ["totalMinted()","totalSupply()","totalFreeMinted()","totalPaidMinted()","freeAllocation()","paidAllocation()","maxSupply()","mintPrice()"]:
    r[fn]=iv(call(C, sel(fn)))
r["agentRegistry()"]=call(C, sel("agentRegistry()"))
aid=call(C, sel("agentKeyOf(address)")+enc_addr(USER)[2:]); r["agentKeyOf_user"]=aid
if aid:
    r["freeMintedByAgentId"]=words(call(C, sel("freeMintedByAgentId(bytes32)")+aid[2:]))
    r["mintedByAgentId"]=words(call(C, sel("mintedByAgentId(bytes32)")+aid[2:]))
r["balance_user"]=iv(call(C, sel("balanceOf(address)")+enc_addr(USER)[2:]))
out["BHACK"]=r
# Hachiko mint(uint256) payable, quote 0 expected
C="0x48c977d13ef156475F086F907D8da9583E1E072E"
r={}
for fn in ["totalSupply()","freeClaimed()","freeCap()","freePerAgent()","maxSupply()","mintOpen()","mintPriceWei()"]:
    r[fn]=iv(call(C, sel(fn)))
r["registry()"]=call(C, sel("registry()"))
aid2=call(C, sel("agentIdOf(address)")+enc_addr(USER)[2:]); r["agentIdOf_user"]=words(aid2)
if aid2:
    hx=format(aid2[0],'064x') if isinstance(aid2,list) else None
    # agentIdOf returns uint256? words gives list; handle raw
    raw=call(C, sel("agentIdOf(address)")+enc_addr(USER)[2:])
    r["agentIdOf_raw"]=raw
    if raw:
        arg=raw[2:].rjust(64,"0")
        r["mintedByAgent_agentid"]=words(call(C, sel("mintedByAgent(uint256)")+arg))
        r["freeUsedByAgent_agentid"]=words(call(C, sel("freeUsedByAgent(uint256)")+arg))
r["quote_user_1"]=words(call(C, sel("quote(address,uint256)")+enc_addr(USER)[2:]+enc_uint(1)[2:]))
r["balance_user"]=iv(call(C, sel("balanceOf(address)")+enc_addr(USER)[2:]))
out["Hachiko"]=r
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0701-exec-check.json","w"), indent=1)
