import sys, json, time
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
from fast_rpc import batch, race
from eth_hash.auto import keccak
def sel(sig): return '0x'+keccak(sig.encode())[:4].hex()
def call(to, sig, args=b''):
    return ("eth_call", [{"to": to, "data": sel(sig)+args.hex()}, "latest"])
def addr_arg(a): return bytes.fromhex('00'*12 + a[2:])
W='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
A='0xccda6fa01b7ac7475c344b5717f1f59634823d07'
B='0x1c759c4e075103b5b250db5114b832b17b99c456'
C='0x60153d5098eb900273164cb1f8623fa91ec653b4'
D='0xc779c3e4c8b87b4ecac1b2308e4643e9021373fb'
calls=[
 ('A agentIdRegistry', call(A,'agentIdRegistry()')),
 ('A totalMinted', call(A,'totalMinted()')),
 ('A owner', call(A,'owner()')),
 ('A name', call(A,'name()')),
 ('A MINT_FEE', call(A,'MINT_FEE()')),
 ('A nftsLeft', call(A,'nftsLeft()')),
 ('B agentRegistry', call(B,'agentRegistry()')),
 ('B totalSupply', call(B,'totalSupply()')),
 ('B owner', call(B,'owner()')),
 ('B name', call(B,'name()')),
 ('B WEBSITE', call(B,'WEBSITE()')),
 ('B X', call(B,'X()')),
 ('C agentIdRegistry', call(C,'agentIdRegistry()')),
 ('C totalSupply', call(C,'totalSupply()')),
 ('C owner', call(C,'owner()')),
 ('C name', call(C,'name()')),
 ('D FREE_SUPPLY', call(D,'FREE_SUPPLY()')),
 ('D FreeMinted', call(D,'FreeMinted()')),
 ('D freeMintedBy(user)', call(D,'freeMintedBy(address)', addr_arg(W))),
 ('D totalMinted', call(D,'totalMinted()')),
 ('D owner', call(D,'owner()')),
 ('D name', call(D,'name()')),
 ('D hasAgentID(user)', call(D,'hasAgentID(address)', addr_arg(W))),
 ('D PRICE_LOW', call(D,'PRICE_LOW()')),
 ('D MAX_SUPPLY', call(D,'MAX_SUPPLY()')),
]
out={}
for i in range(0, len(calls), 8):
    chunk=calls[i:i+8]
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
for blk in [134716313,134716337,134716565,134720819]:
    for attempt in range(3):
        try:
            b=race('eth_getBlockByNumber',[hex(blk), False], timeout=8)
            ts=int(b['timestamp'],16) if b else None
            print('block',blk,'ts',ts, flush=True); out[f'block_{blk}']=ts; break
        except Exception as e:
            print('block',blk,'attempt',attempt,'ERROR',str(e)[:100], flush=True); time.sleep(5)
    else:
        out[f'block_{blk}']='error'
json.dump(out, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/triage-probe-134716240-results.json','w'), indent=1)
print('saved')
