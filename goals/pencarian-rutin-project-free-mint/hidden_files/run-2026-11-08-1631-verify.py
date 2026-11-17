#!/usr/bin/env python3
"""Deep verification for run 1631 first-seen contracts (read-only).
Single-call eth_calls (one per view) so a reverting view cannot kill the batch.
Block timestamps via fast_rpc eth_getBlockByNumber (NEVER Ankr - fake timestamps).
No preview/mint/approve/sign/transaction of any kind."""
import sys, json, time, urllib.request, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch as _batch
import onchain_nft_scan as scan

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def call(method, params, timeout=15):
    last = None
    for ep in EPS:
        try:
            return _batch([(method, params)], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last

def sel(name):
    import hashlib
    # keccak via eth_call-free local computation using sha3_256? No - use selector table for known views.
    raise NotImplementedError

# selector map (keccak4 of canonical signatures, verified against Sourcify ABIs in prior runs)
SELECTORS = {
    "AGENT_REGISTRY()": "0x0e8a04a0", "AGENT_ID_REGISTRY()": "0x1f2a6c8e",
    "agentRegistry()": "0x0e8a04a0", "PRICE()": "0x0e8a04a0",
}
# NOTE: selectors above are placeholders - real selectors are computed from ABI below.

def keccak4(sig):
    try:
        from Crypto.Hash import keccak
        k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
    except ImportError:
        import sha3
        return "0x" + sha3.keccak_256(sig.encode()).hexdigest()[:8]

def eth_call(addr, sig, args_hex=""):
    data = keccak4(sig) + args_hex
    try:
        out = call("eth_call", [{"to": addr, "data": data}, "latest"])
        return out
    except Exception as e:
        return {"_error": str(e)[:200]}

def as_int(out):
    if isinstance(out, dict): return out
    try: return int(out, 16)
    except Exception: return {"_unparsed": str(out)[:120]}

def as_addr(out):
    if isinstance(out, dict): return out
    try: return "0x" + out[-40:]
    except Exception: return {"_unparsed": str(out)[:120]}

def as_str(out):
    if isinstance(out, dict): return out
    return scan.decode_str_or_bytes32(out)

def addr_arg(a):
    return "000000000000000000000000" + a[2:].lower()

def uint_arg(n):
    return format(n, "064x")

VIEWS = [
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", "addr"),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", "addr"),
    ("agentRegistry", "agentRegistry()", "addr"),
    ("owner", "owner()", "addr"),
    ("totalSupply", "totalSupply()", "int"),
    ("totalMinted", "totalMinted()", "int"),
    ("MAX_SUPPLY", "MAX_SUPPLY()", "int"),
    ("FREE_SUPPLY", "FREE_SUPPLY()", "int"),
    ("FREE_CAP", "FREE_CAP()", "int"),
    ("FREE_SLOTS", "FREE_SLOTS()", "int"),
    ("freeMinted", "freeMinted()", "int"),
    ("freeClaimed_total", "freeClaimed()", "int"),
    ("freeLeft", "freeLeft()", "int"),
    ("mintOpen", "mintOpen()", "int"),
    ("mintOpenTime", "mintOpenTime()", "int"),
    ("mintStart", "mintStart()", "int"),
    ("isFree", "isFree()", "int"),
    ("PRICE", "PRICE()", "int"),
    ("PRICE_1", "PRICE_1()", "int"),
    ("contractURI", "contractURI()", "str"),
]
USER_VIEWS = [
    ("freeClaimed_user", "freeClaimed(address)", "int"),
    ("freeMintedBy_user", "freeMintedBy(address)", "int"),
    ("freeUsed_user", "freeUsed(address)", "int"),
    ("claimedFree_user", "claimedFree(address)", "int"),
    ("mintedBy_user", "mintedBy(address)", "int"),
    ("quote_1", "quote(uint256)", "int"),
    ("costFor_1", "costFor(uint256)", "int"),
]

def verify(addr, first_block):
    r = {"address": addr, "first_block": first_block}
    # block timestamp via fast_rpc (NOT Ankr)
    try:
        blk = call("eth_getBlockByNumber", [hex(first_block), False])
        ts = int(blk["timestamp"], 16)
        r["first_block_ts"] = ts
        r["first_block_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600))
    except Exception as e:
        r["first_block_ts_error"] = str(e)[:200]
    for key, sig, kind in VIEWS:
        out = eth_call(addr, sig)
        if isinstance(out, dict):
            r[key + "_error"] = out["_error"]
        elif kind == "int": r[key] = as_int(out)
        elif kind == "addr": r[key] = as_addr(out)
        else: r[key] = as_str(out)
    for key, sig, kind in USER_VIEWS:
        arg = addr_arg(AGENT) if "address" in sig else uint_arg(1)
        out = eth_call(addr, sig, arg)
        if isinstance(out, dict):
            r[key + "_error"] = out["_error"]
        else:
            r[key] = as_int(out)
    # Sourcify ABI (urllib, curl fallback)
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    abi = None; status = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode()); abi = data.get("abi"); status = "verified"
    except Exception as e:
        status = f"urllib_error:{type(e).__name__}"
        try:
            p = subprocess.run(["curl", "-sS", "-m", "20", "-A", "Mozilla/5.0", url],
                               capture_output=True, text=True, timeout=30)
            if p.returncode == 0 and p.stdout.strip():
                data = json.loads(p.stdout); abi = data.get("abi"); status = "verified(curl)"
            else:
                status = f"curl_error:rc={p.returncode}:{p.stderr[:100]}"
        except Exception as e2:
            status = f"curl_error:{type(e2).__name__}"
    r["sourcify"] = status
    if isinstance(abi, list):
        r["abi_functions"] = sorted({i.get("name","") for i in abi if i.get("type")=="function" and i.get("name")})
        # contractURI external_link / tokenURI hints
        for i in abi:
            if i.get("type")=="function" and i.get("name") in ("contractURI","tokenURI","external_link"):
                pass
    # registry view match
    for k in ("AGENT_REGISTRY","AGENT_ID_REGISTRY","agentRegistry"):
        v = r.get(k)
        if isinstance(v, str):
            r["registry_view_match"] = (v.lower() == REGISTRY.lower())
            break
    return r

if __name__ == "__main__":
    targets = json.loads(sys.argv[1])  # [{"address":..., "first_block":...}]
    out = {}
    for t in targets:
        print(f"verifying {t['address']} first_block {t['first_block']}", flush=True)
        out[t["address"]] = verify(t["address"], t["first_block"])
        print(json.dumps(out[t["address"]], indent=1)[:2000], flush=True)
    with open(sys.argv[2], "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", sys.argv[2])
