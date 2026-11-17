#!/usr/bin/env python3
"""Lean verify of 2 discovery finds, run 1031: Cedar Kiln + APASS.
Read-only. Single eth_call per view (fail-soft), no batch-revert masking.
Writes run-2026-11-08-1031-verify-new.json"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")

VIEWS_NOARG = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
    "freeLeft()", "freeSupply()", "freeMinted()", "FREE_SUPPLY()", "FREE_SLOTS()",
    "FREE_AMOUNT()", "freeAvailable()", "price()", "PRICE()", "owner()",
    "mintOpen()", "startTime()", "START_TIME()", "agentRegistry()", "AGENT_REGISTRY()",
    "AGENT_ID_REGISTRY()", "agentId()", "MAX_SUPPLY()", "maxSupply()", "MAX_FREE_MINTS_PER_WALLET()",
    "freeSharePoolExhausted()", "freeSharesRemaining()", "launched()", "saleStart()"]
VIEWS_ADDR = ["freeClaimed(address)", "freeFor(address)", "freeUsed(address)",
    "freeMintedBy(address)", "balanceOf(address)", "freeLeft(address)", "freeAvailable(address)"]
VIEWS_U = ["quote(uint256)", "cost(uint256)", "priceForSerial(uint256)"]

def call_one(addr, data):
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=8)
            v = r[0]
            if isinstance(v, str) and v.startswith("0x"):
                return v
            return {"error": str(v)[:120]}
        except Exception as e:
            last = str(e)[:120]
    return {"error": last}

def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        # string: offset(32)+len(32)+data
        if len(b) >= 64:
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        pass
    return None

def dec_int(hexv):
    try: return int(hexv, 16)
    except Exception: return None

def verify(addr):
    out = {"address": addr}
    code = None
    for ep in EPS:
        try:
            r = batch([("eth_getCode", [addr, "latest"])], endpoint=ep, timeout=8)
            code = r[0]
            break
        except Exception as e:
            code = {"error": str(e)[:100]}
    if isinstance(code, str):
        out["has_code"] = len(code) > 4
        out["registry_bytes_hit"] = REG in code.lower()
    else:
        out["has_code"] = None
        out["code_error"] = code
    for sig in VIEWS_NOARG:
        v = call_one(addr, sel(sig))
        key = sig.split("(")[0]
        if isinstance(v, dict):
            out[key] = None
            out[key + "_error"] = v["error"]
        elif key in ("name", "symbol"):
            out[key] = dec_str(v)
        else:
            out[key] = dec_int(v)
    for sig in VIEWS_ADDR:
        v = call_one(addr, sel(sig) + enc(USER))
        key = sig.split("(")[0] + "_user"
        if isinstance(v, dict):
            out[key] = None
        else:
            out[key] = dec_int(v)
    for sig in VIEWS_U:
        v = call_one(addr, sel(sig) + enc_u(1))
        key = sig.split("(")[0] + "_1"
        if isinstance(v, dict):
            out[key] = None
        else:
            out[key] = dec_int(v)
    # tokenURI(1) for NFT collections
    v = call_one(addr, sel("tokenURI(uint256)") + enc_u(1))
    if isinstance(v, str):
        out["tokenURI_1"] = dec_str(v)
    else:
        out["tokenURI_1"] = None
    return out

def first_mint(addr, frm, to):
    """Ankr getLogs Transfer from zero address, single chunk. Returns (count, first_block, first_tx) or error."""
    from ankr import ankr_post
    zero = "0x" + "00"*32
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
        "pageSize": 1000, "decodeLogs": False,
        "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", zero, None, None],
        "address": [addr]}, timeout=30)
    logs = body.get("result", {}).get("logs", [])
    # filter to this contract (ankr address filter may be loose)
    logs = [l for l in logs if l.get("address", "").lower() == addr.lower()]
    if not logs:
        return {"count": 0}
    first = min(logs, key=lambda l: int(l["blockNumber"], 16))
    return {"count": len(logs), "first_block": int(first["blockNumber"], 16),
            "first_tx": first.get("transactionHash")}

if __name__ == "__main__":
    t0 = time.time()
    res = {}
    targets = {
        "cedar_collection": "0x7ac89Ff65D1e4aa9C2BBCdEE0bBafAaa092B02bE",
        "cedar_helper": "0x6AA2C9B7C73BF6351E41EaD32Dd082951336953e",
        "cedar_token": "0xbed2d450d57e53ab597b3d349f086d861ee83a66",
        "apass": "0x01c106835091c09d5c69737631af133530093c89",
    }
    for k, a in targets.items():
        print("verify", k, a, flush=True)
        res[k] = verify(a)
    # first-mint bracketing: Cedar Kiln collection around post blocks 132322156-529
    print("first-mint cedar_collection 132322000-132323000", flush=True)
    try:
        res["cedar_first_mint_probe"] = first_mint(targets["cedar_collection"], 132322000, 132323000)
    except Exception as e:
        res["cedar_first_mint_probe"] = {"error": str(e)[:200]}
    # APASS: probe most recent 1000 blocks for mint activity, then one older chunk
    print("first-mint apass 132322860-132323859", flush=True)
    try:
        res["apass_recent_probe"] = first_mint(targets["apass"], 132322860, 132323859)
    except Exception as e:
        res["apass_recent_probe"] = {"error": str(e)[:200]}
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(BASE + "/run-2026-11-08-1031-verify-new.json", "w"), indent=1)
    print(json.dumps(res, indent=1)[:6000], flush=True)
