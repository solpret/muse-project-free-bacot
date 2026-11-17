#!/usr/bin/env python3
"""Run 2026-11-06 1901 WIB Boltbook-verify (subagent A findings).
READ-ONLY. Verifies on-chain: 3 new Boltbook contracts (Ape Agent, Stickman,
ACC) + Dragonmind sold-out claim + Agent Panda reopen claim + HashOre sold-out
claim. Writes run-2026-11-06-1901-boltbook-verify.json.
First-mint lookup: bounded Ankr getLogs (address + Transfer-from-zero),
max 3 chunks of 1000 blocks backwards from the known mint block.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1901"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=8):
    import urllib.request
    for rpc in EPS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""):
    return raw(to, sel(sig) + args)

def sourcify(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "15",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=25)
        if r.returncode == 0 and r.stdout.strip():
            d = json.loads(r.stdout)
            return "verified" if d.get("abi") is not None else "not_verified"
    except Exception as e:
        print("  sourcify err", addr, e, flush=True)
    return "error"

def first_mint(addr, start_block, max_chunks=3):
    """Walk backwards in 1000-block chunks; return first mint block or None."""
    to_b = start_block
    for _ in range(max_chunks):
        from_b = max(0, to_b - 999)
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
                "fromBlock": hex(from_b), "toBlock": hex(to_b),
                "address": addr, "pageSize": 1000, "decodeLogs": False,
                "topics": [TRANSFER, ZERO_TOPIC]}, timeout=30)
            logs = body.get("result", {}).get("logs", [])
            if logs:
                blk = min(int(l.get("blockNumber", "0x0"), 16) for l in logs)
                return {"firstMintBlock": blk, "chunk": [from_b, to_b], "mintsInChunk": len(logs)}
        except Exception as e:
            print(f"  first-mint lookup {addr} chunk {from_b}-{to_b} failed: {e}", flush=True)
            return None
        to_b = from_b - 1
    return {"firstMintBlock": None, "note": f"no mint in {max_chunks}x1000 blocks before {start_block} — first mint earlier or lookup inconclusive"}

ITEMS = {
 "ApeAgent": {"addr": "0x8150922eb36b7d5972b6b06254435dd755a7c54c",
              "views": ["totalSupply()", "totalMinted()", "balanceOf(address)", "mintOpen()", "MAX_SUPPLY()"],
              "start_block": 132004404, "note": "Boltbook lloyd.ai /p/skuGZal9P9LZ ~18:56 WIB: mint(1) value 0, 1 gratis/wallet lalu 0,001 BNB, max 10; 251/4444; NO Agent ID gate (eksplisit di post); Sourcify 404 per subagent A."},
 "Stickman": {"addr": "0x345b0eb3180ae510cB2f05EfD49085E79477b330",
              "views": ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)", "mintOpen()", "MAX_SUPPLY()"],
              "start_block": 132004933, "note": "Boltbook sanity.ai /p/sCAVq2-DKIb8; site stickmanmaster.xyz; supply 4444, 1 gratis/wallet; totalMinted 332 (406 per komentar); freeMint() sim bersih per subagent A; decoy 0xd8B956e5D50fFB592ed06FBc37664056c2C18165 tanpa code."},
 "ACC": {"addr": "0xeeb4e27bcf62e257920cb573eb8ca14392c62637",
         "views": ["totalSupply()", "balanceOf(address)", "decimals()"],
         "start_block": 132005091, "note": "Boltbook grandtheftauto6.ai /p/bROAOqK7Jsw2; fungible token, claim() static ok value 0, mint/freeMint revert, tanpa pair V2 WBNB; totalSupply loncat +14.299.995.698 (4.302 -> 14.300.000.000) = RED FLAG."},
 "Dragonmind": {"addr": "0x84ce3c8662c081232ae505195f3c3a7f1a9f4ac0",
                "views": ["totalSupply()", "totalMinted()", "mintOpen()", "MAX_SUPPLY()"],
                "start_block": 132005254, "note": "Sold-out claim subagent A: 777/777 blok 132005254 (hensyah08.ai /p/Q9PnwbxkPo25); sebelumnya early-lead-reported-2026-11-04, totalSupply 143 di snapshot."},
 "AgentPanda": {"addr": "0x7561c414a7a6ff44fc81e9bfc2eda8f57c3ec61e",
                "views": ["totalMinted()", "mintOpen()", "totalSupply()"],
                "start_block": 132003641, "note": "Reopen claim subagent A: totalMinted 8.178/10.000, mintOpen 1 (blok 132003641, hi5.ai /p/knoxzbDi7_7w); sebelumnya TUTUP (mintOpen 0 di 8.115); item age-excluded (first mint 2026-11-03 03:05:04 WIB, ~88 jam); free mint butuh PoW."},
 "HashOre": {"addr": "0x828e7073Ef57Ed778E4acF82cC45BC43eF760b54",
             "views": ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "mintOpen()"],
             "start_block": 132005500, "note": "Sold-out claim subagent A: 10.000/10.000, mining selesai (akeyy.ai /p/OO052Gh9Gu9X); baru bagi snapshot."},
}

out = {}
for name, meta in ITEMS.items():
    a = meta["addr"]
    r = {"address": a, "note": meta["note"]}
    for sig in meta["views"]:
        key = sig.split("(")[0]
        if "address" in sig:
            v = call(a, sig, enc(USER)); key += "_user"
        else:
            v = call(a, sig)
        r[key] = v
    r["sourcify"] = sourcify(a)
    r["firstMint"] = first_mint(a, meta["start_block"])
    out[name] = r
    print(name, a, json.dumps(r), flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-boltbook-verify.json", "w"), indent=1)
print("BOLTBOOK-VERIFY DONE", flush=True)
