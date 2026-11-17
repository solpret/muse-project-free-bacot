#!/usr/bin/env python3
"""Backfill triage run 2026-11-07 ~10:31 WIB, window 132126342-132129578.
Based on backfill-triage-run.py (07:01 run) + free-path verification for
free/agent-shaped first-seen (quote/views for user wallet) + proper keccak
agentRegistry() selector + track-c-scan-checked.json persistence.
Read-only on chain; writes only backfill-triage-132126342-132129578.json
and appends newly 5c-checked addresses to track-c-scan-checked.json.
Transport failure recorded as such, NEVER as not-sale-shape / not-verified.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_NOPREFIX = USER[2:].lower()
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    last = None
    for attempt in (1, 2):
        try:
            r = subprocess.run(["curl", "-s", "-m", "25", "-A", "free-bacot-backfill-triage/1.0", url],
                               capture_output=True, text=True, timeout=40)
            if r.returncode != 0:
                last = f"curl rc={r.returncode} {r.stderr[:120]}"
                time.sleep(2); continue
            return json.loads(r.stdout), None
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

def call_view(addr, fn):
    """Call a view fn from ABI entry; returns int/str/None/'revert'."""
    name = fn["name"]
    inputs = fn.get("inputs", [])
    try:
        if len(inputs) == 0:
            data = sel(f"{name}()")
        elif len(inputs) == 1 and inputs[0].get("type") == "address":
            data = sel(f"{name}(address)") + USER_NOPREFIX
        elif len(inputs) == 1 and inputs[0].get("type", "").startswith("uint"):
            data = sel(f"{name}(uint256)") + "0" * 63 + "1"
        else:
            return "skip-inputs"
    except Exception as e:
        return f"ERROR {type(e).__name__}: {e}"
    r = eth_call(addr, data)
    if not isinstance(r, str) or not r.startswith("0x") or len(r) < 66:
        return f"revert-or-short: {str(r)[:120]}"
    try:
        v = int(r, 16)
    except Exception:
        return r
    if fn.get("outputs") and fn["outputs"][0].get("type") == "bool":
        return bool(v)
    if fn.get("outputs") and fn["outputs"][0].get("type") == "address":
        return "0x" + r[-40:]
    return v

def shape_s1_s2(abi_list):
    fns = [e for e in abi_list if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi_list).lower()
    mint_fns = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote_fns = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    free_views = [n for n in names if n in FREE_VIEWS]
    has_registry = REG_HEX in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = ("name" in name_set and "symbol" in name_set and "totalsupply" in name_set
                and "decimals" in name_set and "balanceof" in name_set)
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree", "freemint")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint_fns and quote_fns and free_views and has_registry)
    s2 = bool(is_token and noarg_free and free_views and has_registry)
    return {"mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views,
            "agent_gate": has_registry, "is_token": is_token,
            "noarg_free": noarg_free, "S1": s1, "S2": s2, "fn_count": len(fns),
            "fn_names": names}

# ---- first-seen (deduped across chunks) ----
chunks = ["backfill-132126342-132128341.json", "backfill-132128342-132129578.json"]
merged_fs = {}
for f in chunks:
    d = json.load(open(f"{BASE}/{f}"))
    for c in d.get("first_seen", []):
        a = c["address"].lower()
        if a in merged_fs:
            m = merged_fs[a]
            m["mint_count"] = m.get("mint_count", 0) + c.get("mint_count", 0)
            m["distinct_minters"] = max(m.get("distinct_minters", 0), c.get("distinct_minters", 0))
            m["first_block"] = min(m["first_block"], c["first_block"])
            m["last_block"] = max(m["last_block"], c["last_block"])
            m["chunks"].append(f)
        else:
            c = dict(c); c["chunks"] = [f]
            merged_fs[a] = c
first_seen = list(merged_fs.values())
print(f"first-seen unique: {len(first_seen)}")

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
           "scan_mint_funcs": c.get("mint_funcs", []),
           "chunks": c.get("chunks")}
    ts, ts_wib = block_ts(c["first_block"])
    row["first_block_timestamp"] = ts
    row["first_block_wib"] = ts_wib
    data, err = fetch_abi_curl(addr)
    abi = abi_of(data) if data else None
    if data is not None and abi is None:
        row["sourcify_deep"] = "not_verified"
        row["agent_shaped"] = bool(c.get("registry_bytes_hit"))
    elif abi is not None:
        sh = shape_s1_s2(abi)
        row["sourcify_deep"] = "verified"
        row["abi_functions"] = sh["fn_names"]
        row["has_registry_ref"] = sh["agent_gate"]
        row["free_funcs"] = [n for n in sh["fn_names"] if "free" in n and not n.startswith("freeze")]
        row["agent_shaped"] = bool(sh["agent_gate"] or c.get("registry_bytes_hit"))
        row["shape"] = {k: v for k, v in sh.items() if k != "fn_names"}
        # agentRegistry() exact on-chain call (proper keccak selector)
        reg = eth_call(addr, sel("agentRegistry()"))
        if isinstance(reg, str) and reg.startswith("0x") and len(reg) >= 66:
            reg_addr = "0x" + reg[-40:]
            row["agentRegistry_call"] = reg_addr
            row["agentRegistry_exact"] = reg_addr.lower() == REGISTRY.lower()
            if row["agentRegistry_exact"]:
                row["agent_shaped"] = True
        else:
            row["agentRegistry_call"] = f"revert-or-short: {str(reg)[:120]}"
            row["agentRegistry_exact"] = False
        # AGENT_REGISTRY constant if present
        if "agent_registry" in [n.lower() for n in sh["fn_names"]] or "agentregistry" in sh["fn_names"]:
            pass
        # free-path verification when free-shaped or agent-shaped
        if row["agent_shaped"] or row["free_funcs"] or c.get("free_shaped"):
            fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
            wanted = ("hasfreemint", "free_per_wallet", "freeperwallet", "mintopen",
                      "mintmode", "mintedby", "freeleft", "freeminted", "freeclaimed",
                      "freesupply", "free_supply", "max_mints", "maxmints", "maxsupply",
                      "totalminted", "totalsupply", "price", "quote", "mintprice",
                      "remainingfree", "freequota", "free_pool", "freeused", "mintopensat", "mintfree", "mythicminted", "paidminted", "tierminted", "mintmythic")
            fp = {}
            for fn in fns:
                if fn.get("name", "").lower() in wanted:
                    fp[fn["name"]] = call_view(addr, fn)
            row["free_path"] = fp
            # explicit quote(user,1): (address,uint256) quote-like fn, per body
            for fn in fns:
                nm = fn.get("name", "").lower()
                ins = fn.get("inputs", [])
                if (any(w in nm for w in QUOTE_WORDS) and len(ins) == 2
                        and ins[0].get("type") == "address"
                        and ins[1].get("type", "").startswith("uint")):
                    data = sel(f"{fn['name']}(address,uint256)") + USER_NOPREFIX + "0" * 63 + "1"
                    r = eth_call(addr, data)
                    if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
                        row["quote_user_1"] = int(r, 16)
                        row["quote_fn"] = fn["name"]
                    else:
                        row["quote_user_1"] = f"revert-or-short: {str(r)[:120]}"
                        row["quote_fn"] = fn["name"]
                    break
    else:
        row["sourcify_deep"] = f"transport-failed: {err}"
        row["agent_shaped"] = bool(c.get("registry_bytes_hit"))
    code = get_code(addr)
    if isinstance(code, str) and code.startswith("0x"):
        row["code_registry_bytes_hit"] = REG_HEX in code.lower()
        row["code_len"] = len(code)
    else:
        row["code_registry_bytes_hit"] = None
        row["code_error"] = str(code)[:200]
    if row["code_registry_bytes_hit"]:
        row["agent_shaped"] = True
    own = eth_call(addr, "0x8da5cb5b")
    if isinstance(own, str) and own.startswith("0x") and len(own) >= 66:
        owner = "0x" + own[-40:]
        row["owner"] = owner
        row["owner_in_discards"] = owner.lower() in discard_owners
    else:
        row["owner"] = None
        row["owner_call"] = str(own)[:200]
        row["owner_in_discards"] = False
    row["owner_verdict"] = ("SAME-OWNER-DISCARD" if row["owner_in_discards"]
                            else ("unverified (owner() revert, per body rule - not forced)" if row["owner"] is None else "owner-ok"))
    fs_results.append(row)
    print(json.dumps(row, indent=1))

# ---- track-C 5c ----
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = {a.lower() for a in checked.get("checked", [])}
checked_set |= {k.lower() for k in checked.keys() if k.startswith("0x")}
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

# persist newly checked 5c addresses
for r in results5c:
    a = r["address"]
    if a not in checked.get("checked", []):
        checked.setdefault("checked", []).append(a)
    checked[a] = {"source": "backfill-triage-132126342-132129578-5c",
                  "status": ("checked-sale-shape" if r.get("verdict") == "SALE-SHAPE"
                             else "checked-not-sale-shape" if r.get("verdict") == "not-sale-shape"
                             else "checked-" + str(r.get("verdict"))),
                  "note": f"mint_count={r.get('mint_count')} S1={r.get('S1')} S2={r.get('S2')} mint={bool(r.get('mint_fns'))} quote={bool(r.get('quote_fns'))} free={r.get('free_views')} agent={r.get('agent_gate')}"}
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print(f"track-c-scan-checked.json updated: checked list now {len(checked.get('checked', []))}")

out = {"run": "backfill 2026-11-07 ~10:31 WIB", "window": [132126342, 132129578],
       "watermark_after": 132129578,
       "first_seen_triage": fs_results,
       "early_leads": [r for r in fs_results if r.get("agent_shaped")],
       "track_c_5c": {"merged_erc20": len(merged), "ge10": len(cands),
                      "new_checked": len(new), "transport_failed": transport_failed,
                      "results": results5c},
       "sale_shape_hits": [r for r in results5c if r.get("verdict") == "SALE-SHAPE"]}
json.dump(out, open(f"{BASE}/backfill-triage-132126342-132129578.json", "w"), indent=1)
print("WROTE backfill-triage-132126342-132129578.json")
print("early_leads:", len(out["early_leads"]), "sale_shape_hits:", len(out["sale_shape_hits"]))
