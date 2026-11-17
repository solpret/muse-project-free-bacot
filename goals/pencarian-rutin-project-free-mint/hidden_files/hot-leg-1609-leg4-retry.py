#!/usr/bin/env python3
"""Hot-leg leg-4 re-read retry, run 2026-11-14 16:09 WIB.
Direct curl-style JSON-RPC batch to bsc-dataseed (fast_rpc batch_race failed:
publicnode 429, onfinality/drpc timeouts). Read-only. Writes only this run's JSON."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
URLS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed1.defibit.io/",
        "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def noarg(fn): return sel(fn + "()")
def addrarg(fn): return sel(fn + "(address)") + enc_addr(USER)

ITEMS = [
 ("RoyalRush", "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",
  [("freeMinted", noarg("freeMinted")), ("totalSupply", noarg("totalSupply")),
   ("mintOpen", noarg("mintOpen")), ("balanceOf_user", addrarg("balanceOf"))]),
 ("PixelFrogs", "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted")),
   ("freeLeft", noarg("freeLeft")), ("freeClaimed_user", addrarg("freeClaimed"))]),
 ("ORBIT", "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680",
  [("freeClaimed", noarg("freeClaimed")), ("freeRemaining", noarg("freeRemaining")),
   ("claimOpen", noarg("claimOpen")), ("hasFreeClaimed_user", addrarg("hasFreeClaimed")),
   ("totalSupply", noarg("totalSupply"))]),
 ("BRAVO", "0xd57a06f0c37e303704261080Fc884f7BE941331D",
  [("freeClaimed", noarg("freeClaimed")), ("FREE_SHARES", noarg("FREE_SHARES")),
   ("seatsTaken", noarg("seatsTaken")), ("openedAt", noarg("openedAt"))]),
 ("NIUBI", "0x2c8EDa46dd4E5228375912f3efFf3781D25a54B7",
  [("refunding", noarg("refunding")), ("opened", noarg("opened")),
   ("freeLeft", noarg("freeLeft"))]),
 ("binanceai", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", noarg("launched")), ("failed", noarg("failed")),
   ("isRefundPhase", noarg("isRefundPhase")), ("tokenClaimed_user", addrarg("tokenClaimed"))]),
 ("Pengu", "0x5AEc03C90656743475810926B2B2bd443D5c26a4",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("RAVE", "0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("CPASS", "0x5877d2bb9f226cc3e438f4d656caeb27deafc576",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("Zephyra", "0x00a9791be6317d6e3a6c60f75a706c870d882048",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("REOPIR", "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("SlateInsignia", "0x5893199322A5300775912ebD236d8f1fEFC700Db",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("VioletWaybill", "0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("AngelEye77D9", "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
  [("totalSupply", noarg("totalSupply")), ("freeMinted", noarg("freeMinted"))]),
 ("MAMI", "0xfe36c6d7a1e352cd0822c6818269d190e8e63c13",
  [("totalSupply", noarg("totalSupply")), ("mintedBy_user", addrarg("mintedBy")),
   ("balanceOf_user", addrarg("balanceOf"))]),
 ("AgentGrove", "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c",
  [("freeMinted", noarg("freeMinted")), ("FREE_SUPPLY", noarg("FREE_SUPPLY")),
   ("freeOpen", noarg("freeOpen")), ("paidMinted", noarg("paidMinted"))]),
 ("LumenFindings", "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
  [("totalSpecimens", noarg("totalSpecimens")), ("currentExperiment", noarg("currentExperiment")),
   ("genesisOpen", noarg("genesisOpen"))]),
 ("WANGCAI", "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd",
  [("freeClaimed", noarg("freeClaimed")), ("mintedBy_user", addrarg("mintedBy"))]),
 ("YUANBAO", "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E",
  [("freeClaimed", noarg("freeClaimed")), ("mintedBy_user", addrarg("mintedBy"))]),
]

calls, meta = [], []
for label, addr, fields in ITEMS:
    for fname, data in fields:
        meta.append((label, fname))
        calls.append({"jsonrpc": "2.0", "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"],
                      "id": len(calls) + 1})

def post_batch(url, payload, timeout=30):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

t0 = time.time()
block_n = None
for u in URLS:
    try:
        b = post_batch(u, {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 0}, timeout=12)
        block_n = int(b["result"], 16)
        print("block ok via", u, block_n)
        break
    except Exception as e:
        print("block fail", u, str(e)[:100])

res = None
errs = []
# split into 2 chunks to stay under per-request limits
for chunk_i in range(0, len(calls), 30):
    chunk = calls[chunk_i:chunk_i + 30]
    ok = False
    for u in URLS:
        try:
            r = post_batch(u, chunk, timeout=30)
            if isinstance(r, list) and len(r) == len(chunk):
                res = (res or []) + r
                ok = True
                print("chunk", chunk_i, "ok via", u)
                break
            errs.append(f"{u} chunk{chunk_i}: bad shape {str(r)[:120]}")
        except Exception as e:
            errs.append(f"{u} chunk{chunk_i}: {str(e)[:120]}")
    if not ok:
        print("chunk", chunk_i, "FAILED on all endpoints")

print("elapsed %.1fs block %s" % (time.time() - t0, block_n))

def dec(r):
    if isinstance(r, dict):
        r = r.get("result")
    if not isinstance(r, str) or not r.startswith("0x"):
        return None
    try:
        return int(r, 16)
    except Exception:
        return None

out = {"run_wib": "2026-11-14T16:09+07:00", "block": block_n, "items": {}, "errors": errs}
if res:
    for (label, fname), r in zip(meta, res):
        out["items"].setdefault(label, {})[fname] = dec(r)
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "hot-leg-2026-11-14-1609-reread.json", "w"), indent=1)
