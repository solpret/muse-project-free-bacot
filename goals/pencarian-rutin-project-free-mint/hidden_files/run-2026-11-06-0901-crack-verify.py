#!/usr/bin/env python3
"""Run 0901: post-mint on-chain verification for Crack mint."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
ADDR="0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TX="0xf3c1478fc8f66b3dc669a18858fb8e321c65e843f121f3607686854e8de2e41a"
EPS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(data):
    for ep in EPS:
        try:
            out=_single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],8,retries=0)
            if out is None or out=="0x": return None
            return int(out,16)
        except Exception: continue
    return None
def call_raw(data):
    for ep in EPS:
        try:
            return _single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],8,retries=0)
        except Exception: continue
    return None
receipt=None
for i in range(20):
    for ep in EPS:
        try:
            r=_single(ep,"eth_getTransactionReceipt",[TX],8,retries=0)
            if r: receipt=r; break
        except Exception: continue
    if receipt: break
    print("waiting receipt, try", i+1, flush=True); time.sleep(5)
print("RECEIPT:", json.dumps(receipt, indent=1) if receipt else None, flush=True)
out={"tx":TX, "receipt":receipt}
if receipt:
    out["status"]=int(receipt.get("status","0x0"),16)
    out["block"]=int(receipt.get("blockNumber","0x0"),16)
    out["gasUsed"]=int(receipt.get("gasUsed","0x0"),16)
    # ownership + flags after mint
    out["balanceOf_user"]=call(sel("balanceOf(address)")+enc(USER))
    out["ownerOf_790"]=call_raw(sel("ownerOf(uint256)")+format(790,"064x"))
    out["freeUsed_user"]=call(sel("freeUsed(address)")+enc(USER))
    out["mintedBy_user"]=call(sel("mintedBy(address)")+enc(USER))
    out["totalMinted"]=call(sel("totalMinted()"))
    out["totalSupply"]=call(sel("totalSupply()"))
    out["publicRemaining"]=call(sel("publicRemaining()"))
    # tokenURI of 790 for rarity traits
    out["tokenURI_790_raw"]=call_raw(sel("tokenURI(uint256)")+format(790,"064x"))
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-06-0901-crack-verify.json","w"), indent=1)
