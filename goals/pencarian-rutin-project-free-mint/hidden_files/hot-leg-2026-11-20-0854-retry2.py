#!/usr/bin/env python3
"""Hot-leg 0854 leg-4 retry #2: chunked curl batches (5 calls each).
Diagnosis: 43-call batch to bsc-dataseed returns 403 / null results (batch-size
rate limiting); 2-3 call batches succeed. Chunked batches should succeed.
Patches hot-leg-run-2026-11-20-0854-reread.json + -reread-retry.json + run JSON."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0854"
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
def num(v): return v if isinstance(v, int) and not isinstance(v, bool) else None

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

EP = "https://bsc-dataseed.binance.org/"
def chunk_batch(chunk):
    payload = [{"jsonrpc":"2.0","id":i,"method":"eth_call",
                "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(chunk)]
    p = subprocess.run(["curl","-s","--max-time","25","-H","Content-Type: application/json",
        "-d", json.dumps(payload), EP], capture_output=True, text=True)
    resp = json.loads(p.stdout)
    if not isinstance(resp, list):
        raise ValueError(f"non-list response: {str(resp)[:200]}")
    by_id = {r.get("id"): r for r in resp}
    out_list = []
    for i in range(len(chunk)):
        r = by_id.get(i, {})
        if "result" in r: out_list.append(r["result"])
        elif "error" in r: out_list.append({"error": str(r["error"])[:120]})
        else: out_list.append(None)
    return out_list

t0 = time.time()
results = [None]*len(calls)
errors = []
CH = 5
for s in range(0, len(calls), CH):
    try:
        res = chunk_batch(calls[s:s+CH])
        results[s:s+CH] = res
    except Exception as ex:
        errors.append(f"chunk@{s}: {type(ex).__name__}: {str(ex)[:120]}")
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
for (name, vk), r in zip(keys, results):
    if isinstance(r, str): reads[name]["views"][vk] = iv(r)
    elif isinstance(r, dict): reads[name]["views"][vk] = r
    else: reads[name]["views"][vk] = None
try:
    p = subprocess.run(["curl","-s","--max-time","15","-H","Content-Type: application/json",
        "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}', EP],
        capture_output=True, text=True)
    blk = int(json.loads(p.stdout)["result"], 16)
except Exception:
    blk = None
json.dump({"started_wib": NOW, "block": blk, "reads": reads,
           "method": "curl-batch-chunked-5", "endpoint": EP, "chunk_errors": errors},
          open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
prev = json.load(open(BASE+"hot-leg-run-2026-11-20-0844-reread.json")).get("reads", {})
changes = {}
for k, cur in reads.items():
    pv = prev.get(k, {}).get("views", {})
    cv = cur["views"]
    diff = {}
    for kk, vv in cv.items():
        pvv = pv.get(kk)
        if isinstance(vv, int) and isinstance(pvv, int) and pvv != vv:
            diff[kk] = {"prev": pvv, "now": vv}
        elif isinstance(vv, int) and pvv is None:
            diff[kk] = {"prev": "unreadable-prev", "now": vv}
        elif isinstance(vv, dict) and pvv is None:
            diff[kk] = {"prev": "unreadable-prev", "now": vv}
    changes[k] = diff
def pct(c, t):
    c, t = num(c), num(t)
    return round(100*c/t, 1) if c is not None and t else None
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
st_fs, st_fl = num(st.get("FREE_SUPPLY")), num(st.get("freeLeft"))
stock_pct = pct((st_fs - st_fl) if st_fs is not None and st_fl is not None else None, st_fs)
lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY"))
out = {"retry2_started_wib": NOW, "method": "curl-batch-chunked-5", "endpoint": EP,
       "chunk_errors": errors, "elapsed_s": round(time.time()-t0, 1), "block": blk,
       "changes_vs_0844": changes,
       "threshold_check": {"STOCKAGENT_free_pct": stock_pct, "STOCKAGENT": st,
                           "Lumenhold_free_pct": lumen_pct, "Lumenhold": lu,
                           "AUGENT": reads["AUGENT"]["views"],
                           "binanceai": reads["binanceai-mint"]["views"],
                           "AONE_sale": reads["AONE-sale"]["views"],
                           "bsccat_sale": reads["bsccat-sale"]["views"],
                           "CTXGRAPH4": reads["CTXGRAPH4-nodesv2"]["views"],
                           "AgentGrove": reads["Agent Grove"]["views"],
                           "YAMA": reads["YAMA-sale"]["views"]}}
json.dump(out, open(BASE+f"hot-leg-run-{RUN}-reread-retry2.json","w"), indent=1)
print(json.dumps(out, indent=1))
