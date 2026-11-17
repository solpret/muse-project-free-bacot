#!/usr/bin/env python3
"""Backfill triage run 2026-11-09 ~08:2x WIB, window 132468915-132474914 (driver exit 0, 3/3 chunks).
Read-only on-chain/state inputs; writes only backfill-triage-132468915-132474914.json.
First-seen (1 deduped): Sourcify ABI via curl, agentRegistry()/agentId() check
(registry must equal 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), free views +
quote(user,1) for user wallet, first-block timestamp via curl RPC (NOT Ankr -
Ankr returns fake 'now' timestamps), owner() vs same-owner-discards.json.
Transport: fast_rpc (urllib) timed out on all public endpoints (see 03:16 run);
use curl JSON-RPC to bsc-dataseed2/3. No preview/mint/sign/approve/swap.
"""
import json, subprocess, sys
from eth_hash.auto import keccak

RPC_EPS = ["https://bsc-dataseed2.bnbchain.org/",
           "https://bsc-dataseed3.bnbchain.org/",
           "https://bsc-dataseed.binance.org/",
           "https://bsc-dataseed1.bnbchain.org/"]

def rpc(method, params, timeout=30):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    last = None
    for ep in RPC_EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST", ep,
                                "-H", "Content-Type: application/json",
                                "-d", payload],
                               capture_output=True, text=True, timeout=timeout + 10)
            d = json.loads(r.stdout)
            if "error" in d:
                return {"error": str(d["error"])[:150]}
            return d.get("result")
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
    raise OSError(f"all curl-RPC endpoints failed: {last}")

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591"
FIRST_BLOCK = 132474152

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data):
    try:
        r = rpc("eth_call", [{"to": to, "data": data}, "latest"])
        if isinstance(r, dict) and "error" in r:
            return {"error": str(r["error"])[:150]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:150]}"}

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

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def vcall(sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(ADDR, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "addr":
        v = dec_addr(h)
    elif decode == "str":
        v = dec_str(h)
    elif decode == "raw":
        v = h
    else:
        v = h
    return {"fn": sig, "value": v}

out = {"contract": ADDR, "first_block": FIRST_BLOCK, "mint_count_window": 178,
       "distinct_minters_window": 44, "kind": "ERC721"}

# Sourcify ABI via curl
try:
    r = subprocess.run(["curl", "-s", "-m", "30",
                        f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],
                       capture_output=True, text=True, timeout=40)
    d = json.loads(r.stdout)
    out["sourcify_match"] = d.get("match")
    abi = d.get("abi") or []
    out["sourcify_abi_fns"] = len([e for e in abi if e.get("type") == "function"])
    out["sourcify_fn_names"] = sorted({e.get("name") for e in abi if e.get("type") == "function"})
except Exception as e:
    out["sourcify_error"] = f"{type(e).__name__}: {e}"

# Views
for sig, dec in [("name()", "str"), ("symbol()", "str"), ("agentId()", "addr"),
                 ("FREE_CAP()", "uint"), ("FREE_PER_WALLET()", "uint"),
                 ("freeMinted()", "uint"), ("totalMinted()", "uint"),
                 ("mintPriceWei()", "uint"), ("mintStart()", "uint"),
                 ("mintEnd()", "uint"), ("paidMinted()", "uint"),
                 ("epicMinted()", "uint")]:
    out[sig] = vcall(sig, decode=dec)
out["freeAllowance(user)"] = vcall("freeAllowance(address)", [USER])
out["freeCount(user)"] = vcall("freeCount(address)", [USER])
out["costWei(1)"] = vcall("costWei(uint256)", [1])
# quote(user,1): 6 return values
q = vcall("quote(address,uint256)", [USER, 1], decode="raw")
if "value" in q and q["value"]:
    h = q["value"]
    try:
        vals = [int(h[2 + i * 64:2 + (i + 1) * 64], 16) for i in range(6)]
        out["quote(user,1)"] = {"raw_uints": vals}
    except Exception as e:
        out["quote(user,1)"] = {"error": f"decode: {e}", "raw": h}
else:
    out["quote(user,1)"] = q
# agentRegistry() — absent from ABI; try anyway
out["agentRegistry()"] = vcall("agentRegistry()", decode="addr")
# owner() — absent from ABI; try anyway
out["owner()"] = vcall("owner()", decode="addr")

# registry bytes in deployed code
try:
    code = rpc("eth_getCode", [ADDR, "latest"])
    out["code_len_bytes"] = (len(code) - 2) // 2 if code else 0
    out["registry_bytes_in_code"] = REGISTRY[2:].lower() in (code or "").lower()
except Exception as e:
    out["code_error"] = f"{type(e).__name__}: {e}"

# first-mint block timestamp (curl RPC, NOT Ankr)
try:
    blk = rpc("eth_getBlockByNumber", [hex(FIRST_BLOCK), False])
    out["first_block_ts"] = int(blk["timestamp"], 16) if blk else None
    out["first_block_hash"] = blk.get("hash") if blk else None
except Exception as e:
    out["first_block_error"] = f"{type(e).__name__}: {e}"

# owner vs same-owner-discards
try:
    disc = json.load(open(f"{BASE}/same-owner-discards.json"))
    owners = set()
    if isinstance(disc, dict):
        for v in disc.values():
            if isinstance(v, dict):
                o = v.get("owner") or v.get("owner_address")
                if o:
                    owners.add(o.lower())
            elif isinstance(v, str):
                owners.add(v.lower())
    elif isinstance(disc, list):
        for v in disc:
            if isinstance(v, dict):
                o = v.get("owner") or v.get("owner_address")
                if o:
                    owners.add(o.lower())
            elif isinstance(v, str):
                owners.add(v.lower())
    out["discards_owner_count"] = len(owners)
    oc = out.get("owner()", {})
    ov = oc.get("value") if isinstance(oc, dict) else None
    out["owner_in_discards"] = (ov.lower() in owners) if ov else None
    out["owner_check_note"] = "owner() not in ABI; call result above" if not ov else ""
except Exception as e:
    out["discards_error"] = f"{type(e).__name__}: {e}"

with open(f"{BASE}/backfill-triage-132468915-132474914.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
