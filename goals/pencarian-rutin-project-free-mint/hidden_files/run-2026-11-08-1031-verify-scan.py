#!/usr/bin/env python3
"""Lean verify of scan first-seen (PANDORA, Rose Genesis) + registry storage-slot
probe for Cedar helper + APASS. Read-only. Writes run-2026-11-08-1031-verify-scan.json"""
import json, sys, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
DEAD = "0x000000000000000000000000000000000000dEaD"
REG = "60b9262456de011f7d15a54cdd8c48baa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")

VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
    "freeLeft()", "freeSupply()", "freeMinted()", "FREE_SUPPLY()", "FREE_SLOTS()",
    "FREE_AMOUNT()", "freeAvailable()", "price()", "PRICE()", "owner()",
    "mintOpen()", "startTime()", "START_TIME()", "agentRegistry()", "AGENT_REGISTRY()",
    "AGENT_ID_REGISTRY()", "agentId()", "MAX_SUPPLY()", "maxSupply()"]

def call_one(addr, data, frm=None):
    tx = {"to": addr, "data": data}
    if frm: tx["from"] = frm
    for ep in EPS:
        try:
            r = batch([("eth_call", [tx, "latest"])], endpoint=ep, timeout=8)
            v = r[0]
            if isinstance(v, str) and v.startswith("0x"):
                return v
            return {"error": str(v)[:150]}
        except Exception as e:
            last = str(e)[:150]
    return {"error": last}

def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) >= 64:
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
    except Exception: pass
    return None
def dec_int(h):
    try: return int(h, 16)
    except Exception: return None

def verify(addr):
    out = {"address": addr}
    for ep in EPS:
        try:
            r = batch([("eth_getCode", [addr, "latest"])], endpoint=ep, timeout=8)
            code = r[0]; break
        except Exception as e:
            code = {"error": str(e)[:100]}
    if isinstance(code, str):
        out["registry_bytes_hit"] = REG in code.lower()
    for sig in VIEWS:
        v = call_one(addr, sel(sig))
        key = sig.split("(")[0]
        if isinstance(v, dict): out[key] = None
        elif key in ("name", "symbol"): out[key] = dec_str(v)
        else: out[key] = dec_int(v)
    for sig in ["freeClaimed(address)", "freeFor(address)", "balanceOf(address)"]:
        v = call_one(addr, sel(sig) + enc(USER))
        out[sig.split("(")[0] + "_user"] = None if isinstance(v, dict) else dec_int(v)
    # Sourcify via curl
    try:
        p = subprocess.run(["curl", "-s", "--max-time", "20",
            f"https://sourcify.dev/server/v2/contracts/56/{addr}"],
            capture_output=True, text=True, timeout=30)
        j = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {}
        out["sourcify"] = j.get("stdJson", {}).get("match") or j.get("match") or str(j)[:200]
        abi = None
        try:
            abi = j["stdJson"]["abi"]
        except Exception:
            pass
        if abi:
            fns = [e.get("name") for e in abi if e.get("type") == "function"]
            out["abi_fns"] = fns
            out["abi_has_free"] = [f for f in fns if "free" in f.lower()]
            out["abi_has_mint"] = [f for f in fns if "mint" in f.lower()]
            out["abi_has_quote"] = [f for f in fns if "quote" in f.lower() or "cost" in f.lower()]
            out["abi_has_registry"] = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
    except Exception as e:
        out["sourcify"] = f"error:{str(e)[:120]}"
    return out

def storage_probe(addr, slots=8):
    hits = []
    for i in range(slots):
        for ep in EPS:
            try:
                r = batch([("eth_getStorageAt", [addr, hex(i), "latest"])], endpoint=ep, timeout=8)
                v = r[0]
                if isinstance(v, str) and REG in v.lower():
                    hits.append({"slot": i, "value": v})
                break
            except Exception:
                continue
    return hits

if __name__ == "__main__":
    t0 = time.time()
    res = {}
    for k, a in {"pandora": "0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8",
                 "rose_genesis": "0x7aA9eF2f304ef97d93b35f7E51E6F2c82e61333a"}.items():
        print("verify", k, flush=True)
        res[k] = verify(a)
    print("storage probe cedar helper", flush=True)
    res["cedar_helper_storage_registry"] = storage_probe("0x6AA2C9B7C73BF6351E41EaD32Dd082951336953e")
    print("storage probe apass", flush=True)
    res["apass_storage_registry"] = storage_probe("0x01c106835091c09d5c69737631af133530093c89")
    # APASS mint simulation from user + dead (read-only eth_call, value 0)
    # mint() no-arg and mint(uint256) both tried
    for name, data in [("mint()", sel("mint()")), ("mint(uint256,1)", sel("mint(uint256)") + enc_u(1))]:
        for who, frm in [("user", USER), ("dead", DEAD)]:
            v = call_one("0x01c106835091c09d5c69737631af133530093c89", data, frm=frm)
            res[f"apass_sim_{name}_{who}"] = "OK" if isinstance(v, str) else v
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(BASE + "/run-2026-11-08-1031-verify-scan.json", "w"), indent=1)
    print(json.dumps(res, indent=1)[:5000], flush=True)
