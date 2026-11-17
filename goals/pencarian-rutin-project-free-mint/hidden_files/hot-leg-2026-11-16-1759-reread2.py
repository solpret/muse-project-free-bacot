import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = USER[2:].lower().rjust(64, "0")
def sel(s): return "0x" + keccak(s.encode()).hex()[:8]
exec(open("hot-leg-2026-11-16-1759-reread.py").read().split("def main")[0].split("USER_PAD = ")[0]) if False else None
# rebuild PLAN inline (same as reread.py)
def call0(sig): return sel(sig)
def callAddr(sig): return sel(sig) + PAD
PLAN = [
    ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75", [("totalMinted", call0("totalMinted()")),("freeMinted", call0("freeMinted()")),("FREE_CAP", call0("FREE_CAP()")),("mintOpen", call0("mintOpen()")),("balanceOf_user", callAddr("balanceOf(address)"))]),
    ("BinanceAI-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched", call0("launched()")),("failed", call0("failed()")),("isRefundPhase", call0("isRefundPhase()")),("tokenClaimed_user", callAddr("tokenClaimed(address)"))]),
    ("ORBIT", "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [("freeClaimed", call0("freeClaimed()")),("FREE_MAX", call0("FREE_MAX()")),("claimOpen", call0("claimOpen()")),("hasFreeClaimed_user", callAddr("hasFreeClaimed(address)")),("totalSupply", call0("totalSupply()"))]),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [("freeSharesLeft", call0("freeSharesLeft()")),("openedAt", call0("openedAt()")),("freeClaimed", call0("freeClaimed()")),("freeBooked_user", callAddr("freeBooked(address)"))]),
    ("CosmicSentinel", "0x88731d1eb41c36f3d705fdb58b658244c06afc36", [("totalSupply", call0("totalSupply()")),("totalMinted", call0("totalMinted()")),("freeMinted", call0("freeMinted()")),("mintOpen", call0("mintOpen()")),("balanceOf_user", callAddr("balanceOf(address)"))]),
    ("BUBB", "0x0d72970046c056db90888351b739246f468bff0b", [("totalSupply", call0("totalSupply()")),("freeMinted", call0("freeMinted()")),("mintOpen", call0("mintOpen()")),("balanceOf_user", callAddr("balanceOf(address)"))]),
]
def dec(h):
    if h is None: return None
    h = h[2:] if h.startswith("0x") else h
    return int(h, 16) if h else None
t0=time.time()
flat=[]; meta=[]
for name, addr, views in PLAN:
    for vname, data in views:
        flat.append((addr, data)); meta.append((name, vname))
results={}; mode=""
try:
    raw = fast_rpc.call_many(flat, timeout=15)
    for (name, vname), r in zip(meta, raw):
        results.setdefault(name, {})[vname] = dec(r)
    mode="call_many single-batch"
except Exception as e:
    mode=f"call_many FAILED: {type(e).__name__}: {str(e)[:150]}"
    # per-call race, but cap: only 1 attempt each, record errors
    for (name, vname), (addr, data) in zip(meta, flat):
        try:
            r = fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"], timeout=8)
            results.setdefault(name, {})[vname] = dec(r)
        except Exception as e2:
            results.setdefault(name, {})[vname] = f"ERROR: {type(e2).__name__}: {str(e2)[:100]}"
try:
    blk = fast_rpc.race("eth_blockNumber", [], timeout=8); block=int(blk,16)
except Exception as e:
    block=f"ERROR: {e}"
out={"mode":mode,"block":block,"elapsed_s":round(time.time()-t0,1),
     "reads":{n:{"address":a,"views":results.get(n,{})} for n,a,_ in PLAN}}
print(json.dumps(out, indent=1))
json.dump(out, open("hot-leg-2026-11-16-1759-reread.json","w"), indent=1)
