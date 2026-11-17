#!/usr/bin/env python3
"""Run 1831: quick on-chain check of Sourcify-feed near-pass sale engine 0x9f10..."""
import json, sys, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
ADDR = "0x9f10c0D8b8E5eFB8706243b1E9336A19E924CCeF"
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
def call_raw(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            v = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 6, retries=0)
            if v in (None, "0x", ""): return None
            return v
        except Exception:
            continue
    return None
out = {"address": ADDR}
for sig in ["token()", "freeMinted()", "freeMintedCount()", "registry()", "isAgent(address)",
            "tokenPrice()", "totalSupply()", "maxSupply()", "mintOpen()", "saleOpen()",
            "freeMinted(address)", "freeClaimed(address)", "hasFreeShare(address)",
            "freeSharesRemaining()", "freeSupply()", "FREE_SUPPLY()", "spotsLeft()",
            "mintedBy(address)", "balanceOf(address)"]:
    key = sig.split("(")[0]
    try:
        if "address" in sig:
            v = call(ADDR, sig, enc(USER)); key += "_user"
        else:
            v = call(ADDR, sig)
    except Exception as e:
        v = f"err:{e}"
    out[key] = v
# token address decode + name/symbol of token + agentHandleOf
tok = call_raw(ADDR, "token()")
print("token() raw:", tok, flush=True)
if tok:
    taddr = "0x" + tok[-40:]
    out["token_address"] = taddr
    for sig in ["name()", "symbol()", "totalSupply()"]:
        out["token_" + sig.split("(")[0]] = call_raw(taddr, sig)
print(json.dumps(out, indent=1), flush=True)
# Sourcify ABI full fn list
r = subprocess.run(["curl", "-sS", "--max-time", "20",
    f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],
    capture_output=True, text=True, timeout=30)
try:
    d = json.loads(r.stdout)
    abi = d.get("abi") or []
    fns = [(f.get("name"), ",".join((i.get("type") or "") for i in f.get("inputs", []))) for f in abi if isinstance(f, dict) and f.get("type") == "function"]
    print("ABI fns:", fns, flush=True)
    out["abi_fns"] = fns
except Exception as e:
    print("sourcify err", e, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-06-1831-sourcify-9f10.json", "w"), indent=1)
print("DONE", flush=True)
