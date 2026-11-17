#!/usr/bin/env python3
"""Backfill triage run 2026-11-09 ~09:1x WIB, window 132480915-132486914 (driver exit 2,
3/3 chunks, watermark 132480914 -> 132481864, 4 first-seen deduped, 2 failed sub-chunks).
Read-only on-chain/state inputs; writes only backfill-triage-132480915-132486914.json.
First-seen (4 deduped): Sourcify ABI via curl, agentRegistry() exact
(registry must equal 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), free views +
quote(user,1) for user wallet, first-block timestamp via curl RPC (NOT Ankr -
Ankr returns fake 'now' timestamps), owner() vs same-owner-discards.json.
Track-C 5c: merged ERC20 lists, mint_count>=10 desc, max 20 NEW, S1/S2 shape via
Sourcify ABI (curl). Transport failure recorded as such, NEVER as not-sale-shape /
not-verified. No preview/mint/sign/approve/swap.
"""
import json, subprocess, time
from eth_hash.auto import keccak

RPC_EPS = ["https://bsc-dataseed2.bnbchain.org/",
           "https://bsc-dataseed3.bnbchain.org/",
           "https://bsc-dataseed.binance.org/",
           "https://bsc-dataseed1.bnbchain.org/"]

def rpc(method, params, timeout=30):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    last = None
    for ep in RPC_EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST", ep,
                                "-H", "Content-Type: application/json",
                                "-d", payload],
                               capture_output=True, text=True, timeout=timeout + 10)
            d = json.loads(r.stdout)
            if "error" in d:
                return {"error": str(d["error"])[:150]}
            return d.get("result")
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
    raise OSError(f"all curl-RPC endpoints failed: {last}")

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

CHUNKS = ["backfill-132480915-132482914.json",
          "backfill-132482915-132484914.json",
          "backfill-132484915-132486914.json"]

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data):
    try:
        r = rpc("eth_call", [{"to": to, "data": data}, "latest"])
        if isinstance(r, dict) and "error" in r:
            return {"error": str(r["error"])[:150]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:150]}"}

def dec_addr(h):
    if not h or h == "0x" or len(h) < 66:
        return None
    return "0x" + h[-40:]

def dec_uint(h):
    if not h or h == "0x":
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def vcall(addr, sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(addr, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "addr":
        v = dec_addr(h)
    elif decode == "str":
        v = dec_str(h)
    elif decode == "raw":
        v = h
    else:
        v = h
    return {"fn": sig, "value": v}

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
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

# ---- first-seen (deduped across chunks) ----
merged_fs = {}
for f in CHUNKS:
    d = json.load(open(f"{BASE}/{f}"))
    for c in d.get("first_seen", []):
        a = c["address"].lower()
        if a in merged_fs:
            merged_fs[a]["mint_count"] += c.get("mint_count", 0)
            merged_fs[a]["distinct_minters"] = max(merged_fs[a].get("distinct_minters", 0), c.get("distinct_minters", 0))
            merged_fs[a]["first_block"] = min(merged_fs[a]["first_block"], c["first_block"])
            merged_fs[a]["last_block"] = max(merged_fs[a]["last_block"], c["last_block"])
        else:
            merged_fs[a] = dict(c)
first_seen = sorted(merged_fs.values(), key=lambda c: c["first_block"])
print(f"first-seen deduped: {len(first_seen)}")

# discards owners
disc = json.load(open(f"{BASE}/same-owner-discards.json"))
owners = set()
if isinstance(disc, dict):
    for v in disc.values():
        if isinstance(v, dict):
            o = v.get("owner") or v.get("owner_address")
            if o: owners.add(o.lower())
        elif isinstance(v, str):
            owners.add(v.lower())
elif isinstance(disc, list):
    for v in disc:
        if isinstance(v, dict):
            o = v.get("owner") or v.get("owner_address")
            if o: owners.add(o.lower())
        elif isinstance(v, str):
            owners.add(v.lower())

FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply", "freeallowance", "freecount",
              "freecap", "free_per_wallet", "freeperwallet"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

fs_results = []
for c in first_seen:
    addr = c["address"]
    row = {"address": addr, "kind": c.get("kind"), "mint_count": c.get("mint_count"),
           "distinct_minters": c.get("distinct_minters"),
           "first_block": c.get("first_block"), "last_block": c.get("last_block")}
    # first-block timestamp (curl RPC, NOT Ankr)
    try:
        blk = rpc("eth_getBlockByNumber", [hex(c["first_block"]), False])
        ts = int(blk["timestamp"], 16)
        row["first_block_timestamp"] = ts
        row["first_block_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600))
    except Exception as e:
        row["first_block_error"] = f"{type(e).__name__}: {e}"
    # Sourcify ABI
    data, err = fetch_abi_curl(addr)
    abi = None
    if data is not None:
        row["sourcify_match"] = data.get("match")
        abi = data.get("abi") or (data.get("stdJson", {}) or {}).get("abi")
    if abi is not None:
        fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
        names = sorted({e.get("name") for e in fns})
        row["sourcify_deep"] = "verified"
        row["sourcify_abi_fns"] = len(fns)
        row["abi_fn_names"] = names
        raw = json.dumps(abi).lower()
        row["registry_ref_in_abi"] = REG_HEX in raw or "agentregistry" in {n.lower() for n in names} or "agentgate" in {n.lower() for n in names}
        row["free_funcs"] = [n for n in names if "free" in n.lower() and not n.lower().startswith("freeze")]
        # call views present in ABI (or registry/owner regardless)
        for sig, dec in [("name()", "str"), ("symbol()", "str"),
                         ("agentRegistry()", "addr"), ("owner()", "addr"),
                         ("totalSupply()", "uint"), ("totalMinted()", "uint"),
                         ("freeMinted()", "uint"), ("FREE_CAP()", "uint"),
                         ("FREE_PER_WALLET()", "uint"), ("FREE_SUPPLY()", "uint"),
                         ("FREE_SLOTS()", "uint"), ("PRICE()", "uint"),
                         ("mintPrice()", "uint"), ("mintPriceWei()", "uint"),
                         ("costWei(uint256)", "uint")]:
            row[sig] = vcall(addr, sig, decode=dec)
        row["freeClaimed(user)"] = vcall(addr, "freeClaimed(address)", [USER])
        row["freeCount(user)"] = vcall(addr, "freeCount(address)", [USER])
        row["freeAllowance(user)"] = vcall(addr, "freeAllowance(address)", [USER])
        row["cost(1)"] = vcall(addr, "cost(uint256)", [1])
        q = vcall(addr, "quote(address,uint256)", [USER, 1], decode="raw")
        if "value" in q and q["value"]:
            h = q["value"]
            try:
                vals = [int(h[2 + i*64:2 + (i+1)*64], 16) for i in range(6)]
                row["quote(user,1)"] = {"raw_uints": vals}
            except Exception as e:
                row["quote(user,1)"] = {"error": f"decode: {e}", "raw": h}
        else:
            row["quote(user,1)"] = q
    elif data is not None:
        row["sourcify_deep"] = "not_verified"
        row["agent_shaped"] = False
    else:
        row["sourcify_deep"] = f"transport-failed: {err}"
    # registry bytes in deployed code
    try:
        code = rpc("eth_getCode", [addr, "latest"])
        row["code_len_bytes"] = (len(code) - 2) // 2 if code else 0
        row["registry_bytes_in_code"] = REG_HEX in (code or "").lower()
    except Exception as e:
        row["code_error"] = f"{type(e).__name__}: {e}"
    # agent-shaped verdict
    reg_val = None
    ar = row.get("agentRegistry()")
    if isinstance(ar, dict) and ar.get("value"):
        reg_val = ar["value"]
    row["agentRegistry_exact"] = (reg_val.lower() == REGISTRY.lower()) if reg_val else None
    row["agent_shaped"] = bool(
        row.get("agentRegistry_exact") or row.get("registry_ref_in_abi")
        or row.get("registry_bytes_in_code") or row.get("free_funcs"))
    # owner vs discards
    oc = row.get("owner()")
    ov = oc.get("value") if isinstance(oc, dict) else None
    row["owner_in_discards"] = (ov.lower() in owners) if ov else None
    row["discards_owner_count"] = len(owners)
    fs_results.append(row)
    print(json.dumps(row, indent=1))

# ---- track-C 5c ----
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
if isinstance(checked, dict):
    checked_set = {a.lower() for a in checked.get("checked", [])}
    per_addr_before = len([k for k in checked.keys() if k != "checked"])
else:
    checked_set = set()
    per_addr_before = 0
merged = {}
for f in CHUNKS:
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
    abi = data.get("abi") or (data.get("stdJson", {}) or {}).get("abi")
    if abi is None:
        results5c.append({"address": addr, "mint_count": e["mint_count"],
                          "distinct_minters": e.get("distinct_minters"), "verdict": "not_verified",
                          "sourcify_match": data.get("match")})
        print(f"  {addr} mint_count={e['mint_count']} NOT_VERIFIED")
        continue
    fns = [x for x in abi if isinstance(x, dict) and x.get("type") == "function"]
    names = [x.get("name", "").lower() for x in fns]
    name_set = set(names)
    raw = json.dumps(abi).lower()
    mint_fns = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote_fns = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    free_views = [n for n in names if n in FREE_VIEWS]
    has_registry = REG_HEX in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = any(n in name_set for n in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(x.get("name", "").lower() in ("mintfree", "claimfree", "freemint")
                     and len(x.get("inputs", [])) == 0 for x in fns)
    s1 = bool(mint_fns and quote_fns and free_views and has_registry)
    s2 = bool(is_token and noarg_free and free_views and has_registry)
    verdict = "SALE-SHAPE" if (s1 or s2) else "not-sale-shape"
    results5c.append({"address": addr, "mint_count": e["mint_count"],
                      "distinct_minters": e.get("distinct_minters"), "verdict": verdict,
                      "sourcify": "verified", "S1": s1, "S2": s2,
                      "mint_fns": mint_fns, "quote_fns": quote_fns,
                      "free_views": free_views, "agent_gate": has_registry,
                      "is_token": is_token, "noarg_free": noarg_free})
    print(f"  {addr} mint_count={e['mint_count']} {verdict} S1={s1} S2={s2}")
    time.sleep(0.5)

# record newly checked in track-c-scan-checked.json
if isinstance(checked, dict):
    for e in new:
        checked.setdefault("checked", []).append(e["address"])
        checked[e["address"]] = {"mint_count": e["mint_count"], "checked_run": "backfill-132480915-132486914"}
    json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
    per_addr_after = len([k for k in checked.keys() if k != "checked"])
    checked_list_after = len(checked.get("checked", []))
else:
    per_addr_after = per_addr_before
    checked_list_after = len(checked_set)

out = {"run": "backfill 2026-11-09 ~09:1x WIB", "window": [132480915, 132486914],
       "driver_exit": 2, "watermark_before": 132480914, "watermark_after": 132481864,
       "failed_sub_chunks": [{"chunk": "132480915-132482914", "from": 132481865, "to": 132481914, "topic": "Transfer"},
                             {"chunk": "132482915-132484914", "from": 132483865, "to": 132483914, "topic": "Transfer"}],
       "first_seen_triage": fs_results,
       "early_leads": [r for r in fs_results if r.get("agent_shaped")],
       "track_c_5c": {"merged_erc20": len(merged), "ge10": len(cands),
                      "new_checked": len(new), "transport_failed": transport_failed,
                      "results": results5c,
                      "track_c_checked_per_addr": f"{per_addr_before} -> {per_addr_after}",
                      "track_c_checked_list": checked_list_after},
       "sale_shape_hits": [r for r in results5c if r.get("verdict") == "SALE-SHAPE"]}
json.dump(out, open(f"{BASE}/backfill-triage-132480915-132486914.json", "w"), indent=1)
print("WROTE backfill-triage-132480915-132486914.json")
print("early_leads:", len(out["early_leads"]), "sale_shape_hits:", len(out["sale_shape_hits"]))
