import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v, 16) if v else None
out = {"block": None}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
C = "0xa2E9e8ad747b2422010F79DF62562Ade8Ab09738"
r = {}
for fn in ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeClaimed()", "freeMinted()", "freeFee()", "maxFreePerWallet()", "mintOpen()", "freeOpen()"]:
    r[fn] = iv(call(C, sel(fn)))
r["agentRegistry_reads"] = {}
for fn in ["AGENT_ID()", "agentRegistry()", "agentIdRegistry()", "REGISTRY()", "registry()"]:
    v = call(C, sel(fn))
    if v: r["agentRegistry_reads"][fn] = v
out["Belyore"] = r
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0631-scan-triage.json","w"), indent=1)
