#!/usr/bin/env python3
"""Hot-leg 2026-11-20 09:09 leg-4 retry (single retry): leg-4 batch read failed
totally in the main run (0/43 ints; batch_race + call_many OSError, curl-batch
returned no results). Endpoint now responds again (eth_blockNumber OK).
Re-runs ONLY the leg-4 batch read + change diff vs 0904 reread + thresholds,
updates hot-leg-run-2026-11-20-0909-reread.json and patches the run JSON."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race, batch_race, call_many
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0909"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
def num(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else None

ITEMS = [
 ("STOCKAGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply","totalSupply()",""),("freeLeft","freeLeft()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("mintOpen","mintOpen()",""),("quote_user_1","quote(address,uint256)","addr_uint1"),
   ("freeMintedByWallet_user","freeMintedByWallet(address)","addr"),
   ("balanceOf_user","balanceOf(address)","addr")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply","totalSupply()",""),("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("mintOpen","mintOpen()",""),("balanceOf_user","balanceOf(address)","addr"),
   ("mintedBy_user","mintedBy(address)","addr")]),
 ("AUGENT", "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
  [("freeClaimed","freeClaimed()",""),("freeClaimed_user","freeClaimed(address)","addr"),
   ("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched","launched()",""),("failed","failed()",""),("isRefundPhase","isRefundPhase()",""),
   ("totalShares","totalShares()",""),("tokenClaimed_user","tokenClaimed(address)","addr")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),("totalSupply","totalSupply()","")]),
 ("bsccat-sale", "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
  [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()","")]),
 ("Agent Grove", "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c",
  [("totalSupply","totalSupply()",""),("freeOpen","freeOpen()",""),
   ("freeClaimed_user","freeClaimed(address)","addr"),
   ("balanceOf_user","balanceOf(address)","addr")]),
 ("YAMA-sale", "0x86D779fc4d83044cCECCb53639f9a98E367D6E46",
  [("totalShares","totalShares()",""),("totalFreeShares","totalFreeShares()",""),
   ("freeUsed_user","freeUsed(address)","addr"),
   ("quote_user_1","quote(address,uint256)","addr_uint1")]),
 ("CTXGRAPH4-nodesv2", "0x189DB6602B8D41a0d14CcCc9e999DC3aF895c3f2",
  [("currentGraph","currentGraph()",""),("mintOpen","mintOpen()",""),
   ("isSealed4","isSealed(uint256)","uint4"),
   ("nodesInGraph4","nodesInGraph(uint256)","uint4"),
   ("participantsOf4","participantsOf(uint256)","uint4"),
   ("nodesOf_user_4","nodesOf(address,uint256)","addr_uint4"),
   ("priceFor_user","priceFor(address)","addr"),
   ("holdsAgentId_user","holdsAgentId(address)","addr")]),
]
calls, keys = [], []
for name, addr, views in ITEMS:
    for vk, sig, argt in views:
        data = sel(sig)
        if argt == "addr": data += UA
        elif argt == "addr_uint1": data += UA + enc_uint(1)[2:]
        elif argt == "uint4": data += enc_uint(4)[2:]
        elif argt == "addr_uint4": data += UA + enc_uint(4)[2:]
        calls.append({"to": addr, "data": data})
        keys.append((name, vk))

out = {"retry": "leg4-only", "started_wib": NOW}
t0 = time.time()
results = None; method = None
try:
    results = batch_race(calls, timeout=12); method = "batch_race"
except Exception as ex:
    out["batch_race_error"] = f"{type(ex).__name__}: {str(ex)[:160]}"
    try:
        results = call_many(calls, timeout=12); method = "call_many-fallback"
    except Exception as ex2:
        out["call_many_error"] = f"{type(ex2).__name__}: {str(ex2)[:160]}"
out["method"] = method
out["batch_s"] = round(time.time()-t0, 1)
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
if results:
    for (name, vk), r in zip(keys, results):
        if isinstance(r, str): reads[name]["views"][vk] = iv(r)
        elif isinstance(r, dict): reads[name]["views"][vk] = r
        else: reads[name]["views"][vk] = None
n_int = sum(1 for it in reads.values() for v in it["views"].values() if isinstance(v, int))
n_tot = sum(len(it["views"]) for it in reads.values())
out["ints"] = f"{n_int}/{n_tot}"
try:
    blk = int(race("eth_blockNumber", [], timeout=8), 16)
except Exception:
    blk = None
json.dump({"started_wib": NOW, "block": blk, "reads": reads, "method": method,
           "retry_of_failed_main_run": True},
          open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
out["block"] = blk

# diff vs 0904 reread (0/43 ints there too, so diff mostly unreadable-prev -> value)
try:
    prev = json.load(open(BASE+"hot-leg-run-2026-11-20-0904-reread.json"))
    prev_reads = prev.get("reads", {})
except Exception as ex:
    prev_reads = {}; out["prev_error"] = str(ex)[:120]
changes = {}
for k, cur in reads.items():
    pv = prev_reads.get(k, {}).get("views", {})
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        pvv = pv.get(kk)
        if isinstance(vv, int) and isinstance(pvv, int) and pvv != vv:
            diff[kk] = {"prev": pvv, "now": vv}
        elif isinstance(vv, int) and pvv is None:
            diff[kk] = {"prev": "unreadable-prev", "now": vv}
    changes[k] = diff
out["changes_vs_0904"] = changes
def pct(c, t):
    c, t = num(c), num(t)
    return round(100*c/t, 1) if c is not None and t else None
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
st_fs, st_fl = num(st.get("FREE_SUPPLY")), num(st.get("freeLeft"))
stock_pct = pct((st_fs - st_fl) if st_fs is not None and st_fl is not None else None, st_fs)
lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY"))
out["threshold_check"] = {
  "STOCKAGENT_free_pct": stock_pct, "STOCKAGENT": st,
  "Lumenhold_free_pct": lumen_pct, "Lumenhold": lu,
  "AUGENT": reads["AUGENT"]["views"],
  "binanceai": reads["binanceai-mint"]["views"],
  "AONE_sale": reads["AONE-sale"]["views"],
  "bsccat_sale": reads["bsccat-sale"]["views"],
  "CTXGRAPH4": reads["CTXGRAPH4-nodesv2"]["views"],
  "AgentGrove": reads["Agent Grove"]["views"],
  "YAMA": reads["YAMA-sale"]["views"],
}
json.dump(out, open(BASE+f"hot-leg-run-{RUN}-reread-retry.json","w"), indent=1)
# patch main run json with the retried leg4 results
main = json.load(open(BASE+f"hot-leg-run-{RUN}.json"))
main["leg4_retry"] = out
main["leg4_block"] = blk
main["leg4_method"] = method
main["leg4_changes_vs_2026-11-20-0904_reread"] = changes
main["threshold_check"] = out["threshold_check"]
json.dump(main, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
