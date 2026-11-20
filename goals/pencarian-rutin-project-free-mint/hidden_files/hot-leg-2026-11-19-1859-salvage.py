#!/usr/bin/env python3
"""Salvage probe 2026-11-19 18:59 run: leg-4 batch failed on all chunks
(batch_race timeout + call_many fallback failed). Retry ONLY the 4 most
decision-relevant items with the proven _single sequential method (1854 run).
Read-only; compares vs 1854 reread. If _single also fails, leg-4 stays FAILED."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def call(to, data):
    err = None
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
def collect(to, tests):
    res = {}
    for name, arg in tests:
        val, err = call(to, sel(name)+arg)
        res[name] = iv(val)
        if val is None: res[name+"_err"] = err
    return res
reads = {}
a = "0xba7068233da805bdebcc167be361c219002e6b7f"  # STOCKAGENT
q,_ = call(a, sel("quote(address,uint256)")+UA+enc_uint(1)[2:])
reads["STOCKAGENT"] = {"address": a, "views": collect(a, [("totalSupply()",""),("freeLeft()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("freeMintedByWallet(address)",UA),("balanceOf(address)",UA)])}
reads["STOCKAGENT"]["views"]["quote_user_1"] = iv(q)
a = "0x9701980b0afd825134390ee46fb3bd675a2f356f"  # Lumenhold
reads["Lumenhold"] = {"address": a, "views": collect(a, [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("balanceOf(address)",UA),("mintedBy(address)",UA)])}
a = "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393"  # AUGENT
reads["AUGENT"] = {"address": a, "views": collect(a, [("freeClaimed()",""),("freeClaimed(address)",UA),("totalSupply()",""),("balanceOf(address)",UA)])}
a = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"  # binanceai-mint
reads["binanceai-mint"] = {"address": a, "views": collect(a, [("launched()",""),("failed()",""),("isRefundPhase()",""),("totalShares()",""),("tokenClaimed(address)",UA)])}
try:
    blk = int(_single(EPS[0],"eth_blockNumber",[],8,retries=0),16)
except Exception:
    blk = None
out = {"started_wib": NOW, "block": blk, "reads": reads, "method": "_single sequential (1854-proven)"}
json.dump(out, open(BASE+"hot-leg-run-2026-11-19-1859-salvage.json","w"), indent=1)
# compare vs 1854 reread
prev = json.load(open(BASE+"hot-leg-run-2026-11-19-1854-reread.json"))
changes = {}
for k, cur in reads.items():
    pv = prev.get("reads", {}).get(k, {}).get("views", {})
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        if kk.endswith("_err"): continue
        if pv.get(kk) != vv:
            diff[kk] = {"prev": pv.get(kk), "now": vv}
    changes[k] = diff
out["changes_vs_1854"] = changes
def pct(c, t): return round(100*c/t,1) if c is not None and t else None
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
out["threshold"] = {
  "STOCKAGENT_free_pct": pct((st.get("FREE_SUPPLY()")-st.get("freeLeft()")) if st.get("FREE_SUPPLY()") is not None and st.get("freeLeft()") is not None else None, st.get("FREE_SUPPLY()")),
  "STOCKAGENT": st, "Lumenhold_free_pct": pct(lu.get("freeClaimed()"), lu.get("FREE_SUPPLY()")),
  "Lumenhold": lu, "AUGENT_freeClaimed": reads["AUGENT"]["views"].get("freeClaimed()"),
  "AUGENT_slot_user": reads["AUGENT"]["views"].get("freeClaimed(address)"),
  "binanceai": reads["binanceai-mint"]["views"]}
json.dump(out, open(BASE+"hot-leg-run-2026-11-19-1859-salvage.json","w"), indent=1)
print(json.dumps(out, indent=1))
