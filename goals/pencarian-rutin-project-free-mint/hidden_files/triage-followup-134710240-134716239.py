#!/usr/bin/env python3
"""Follow-up probes for triage run 134710240-134716239.
- Retry 429-affected decisive registry calls.
- Check ABI fn lists of regbytes contracts for unprobed registry getters.
- First-mint timestamps + owner-discard check for AGENT_ID_REGISTRY-exact passers.
Read-only.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRI = f"{BASE}/backfill-triage-134710240-134716239.json"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"
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
            last = f"{type(e).__name__}: {str(e)[:100]}"
    return None, last

def call(to, data, pause=3):
    r, e = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    time.sleep(pause)
    return r, e

def dec_addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def dec_uint(raw):
    if isinstance(raw, str) and raw.startswith("0x"):
        try:
            return int(raw, 16)
        except Exception:
            return None
    return None

out = json.load(open(TRI))
disc = json.load(open(f"{BASE}/same-owner-discards.json"))
disc_owners = {r["owner"].lower() for r in disc if r.get("owner")}

# 1. ABI fn lists of regbytes contracts: unprobed registry-like getters?
print("== registry-like fns in regbytes ABIs ==", flush=True)
for addr, row in out.items():
    if not row.get("registry_bytes_hit"):
        continue
    fns = row.get("sourcify", {}).get("functions", [])
    reg_like = [f for f in fns if "regist" in f.lower() or f.lower() in ("registry",)]
    print(f"{addr} reg-like fns: {reg_like}", flush=True)

# 2. Retries of 429-affected decisive calls
RETRIES = [
    ("0x00c5579F105fE340eE197E9aF103E06b33fFEa3a", "agentRegistry()", "zero"),
    ("0x82FdA371747880a36fEFCD14526D428860F7644A", "AGENT_ID_REGISTRY()", "zero"),
    ("0x81CF8356F354f8bB454200C0a8aAaa22131C7215", "agentRegistry()", "zero"),
    ("0x2D9943D20930ec59d7B432A0cF30521f8c0CC016", "freeClaimed(address)", "addr"),
]
for addr, sig, kind in RETRIES:
    row = out[addr]
    prev = row.get("calls", {}).get(sig, {})
    data = sel(sig)
    if kind == "addr":
        data += USER_PAD
    raw, err = call(addr, data)
    row.setdefault("calls", {})[sig] = {
        "raw": (raw or "")[:130], "uint": dec_uint(raw) if raw else None,
        "addr": dec_addr(raw) if raw else None, "error": err,
        "retry": True, "prev_error": prev.get("error")}
    print(f"RETRY {addr} {sig}: uint={dec_uint(raw) if raw else None} "
          f"addr={dec_addr(raw) if raw else None} err={str(err)[:100] if err else None} "
          f"(prev err: {str(prev.get('error'))[:60]})", flush=True)
    json.dump(out, open(TRI, "w"), indent=1)

# 3. Timestamps + owner-discard for registry-exact passers (either getter)
for addr in ["0x81CF8356F354f8bB454200C0a8aAaa22131C7215",
             "0x2D9943D20930ec59d7B432A0cF30521f8c0CC016",
             "0x8D0619C59418Ed042e43838bb6e83038303d27f6"]:
    row = out[addr]
    calls = row.get("calls", {})
    regs = [calls.get("agentRegistry()", {}).get("addr"),
            calls.get("AGENT_ID_REGISTRY()", {}).get("addr")]
    exact = any(r and r.lower() == REGISTRY.lower() for r in regs)
    row["registry_exact_any_getter"] = exact
    fb = row["first_block"]
    blk, err = rpc("eth_getBlockByNumber", [hex(fb), False])
    ts = int(blk["timestamp"], 16) if isinstance(blk, dict) and blk.get("timestamp") else None
    row["first_mint_ts"] = ts
    own = calls.get("owner()", {}).get("addr")
    row["owner"] = own
    row["same_owner_discard"] = bool(own and own.lower() in disc_owners)
    print(f"{addr} registry_exact={exact} first_block={fb} ts={ts} "
          f"owner={own} same_owner_discard={row['same_owner_discard']}", flush=True)
    json.dump(out, open(TRI, "w"), indent=1)

print("DONE", flush=True)
