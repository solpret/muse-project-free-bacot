#!/usr/bin/env python3
"""Triage v2-retry run 0401 — 7 kontrak gagal batch + SpecLaunchpad.
Lean: hanya view kunci, satu batch kecil per kontrak, dataseed1 dulu."""
import json, time, urllib.request
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]

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
    body = json.dumps([{"jsonrpc": "2.0", "id": i+1, "method": m, "params": p}
                       for i, (m, p) in enumerate(calls)]).encode()
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                d = json.loads(resp.read().decode())
            if isinstance(d, list):
                return [x.get("result") if isinstance(x, dict) and "error" not in x else None for x in d]
            return [None] * len(calls)
        except Exception:
            continue
    return [None] * len(calls)

CONTRACTS = {
 "Chrome Runner": ("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", "~03:30 WIB 13 Nov"),
 "BOLTBOTS": ("0xdc0cf81f5d38484d1c3b2f2a2c6a11d6d355a56e", "~02:30 WIB 13 Nov"),
 "Agc": ("0xdac222886b887fc5b6262889b189b8eb57e99794", "~01:30 WIB 13 Nov"),
 "HASHHIVE": ("0x318abbb76631bdd4111ce2951f368fdb48def905", "~22:30 WIB 12 Nov"),
 "Airdrop Card": ("0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69", "~21:30 WIB 12 Nov"),
 "Daybreak Drachma": ("0xa8a508ee984277a548f096117d58266afa5c259e", "~20:30 WIB 12 Nov"),
 "Pulse Runner": ("0xa5f518e3dc77ccd714b49ec9643bfe8702c65968", "~18:30 WIB 12 Nov"),
}
VIEWS = [("name", "name()", "", "str"), ("symbol", "symbol()", "", "str"),
         ("totalSupply", "totalSupply()", "", "uint"),
         ("totalMinted", "totalMinted()", "", "uint"),
         ("freeClaimed", "freeClaimed()", "", "uint"),
         ("freeMinted", "freeMinted()", "", "uint"),
         ("freeLeft", "freeLeft()", "", "uint"),
         ("FREE_SUPPLY", "FREE_SUPPLY()", "", "uint"),
         ("FREE_CAP", "FREE_CAP()", "", "uint"),
         ("MAX_SUPPLY", "MAX_SUPPLY()", "", "uint"),
         ("mintOpen", "mintOpen()", "", "uint"),
         ("balanceOf_user", "balanceOf(address)", enc_addr(USER), "uint"),
         ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_uint(1), "uint"),
         ("owner", "owner()", "", "addr")]

out = {"run": "triage-0401-1113-v2-retry", "contracts": {}, "spec": {}}
r = rpc_batch([("eth_blockNumber", [])])
out["headBlock"] = int(r[0], 16) if r and r[0] else None
t_start = time.time()
for name, (addr, post) in CONTRACTS.items():
    calls = [("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"]) for _, sig, args, _ in VIEWS]
    calls.append(("eth_getCode", [addr, "latest"]))
    t0 = time.time()
    res = rpc_batch(calls)
    entry = {"post": post, "address": addr, "batch_s": round(time.time() - t0, 1)}
    for (label, sig, args, kind), raw in zip(VIEWS, res):
        if kind == "uint":
            entry[label] = dec_uint(raw)
        elif kind == "str":
            entry[label] = dec_str(raw)
        else:
            entry[label] = (raw or "")[-40:] if isinstance(raw, str) and len(raw or "") >= 42 else raw
    entry["code_len"] = len(res[-1] or "")
    entry["registry_bytes"] = REG in (res[-1] or "").lower()
    out["contracts"][name] = entry
    print(name, "done", entry["batch_s"], "s | ts", entry.get("totalSupply"), "| freeLeft", entry.get("freeLeft"), "| freeM", entry.get("freeMinted"), "| cost1", entry.get("costOf_user_1"), "| regBytes", entry.get("registry_bytes"), flush=True)

SPEC = "0x57Fc464839dfC7A4BAB5c07d6CFeF011CfC77514"
spec_views = [("name", "name()", "", "str"), ("symbol", "symbol()", "", "str"),
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
calls = [("eth_call", [{"to": SPEC, "data": sel(sig) + args}, "latest"]) for _, sig, args, _ in spec_views]
calls.append(("eth_getCode", [SPEC, "latest"]))
res = rpc_batch(calls)
for (label, sig, args, kind), raw in zip(spec_views, res):
    out["spec"][label] = dec_str(raw) if kind == "str" else (dec_uint(raw) if kind == "uint" else ((raw or "")[-40:] if isinstance(raw, str) and len(raw or "") >= 42 else raw))
out["spec"]["code_len"] = len(res[-1] or "")
out["spec"]["registry_bytes"] = REG in (res[-1] or "").lower()
out["elapsed_s"] = round(time.time() - t_start, 1)
with open(f"{BASE}/run-0401-1113-triage-retry.json", "w") as f:
    json.dump(out, f, indent=1)
print("ELAPSED", out["elapsed_s"], "head", out.get("headBlock"))
print("SPEC:", json.dumps(out["spec"]))
