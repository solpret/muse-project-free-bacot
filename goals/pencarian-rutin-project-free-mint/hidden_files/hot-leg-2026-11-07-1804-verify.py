import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
C = "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
def dec_str(v):
    if not v: return None
    b=bytes.fromhex(v[2:])
    if len(b)>=64:
        ln=int.from_bytes(b[32:64],"big")
        if 0<ln<=len(b)-64: return b[64:64+ln].decode('utf-8','replace')
    return None
head=None
for ep in EPS:
    try: head=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception: pass
print("head", head)
print("name", dec_str(call(C, sel("name()"))), "symbol", dec_str(call(C, sel("symbol()"))))
for fn in ["freeTotal()","freeTakenBy()","mintedTotal()","supplyCap()","opensAt()","closesAt()","priceWei()","paidTotal()","paidTakenBy()","settled()","gate()"]:
    print(" ", fn, iv(call(C, sel(fn))))
print("  freeUsed(user)", iv(call(C, sel("freeUsed(address)")+enc_addr(USER))))
print("  balanceOf(user)", iv(call(C, sel("balanceOf(address)")+enc_addr(USER))))
print("  contractURI", dec_str(call(C, sel("contractURI()"))))
print("  baseURI", dec_str(call(C, sel("baseURI()"))))
# first Transfer (mint) via ankr getLogs
try:
    body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(head-200000),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":C}, timeout=30)
    res=body.get("result",{}) if isinstance(body,dict) else {}
    logs=[l for l in res.get("logs",[]) if l.get("address","").lower()==C.lower()]
    print("  transfer-logs-in-200k-window:", len(logs), "firstBlock:", logs[0]["blockNumber"] if logs else None, "lastBlock:", logs[-1]["blockNumber"] if logs else None)
except Exception as e:
    print("  getLogs err", str(e)[:200])
