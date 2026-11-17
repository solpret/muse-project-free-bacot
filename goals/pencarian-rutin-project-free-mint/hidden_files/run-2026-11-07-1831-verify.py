#!/usr/bin/env python3
"""First-seen agent-shape verification run 1831 (Leg 4). Read-only except own output.
Verifies DinoAgent + Tri333 (both registry_bytes_hit + Sourcify verified + free-shape
in scan enrichment) and light-checks XiaomiS7 (not agent-shaped per scan).
- Sourcify ABI fn list (curl fallback), registry view value vs Agent ID registry
- free/paid supply views, user slot (agent wallet 0xeb23...), owner vs discards
- first-mint block timestamp via fast_rpc (NEVER Ankr for timestamps)
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call(addr, sig, arg=None, arg2=None):
    data = sel(sig)
    if arg: data += enc(arg)
    if arg2 is not None: data += str(arg2).rjust(64, "0")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return r[0]
        except Exception:
            continue
    return None

def call_int(addr, sig, arg=None):
    return to_int(call(addr, sig, arg)) if call(addr, sig, arg) is not None else None

def call_addr(addr, sig):
    raw = call(addr, sig)
    if raw is None or len(raw) < 42: return None
    return "0x" + raw[-40:]

def call_str(addr, sig):
    raw = call(addr, sig)
    if raw is None: return None
    try:
        b = bytes.fromhex(raw[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception:
        return None

def sourcify_fns(addr):
    try:
        p = subprocess.run(["curl", "-s", "-m", "20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=30)
        d = json.loads(p.stdout)
        abi = d.get("abi") or d.get("stdJson", {}).get("abi") or []
        if not abi and d.get("match") is None and "abi" not in d:
            return ("not_verified", [])
        fns = sorted({e.get("name") for e in abi if e.get("type") == "function" and e.get("name")})
        return ("verified" if fns else d.get("match") or "unknown", fns)
    except Exception as e:
        return (f"error:{type(e).__name__}", [])

def block_ts(blk):
    for ep in EPS:
        try:
            r = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            return int(r[0]["timestamp"], 16)
        except Exception:
            continue
    return None

def head():
    for ep in EPS:
        try:
            r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
            return int(r[0], 16)
        except Exception:
            continue
    return None

discards = set()
try:
    discards = {a.lower() for a in json.load(open(f"{BASE}/same-owner-discards.json"))}
except Exception:
    pass

CONTRACTS = {
    "0xcE19D6A5FF15e088D4bf23614242927139084895": {"first_block": 132194540},
    "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f": {"first_block": 132194550},
    "0xfA3a8bA545FebccaE0b88aF8D5f8b7f4D4173333": {"first_block": 132194709},
}
NOARG_INT = ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "FREE_CAP()",
             "MAX_SUPPLY()", "MAX_FREE_PER_WALLET()", "FREE_PER_WALLET()",
             "freeMinted()", "freeClaimed()", "freeLeft()", "freeCount()",
             "freeTotal()", "freeUsed()", "mintOpen()", "price()", "PRICE()",
             "paidMinted()", "paidMintedCount()", "opensAt()", "closesAt()"]
ADDR_INT = ["freeClaimed(address)", "freeUsed(address)", "freeTakenBy(address)",
            "balanceOf(address)", "freeFor(address)", "mintsOf(address)"]
REG_VIEWS = ["agentRegistry()", "AGENT_REGISTRY()", "AGENT_ID_REGISTRY()",
             "gate()", "registry()", "AGENT_ID()"]

out = {"run": "1831", "head": head(), "verified_at_wib": time.strftime("%Y-%m-%d %H:%M WIB", time.gmtime(time.time() + 7*3600))}
for addr, meta in CONTRACTS.items():
    o = {"first_block": meta["first_block"]}
    o["name"] = call_str(addr, "name()")
    o["symbol"] = call_str(addr, "symbol()")
    status, fns = sourcify_fns(addr)
    o["sourcify"] = status
    o["abi_functions"] = fns
    o["registry_views"] = {v: call_addr(addr, v) for v in REG_VIEWS}
    o["registry_match"] = any(v and v.lower() == REGISTRY.lower() for v in o["registry_views"].values())
    o["owner"] = call_addr(addr, "owner()")
    o["owner_in_discards"] = (o["owner"] or "").lower() in discards if o["owner"] else None
    for v in NOARG_INT:
        o[v] = call_int(addr, v)
    for v in ADDR_INT:
        o[v + "_user"] = call_int(addr, v, USER)
    q1 = call(addr, "quote(address,uint256)", USER, 1)
    o["quote_user_1_raw"] = q1
    q2 = call(addr, "quote(uint256)", None, 1) if False else None
    # quote(uint256) single-arg: build manually
    try:
        data = sel("quote(uint256)") + "1".rjust(64, "0")
        for ep in EPS:
            try:
                r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
                o["quote_1_raw"] = r[0]; break
            except Exception:
                continue
    except Exception:
        pass
    ts = block_ts(meta["first_block"])
    o["first_block_timestamp"] = ts
    if ts:
        o["first_mint_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600))
    out[addr] = o
    print(f"done {addr} {o.get('name')} registry_match={o['registry_match']} sourcify={status}", flush=True)

print(json.dumps(out, indent=1), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-1831-verify.json", "w"), indent=1)
