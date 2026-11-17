#!/usr/bin/env python3
"""Triage backfill chunk 131897549-131899548: 5 first-seen NFT + Track-C 5c.
Read-only. No preview/mint/claim/approve/sign/swap.
"""
import json, sys, time, subprocess, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def eth_call(to, data, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def eth_block_ts(blk):
    last = None
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(blk), False], 10, retries=0)
            return int(b["timestamp"], 16)
        except Exception as e:
            last = e
    raise last

def call_ok(to, data):
    try:
        r = eth_call(to, data)
        if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
            return r
        return None
    except Exception:
        return None

def u256(hexdata):
    try:
        return int(hexdata[-64:], 16)
    except Exception:
        return None

def addr_of(hexdata):
    try:
        return "0x" + hexdata[-40:]
    except Exception:
        return None

def sourcify_abi_curl(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    try:
        p = subprocess.run(["curl", "-s", "--max-time", "15",
                            "-H", "User-Agent: curl",
                            url], capture_output=True, text=True, timeout=20)
        if p.returncode != 0 or not p.stdout.strip():
            return ("error:curl_empty", None)
        d = json.loads(p.stdout)
        if "abi" in d:
            return ("verified", d["abi"])
        return (f"unverified:{str(d)[:120]}", None)
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

def decode_str(hexdata):
    if not isinstance(hexdata, str) or not hexdata.startswith("0x"):
        return None
    try:
        raw = bytes.fromhex(hexdata[2:])
    except Exception:
        return None
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64+ln].decode("utf-8", "replace")
        except Exception:
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None

USER_PAD = USER[2:].lower().rjust(64, "0")

def triage_nft(entry):
    a = entry["address"]
    out = {"address": a, "kind": entry.get("kind"), "mint_count": entry.get("mint_count"),
           "distinct_minters": entry.get("distinct_minters"),
           "first_block": entry.get("first_block"), "last_block": entry.get("last_block")}
    # timestamp first mint
    try:
        ts = eth_block_ts(entry["first_block"])
        out["first_mint_ts"] = ts
        out["first_mint_wib"] = (datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))).strftime("%Y-%m-%d %H:%M WIB")
        out["age_hours_at_run"] = round((time.time() - ts) / 3600, 2)
    except Exception as e:
        out["first_mint_ts_error"] = str(e)
    # Sourcify ABI via curl
    status, abi = sourcify_abi_curl(a)
    out["sourcify"] = status
    fnames = set()
    if abi:
        for item in abi:
            if item.get("type") == "function":
                fnames.add(item.get("name"))
        out["abi_functions"] = sorted(fnames)
    # agentRegistry
    r = call_ok(a, sel("agentRegistry()"))
    out["agentRegistry"] = addr_of(r) if r else None
    out["agentRegistry_match"] = (out["agentRegistry"] or "").lower() == REGISTRY.lower()
    # name / symbol
    r = call_ok(a, sel("name()"))
    out["name"] = decode_str(r) if r else entry.get("name")
    r = call_ok(a, sel("symbol()"))
    out["symbol"] = decode_str(r) if r else entry.get("symbol")
    # owner
    r = call_ok(a, sel("owner()"))
    out["owner"] = addr_of(r) if r else None
    # free views (no-arg uint)
    free_views = {}
    for fn in ["freeSupply", "freeMinted", "freeLeft", "freeRemaining", "FREE_SUPPLY",
               "FREE_SLOTS", "FREE_MINTED", "FREE_AMOUNT", "maxFreeSupply", "freeMintSupply",
               "remainingFree", "availableFree", "freeClaimedSupply", "totalFreeMinted"]:
        rr = call_ok(a, sel(f"{fn}()"))
        if rr is not None:
            free_views[fn] = u256(rr)
    out["free_views"] = free_views
    # address-arg bool views
    for fn in ["freeClaimed", "claimedFree", "hasClaimed", "freeMintedBy", "hasFreeMinted"]:
        rr = call_ok(a, sel(f"{fn}(address)") + USER_PAD)
        if rr is not None:
            out[f"{fn}(user)"] = (u256(rr) == 1)
    # quote(user,1)
    rr = call_ok(a, sel("quote(address,uint256)") + USER_PAD + "0000000000000000000000000000000000000000000000000000000000000001")
    out["quote_user_1"] = u256(rr) if rr is not None else None
    # price views
    price_views = {}
    for fn in ["PRICE", "mintPrice", "price", "cost", "MINT_PRICE"]:
        rr = call_ok(a, sel(f"{fn}()"))
        if rr is not None:
            price_views[fn] = u256(rr)
    out["price_views"] = price_views
    # supply
    for fn in ["totalSupply", "maxSupply", "MAX_SUPPLY", "totalMinted"]:
        rr = call_ok(a, sel(f"{fn}()"))
        if rr is not None:
            out[fn] = u256(rr)
    # mint funcs present
    out["mint_funcs"] = [f for f in fnames if "mint" in f.lower() or "claim" in f.lower()] if fnames else entry.get("mint_funcs", [])
    return out

def main():
    chunk = json.load(open(f"{BASE}/backfill-131897549-131899548.json"))
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    discard_owners = {d["owner"].lower() for d in discards}
    results = []
    for e in chunk.get("first_seen", []):
        print(f"--- triage {e['address']} ...", flush=True)
        r = triage_nft(e)
        r["owner_in_discards"] = (r.get("owner") or "").lower() in discard_owners
        results.append(r)
        print(json.dumps(r, indent=1), flush=True)
    # ---- Track-C 5c ----
    tc = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    checked = tc.get("checked", {})
    erc20 = sorted(chunk.get("erc20_mint_contracts_list", []),
                   key=lambda c: -c.get("mint_count", 0))
    cands = [c for c in erc20 if c.get("mint_count", 0) >= 10]
    tc_results = []
    n = 0
    for c in cands:
        if n >= 20:
            break
        a = c["address"]
        if a in checked or a.lower() in {k.lower() for k in checked}:
            continue
        n += 1
        print(f"--- track-c shape {a} mint_count={c['mint_count']} ...", flush=True)
        status, abi = sourcify_abi_curl(a)
        fnames = set()
        if abi:
            for item in abi:
                if item.get("type") == "function":
                    fnames.add(item.get("name"))
        s1 = ("mint" in str(fnames).lower() and "quote" in fnames
              and bool(fnames & {"freeSupply", "freeMinted", "freeLeft", "FREE_SUPPLY", "FREE_SLOTS", "freeClaimed", "freeRemaining"})
              and "agentRegistry" in fnames)
        s2 = (bool(fnames & {"mintFree", "freeClaimed", "freeMinted", "FREE_SLOTS", "FREE_SUPPLY"})
              and "agentRegistry" in fnames
              and bool(fnames & {"name", "symbol", "decimals", "totalSupply"}))
        rec = {"address": a, "mint_count": c["mint_count"], "distinct_minters": c.get("distinct_minters"),
               "first_block": c.get("first_block"), "sourcify": status,
               "shape_S1": s1, "shape_S2": s2,
               "sale_funcs": sorted([f for f in fnames if any(k in f.lower() for k in ["mint", "quote", "free", "claim", "price", "buy"])]) if fnames else []}
        if s1 or s2:
            # verify on-chain: registry + free pool + user quote
            rr = call_ok(a, sel("agentRegistry()"))
            rec["agentRegistry"] = addr_of(rr) if rr else None
            rec["agentRegistry_match"] = (rec["agentRegistry"] or "").lower() == REGISTRY.lower()
            for fn in ["freeSupply", "freeMinted", "freeLeft", "FREE_SUPPLY", "FREE_SLOTS"]:
                r2 = call_ok(a, sel(f"{fn}()"))
                if r2 is not None:
                    rec[fn] = u256(r2)
            rr = call_ok(a, sel("freeClaimed(address)") + USER_PAD)
            if rr is not None:
                rec["freeClaimed(user)"] = (u256(rr) == 1)
            rr = call_ok(a, sel("quote(address,uint256)") + USER_PAD + "0000000000000000000000000000000000000000000000000000000000000001")
            rec["quote_user_1"] = u256(rr) if rr is not None else None
        tc_results.append(rec)
        checked[a] = {"source": "backfill-131897549-131899548", "checked_wib": "2026-11-06",
                      "mint_count": c["mint_count"], "shape_S1": s1, "shape_S2": s2,
                      "sourcify": status}
        print(json.dumps(rec), flush=True)
    tc["checked"] = checked
    json.dump(tc, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
    out = {"triage_wib": "2026-11-06", "chunk": "131897549-131899548",
           "first_seen_triage": results, "track_c_5c": tc_results,
           "track_c_checked_this_run": n,
           "track_c_candidates_ge10": len(cands)}
    json.dump(out, open(f"{BASE}/triage-backfill-131897549-131899548.json", "w"), indent=1)
    print("TRIAGE_DONE", json.dumps(out, indent=1)[:4000], flush=True)

if __name__ == "__main__":
    main()
