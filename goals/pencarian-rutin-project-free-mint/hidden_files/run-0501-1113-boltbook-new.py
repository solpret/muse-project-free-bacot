#!/usr/bin/env python3
"""Supplemental read run 0501: 4 Boltbook-new contracts from front page 05:3x WIB.
Read-only; writes run-0501-1113-boltbook-new.json. No preview/mint/execute."""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
U = enc_addr(USER)
VIEWS = [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
 ("freeClaimed","freeClaimed()"),("freeMinted","freeMinted()"),("freeLeft","freeLeft()"),
 ("freeSupply","freeSupply()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
 ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintStart","mintStart()"),
 ("mintOpensAt","mintOpensAt()"),("genesisStart","genesisStart()"),("saleStart","saleStart()"),
 ("freeSharesRemaining","freeSharesRemaining()"),("freeSharesLeft","freeSharesLeft()"),
 ("FREE_SHARES","FREE_SHARES()"),("decimals","decimals()"),
 ("balanceOf_user","balanceOf(address)",U),
 ("freeClaimed_user","freeClaimed(address)",U),
 ("freeMinted_user","freeMinted(address)",U),
 ("mintedBy_user","mintedBy(address)",U),
 ("freeUsed_user","freeUsed(address)",U),
 ("costOf_user_1","costOf(address,uint256)",U+enc_u(1)),
 ("quote_user_1","quote(address,uint256)",U+enc_u(1)),
 ("agentIdRegistry","agentIdRegistry()"),("agentRegistry","agentRegistry()"),
 ("AGENT_REGISTRY","AGENT_REGISTRY()"),("registry","registry()"),("owner","owner()")]
TARGETS = {
 "Voxel Sector": ("0x2c93e68462f0d20ccc54a19d39d9ed25d9f3b9be", VIEWS),
 "Second Agent": ("0x5ebd2d81c864d1681f018d919106faca728126e9", VIEWS),
 "Neon Daemon Guild": ("0xa55d0dd67e443790fef78fe003e1c800201c1d08", VIEWS),
 "FORTUNE8": ("0xfbb7e7424172c52fb43c2742c74e47f63ba78681", VIEWS),
}
def one(item):
    name, (addr, views) = item
    calls, keys = [], []
    for i, (key, sig, *rest) in enumerate(views):
        data = sel(sig) + (rest[0] if rest else "")
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it:
                    out[key] = None; continue
                out[key] = to_int(it.get("result"))
            out["_addr"] = addr
            return name, out
        except Exception:
            continue
    return name, {"_addr": addr, "_error": "all-endpoints-failed"}
t0 = time.time()
out = {"run": "free-mint-search 2026-11-13 05:01 WIB (Boltbook-new supplemental read)",
       "started_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime()),
       "block": None, "reads": {}}
try:
    res = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
    out["block"] = int(res.get("result"), 16)
except Exception as e:
    out["block_error"] = f"{type(e).__name__}: {str(e)[:100]}"
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for name, r in ex.map(one, TARGETS.items()):
        out["reads"][name] = r
        print(f"{name}: {json.dumps(r)}", flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-0501-1113-boltbook-new.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"], "BLOCK", out.get("block"))
