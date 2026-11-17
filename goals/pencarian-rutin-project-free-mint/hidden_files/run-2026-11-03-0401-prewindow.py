#!/usr/bin/env python3
import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
ZERO="0x0000000000000000000000000000000000000000"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def ta(a): return "0x000000000000000000000000"+a[2:].lower()
def wib(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def dec_str(raw):
    try:
        b = bytes.fromhex(raw[2:])
        if len(b) < 96: return f"short:{raw[:80]}"
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode(errors="replace")
    except Exception as e: return f"ERR {e}"
targets={"Feed-7BA27":"0x7BA27f90c7b509af1dFBDa2a788Fe4488ff3aab4","Feed-56503":"0x56503C6540411ABa95824A047c50651dcE625Fb3"}
head=int(_single(EPS[0],"eth_blockNumber",[],8,retries=0),16)
print("HEAD", head)
out={"head":head}
for name,addr in targets.items():
    # name/symbol/contractURI raw
    raw_name=call(addr, sel("name()"))
    raw_sym=call(addr, sel("symbol()"))
    raw_uri=call(addr, sel("contractURI()"))
    print(name, "name raw:", (raw_name or "")[:160])
    print(name, "name:", dec_str(raw_name) if raw_name else None, "| symbol:", dec_str(raw_sym) if raw_sym else None, "| uri:", dec_str(raw_uri) if raw_uri else None)
    earliest=None; total=0; chunks=[]; frm=131290000
    while frm<=head:
        to=min(frm+1999,head)
        try:
            body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":[addr],"topics":[TRANSFER,ta(ZERO)],"pageSize":100},timeout=60)
            logs=body.get("result",body).get("logs",[])
        except Exception as e:
            chunks.append((frm,to,f"ERR {type(e).__name__} {str(e)[:80]}")); frm=to+1; continue
        logs=[l for l in logs if len(l.get("topics",[]))>1 and l["topics"][1].lower()==ta(ZERO)]
        chunks.append((frm,to,len(logs))); total+=len(logs)
        for l in logs:
            b=int(l["blockNumber"],16)
            if earliest is None or b<earliest[0]: earliest=(b,l["transactionHash"])
        frm=to+1
    ts=None
    if earliest:
        blk=_single(EPS[0],"eth_getBlockByNumber",[hex(earliest[0]),False],8,retries=0)
        ts=wib(int(blk["timestamp"],16))
    out[name]={"from_zero_logs":total,"earliest_block":earliest[0] if earliest else None,"earliest_tx":earliest[1] if earliest else None,"earliest_wib":ts,"chunks":chunks,
               "name": dec_str(raw_name) if raw_name else None, "symbol": dec_str(raw_sym) if raw_sym else None, "uri": dec_str(raw_uri) if raw_uri else None}
    print(name, "from-zero:", total, "earliest:", earliest, ts)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0401-prewindow.json","w"), indent=1)
