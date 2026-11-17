#!/usr/bin/env python3
"""FIND (LumenFindings) exp8 verification, run 2026-11-14 05:31 WIB.
Read-only; writes run-2026-11-14-0531-find-verify.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=150):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

VIEWS = [
 ("AGENT_ID","AGENT_ID()",[]),("MAX_PER_EXPERIMENT","MAX_PER_EXPERIMENT()",[]),
 ("currentExperiment","currentExperiment()",[]),("totalSpecimens","totalSpecimens()",[]),
 ("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),
 ("expStart_8","experimentStart(uint256)",[8]),("expEnd_8","experimentEnd(uint256)",[8]),
 ("specimens_8","specimensInExperiment(uint256)",[8]),
 ("participants_8","participantsOf(uint256)",[8]),
 ("isSealed_8","isSealed(uint256)",[8]),
 ("priceFor_user","priceFor(address)",[USER]),
 ("holdsAgentId_user","holdsAgentId(address)",[USER]),
 ("specimensOf_8_user","specimensOf(uint256,address)",[8, USER]),
 ("baseTokenURI","baseTokenURI()",[]),
 ("name","name()",[]),("symbol","symbol()",[]),
 ("TIER1_PRICE","TIER1_PRICE()",[]),("TIER2_PRICE","TIER2_PRICE()",[]),
]
calls, meta = [], []
for key, sig, args in VIEWS:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": build_data(sig, args)}, "latest"]})
    meta.append(key)
out, ep = None, None
for e in EPS:
    try:
        res = post_rpc(e, calls, timeout=150)
        if isinstance(res, list) and len(res) == len(calls):
            out, ep = res, e; break
        print("ep", e, "bad shape", str(res)[:120], flush=True)
    except Exception as ex:
        print("ep", e, "exc", str(ex)[:100], flush=True)
views = {}
if out is not None:
    for it, key in zip(out, meta):
        if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
            views[key] = None
        else:
            r = it["result"]
            if key in ("AGENT_ID",):
                views[key] = "0x" + r[-40:] if len(r) >= 42 else r
            elif key in ("baseTokenURI", "name", "symbol"):
                views[key] = r  # raw hex, decode later
            else:
                views[key] = to_int(r[:66]) if len(r) >= 66 else r
blk = None
for e in EPS:
    try:
        r = post_rpc(e, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=150)
        if isinstance(r, dict) and r.get("result"): blk = int(r["result"], 16); break
    except Exception: continue
res = {"started_wib": "2026-11-14T05:31+07:00", "address": ADDR, "views": views,
       "endpoint": ep, "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(res, open(BASE + "run-2026-11-14-0531-find-verify.json", "w"), indent=1)
print(json.dumps(res, indent=1))
