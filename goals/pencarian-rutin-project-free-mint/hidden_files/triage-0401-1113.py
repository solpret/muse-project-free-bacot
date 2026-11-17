#!/usr/bin/env python3
"""Triage run 0401 WIB 13 Nov 2026 — 10 kontrak baru Boltbook + SpecLaunchpad.
Read-only. Satu JSON-RPC batch (fast_rpc.batch_race) untuk semua eth_call;
eth_getCode terpisah untuk cek registry bytes. Tanpa mint/preview."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

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
USER_UINT = [("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
             ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
             ("freeMinted_user", "freeMinted(address)", enc_addr(USER)),
             ("mintedBy_user", "mintedBy(address)", enc_addr(USER)),
             ("freeUsed_user", "freeUsed(address)", enc_addr(USER)),
             ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_uint(1)),
             ("quote_user_1", "quote(address,uint256)", enc_addr(USER) + enc_uint(1)),
             ("owner", "owner()", "")]
# registry views
REG_VIEWS = [("agentIdRegistry", "agentIdRegistry()", ""),
             ("agentRegistry", "agentRegistry()", ""),
             ("AGENT_REGISTRY", "AGENT_REGISTRY()", ""),
             ("registry", "registry()", "")]

calls, meta = [], []
for name, (addr, post) in CONTRACTS.items():
    for sig in UINT_VIEWS:
        calls.append({"to": addr, "data": sel(sig)}); meta.append((name, sig, "uint"))
    for sig in STR_VIEWS:
        calls.append({"to": addr, "data": sel(sig)}); meta.append((name, sig, "str"))
    for label, sig, args in USER_UINT:
        calls.append({"to": addr, "data": sel(sig) + args}); meta.append((name, label, "uint"))
    for label, sig, args in REG_VIEWS:
        calls.append({"to": addr, "data": sel(sig) + args}); meta.append((name, label, "addr"))

# SpecLaunchpad
SPEC = "0x57Fc464839dfC7A4BAB5c07d6CFeF011CfC77514"
SPEC_VIEWS = [("name", "name()", "", "str"), ("symbol", "symbol()", "", "str"),
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
for label, sig, args, kind in SPEC_VIEWS:
    calls.append({"to": SPEC, "data": sel(sig) + args}); meta.append(("SpecLaunchpad", label, kind))

t0 = time.time()
try:
    results = fast_rpc.batch_race(calls, timeout=10)
    batch_ok = True
except Exception as e:
    results = [None] * len(calls)
    batch_ok = False
    batch_err = f"{type(e).__name__}:{e}"
elapsed = round(time.time() - t0, 1)

out = {"run": "triage-0401-1113", "batch_ok": batch_ok, "elapsed_s": elapsed,
       "n_calls": len(calls), "contracts": {}, "spec": {}}
if not batch_ok:
    out["batch_error"] = batch_err
for (name, label, kind), res in zip(meta, results):
    tgt = out["spec"] if name == "SpecLaunchpad" else out["contracts"].setdefault(name, {"post": CONTRACTS[name][1], "address": CONTRACTS[name][0]})
    if kind == "uint":
        tgt[label] = dec_uint(res)
    elif kind == "str":
        tgt[label] = dec_str(res)
    else:
        tgt[label] = (res or "")[-40:] if isinstance(res, str) and len(res or "") >= 42 else res

# head block
try:
    head = fast_rpc.race("eth_blockNumber", [], timeout=8)
    out["headBlock"] = int(head, 16) if isinstance(head, str) else head
except Exception as e:
    out["headBlock"] = f"ERR {e}"

# eth_getCode registry-bytes check per contract (sequential, murah: 11 calls)
import urllib.request
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def get_code(addr):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                       "params": [addr, "latest"]}).encode()
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                d = json.loads(resp.read().decode())
            code = d.get("result", "")
            return {"len": len(code), "registry_bytes": REG in (code or "").lower()}
        except Exception:
            continue
    return {"len": None, "registry_bytes": None}
for name, (addr, post) in CONTRACTS.items():
    out["contracts"][name]["code"] = get_code(addr)
out["spec"]["code"] = get_code(SPEC)

with open(f"{BASE}/run-0401-1113-triage.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"batch_ok": batch_ok, "elapsed_s": elapsed, "headBlock": out.get("headBlock"),
                  "n": len(calls)}, indent=1))
for name, c in out["contracts"].items():
    print(name, "| ts", c.get("totalSupply()"), "/", c.get("totalMinted()"), "| freeClaimed", c.get("freeClaimed()"), "| freeMinted", c.get("freeMinted()"), "| freeLeft", c.get("freeLeft()"), "| FREE_SUPPLY", c.get("FREE_SUPPLY()"), "| FREE_CAP", c.get("FREE_CAP()"), "| MAX", c.get("MAX_SUPPLY()"), "| open", c.get("mintOpen()"), "| bal_user", c.get("balanceOf_user"), "| cost1", c.get("costOf_user_1"), "| owner", (c.get("owner") or "")[-10:], "| regBytes", c.get("code", {}).get("registry_bytes"), "| agentReg", c.get("agentIdRegistry") or c.get("agentRegistry") or c.get("AGENT_REGISTRY") or c.get("registry"))
print("SPEC |", json.dumps(out["spec"], indent=0)[:600])
