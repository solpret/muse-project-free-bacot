#!/usr/bin/env python3
"""Triage backfill run 132273098-132275169 (2026-11-08 ~04:46 WIB).
READ-ONLY. 2 first-seen ERC721 (both Sourcify match=null, no ABI -> on-chain
view calls via fast_rpc call_many; block ts via dataseed race, NOT Ankr).
Track-C 5c: merged ERC20 lists, mint_count>=10 desc, max 20 NEW, S1/S2 shape
via Sourcify ABI (curl). Transport failure recorded as such, NEVER as
not-sale-shape / not-verified.
Writes backfill-triage-132273098-132275169.json; appends newly-checked
addresses to track-c-scan-checked.json. NEVER previews/mints.
"""
import json, subprocess, sys, time
from datetime import datetime, timezone

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race, ENDPOINTS
from eth_hash.auto import keccak
from eth_abi import decode

# Dataseeds rate-limit batched eth_call (-32005); sequential single-endpoint
# calls are too slow (endpoints 3-8s each). Use race() ONE call at a time:
# all healthy endpoints concurrently, first success wins (~3-4s/call).
# A revert/transport failure is a per-call result, never a crash.
def call_many_gentle(items):
    """items: list of (to, hexdata). Returns list of hex result or None
    (None = transport failed on all endpoints OR eth_call reverted)."""
    out = []
    for (to, data) in items:
        try:
            out.append(race("eth_call", [{"to": to, "data": data}, "latest"]))
        except Exception:
            out.append(None)
        time.sleep(0.3)
    return out

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
CHUNKS = ["backfill-132273098-132275097.json", "backfill-132275098-132275169.json"]
RUN_TAG = "backfill-132273098-132275169-5c"
FIRST_SEEN = [
    {"address": "0x4E0a99e8b3b5E4BBb5794315DD0a3E2Ed493DF35", "kind": "ERC721",
     "mint_count": 2, "distinct_minters": 2, "first_block": 132274429,
     "last_block": 132274598,
     "minters_sample": ["0x2a3f3ffb5b5e65ee860d613efb21fecf650435da",
                        "0x9442453a44033b126efaffc40a5d9ba201224a4c"]},
    {"address": "0x6a6601F2D1B8B4CCa97cE8800dF5E8F4fE1910C8", "kind": "ERC721",
     "mint_count": 1, "distinct_minters": 1, "first_block": 132274452,
     "last_block": 132274452,
     "minters_sample": ["0x2a3f3ffb5b5e65ee860d613efb21fecf650435da"]},
]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def enc_uint(n):
    return format(n, "064x")

CALLS = [
    ("agentRegistry", "agentRegistry()", "address", None),
    ("agentIdRegistry", "agentIdRegistry()", "address", None),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", "address", None),
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", "address", None),
    ("REGISTRY", "REGISTRY()", "address", None),
    ("name", "name()", "string", None),
    ("symbol", "symbol()", "string", None),
    ("totalSupply", "totalSupply()", "uint256", None),
    ("totalMinted", "totalMinted()", "uint256", None),
    ("owner", "owner()", "address", None),
    ("FREE_CAP", "FREE_CAP()", "uint256", None),
    ("FREE_SUPPLY", "FREE_SUPPLY()", "uint256", None),
    ("FREE_SLOTS", "FREE_SLOTS()", "uint256", None),
    ("FREE_AMOUNT", "FREE_AMOUNT()", "uint256", None),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", "uint256", None),
    ("freeMinted", "freeMinted()", "uint256", None),
    ("freeSupply", "freeSupply()", "uint256", None),
    ("freeClaimed_user", "freeClaimed(address)", "bool", USER),
    ("freeClaimed_noarg", "freeClaimed()", "bool", None),
    ("freeCount_user", "freeCount(address)", "uint256", USER),
    ("MAX_SUPPLY", "MAX_SUPPLY()", "uint256", None),
    ("maxSupply", "maxSupply()", "uint256", None),
    ("PRICE", "PRICE()", "uint256", None),
    ("mintOpen", "mintOpen()", "bool", None),
    ("paidMintedCount", "paidMintedCount()", "uint256", None),
    ("paidUnlocked", "paidUnlocked()", "bool", None),
    ("balanceOf_user", "balanceOf(address)", "uint256", USER),
    ("quote_user_1", "quote(address,uint256)", "uint256", ("addr_uint", USER, 1)),
    ("quote_1", "quote(uint256)", "uint256", ("uint", 1)),
    ("cost_user_1", "cost(address,uint256)", "uint256", ("addr_uint", USER, 1)),
    ("spotsLeft", "spotsLeft()", "uint256", None),
    ("baseURI", "baseURI()", "string", None),
]

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

def triage_first_seen(fs):
    addr = fs["address"]
    data, err = fetch_abi_curl(addr)
    sourcify = "transport-failed" if data is None else (
        "verified" if abi_of(data) else f"not_verified (match={data.get('match')})")
    abi = abi_of(data) if data else None
    items = []
    for name, sig, typ, arg in CALLS:
        d = sel(sig)
        if arg is None:
            pass
        elif isinstance(arg, tuple) and arg[0] == "addr_uint":
            d += enc_addr(arg[1]) + enc_uint(arg[2])
        elif isinstance(arg, tuple) and arg[0] == "uint":
            d += enc_uint(arg[1])
        else:
            d += enc_addr(arg)
        items.append((addr, d))
    results = call_many_gentle(items)
    calls = {}
    for (name, sig, typ, arg), res in zip(CALLS, results):
        if res is None or res == "0x":
            calls[name] = {"error": "empty/revert-or-transport-failed"}
            continue
        try:
            v = decode([typ], bytes.fromhex(res[2:]))[0]
            calls[name] = {"value": v.hex() if isinstance(v, bytes) else v}
        except Exception as e:
            calls[name] = {"error": f"decode: {e}", "raw": res}
    try:
        blk = race("eth_getBlockByNumber", [hex(fs["first_block"]), False])
    except Exception:
        blk = None
    if blk:
        ts = int(blk["timestamp"], 16)
        ts_wib = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(
            timezone(__import__("datetime").timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        first_ts = {"value": ts, "wib": ts_wib}
    else:
        first_ts = {"error": "eth_getBlockByNumber failed all endpoints"}
    disc = json.load(open(f"{BASE}/same-owner-discards.json"))
    owners = {d["owner"].lower() for d in disc}
    contracts = {d["contract"].lower() for d in disc}
    owner = calls.get("owner", {}).get("value", "")
    registry_match = any(
        calls.get(k, {}).get("value", "").lower() == REGISTRY.lower()
        for k in ("agentRegistry", "agentIdRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "REGISTRY"))
    # free % from free views
    cap = None
    for k in ("FREE_CAP", "FREE_SUPPLY", "FREE_SLOTS", "freeSupply"):
        v = calls.get(k, {}).get("value")
        if isinstance(v, int):
            cap = v; break
    minted = calls.get("freeMinted", {}).get("value")
    free_pct = (minted / cap * 100) if isinstance(minted, int) and isinstance(cap, int) and cap else None
    quote = calls.get("quote_user_1", {}).get("value")
    if quote is None:
        quote = calls.get("quote_1", {}).get("value")
    out = dict(fs)
    out.update({"sourcify": sourcify, "calls": calls, "first_block_ts": first_ts,
                "owner_in_discards": owner.lower() in owners if owner else None,
                "contract_in_discards": addr.lower() in contracts,
                "registry_exact_match": registry_match,
                "free_cap": cap, "free_minted": minted, "free_pct": free_pct,
                "quote_user_1_wei": quote})
    # verdict
    if out["owner_in_discards"] or out["contract_in_discards"]:
        out["verdict"] = "same-owner-discard"
    elif not registry_match and sourcify.startswith("not_verified"):
        out["verdict"] = "not-agent-shaped"
    elif isinstance(quote, int) and quote > 0 and free_pct in (None, 0):
        out["verdict"] = "paid-only"
    elif isinstance(quote, int) and quote == 0:
        out["verdict"] = "free-path"
    else:
        out["verdict"] = "unresolved"
    return out

print("== FIRST-SEEN TRIAGE ==")
triage = []
for fs in FIRST_SEEN:
    t = triage_first_seen(fs)
    triage.append(t)
    print(f"  {t['address']} verdict={t['verdict']} sourcify={t['sourcify']} "
          f"registry={t['registry_exact_match']} name={t['calls'].get('name',{}).get('value')} "
          f"symbol={t['calls'].get('symbol',{}).get('value')} quote={t['quote_user_1_wei']} "
          f"free%={t['free_pct']} owner_disc={t['owner_in_discards']} "
          f"first_ts={t['first_block_ts']}")

# ---- Track-C 5c ----
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

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
            "noarg_free": noarg_free, "S1": s1, "S2": s2, "fn_count": len(fns)}

checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_list = checked.get("checked", [])
checked_set = {a.lower() for a in checked_list}
checked_keys = {k.lower() for k in checked.keys() if k.startswith("0x")}

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
new = [e for e in cands
       if e["address"].lower() not in checked_set and e["address"].lower() not in checked_keys][:20]
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
                      "sourcify": "verified", **sh})
    print(f"  {addr} mint_count={e['mint_count']} {verdict} S1={sh['S1']} S2={sh['S2']} "
          f"registry={sh['agent_gate']} mint={bool(sh['mint_fns'])} quote={bool(sh['quote_fns'])} free={bool(sh['free_views'])} token={sh['is_token']}")
    time.sleep(0.5)

added_list, added_keys = 0, 0
for r in results5c:
    if r["verdict"] == "transport-failed":
        continue
    addr = r["address"]
    if r["verdict"] == "not_verified":
        status, note = "not_verified", ""
    elif r["verdict"] == "SALE-SHAPE":
        status, note = "SALE-SHAPE", f"S1={r['S1']} S2={r['S2']}"
    else:
        status = "checked-not-sale-shape"
        note = (f"S1={r['S1']} S2={r['S2']} (registry={r['agent_gate']} mint={bool(r['mint_fns'])} "
                f"quote={bool(r['quote_fns'])} free={bool(r['free_views'])} token={r['is_token']})")
    if addr.lower() not in checked_set:
        checked_list.append(addr); added_list += 1
    if addr not in checked:
        checked[addr] = {"source": RUN_TAG, "status": status,
                         "mint_count": r["mint_count"], "note": note}
        added_keys += 1
checked["checked"] = checked_list
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print(f"track-c-scan-checked: list +{added_list}, keys +{added_keys}")

out = {"run": "backfill 2026-11-08 ~04:46 WIB", "window": [132273098, 132275169],
       "first_seen_triage": triage,
       "early_leads": [t for t in triage if t["verdict"] == "free-path"],
       "strong_leads": [],
       "track_c_5c": {"merged_erc20": len(merged), "ge10": len(cands),
                      "new_checked": len(new), "transport_failed": transport_failed,
                      "results": results5c},
       "sale_shape_hits": [r for r in results5c if r.get("verdict") == "SALE-SHAPE"]}
json.dump(out, open(f"{BASE}/backfill-triage-132273098-132275169.json", "w"), indent=1, default=str)
print("WROTE backfill-triage-132273098-132275169.json")
print("sale_shape_hits:", len(out["sale_shape_hits"]))
print("early_leads:", len(out["early_leads"]))
