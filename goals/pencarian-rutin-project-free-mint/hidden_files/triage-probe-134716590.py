import sys, json, time
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
from fast_rpc import batch, race
from eth_hash.auto import keccak
def sel(sig): return '0x'+keccak(sig.encode())[:4].hex()
def call(to, sig, args=b''):
    return ("eth_call", [{"to": to, "data": sel(sig)+args.hex()}, "latest"])
A='0xa37b3fF7A1cABf77256a4B246eBa1652011e4569'
calls=[
 ('owner', call(A,'owner()')),
 ('totalSupply', call(A,'totalSupply()')),
 ('name', call(A,'name()')),
 ('symbol', call(A,'symbol()')),
 ('macroSwap', call(A,'macroSwap()')),
 ('agentRegistry', call(A,'agentRegistry()')),
 ('agentIdRegistry', call(A,'agentIdRegistry()')),
]
out={}
for i in range(0, len(calls), 7):
    chunk=calls[i:i+7]
    ok=False
    for attempt in range(4):
        try:
            res=batch([c for _,c in chunk], timeout=15)
            for (label,_), r in zip(chunk, res):
                out[label]=r; print(label,'=>',r, flush=True)
            ok=True; break
        except Exception as e:
            print('chunk',i,'attempt',attempt,'FAIL',str(e)[:150], flush=True); time.sleep(8)
    if not ok:
        for label,_ in chunk: out[label]='BATCH_FAILED'
for blk in [134722341]:
    for attempt in range(3):
        try:
            b=race('eth_getBlockByNumber',[hex(blk), False], timeout=8)
            ts=int(b['timestamp'],16) if b else None
            print('block',blk,'ts',ts, flush=True); out[f'block_{blk}']=ts; break
        except Exception as e:
            print('block',blk,'attempt',attempt,'ERROR',str(e)[:100], flush=True); time.sleep(5)
    else:
        out[f'block_{blk}']='error'
json.dump(out, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/triage-probe-134716590-results.json','w'), indent=1)
print('saved')
