#!/usr/bin/env python3
"""Run 2026-11-06 1831 WIB: targeted on-chain verification of Boltbook leads
(MoonCat, WHALE A/B, Swarmdrake, Lion's Share, Muster, PixelTrump) + HIVE
free-tier-closure claim re-check + age timestamps for Swarmdrake/PixelTrump
first-seen blocks. READ-ONLY; writes run-2026-11-06-1831-boltbook-verify.json."""
import json, sys, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1831"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def call(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            v = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 6, retries=0)
            if v in (None, "0x", ""): return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def block_ts(num):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(num), False], 6, retries=0)
            if b: return int(b["timestamp"], 16)
        except Exception:
            continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)",
         "claimedFree(address)", "quote(address,uint256)", "costOf(address,uint256)",
         "price()", "FREE_PER_WALLET()", "freeFor(address)", "freeLeft()",
         "spotsLeft()", "agentId()", "agentRegistry()"]

TARGETS = {
 "MoonCat": "0x045425004b622733ced4139e930c622187ea6c73",
 "WHALE-A": "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0",
 "WHALE-B": "0xf81b542c41f982a7d7a8e2ee8cab5feee6203218",
 "Swarmdrake": "0x3807470b75f332461d8aae40501e83a7e1fe1819",
 "LionsShare": "0x6ac03204afe631d673938eb82d2f121b015eab3f",
 "Muster": "0x74a7c48e18ac557bdbb43c2e4d0e3820dff3eb77",
 "PixelTrump": "0x3054a5530F1852C33bD2749BFAF7155F162A581b",
 "HIVE": "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
}

out = {}
for name, addr in TARGETS.items():
    d = {"address": addr}
    for sig in VIEWS:
        key = sig.split("(")[0]
        try:
            if "address" in sig and "uint256" in sig:
                v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
            elif "address" in sig:
                v = call(addr, sig, enc(USER)); key += "_user"
            else:
                v = call(addr, sig)
        except Exception as e:
            v = f"err:{e}"
        d[key] = v
    print(name, d, flush=True)
    out[name] = d
    json.dump(out, open(f"{BASE}/run-{TS}-boltbook-verify.json", "w"), indent=1)

# Sourcify ABI for the three brand-new contracts
def sourcify_abi(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,match"],
            capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            d = json.loads(r.stdout)
            return {"match": d.get("match"), "verified": d.get("abi") is not None,
                    "fns": [f.get("name") for f in (d.get("abi") or []) if isinstance(f, dict) and f.get("type") == "function"]}
    except Exception as e:
        return {"error": str(e)}
    return {"verified": False}

for name in ["WHALE-A", "WHALE-B", "Muster"]:
    a = sourcify_abi(TARGETS[name])
    print("SOURCIFY", name, json.dumps(a)[:600], flush=True)
    out[name]["sourcify"] = a
    json.dump(out, open(f"{BASE}/run-{TS}-boltbook-verify.json", "w"), indent=1)

# Age timestamps for first-seen blocks (Swarmdrake / PixelTrump)
for name, blk in [("Swarmdrake", 131470551), ("PixelTrump", 131463433)]:
    ts = block_ts(blk)
    print("BLOCKTS", name, blk, ts, flush=True)
    out[name]["firstSeenBlockTs"] = ts

# First-mint walk (Ankr getLogs, Transfer-from-zero, address-filtered) for new contracts
from ankr import ankr_post
ZERO = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def first_mint(addr):
    head = None
    for ep in EPS:
        try:
            head = int(_single(ep, "eth_blockNumber", [], 6, retries=0), 16); break
        except Exception:
            continue
    if head is None: return {"error": "no head"}
    lo = head - 400000
    hi = head
    earliest = None
    # walk backwards in 20000-block chunks (small calls, fast-fail)
    while hi > lo:
        frm = max(lo, hi - 19999)
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
                "fromBlock": hex(frm), "toBlock": hex(hi), "pageSize": 1000,
                "decodeLogs": False, "topics": [TRANSFER, ZERO],
                "address": [addr.lower()]}, timeout=25)
            logs = body.get("result", {}).get("logs", [])
            if logs:
                earliest = min(int(l["blockNumber"], 16) for l in logs)
                break
        except Exception as e:
            print("  firstmint err", addr, frm, hi, e, flush=True)
        hi = frm - 1
    if earliest is None:
        return {"firstMintBlock": None, "searchedFrom": lo, "head": head}
    ts = block_ts(earliest)
    return {"firstMintBlock": earliest, "firstMintTs": ts, "head": head}

for name in ["WHALE-A", "WHALE-B", "Muster"]:
    fm = first_mint(TARGETS[name])
    print("FIRSTMINT", name, fm, flush=True)
    out[name]["firstMint"] = fm
    json.dump(out, open(f"{BASE}/run-{TS}-boltbook-verify.json", "w"), indent=1)

print("VERIFY DONE", flush=True)
