#!/usr/bin/env python3
"""Fresh on-chain verify for feed candidates 1731: 0x184701d8 (NFT?) and KIKO9393 0x34aE861F (sale). Read-only."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
import onchain_nft_scan as scan

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def call(fn, args, addr):
    # fn selector helpers via eth_call with encoded data
    import eth_abi
    sig = fn
    return None

def raw_call(addr, data, timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last

def sel(name, types=()):
    import hashlib
    s = f"{name}({','.join(types)})"
    return "0x" + hashlib.sha3_256(s.encode()).hexdigest()[:8] if False else None

# Use eth-abi style: build selectors with keccak via web3-free approach: use known selectors from scan module? Simpler: use function signatures via keccak from hashlib (keccak256 not sha3). Use eth_hash if available.
try:
    from eth_hash.auto import keccak
    def selector(sig):
        return "0x" + keccak(sig.encode()).hex()[:8]
except Exception:
    import subprocess
    def selector(sig):
        p = subprocess.run(["cast", "sig", sig], capture_output=True, text=True)
        return p.stdout.strip()

def enc_addr(a):
    return "000000000000000000000000" + a[2:].lower()

def enc_uint(n):
    return format(n, "064x")

def dec_uint(h):
    if not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None

def dec_bool(h):
    v = dec_uint(h)
    return None if v is None else bool(v)

def dec_str(h):
    if not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception:
        return None

def try_call(addr, sig, args_hex=""):
    try:
        r = raw_call(addr, selector(sig) + args_hex)
        return r
    except Exception as e:
        return f"ERR:{type(e).__name__}"

out = {}
# --- 0x184701d8 NFT-shaped? ---
A = "0x184701d8E75C96639734D439BA7949796Af7F285"
r = {}
r["name"] = dec_str(try_call(A, "name()"))
r["symbol"] = dec_str(try_call(A, "symbol()"))
r["totalSupply"] = dec_uint(try_call(A, "totalSupply()"))
r["totalMinted"] = dec_uint(try_call(A, "totalMinted()"))
r["FREE_CAP"] = dec_uint(try_call(A, "FREE_CAP()"))
r["FREE_SUPPLY"] = dec_uint(try_call(A, "FREE_SUPPLY()"))
r["freeMinted"] = dec_uint(try_call(A, "freeMinted()"))
r["freeCount_agent"] = dec_uint(try_call(A, "freeCount(address)", enc_addr(AGENT)))
r["freeClaimed_agent"] = dec_uint(try_call(A, "freeClaimed(address)", enc_addr(AGENT)))
r["mintOpen"] = dec_uint(try_call(A, "mintOpen()"))
r["mintStart"] = dec_uint(try_call(A, "mintStart()"))
r["owner"] = try_call(A, "owner()")
r["agentId"] = try_call(A, "agentId()")
r["quote_user_1"] = try_call(A, "quote(address,uint256)", enc_addr(AGENT) + enc_uint(1))
r["costWei_1"] = dec_uint(try_call(A, "costWei(uint256)", enc_uint(1)))
out["0x184701d8"] = r
print("1847:", json.dumps(r, indent=1), flush=True)

# --- KIKO9393 sale re-check ---
K = "0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf"
k = {}
k["freeMinted"] = dec_uint(try_call(K, "freeMinted()"))
k["sharesMinted"] = dec_uint(try_call(K, "sharesMinted()"))
k["paidShares"] = dec_uint(try_call(K, "paidShares()"))
k["MAX_FREE"] = dec_uint(try_call(K, "MAX_FREE()"))
k["MAX_SHARES"] = dec_uint(try_call(K, "MAX_SHARES()"))
k["soldOut"] = dec_bool(try_call(K, "soldOut()"))
k["closed"] = dec_bool(try_call(K, "closed()"))
k["freeAvailable_agent"] = dec_bool(try_call(K, "freeAvailable(address)", enc_addr(AGENT)))
k["freeClaimed_agent"] = dec_bool(try_call(K, "freeClaimed(address)", enc_addr(AGENT)))
k["hasMinted_agent"] = dec_bool(try_call(K, "hasMinted(address)", enc_addr(AGENT)))
k["quotaOf_agent"] = dec_uint(try_call(K, "quotaOf(address)", enc_addr(AGENT)))
k["quote_0"] = try_call(K, "quote(uint256)", enc_uint(0))
k["deployedAt"] = dec_uint(try_call(K, "deployedAt()"))
k["agentId"] = try_call(K, "agentId()")
out["KIKO9393"] = k
print("KIKO:", json.dumps(k, indent=1), flush=True)
json.dump(out, open("run-2026-11-08-1731-feed-verify.json", "w"), indent=1)
print("WROTE feed-verify.json")
