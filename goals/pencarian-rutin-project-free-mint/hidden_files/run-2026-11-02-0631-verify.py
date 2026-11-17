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
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def words(v):
    if not v: return None
    b = bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
out = {"block": blk()}
C = "0x072154bD66Ac9D65Fd29fabCEe1ca1dD52342c5c"
r = {}
for fn in ["totalMinted()","totalSupply()","totalFreeMinted()","totalPaidMinted()","freeAllocation()","paidAllocation()","maxSupply()","mintPrice()"]:
    r[fn] = iv(call(C, sel(fn)))
r["agentRegistry()"] = call(C, sel("agentRegistry()"))
aid = call(C, sel("agentKeyOf(address)")+enc_addr(USER)[2:]); r["agentKeyOf_user"] = aid
if aid:
    r["freeMintedByAgentId"] = words(call(C, sel("freeMintedByAgentId(bytes32)")+aid[2:]))
    r["mintedByAgentId"] = words(call(C, sel("mintedByAgentId(bytes32)")+aid[2:]))
r["balance_user"] = iv(call(C, sel("balanceOf(address)")+enc_addr(USER)[2:]))
out["BHACK"] = r
C = "0x0b32Ab148B57043fBc6F37d762449112387Fa662"
r = {}
for fn in ["totalMinted()","totalSupply()","FREE_SUPPLY()","MAX_SUPPLY()","MAX_PER_WALLET()","PRICE()","currentPrice()"]:
    r[fn] = iv(call(C, sel(fn)))
r["agentIdRegistry()"] = call(C, sel("agentIdRegistry()"))
r["mintedBy_user"] = iv(call(C, sel("mintedBy(address)")+enc_addr(USER)[2:]))
r["balance_user"] = iv(call(C, sel("balanceOf(address)")+enc_addr(USER)[2:]))
r["costFor_1"] = words(call(C, sel("costFor(uint256)")+enc_uint(1)[2:]))
r["quote_user_1"] = words(call(C, sel("quote(address,uint256)")+enc_addr(USER)[2:]+enc_uint(1)[2:]))
out["VOLC"] = r
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0631-verify.json","w"), indent=1)
