#!/usr/bin/env python3
"""One retry of leg-4 for hot-leg 2026-11-20 08:44 WIB (transport flap: batch_race +
call_many all-endpoint OSError; curl-batch-fallback returned all nulls).
Single retry, curl batch in chunks of 10, 20s timeout, then stop."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
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
def curl_batch(chunk):
    payload = [{"jsonrpc":"2.0","id":i,"method":"eth_call",
                "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(chunk)]
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
               "https://bsc-dataseed3.bnbchain.org/"):
        p = subprocess.run(["curl","-s","--max-time","20","-H","Content-Type: application/json",
            "-d", json.dumps(payload), ep], capture_output=True, text=True)
        try:
            resp = json.loads(p.stdout)
            if isinstance(resp, list):
                by_id = {r.get("id"): r for r in resp}
                outl = []
                for i in range(len(chunk)):
                    r = by_id.get(i, {})
                    outl.append(r.get("result") if "result" in r else ({"error": str(r.get("error"))[:120]} if "error" in r else None))
                return outl, ep
        except Exception:
            continue
    return [None]*len(chunk), None
t0 = time.time()
results = []
eps = []
for i in range(0, len(calls), 10):
    r, ep = curl_batch(calls[i:i+10])
    results.extend(r); eps.append(ep)
    time.sleep(1)
blk = None
p = subprocess.run(["curl","-s","--max-time","15","-H","Content-Type: application/json",
    "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}',
    "https://bsc-dataseed.binance.org/"], capture_output=True, text=True)
try: blk = int(json.loads(p.stdout)["result"], 16)
except Exception: pass
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
for (name, vk), r in zip(keys, results):
    reads[name]["views"][vk] = iv(r) if isinstance(r, str) else r
n_ok = sum(1 for v in reads.values() for x in v["views"].values() if isinstance(x, int))
json.dump({"started_wib": "2026-11-20T08:49:24+07:00", "block": blk, "reads": reads,
           "method": "curl-batch-chunk10-retry", "endpoints": eps, "ok_ints": n_ok,
           "elapsed_s": round(time.time()-t0,1)},
          open(BASE+"hot-leg-run-2026-11-20-0844-reread-retry.json","w"), indent=1)
print(json.dumps({"block": blk, "ok_ints": n_ok, "of": len(keys), "elapsed_s": round(time.time()-t0,1)}))
print(json.dumps(reads, indent=1))
