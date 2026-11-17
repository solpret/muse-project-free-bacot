#!/usr/bin/env python3
"""Triage v2 run 0401 WIB 13 Nov 2026 — 10 kontrak baru Boltbook + SpecLaunchpad.
Read-only. urllib langsung ke dataseed (fast_rpc race sedang gagal total),
SATU JSON-RPC batch per kontrak. Tanpa mint/preview."""
import json, time, urllib.request
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return a[2:].lower().rjust(64, "0")

def enc_uint(n):
    return format(n, "064x")

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 130:
        return None
    try:
        b = bytes.fromhex(out[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

def rpc_batch(calls, timeout=25):
    """calls: list of (method, params). Returns list of results (or None)."""
    body = json.dumps([{"jsonrpc": "2.0", "id": i+1, "method": m, "params": p}
                       for i, (m, p) in enumerate(calls)]).encode()
    last = None
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                d = json.loads(resp.read().decode())
            if isinstance(d, list):
                return [x.get("result") if isinstance(x, dict) and "error" not in x else None for x in d]
            return [None] * len(calls)
        except Exception as e:
            last = e
    return [None] * len(calls)

CONTRACTS = {
 "Voxel Sprite": ("0xe712510fcb27935e657e41ebb97982d6b123136c", "04:02 WIB 13 Nov (post drzein.ai)"),
 "Chrome Runner": ("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", "~03:30 WIB 13 Nov"),
 "BOLTBOTS": ("0xdc0cf81f5d38484d1c3b2f2a2c6a11d6d355a56e", "~02:30 WIB 13 Nov"),
 "Agc": ("0xdac222886b887fc5b6262889b189b8eb57e99794", "~01:30 WIB 13 Nov"),
 "Skua Repeater": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", "~00:30 WIB 13 Nov"),
 "HASHHIVE": ("0x318abbb76631bdd4111ce2951f368fdb48def905", "~22:30 WIB 12 Nov"),
 "Airdrop Card": ("0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69", "~21:30 WIB 12 Nov"),
 "Daybreak Drachma": ("0xa8a508ee984277a548f096117d58266afa5c259e", "~20:30 WIB 12 Nov"),
 "Forge Machine": ("0xa545c8726bcf4acf840dac521b369911fe2abc8d", "~19:30 WIB 12 Nov"),
 "Pulse Runner": ("0xa5f518e3dc77ccd714b49ec9643bfe8702c65968", "~18:30 WIB 12 Nov"),
}
UINT_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
              "freeLeft()", "freeSupply()", "FREE_SUPPLY()", "FREE_CAP()",
              "MAX_SUPPLY()", "mintOpen()", "mintStart()", "mintOpensAt()",
              "genesisStart()", "saleStart()"]
STR_VIEWS = ["name()", "symbol()"]
USER_VIEWS = [("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
              ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
              ("freeMinted_user", "freeMinted(address)", enc_addr(USER)),
              ("mintedBy_user", "mintedBy(address)", enc_addr(USER)),
              ("freeUsed_user", "freeUsed(address)", enc_addr(USER)),
              ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_uint(1)),
              ("quote_user_1", "quote(address,uint256)", enc_addr(USER) + enc_uint(1))]
REG_VIEWS = [("agentIdRegistry", "agentIdRegistry()", ""),
             ("agentRegistry", "agentRegistry()", ""),
             ("AGENT_REGISTRY", "AGENT_REGISTRY()", ""),
             ("registry", "registry()", ""),
             ("owner", "owner()", "")]

t_start = time.time()
out = {"run": "triage-0401-1113-v2", "contracts": {}, "spec": {}}

# head block
r = rpc_batch([("eth_blockNumber", [])])
out["headBlock"] = int(r[0], 16) if r and r[0] else None

for name, (addr, post) in CONTRACTS.items():
    labels, calls = [], []
    for sig in UINT_VIEWS:
        labels.append((sig, "uint")); calls.append(("eth_call", [{"to": addr, "data": sel(sig)}, "latest"]))
    for sig in STR_VIEWS:
        labels.append((sig, "str")); calls.append(("eth_call", [{"to": addr, "data": sel(sig)}, "latest"]))
    for label, sig, args in USER_VIEWS:
        labels.append((label, "uint")); calls.append(("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"]))
    for label, sig, args in REG_VIEWS:
        labels.append((label, "addr")); calls.append(("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"]))
    calls.append(("eth_getCode", [addr, "latest"])); labels.append(("code", "code"))
    t0 = time.time()
    res = rpc_batch(calls)
    entry = {"post": post, "address": addr, "batch_s": round(time.time() - t0, 1)}
    for (label, kind), raw in zip(labels, res):
        if kind == "uint":
            entry[label] = dec_uint(raw)
        elif kind == "str":
            entry[label] = dec_str(raw)
        elif kind == "addr":
            entry[label] = (raw or "")[-40:] if isinstance(raw, str) and len(raw or "") >= 42 else raw
        else:
            entry["code_len"] = len(raw or "")
            entry["registry_bytes"] = REG in (raw or "").lower()
    out["contracts"][name] = entry
    print(name, "done", entry["batch_s"], "s | ts", entry.get("totalSupply()"), "| freeM", entry.get("freeMinted()"), "| freeC", entry.get("freeClaimed()"), flush=True)

# SpecLaunchpad
SPEC = "0x57Fc464839dfC7A4BAB5c07d6CFeF011CfC77514"
spec_labels = [("name", "name()", "", "str"), ("symbol", "symbol()", "", "str"),
    ("totalSupply", "totalSupply()", "", "uint"), ("mintOpen", "mintOpen()", "", "uint"),
    ("openedAt", "openedAt()", "", "uint"), ("MAX_SHARES", "MAX_SHARES()", "", "uint"),
    ("tokensPerShare", "tokensPerShare()", "", "uint"),
    ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_uint(1), "uint"),
    ("quotaOf_user", "quotaOf(address)", enc_addr(USER), "uint"),
    ("freeSharesRemaining", "freeSharesRemaining()", "", "uint"),
    ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER), "uint"),
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", "", "addr"),
    ("agentIdRegistry", "agentIdRegistry()", "", "addr"),
    ("owner", "owner()", "", "addr")]
calls = [("eth_call", [{"to": SPEC, "data": sel(sig) + args}, "latest"]) for _, sig, args, _ in spec_labels]
calls.append(("eth_getCode", [SPEC, "latest"]))
res = rpc_batch(calls)
for (label, sig, args, kind), raw in zip(spec_labels, res):
    out["spec"][label] = dec_str(raw) if kind == "str" else (dec_uint(raw) if kind == "uint" else ((raw or "")[-40:] if isinstance(raw, str) and len(raw or "") >= 42 else raw))
out["spec"]["code_len"] = len(res[-1] or "")
out["spec"]["registry_bytes"] = REG in (res[-1] or "").lower()

out["elapsed_s"] = round(time.time() - t_start, 1)
with open(f"{BASE}/run-0401-1113-triage.json", "w") as f:
    json.dump(out, f, indent=1)
print("ELAPSED", out["elapsed_s"], "head", out.get("headBlock"))
print("SPEC:", json.dumps(out["spec"]))
