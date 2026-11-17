#!/usr/bin/env python3
"""Closeout verification run 0431: BNAgentFile 0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1.
Website evidence already verified by Leg 2 (bnagent.si /skill.md prints exact contract).
This script: (1) Sourcify ABI function list, (2) fresh single-call free views + user slot,
(3) first-mint block via address-filtered Ankr getLogs binary search over ~48h.
Read-only; never previews/mints. Writes run-2026-11-08-0431-bna-verify.json/.log
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch as _batch
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
LOG = open(f"{HF}/run-2026-11-08-0431-bna-verify.log", "w")
def log(*a):
    print(*a, flush=True); print(*a, file=LOG, flush=True)

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def rpc_call(method, params, timeout=15):
    last = None
    for ep in EPS:
        try:
            return _batch([(method, params)], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last

out = {"address": ADDR}

# --- 1. ABI ---
d = json.load(open("/tmp/bna-sourcify2.json"))
abi = d.get("abi", [])
out["sourcify_match"] = d.get("match")
fns = []
for e in abi:
    if e.get("type") == "function":
        sig = e["name"] + "(" + ",".join(i["type"] for i in e.get("inputs", [])) + ")"
        fns.append(sig)
out["functions"] = fns
log("ABI fns:", len(fns))
for f in fns:
    log("  ", f)
names = [f.split("(")[0] for f in fns]
out["has_free_views"] = [f for f in fns if any(w in f.lower() for w in ("free",))]
out["has_registry"] = any("agent" in f.lower() or "registry" in f.lower() for f in fns)

# --- 2. single-call views (one call per batch -> a revert kills only itself) ---
views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "freeLeft(address)", "freeFor(address)",
         "mintedBy(address)", "freeUsed(address)", "AGENT_ID()",
         "agentRegistry()", "registry()", "quote(uint256)", "quote(address,uint256)"]
vals = {}
for sig in views:
    base = sig.split("(")[0]
    data = sel(sig) + (enc(USER) if "(address)" in sig else ("0"*63 + "1" if "(uint256)" in sig else ""))
    try:
        r = rpc_call("eth_call", [{"to": ADDR, "data": data}, "latest"], timeout=10)
        vals[base] = to_int(r)
    except Exception as e:
        vals[base] = None
        log("  view fail", sig, str(e)[:80])
out["views"] = vals
for k, v in vals.items():
    log(f"  {k} = {v}")
try:
    head = int(rpc_call("eth_blockNumber", [], timeout=10), 16)
except Exception as e:
    head = None
    log("head fail", e)
out["head"] = head
log("head:", head)

# --- 3. first-mint binary search (address-filtered Ankr getLogs, 1000-blk chunks) ---
def ankr_addr_logs(frm, to):
    params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
              "address": ADDR, "pageSize": 1000, "decodeLogs": False,
              "topics": [TRANSFER, ZERO_TOPIC]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    res = body.get("result", {}) if isinstance(body, dict) else {}
    return res.get("logs", [])

fm = {"firstMintBlock": None, "firstMintWib": None, "calls": 0}
if head:
    lo, hi = head - 390000, head
    # sanity: any mint in full window?
    t0 = time.time()
    try:
        probe = ankr_addr_logs(hi - 999, hi)
        fm["calls"] += 1
        log(f"probe last chunk [{hi-999},{hi}]: {len(probe)} logs")
    except Exception as e:
        log("probe fail", str(e)[:120])
        probe = None
    if probe is not None:
        # binary search: invariant firstMint in (lo, hi]
        while hi - lo > 1000:
            mid = (lo + hi) // 2
            try:
                logs = ankr_addr_logs(mid - 999, mid)
                fm["calls"] += 1
            except Exception as e:
                log("chunk fail", mid, str(e)[:100]); break
            if logs:
                hi = mid
            else:
                lo = mid
            log(f"  bs lo={lo} hi={hi} logs={len(logs)}")
        # exact first log in [lo, hi]
        try:
            logs = ankr_addr_logs(lo, hi)
            fm["calls"] += 1
            if logs:
                first = min(logs, key=lambda l: int(l["blockNumber"], 16))
                fb = int(first["blockNumber"], 16)
                fm["firstMintBlock"] = fb
                # block timestamp via fast_rpc (NOT Ankr - fake timestamps)
                blk = rpc_call("eth_getBlockByNumber", [hex(fb), False], timeout=15)
                ts = int(blk["timestamp"], 16)
                import datetime
                fm["firstMintWib"] = datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                fm["firstMintTx"] = first.get("transactionHash")
                log("FIRST MINT block", fb, fm["firstMintWib"], "tx", first.get("transactionHash"))
            else:
                log("no mint logs in final window - first mint older than 48h window or none")
        except Exception as e:
            log("final window fail", str(e)[:120])
    fm["seconds"] = round(time.time() - t0, 1)
out["firstMint"] = fm
log("firstMint:", json.dumps(fm))

json.dump(out, open(f"{HF}/run-2026-11-08-0431-bna-verify.json", "w"), indent=1)
log("DONE")
