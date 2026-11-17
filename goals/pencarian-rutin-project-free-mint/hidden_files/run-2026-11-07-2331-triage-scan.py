#!/usr/bin/env python3
"""Triage run 2331 (keccak fix: selectors via pycryptodome keccak256; same-owner list-of-dicts fix) — first-seen detection + agent-shape verdicts (lean).
Reads onchain-scan-2026-11-07-2331.json, onchain-snapshot.json,
onchain-scan-seen.json, track-c-scan-checked.json, same-owner-discards.json.
First-seen = absent from BOTH seen (nested contracts) AND snapshot
(contract addresses + track_c addresses + excluded). Registry address
itself excluded. Agent-shape verdicts from scan fields first; deeper
on-chain/Sourcify checks only for registry/free-shaped candidates.
Timestamps via fast_rpc ONLY (Ankr block timestamps are fake).
Appends newly seen contracts to onchain-scan-seen.json (nested contracts).
Writes run-2026-11-07-2331-triage-scan.json. Read-only otherwise."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"  # agent wallet (baw)

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-2331.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
try:
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
except Exception:
    discards = {}
discard_owners = set()
if isinstance(discards, dict):
    for v in discards.values():
        if isinstance(v, dict):
            o = v.get("owner") or v.get("address")
            if o: discard_owners.add(o.lower())
        elif isinstance(v, str):
            discard_owners.add(v.lower())
elif isinstance(discards, list):
    for x in discards:
        if isinstance(x, dict):
            o = x.get("owner") or x.get("address")
            if o: discard_owners.add(o.lower())
        elif isinstance(x, str):
            discard_owners.add(x.lower())

snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("address", "sale", "sale_address", "token", "token_address"):
            if v.get(k): snap_addrs.add(str(v[k]).lower())
for e in snap.get("excluded", []) or []:
    if isinstance(e, dict) and e.get("address"):
        snap_addrs.add(e["address"].lower())
    elif isinstance(e, str):
        snap_addrs.add(e.lower())

seen_addrs = set()
if isinstance(seen, dict):
    seen_addrs = {a.lower() for a in seen.get("contracts", {}).keys()}
    for a in seen.keys():
        if a.startswith("0x"): seen_addrs.add(a.lower())

first_seen, known = [], []
for c in scan.get("contracts", []):
    a = c.get("address", "").lower()
    if a == REG.lower():
        continue
    if a not in snap_addrs and a not in seen_addrs:
        first_seen.append(c)
    else:
        known.append(c)
print(f"enriched={len(scan.get('contracts', []))} first_seen_new={len(first_seen)} known={len(known)} partial={scan.get('partial')}", flush=True)

EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com/"]

def block_time(blk):
    for ep in EPS:
        try:
            res = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            ts = int(res[0]["timestamp"], 16)
            return ts
        except Exception:
            continue
    return None

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        abi = d.get("abi") or d.get("stdJson", {}).get("abi") or []
        return [f.get("name") for f in abi if isinstance(f, dict) and f.get("name")]
    except Exception as e:
        return {"error": str(e)[:120]}

def eth_call(to, data):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": to, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return res[0]
        except Exception:
            continue
    return None

from Crypto.Hash import keccak
def sel(sig):
    # keccak256 (Ethereum) via pycryptodome — NOT hashlib.sha3_256 (NIST SHA-3)
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

FREE_VIEWS = ["freeClaimed(address)", "freeFor(address)", "freeLeft()",
              "freeUsed(address)", "freeAvailable()", "freeSupply()",
              "freeMinted()", "freeClaimed()", "freeLeft(address)"]
REGISTRY_VIEWS = ["AGENT_REGISTRY()", "AGENT_ID_REGISTRY()", "agentRegistry()",
                  "AGENT_ID()", "registry()"]

verdicts = []
for c in first_seen:
    a = c["address"]
    v = {"address": a, "name": c.get("name"), "symbol": c.get("symbol"),
         "kind": c.get("kind"), "mint_count": c.get("mint_count"),
         "distinct_minters": c.get("distinct_minters"),
         "first_block": c.get("first_block"),
         "registry_bytes_hit": c.get("registry_bytes_hit"),
         "sourcify": c.get("sourcify"), "free_shaped": c.get("free_shaped"),
         "mint_funcs": c.get("mint_funcs")}
    ts = block_time(c["first_block"]) if c.get("first_block") else None
    if ts:
        v["first_mint_wib"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts + 7*3600))
    else:
        v["first_mint_wib"] = None
    # Deep check only if any agent-shape signal in scan fields
    need_deep = bool(c.get("registry_bytes_hit") or c.get("free_shaped") or
                     (c.get("sourcify") == "verified" and c.get("mint_funcs")))
    if not need_deep:
        v["verdict"] = "NOT agent-shaped (no registry bytes, no free shape, Sourcify %s)" % c.get("sourcify")
        v["lead"] = False
        verdicts.append(v)
        print("FIRST-SEEN:", a, c.get("name"), c.get("symbol"), "->", v["verdict"], flush=True)
        continue
    fns = sourcify_abi(a)
    if isinstance(fns, dict):
        v["sourcify_abi_error"] = fns.get("error")
        fns = []
    v["abi_fns"] = fns
    reg_match = None
    for sig in REGISTRY_VIEWS:
        r = eth_call(a, sel(sig))
        if r and len(r) >= 66:
            val = "0x" + r[-40:]
            reg_match = (sig, val, val.lower() == REG.lower())
            break
    v["registry_view"] = reg_match
    free_hits = []
    for sig in FREE_VIEWS:
        if "(address)" in sig:
            data = sel(sig) + USER[2:].lower().rjust(64, "0")
        else:
            data = sel(sig)
        r = eth_call(a, data)
        if r and r != "0x" and not r.startswith("0x00000000000000000000000000000000000000000000000000000000"):
            free_hits.append(sig)
        elif r and len(r) > 2:
            free_hits.append(sig + " (raw " + r[:18] + ")")
    v["free_views_live"] = free_hits
    owner = eth_call(a, sel("owner()"))
    v["owner"] = ("0x" + owner[-40:]) if owner and len(owner) >= 66 else None
    v["same_owner_discarded"] = bool(v["owner"] and v["owner"].lower() in discard_owners)
    has_reg = bool(reg_match and reg_match[2]) or bool(c.get("registry_bytes_hit"))
    has_free = bool(free_hits) or bool(c.get("free_shaped"))
    if v["same_owner_discarded"]:
        v["verdict"] = "SAME-OWNER DISCARD (owner in same-owner-discards.json) - not reported, not in snapshot"
        v["lead"] = False
    elif has_reg and has_free:
        v["verdict"] = "AGENT-SHAPED + free path present - EARLY LEAD candidate (parent: gate/age/quote check)"
        v["lead"] = True
    elif has_reg:
        v["verdict"] = "AGENT-SHAPED (registry match) but NO free view verified - likely PAID-ONLY, not a lead unless quote(user,1)=0 verified"
        v["lead"] = False
    else:
        v["verdict"] = "NOT agent-shaped (registry bytes only, no registry view match, no free view)"
        v["lead"] = False
    verdicts.append(v)
    print("FIRST-SEEN:", a, c.get("name"), c.get("symbol"), "->", v["verdict"], flush=True)

# ERC20 5c triage: mint_count>=10, sort desc, skip already checked (union of
# list form, sub-dict 'checked', and top-level keys — dual structure noted
# in run 1531/1550 notes)
checked_set = set()
if isinstance(checked, list):
    checked_set = {str(x).lower() for x in checked}
elif isinstance(checked, dict):
    for k, val in checked.items():
        if k.startswith("0x"):
            checked_set.add(k.lower())
    sub = checked.get("checked")
    if isinstance(sub, dict):
        checked_set |= {a.lower() for a in sub.keys()}
    elif isinstance(sub, list):
        checked_set |= {str(x).lower() for x in sub}
erc20 = scan.get("erc20_mint_contracts_list", [])
cand = [e for e in erc20 if e.get("mint_count", 0) >= 10
        and e.get("address", "").lower() not in checked_set]
cand.sort(key=lambda e: e.get("mint_count", 0), reverse=True)
print(f"erc20 total={len(erc20)} mint>=10 new-to-check={len(cand)} (cap 20, rest dropped sampling limit)", flush=True)
for e in cand[:20]:
    print("ERC20-CAND:", e.get("address"), "mint_count=", e.get("mint_count"), flush=True)

# Append newly seen contracts (NFT + ERC20) to seen file
new_seen = 0
for c in scan.get("contracts", []):
    a = c.get("address", "").lower()
    if a and a not in seen_addrs and a != REG.lower():
        seen.setdefault("contracts", {})[c["address"]] = c.get("first_block")
        seen_addrs.add(a)
        new_seen += 1
for e in erc20:
    a = e.get("address", "").lower()
    if a and a not in seen_addrs:
        seen.setdefault("contracts", {})[e["address"]] = e.get("first_block")
        seen_addrs.add(a)
        new_seen += 1
if new_seen:
    json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
print(f"seen appended: {new_seen} (total nested now {len(seen.get('contracts', {}))})", flush=True)

out = {"first_seen": verdicts, "erc20_candidates": cand[:20],
       "erc20_total": len(erc20), "erc20_new_to_check": len(cand),
       "enriched": len(scan.get("contracts", [])),
       "window": [scan.get("from_block"), scan.get("to_block")],
       "partial": scan.get("partial"),
       "ankr_calls": scan.get("ankr_calls"), "errors": scan.get("errors")}
json.dump(out, open(f"{BASE}/run-2026-11-07-2331-triage-scan.json", "w"), indent=1)
print("TRIAGE DONE", flush=True)
