import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak
ADDR="0xa900873E65B5F391B6E37d80a98A6b26D07613B8"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(data):
    for ep in EPS:
        try:
            v=_fast_single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],8,retries=0)
            return None if v in (None,"0x") else v
        except Exception: continue
    return "transport-fail"
def dec_int(v):
    if v is None or v=="transport-fail": return v
    try: return int(v,16)
    except Exception: return v
def dec_str(v):
    if not v or v=="transport-fail": return v
    try:
        b=bytes.fromhex(v[2:]); off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode("utf-8","replace")
    except Exception: return f"decode-err:{v[:100]}"
blk=None
for ep in EPS:
    try:
        blk=int(_fast_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception: continue
out={"block":blk}
for sig in ["name()","symbol()"]:
    out[sig.split("(")[0]]=dec_str(raw(sel(sig)))
for sig in ["totalSupply()","totalMints()","MAX_MINTS()","MAX_SUPPLY()","mintOpen()","PRICE()","FREE_PER_WALLET()","MAX_PER_WALLET()","MINT_AMOUNT()","MINT_DEADLINE()","MINT_DURATION()","tradingOpen()","liquidityBNB()","devAccrued()"]:
    out[sig.split("(")[0]]=dec_int(raw(sel(sig)))
out["AGENT_ID"]=raw(sel("AGENT_ID()"))
out["FACTORY"]=raw(sel("FACTORY()"))
out["pair"]=raw(sel("pair()"))
out["dev"]=raw(sel("dev()"))
out["freeLeft_user"]=dec_int(raw(sel("freeLeft(address)")+enc(USER)))
out["mintedBy_user"]=dec_int(raw(sel("mintedBy(address)")+enc(USER)))
out["balanceOf_user"]=dec_int(raw(sel("balanceOf(address)")+enc(USER)))
out["quote_user1"]=dec_int(raw(sel("quote(address,uint256)")+enc(USER)+enc_uint(1)))
print(json.dumps(out,indent=1))
json.dump(out,open("verify-a900-1201.json","w"),indent=1)
