#!/usr/bin/env python3
"""Backfill triage run 2026-11-07 ~07:01 WIB, window 132098932-132101476.
Read-only on chain/state inputs; writes only backfill-triage-132098932-132101476.json.
First-seen (2): Sourcify ABI via curl, getCode registry-bytes, first-block
timestamp, owner() vs same-owner-discards. Track-C 5c: merged ERC20 lists,
mint_count>=10 desc, max 20 NEW, S1/S2 shape via Sourcify ABI (curl).
Transport failure recorded as such, NEVER as not-sale-shape / not-verified.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for attempt in (1, 2):
        try:
            r = subprocess.run(["curl", "-s", "-m", "25", "-A", "free-bacot-backfill-triage/1.0", url],
                               capture_output=True, text=True, timeout=40)
            if r.returncode != 0:
                last = f"curl rc={r.returncode} {r.stderr[:120]}"
                time.sleep(2); continue
            data = json.loads(r.stdout)
            return data, None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2)
    return None, last

def abi_of(data):
    if not isinstance(data, dict):
        return None
    abi = data.get("abi")
    if abi is None and isinstance(data.get("stdJson"), dict):
        abi = data["stdJson"].get("abi")
    return abi

def block_ts(blk):
    try:
        b = race("eth_getBlockByNumber", [hex(blk), False])
        ts = int(b["timestamp"], 16)
        return ts, time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600))
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def eth_call(to, data_hex):
    try:
        return race("eth_call", [{"to": to, "data": data_hex}, "latest"])
    except Exception as e:
        return f"ERROR {type(e).__name__}: {e}"

def get_code(addr):
    try:
        return race("eth_getCode", [addr, "latest"])
    except Exception as e:
        return f"ERROR {type(e).__name__}: {e}"

def shape_s1_s2(abi_list):
    fns = [e for e in abi_list if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi_list).lower()
    mint_fns = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote_fns = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    free_views = [n for n in names if n in FREE_VIEWS]
    has_registry = REG_HEX in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = any(n in name_set for n in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree", "freemint")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint_fns and quote_fns and free_views and has_registry)
    s2 = bool(is_token and noarg_free and free_views and has_registry)
    return {"mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views,
            "agent_gate": has_registry, "is_token": is_token,
            "noarg_free": noarg_free, "S1": s1, "S2": s2, "fn_count": len(fns),
            "fn_names": names}

# ---- first-seen ----
chunks = ["backfill-132098932-132100931.json", "backfill-132100932-132101476.json"]
first_seen = []
for f in chunks:
    d = json.load(open(f"{BASE}/{f}"))
    for c in d.get("first_seen", []):
        c = dict(c); c["chunk"] = f
        first_seen.append(c)

discards = json.load(open(f"{BASE}/same-owner-discards.json"))
discard_owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}

fs_results = []
for c in first_seen:
    addr = c["address"]
    row = {"address": addr, "kind": c.get("kind"), "mint_count": c.get("mint_count"),
           "distinct_minters": c.get("distinct_minters"),
           "first_block": c.get("first_block"), "last_block": c.get("last_block"),
           "name": c.get("name"), "symbol": c.get("symbol"),
           "scan_registry_bytes_hit": c.get("registry_bytes_hit"),
           "scan_sourcify": c.get("sourcify"),
           "scan_free_shaped": c.get("free_shaped", []),
           "scan_mint_funcs": c.get("mint_funcs", [])}
    ts, ts_wib = block_ts(c["first_block"])
    row["first_block_timestamp"] = ts
    row["first_block_wib"] = ts_wib
    data, err = fetch_abi_curl(addr)
    abi = abi_of(data) if data else None
    if data is not None and data.get("match") is None and abi is None:
        row["sourcify_deep"] = "not_verified"
        row["agent_shaped"] = bool(c.get("registry_bytes_hit"))
    elif abi is not None:
        sh = shape_s1_s2(abi)
        row["sourcify_deep"] = "verified"
        row["abi_functions"] = sh["fn_names"]
        row["has_registry_ref"] = sh["agent_gate"]
        row["free_funcs"] = [n for n in sh["fn_names"] if "free" in n and not n.startswith("freeze")]
        row["agent_shaped"] = bool(sh["agent_gate"] or row["free_funcs"] or c.get("registry_bytes_hit"))
        row["shape"] = {k: v for k, v in sh.items() if k != "fn_names"}
    else:
        row["sourcify_deep"] = f"transport-failed: {err}"
        row["agent_shaped"] = bool(c.get("registry_bytes_hit"))
    # bytecode registry-bytes check (independent of Sourcify)
    code = get_code(addr)
    if isinstance(code, str) and code.startswith("0x"):
        row["code_registry_bytes_hit"] = REG_HEX in code.lower()
        row["code_len"] = len(code)
    else:
        row["code_registry_bytes_hit"] = None
        row["code_error"] = str(code)[:200]
    if row["code_registry_bytes_hit"]:
        row["agent_shaped"] = True
    # owner()
    own = eth_call(addr, "0x8da5cb5b")
    if isinstance(own, str) and own.startswith("0x") and len(own) >= 66:
        owner = "0x" + own[-40:]
        row["owner"] = owner
        row["owner_in_discards"] = owner.lower() in discard_owners
    else:
        row["owner"] = None
        row["owner_call"] = str(own)[:200]
        row["owner_in_discards"] = False
    # agentRegistry() exact check (only meaningful if agent-shaped; call anyway, cheap)
    reg = eth_call(addr, "0x" + __import__("hashlib").sha3_256(b"agentRegistry()").hexdigest()[:8] if False else "0x00000000")
    row["agent_registry_call_skipped"] = "selector needs keccak; registry-bytes + ABI-name check used instead"
    fs_results.append(row)
    print(json.dumps(row, indent=1))

# ---- track-C 5c ----
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = {a.lower() for a in checked.get("checked", [])}
merged = {}
for f in chunks:
    d = json.load(open(f"{BASE}/{f}"))
    for e in d.get("erc20_mint_contracts_list", []):
        a = e["address"].lower()
        if a in merged:
            merged[a]["mint_count"] += e.get("mint_count", 0)
            merged[a]["distinct_minters"] = max(merged[a].get("distinct_minters", 0), e.get("distinct_minters", 0))
        else:
            merged[a] = dict(e)
cands = [e for e in merged.values() if e.get("mint_count", 0) >= 10]
cands.sort(key=lambda e: -e["mint_count"])
new = [e for e in cands if e["address"].lower() not in checked_set][:20]
print(f"5c: merged erc20={len(merged)} mint_count>=10: {len(cands)}; already checked: {len(cands)-len(new)}; to check: {len(new)}")
results5c, transport_failed = [], []
for e in new:
    addr = e["address"]
    data, err = fetch_abi_curl(addr)
    if data is None:
        results5c.append({"address": addr, "mint_count": e["mint_count"],
                          "distinct_minters": e.get("distinct_minters"), "verdict": "transport-failed", "error": err})
        transport_failed.append(addr)
        print(f"  {addr} mint_count={e['mint_count']} TRANSPORT-FAILED {err}")
        continue
    abi = abi_of(data)
    if abi is None:
        results5c.append({"address": addr, "mint_count": e["mint_count"],
                          "distinct_minters": e.get("distinct_minters"), "verdict": "not_verified",
                          "sourcify_match": data.get("match")})
        print(f"  {addr} mint_count={e['mint_count']} NOT_VERIFIED")
        continue
    sh = shape_s1_s2(abi)
    verdict = "SALE-SHAPE" if (sh["S1"] or sh["S2"]) else "not-sale-shape"
    results5c.append({"address": addr, "mint_count": e["mint_count"],
                      "distinct_minters": e.get("distinct_minters"), "verdict": verdict,
                      "sourcify": "verified", **{k: v for k, v in sh.items() if k != "fn_names"}})
    print(f"  {addr} mint_count={e['mint_count']} {verdict} S1={sh['S1']} S2={sh['S2']}")
    time.sleep(0.5)

out = {"run": "backfill 2026-11-07 ~07:01 WIB", "window": [132098932, 132101476],
       "first_seen_triage": fs_results,
       "early_leads": [r for r in fs_results if r.get("agent_shaped")],
       "track_c_5c": {"merged_erc20": len(merged), "ge10": len(cands),
                      "new_checked": len(new), "transport_failed": transport_failed,
                      "results": results5c},
       "sale_shape_hits": [r for r in results5c if r.get("verdict") == "SALE-SHAPE"]}
json.dump(out, open(f"{BASE}/backfill-triage-132098932-132101476.json", "w"), indent=1)
print("WROTE backfill-triage-132098932-132101476.json")
print("early_leads:", len(out["early_leads"]), "sale_shape_hits:", len(out["sale_shape_hits"]))
