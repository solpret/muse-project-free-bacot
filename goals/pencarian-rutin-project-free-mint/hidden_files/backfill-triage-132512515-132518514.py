#!/usr/bin/env python3
"""Triage backfill run 132512515-132518514 (read-only).
1 first-seen ERC721: 0xF8D4a41829423E2537daF436B18Df0d294d73Aa8
(90 mints / 1 distinct minter, first_block 132516666).
Per contract: Sourcify ABI (curl), agentRegistry() must be
0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, owner() vs same-owner-discards,
free views + quote/costOf(user,1), first-block timestamp via dataseed
eth_getBlockByNumber (never Ankr timestamps).
Writes backfill-triage-132512515-132518514.json. No preview/mint/sign.
NOTE: driver exit 2 PARSIAL (3/3 workers rc=2, 52 failed sub-chunks,
tail ~450 blok/chunk gagal); watermark 132512514 -> 132512564 (prefix
kontigu saja; retry otomatis run berikut). Chunk 3 first-seen ini tetap
ditriase karena sudah tercatat di seen.
"""
import json, subprocess
from eth_hash.auto import keccak

RPC_EPS = ["https://bsc-dataseed2.bnbchain.org/",
           "https://bsc-dataseed3.bnbchain.org/",
           "https://bsc-dataseed.binance.org/",
           "https://bsc-dataseed1.bnbchain.org/"]

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

CONTRACTS = [
    {"address": "0xF8D4a41829423E2537daF436B18Df0d294d73Aa8", "first_block": 132516666,
     "mint_count": 90, "distinct_minters": 1, "last_block": 132517141},
]

def rpc(method, params, timeout=30):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    last = None
    for ep in RPC_EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", payload],
                               capture_output=True, text=True, timeout=timeout + 10)
            d = json.loads(r.stdout)
            if "error" in d:
                return {"error": str(d["error"])[:200]}
            return d.get("result")
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
    return {"error": f"all RPC endpoints failed: {last}"}

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data):
    r = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    if isinstance(r, dict) and "error" in r:
        return {"error": r["error"]}
    return {"result": r}

def dec_addr(h):
    if not h or h == "0x" or len(h) < 66:
        return None
    return "0x" + h[-40:]

def dec_uint(h):
    if not h or h == "0x":
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

def dec_bool(h):
    v = dec_uint(h)
    return bool(v) if v is not None else None

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def vcall(addr, sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(addr, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    if h is None or (isinstance(h, str) and h.startswith("0x") and len(h) < 66 and decode in ("uint", "addr", "bool")):
        return {"fn": sig, "value": None, "raw": h, "note": "short/empty return"}
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "addr":
        v = dec_addr(h)
    elif decode == "bool":
        v = dec_bool(h)
    elif decode == "str":
        v = dec_str(h)
    else:
        v = h
    return {"fn": sig, "value": v}

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True, timeout=40)
        d = json.loads(r.stdout)
        abi = d.get("abi")
        if abi is None:
            return {"verified": False, "error": str(d)[:200]}
        return {"verified": True, "abi": abi, "match": d.get("match"), "name": d.get("name")}
    except Exception as e:
        return {"verified": False, "error": f"{type(e).__name__}: {e}"}

def block_ts(blk):
    r = rpc("eth_getBlockByNumber", [hex(blk), False])
    if isinstance(r, dict) and "error" in r:
        return {"error": r["error"]}
    if not isinstance(r, dict):
        return {"error": f"unexpected: {str(r)[:100]}"}
    return {"timestamp": int(r["timestamp"], 16), "hash": r.get("hash")}

discards = json.load(open(f"{BASE}/same-owner-discards.json"))
discard_contracts = {d["contract"].lower() for d in discards}
discard_owners = {d["owner"].lower() for d in discards if d.get("owner")}

FREE_VIEWS = [("remainingFree()", "uint"), ("freeClaimed(address)", "uint"),
              ("freeMinted()", "uint"), ("freeSupply()", "uint"),
              ("FREE_SUPPLY()", "uint"), ("FREE_SLOTS()", "uint"),
              ("freeLeft()", "uint"), ("totalMinted()", "uint"),
              ("maxSupply()", "uint"), ("totalSupply()", "uint"),
              ("mintOpen()", "bool"), ("agentGateOn()", "bool"),
              ("currentPhase()", "uint"), ("PRICE()", "uint"),
              ("price()", "uint"), ("mintPrice()", "uint")]

out = {"run": "132512515-132518514", "contracts": []}
for c in CONTRACTS:
    addr = c["address"]
    e = {"contract": addr, "first_block": c["first_block"], "mint_count": c["mint_count"],
         "distinct_minters": c.get("distinct_minters"), "last_block": c.get("last_block")}
    e["in_same_owner_discards_contract"] = addr.lower() in discard_contracts
    e["first_block_info"] = block_ts(c["first_block"])
    ab = sourcify_abi(addr)
    e["sourcify"] = {"verified": ab.get("verified"), "match": ab.get("match"), "name": ab.get("name")}
    if ab.get("error"):
        e["sourcify"]["error"] = ab["error"]
    fn_names = set()
    if ab.get("verified") and isinstance(ab.get("abi"), list):
        for item in ab["abi"]:
            if item.get("type") == "function":
                fn_names.add(item["name"])
        e["sourcify"]["functions"] = sorted(fn_names)
    e["agentRegistry()"] = vcall(addr, "agentRegistry()", decode="addr")
    reg = e["agentRegistry()"].get("value")
    e["agent_shaped"] = (reg.lower() == REGISTRY.lower()) if reg else False
    e["owner()"] = vcall(addr, "owner()", decode="addr")
    ow = e["owner()"].get("value")
    e["owner_in_discards"] = (ow.lower() in discard_owners) if ow else False
    e["name()"] = vcall(addr, "name()", decode="str")
    e["symbol()"] = vcall(addr, "symbol()", decode="str")
    views = {}
    for sig, dec in FREE_VIEWS:
        fname = sig.split("(")[0]
        if fn_names and fname not in fn_names:
            continue
        args = [USER] if "address" in sig else None
        views[sig] = vcall(addr, sig, args=args, decode=dec)
    e["views"] = views
    quotes = {}
    for sig in ["costOf(address,uint256)", "quote(address,uint256)", "getPrice(address,uint256)"]:
        fname = sig.split("(")[0]
        if fn_names and fname not in fn_names:
            continue
        quotes[sig] = vcall(addr, sig, [USER, 1])
    e["quotes"] = quotes
    qvals = [q.get("value") for q in quotes.values() if isinstance(q.get("value"), int)]
    free_left = None
    for k in ["remainingFree()", "freeLeft()"]:
        v = views.get(k, {}).get("value")
        if isinstance(v, int):
            free_left = v
    e["verdict"] = {
        "agent_shaped": e["agent_shaped"],
        "owner_discarded": e["owner_in_discards"] or e["in_same_owner_discards_contract"],
        "quote_zero": (0 in qvals) if qvals else None,
        "quotes_seen": qvals,
        "free_left": free_left,
    }
    out["contracts"].append(e)

with open(f"{BASE}/backfill-triage-132512515-132518514.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
