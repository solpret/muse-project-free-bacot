#!/usr/bin/env python3
"""Triage backfill run 132285182-132290410 (2026-11-08 ~06:25-07:05 WIB).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
Part 1: NFT first-seen x3 - Sourcify ABI (curl), decisive eth_calls, owner, first-block ts.
Part 2: Track-C 5c - merged ERC20 mint>=10, top 20 NEW, S1/S2 shape-check.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132285182-132290410.json"
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

def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

def call(to, data, pause=2):
    r, e = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    time.sleep(pause)
    return r, e

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

def save(obj):
    tmp = OUT + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, ensure_ascii=False)
    import os
    os.replace(tmp, OUT)

def sourcify_abi(address):
    try:
        p = subprocess.run(["curl", "-s", "-m", "20",
            f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"],
            capture_output=True, text=True, timeout=25)
        if p.returncode != 0 or not p.stdout.strip():
            return ("curl_error", None, None)
        d = json.loads(p.stdout)
        if d.get("match") is None and d.get("abi") is None:
            return ("not_verified", None, None)
        return ("verified", d.get("abi"), d.get("match"))
    except Exception as e:
        return (f"error:{type(e).__name__}", None, None)

def block_ts(block):
    r, e = rpc("eth_getBlockByNumber", [hex(block), False], timeout=10)
    time.sleep(1)
    if isinstance(r, dict) and r.get("timestamp"):
        try:
            return int(r["timestamp"], 16), None
        except Exception:
            return None, "bad-ts"
    return None, (e or "no-timestamp")

SIGS = [("agentRegistry()", "zero"), ("AGENT_REGISTRY()", "zero"),
        ("agentIdRegistry()", "zero"), ("REGISTRY()", "zero"),
        ("freeLeft()", "zero"), ("FREE_SUPPLY()", "zero"),
        ("freeMinted()", "zero"), ("freeSupply()", "zero"),
        ("freeClaimed(address)", "addr"), ("freeCount(address)", "addr"),
        ("freeFor(address)", "addr"),
        ("quote(address,uint256)", "addr_uint"), ("quote(uint256)", "uint"),
        ("cost(address,uint256)", "addr_uint"), ("cost(uint256)", "uint"),
        ("PRICE()", "zero"), ("price()", "zero"), ("mintPrice()", "zero"),
        ("MAX_SUPPLY()", "zero"), ("maxSupply()", "zero"),
        ("FREE_CAP()", "zero"), ("FREE_PER_WALLET()", "zero"),
        ("totalMinted()", "zero"), ("totalSupply()", "zero"),
        ("mintOpen()", "zero"), ("maxPerWallet()", "zero")]

TARGETS = [
    ("0x18829898dD7174300877210147f608F1955e7C5b", "1-mint", 132285707, 1),
    ("0x85dF79AD6df9BCa9292E73f973ECF49205E62dB8", "CAISHEN", 132287386, 32),
    ("0x438E76f5CE8B626e34232996988097a0F4FA2907", "AAG", 132288284, 16),
]

out = {}
try:
    out = json.load(open(OUT))
except Exception:
    out = {}

discards = json.load(open(f"{BASE}/same-owner-discards.json"))
discard_owners = {d.get("owner", "").lower() for d in discards if isinstance(d, dict)}

for addr, label, first_block, mints in TARGETS:
    row = out.get(addr, {"address": addr, "label": label,
                         "first_block": first_block, "mint_count_window": mints})
    ts, e = block_ts(first_block)
    row["first_block_ts"] = ts
    row["first_block_ts_error"] = e
    print(f"== {label} {addr} first_block={first_block} ts={ts}", flush=True)
    status, abi, match = sourcify_abi(addr)
    row["sourcify"] = status
    row["sourcify_match"] = match
    fns = [i.get("name") for i in abi if isinstance(abi, list) and i.get("type") == "function"] if isinstance(abi, list) else []
    row["abi_functions"] = fns
    print(f"   sourcify={status} match={match} fns={len(fns)}", flush=True)
    if fns:
        print("   " + ", ".join(fns), flush=True)
    row["calls"] = row.get("calls", {})
    for sig, kind in SIGS:
        if sig in row["calls"] and row["calls"][sig].get("raw"):
            continue
        data = sel(sig)
        if kind == "addr":
            data += USER_PAD
        elif kind == "uint":
            data += ONE
        elif kind == "addr_uint":
            data += USER_PAD + ONE
        raw, err = call(addr, data)
        row["calls"][sig] = {"raw": (raw or "")[:130],
                             "uint": dec_uint(raw) if raw else None,
                             "addr": dec_addr(raw) if raw else None,
                             "error": err}
        print(f"   {sig}: uint={row['calls'][sig]['uint']} addr={row['calls'][sig]['addr']} err={str(err)[:80] if err else None}", flush=True)
        save(out)
    # name/symbol/owner (string decodes skipped; raw kept)
    for sig, key in [("name()", "name_raw"), ("symbol()", "symbol_raw")]:
        if key not in row:
            raw, err = call(addr, sel(sig))
            row[key] = (raw or "")[:200]
            row[key + "_error"] = err
            print(f"   {sig}: raw={(raw or '')[:80]} err={str(err)[:80] if err else None}", flush=True)
            save(out)
    if "owner" not in row:
        raw, err = call(addr, "0x8da5cb5b")
        row["owner"] = dec_addr(raw) if raw else None
        row["owner_error"] = err
        print(f"   owner={row['owner']} err={str(err)[:80] if err else None}", flush=True)
        save(out)
    row["owner_in_discards"] = (row.get("owner") or "").lower() in discard_owners if row.get("owner") else None
    out[addr] = row
    save(out)

# ---- Track-C 5c ----
def load_checked():
    d = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    have = set()
    if isinstance(d, dict):
        lst = d.get("checked", [])
        if isinstance(lst, list):
            have |= {a.lower() for a in lst if isinstance(a, str)}
        have |= {k.lower() for k in d.keys() if isinstance(k, str) and k.startswith("0x")}
    elif isinstance(d, list):
        have |= {a.lower() for a in d if isinstance(a, str)}
    return d, have

merged = {}
for f in ["backfill-132285182-132287181.json", "backfill-132287182-132289181.json",
          "backfill-132289182-132290410.json"]:
    d = json.load(open(f"{BASE}/{f}"))
    for e in d.get("erc20_mint_contracts_list", []):
        m = merged.setdefault(e["address"], {"address": e["address"], "mint_count": 0})
        m["mint_count"] += e["mint_count"]
cands = [m for m in merged.values() if m["mint_count"] >= 10]
cands.sort(key=lambda x: -x["mint_count"])
_, have = load_checked()
NEW = [(c["address"], c["mint_count"]) for c in cands if c["address"].lower() not in have][:20]
print(f"TRACKC merged unique={len(merged)} mint>=10={len(cands)} NEW={len(NEW)}", flush=True)
results = []
for addr, mc in NEW:
    status, abi, match = sourcify_abi(addr)
    fns = [i.get("name") for i in abi if isinstance(abi, list) and i.get("type") == "function"] if isinstance(abi, list) else []
    low = [f.lower() for f in fns]
    has = lambda *names: any(n.lower() in low for n in names)
    s1 = has("mint") and has("quote", "cost") and has("freeclaimed", "freeminted", "freesupply", "freeleft", "free_claimed") and (has("agentregistry") or has("agentgate"))
    s2 = has("mintfree") and has("agentregistry") and has("name", "symbol", "decimals", "totalsupply") and (has("freeclaimed", "freeminted") or has("free_slots", "free_supply"))
    verdict = "S1" if s1 else ("S2" if s2 else "not-sale-shape")
    results.append({"address": addr, "mint_count": mc, "sourcify": status,
                    "abi_functions": fns, "shape": verdict})
    print(f"TRACKC {addr} mc={mc} sourcify={status} fns={len(fns)} shape={verdict}", flush=True)
    if fns:
        print("   " + ", ".join(fns[:40]), flush=True)
out["track_c"] = {"merged_unique": len(merged), "mint_ge10": len(cands),
                  "new_checked": len(NEW), "results": results}
save(out)
# append newly checked
checked, have2 = load_checked()
lst = checked.get("checked", []) if isinstance(checked, dict) else checked
added = [a for a, _ in NEW if a.lower() not in have2]
lst += added
if isinstance(checked, dict):
    checked["checked"] = lst
    json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"))
print(f"TRACKC appended {len(added)} to checked (now {len(lst)})", flush=True)
print("DONE", flush=True)
