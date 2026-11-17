#!/usr/bin/env python3
"""Hot-leg run 2026-11-13 08:09 WIB: batch re-read of active snapshot items.
Read-only eth_call batch via fast_rpc (race + batch). No writes to main snapshot."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

NOARG = ["totalSupply","totalMinted","freeMinted","freeClaimed","freeRemaining",
         "FREE_SUPPLY","FREE_CAP","FREE_SHARES","FREE_LOTS_CAP","mintOpen",
         "isFreeOpen","saleOpen","saleStart","mintOpensAt","mintStart",
         "freeStart","freeEnd","freeClaimedTotal","launched","finalized",
         "refunding","paidMinted","freeCount","freeLeft","refundOpen"]
USERARG = ["balanceOf","freeClaimed","freeMinted","mintedLots","freeAvailable","freeUsed"]

TARGETS = {
 "OBFG": "0x5314071bba19943f58347bA5deC423E5032A6818",
 "RESUME": "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
 "AgentX": "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
 "JNTM": "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
 "AgentMuse": "0x779fa133848d23052B7345F63B3b2E5309cd13ed",
 "Sol": "0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
 "Pickgrid": "0x7f541bcc33abed0e64455565da723e949c6f76f0",
 "OliverAgents": "0xad86e4d52e55709d1bda08f922853d4b109e0810",
 "Stampooor": "0x467696af8c2206B977B24081445104632dc1D459",
 "Tidalune": "0x530695a8e3eb9a1253cafc9239811f4ca88791f9",
 "NOTV": "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
 "WFPASS": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
 "SEVEN": "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
 "LuckyCatch": "0xD405C90079c594DA2456F5b37B4158A12f1382e5",
 "MECHA": "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
 "RigForge": "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
 "BinanceLife": "0x4367b86F889014e6fD57fE812B86A581b913C645",
}

def decode(hexres):
    if not hexres or hexres in ("0x", None):
        return None
    try:
        h = hexres[2:]
        if len(h) < 64:
            return None
        return int(h[-64:], 16)
    except Exception:
        return None

def main():
    t0 = time.time()
    try:
        blk = race("eth_blockNumber", [])
        block = int(blk, 16) if blk else None
    except Exception as e:
        block = None
        print("block read failed:", e)
    calls, keys = [], []
    for name, addr in TARGETS.items():
        for fn in NOARG:
            calls.append((addr, sel(fn + "()")))
            keys.append((name, fn))
        for fn in USERARG:
            calls.append((addr, sel(fn + "(address)") + USER_PAD))
            keys.append((name, fn + "_user"))
    results = {}
    # chunked batches of ~150 calls
    CH = 150
    for i in range(0, len(calls), CH):
        chunk = calls[i:i+CH]
        try:
            res = call_many(chunk)
        except Exception as e:
            print(f"chunk {i} failed: {e}")
            res = [None] * len(chunk)
        for (name, fn), r in zip(keys[i:i+CH], res):
            results.setdefault(name, {})[fn] = decode(r)
        print(f"chunk {i//CH+1}: {len(chunk)} calls in {time.time()-t0:.1f}s")
    out = {"run": "free-mint-hot-leg 2026-11-13 08:09 WIB",
           "started_wib": "2026-11-13T08:09:38+07:00",
           "block": block, "reads": results,
           "elapsed_s": round(time.time() - t0, 1)}
    for name in TARGETS:
        print(name, TARGETS[name], json.dumps(results.get(name, {})))
    json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-13-0809-reads.json", "w"), indent=1)
    print("block", block, "elapsed", round(time.time()-t0, 1))

if __name__ == "__main__":
    main()
