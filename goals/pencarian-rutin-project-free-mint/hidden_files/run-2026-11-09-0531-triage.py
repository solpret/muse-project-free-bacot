#!/usr/bin/env python3
"""Triage run 2026-11-09 0531 WIB — first-seen scan contracts (agent-shape test)
+ track-C 5c ERC-20 backlog shape-check (max 20 new).
Agent-shape test (same as onchain_nft_scan.py): registry bytes in deployed
code + Sourcify ABI free/mint functions.
Read-only; writes run-2026-11-09-0531-triage.json.
"""
import json, subprocess, sys, time
sys.set_int_max_str_digits(100000)
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeRemaining", "FREE_CAP", "freeCount", "freeAllowance", "freeMint"]

def curl_get(url, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def get_code(addr):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                "params": [addr, "latest"]}, timeout=25)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

def sourcify_abi(addr):
    try:
        d = json.loads(curl_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12))
        return d.get("match"), d.get("abi") or []
    except Exception as e:
        return f"error:{type(e).__name__}", []

def shape(addr):
    code = get_code(addr)
    reg = (REGISTRY_BYTES in code[2:].lower()) if isinstance(code, str) and len(code) > 2 else None
    match, abi = sourcify_abi(addr)
    fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    names = set(fns)
    free = sorted([f for f in names if "free" in f.lower() and not f.lower().startswith("freeze")])
    mint = sorted([f for f in names if "mint" in f.lower()])
    has_mint = bool(names & {"mint", "mintFree", "mintWithInviter", "claimMint", "mintShare", "buyShare"})
    has_quote = bool(names & {"quote", "cost", "price", "priceFor", "getPrice", "mintPrice"})
    free_views = sorted([f for f in FREE_VIEWS if f in names])
    agent = bool(names & {"identityRegistry", "agentRegistry", "AgentGate", "agentId", "agentID"}) or any("agent" in (f or "").lower() or "registry" in (f or "").lower() for f in fns)
    token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"})
    agent_shaped = bool(reg) or (match not in (None, "error") and (s1 or s2 or bool(free)))
    return {"address": addr, "registry_bytes": reg, "sourcify": match,
            "free_funcs": free[:10], "mint_funcs": mint[:10],
            "S1": s1, "S2": s2, "agent": agent,
            "agent_shaped": agent_shaped,
            "note": f"registry={reg} sourcify={match} S1={s1} S2={s2} free={free[:6]} mint={mint[:6]}"}

sc = json.load(open(f"{HF}/run-2026-11-09-0531-scan.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
snap_addrs = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
snap_addrs |= {str(v.get("address", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict) and v.get("address")}
snap_addrs |= {str(v.get("sale", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict) and v.get("sale")}
seen_lows = {k.lower() for k in seen}
first = [c for c in sc.get("contracts_raw", [])
         if c["address"].lower() not in seen_lows and c["address"].lower() not in snap_addrs
         and c["address"].lower() != "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"]
print(f"first-seen to triage: {len(first)}", flush=True)
out = {"run": "2026-11-09-0531", "first_seen_triage": [], "track_c_5c": []}
with ThreadPoolExecutor(max_workers=6) as ex:
    for res in ex.map(lambda c: {**shape(c["address"]), "mint_count": c["mint_count"],
                                 "distinct_minters": c["distinct_minters"],
                                 "first_block": c["first_block"]}, first):
        out["first_seen_triage"].append(res)
        print(res["address"], res["note"], f"mints={res['mint_count']}", flush=True)

# --- 5c: ERC-20 backlog ---
checked = json.load(open(f"{HF}/track-c-scan-checked.json")) if True else {}
checked_lows = {k.lower() for k in checked}
cands = [e for e in sc.get("erc20_mint_contracts_list", []) if e["mint_count"] >= 10]
cands.sort(key=lambda e: -e["mint_count"])
new = [e for e in cands if e["address"].lower() not in checked_lows][:20]
dropped = len([e for e in cands if e["address"].lower() not in checked_lows]) - len(new)
print(f"5c: {len(cands)} candidates mc>=10, {len(new)} new to check, {dropped} dropped (sampling limit)", flush=True)
for e in new:
    r = shape(e["address"])
    r["mint_count"] = e["mint_count"]
    r["distinct_minters"] = e["distinct_minters"]
    out["track_c_5c"].append(r)
    print("5c", r["address"], r["note"], f"mints={e['mint_count']}", flush=True)
out["track_c_5c_dropped"] = dropped
json.dump(out, open(f"{HF}/run-2026-11-09-0531-triage.json", "w"), indent=1)
print("TRIAGE DONE hits:", [t for t in out["first_seen_triage"] if t["agent_shaped"]],
      [t for t in out["track_c_5c"] if t["S1"] or t["S2"]])
