#!/usr/bin/env python3
"""Follow-up probe 2026-11-07 ~22:4x WIB run backfill 132197166-132203165.
(a) 4 kontrak Sourcify-UNVERIFIED: blind eth_call agentRegistry()/name/
    symbol()/owner()/quote(1)/quoteFor(user,1)/totalSupply() — tanpa ABI
    satu-satunya cara cek agent-shape.
(b) GORB + GORH (template AGENT_ID_REGISTRY): baca AGENT_ID_REGISTRY(),
    OWNER(), TREASURY(), MAX_SUPPLY(), spotsLeft(), isAgent(user).
Read-only. Append ke backfill-triage-132197166-132203165.json (key probe).
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132197166-132203165.json"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc(method, params, timeout=12):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

def call_retry(to, data, tries=2):
    last = None
    for i in range(tries):
        r, e = rpc("eth_call", [{"to": to, "data": data}, "latest"])
        if r is not None:
            return r, None
        last = e
        if "429" in (e or ""):
            time.sleep(15)
        else:
            break
    return None, last

def dec_addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def dec_uint(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 2:
        try:
            return int(raw, 16)
        except Exception:
            return None
    return None

def dec_str(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 130:
        try:
            b = bytes.fromhex(raw[2:])
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
        except Exception:
            return None
    return None

def probe(addr, sigs):
    out = {}
    for sig, kind, dec in sigs:
        data = sel(sig)
        if kind == "addr":
            data += USER_PAD
        elif kind == "uint":
            data += ONE
        elif kind == "addr_uint":
            data += USER_PAD + ONE
        raw, e = call_retry(addr, data)
        time.sleep(3)
        row = {"raw": (raw or "")[:130], "error": e}
        if dec == "uint":
            row["uint"] = dec_uint(raw) if raw else None
        elif dec == "uint_addr":
            row["uint"] = dec_uint(raw) if raw else None
            row["addr"] = dec_addr(raw) if raw else None
        elif dec == "str":
            row["str"] = dec_str(raw) if raw else None
        out[sig] = row
        print(f"  {addr} {sig}: {row}", flush=True)
    return out

UNVERIFIED = [
    "0xc3Dfd7657EDC2D784beE19FcAee5FaD0A08dCC5d",
    "0xb7C004aD99f02644ea8eBBC7Bd5c60374273E1D5",
    "0x6e08F98ca3a79674D3A436BCA806fE56a5556Dd1",
    "0xE6c435D1fb1B3e8c47b9b1Da7C1a99525f295639",
]
CORE = [
    ("agentRegistry()", "zero", "uint_addr"),
    ("name()", "zero", "str"),
    ("symbol()", "zero", "str"),
    ("quote(uint256)", "uint", "uint"),
    ("quoteFor(address,uint256)", "addr_uint", "uint"),
    ("owner()", "zero", "uint_addr"),
    ("totalSupply()", "zero", "uint"),
]
GORB = "0x5B770a73B43ff42a000b830E063cAB819f5c9C4B"
GORH = "0x5aDABC14a821511c8BA2B7FdB8f79b61B4Eea33a"
REGCHECK = [
    ("AGENT_ID_REGISTRY()", "zero", "uint_addr"),
    ("OWNER()", "zero", "uint_addr"),
    ("TREASURY()", "zero", "uint_addr"),
    ("MAX_SUPPLY()", "zero", "uint"),
    ("MAX_PER_WALLET()", "zero", "uint"),
    ("spotsLeft()", "zero", "uint"),
    ("isAgent(address)", "addr", "uint"),
]

doc = json.load(open(OUT))
probe_out = doc.setdefault("probe", {})
for a in UNVERIFIED:
    print(f"== unverified {a}", flush=True)
    probe_out[a] = probe(a, CORE)
    reg = probe_out[a].get("agentRegistry()", {}).get("addr")
    probe_out[a]["agent_shaped"] = (reg or "").lower() == REGISTRY
    print(f"  agent_shaped={probe_out[a]['agent_shaped']}", flush=True)
for a in (GORB, GORH):
    print(f"== registry-check {a}", flush=True)
    probe_out[a] = probe(a, REGCHECK)
    reg = probe_out[a].get("AGENT_ID_REGISTRY()", {}).get("addr")
    probe_out[a]["registry_is_binance"] = (reg or "").lower() == REGISTRY
    print(f"  registry_is_binance={probe_out[a]['registry_is_binance']} reg={reg}", flush=True)
json.dump(doc, open(OUT, "w"), indent=1)
print("saved", OUT)
