#!/usr/bin/env python3
"""Hot-leg leg-4 re-read, run 2026-11-14 16:09 WIB. Read-only batch re-read of
live snapshot items vs their last recorded values. No preview/mint, no writes
to the main snapshot. Writes only this run's own JSON in hidden_files."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

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
        calls.append({"to": addr, "data": data})

t0 = time.time()
try:
    from fast_rpc import race
    block = race("eth_blockNumber", [], timeout=8)
    block_n = int(block, 16) if isinstance(block, str) else None
except Exception as e:
    block_n = None
    print("blockNumber failed:", e)
try:
    res = batch_race(calls, timeout=10)
except Exception as e:
    print("batch_race failed, fallback call_many:", e)
    from fast_rpc import call_many
    res = call_many(calls, timeout=25)
print("batch elapsed %.1fs block %s" % (time.time() - t0, block_n))

def dec(r):
    if isinstance(r, dict):
        r = r.get("result")
    if not isinstance(r, str) or not r.startswith("0x"):
        return None
    try:
        return int(r, 16)
    except Exception:
        return None

out = {"run_wib": "2026-11-14T16:09+07:00", "block": block_n, "items": {}}
if isinstance(res, list):
    for (label, fname), r in zip(meta, res):
        out["items"].setdefault(label, {})[fname] = dec(r)
else:
    print("batch_race returned non-list:", str(res)[:300])
    out["error"] = str(res)[:300]

print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "hot-leg-2026-11-14-1609-reread.json", "w"), indent=1)
