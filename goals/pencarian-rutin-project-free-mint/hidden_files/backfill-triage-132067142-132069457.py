#!/usr/bin/env python3
"""Triage backfill run 132067142-132069457 (first-seen NFT + Track-C 5c).
READ-ONLY on-chain (eth_call / eth_getBlockByNumber / eth_getCode) + Sourcify
ABI via curl. Writes only its own triage JSON + appends newly-checked
addresses to track-c-scan-checked.json. Never previews/mints/approves.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

try:
    from Crypto.Hash import keccak

    def _keccak(b: bytes) -> bytes:
        k = keccak.new(digest_bits=256)
        k.update(b)
        return k.digest()
except Exception:
    from eth_hash.auto import keccak as _keccak  # type: ignore

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
WIB = timezone(timedelta(hours=7))
RUN_TAG = "backfill-132067142-132069457"
CHUNKS = ["backfill-132067142-132069141.json", "backfill-132069142-132069457.json"]


def sel(sig: str) -> str:
    return "0x" + _keccak(sig.encode()).hex()[:8]


def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    return f"ERROR:{last}"


def call(addr, data):
    r = rpc("eth_call", [{"to": addr, "data": data}, "latest"])
    if isinstance(r, str) and (r.startswith("0x") and len(r) > 2):
        return r
    return None


def u256(v):
    if isinstance(v, str) and v.startswith("0x"):
        try:
            return int(v, 16)
        except Exception:
            return None
    return None


def addr_ret(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 42:
        return "0x" + v[-40:]
    return None


def decode_str(v):
    if not isinstance(v, str) or not v.startswith("0x"):
        return None
    try:
        raw = bytes.fromhex(v[2:])
    except Exception:
        return None
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64 + ln].decode("utf-8", "replace")
        except Exception:
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None


def addr_arg(a: str) -> str:
    return "00" * 12 + a[2:].lower()


def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    try:
        p = subprocess.run(["curl", "-s", "--max-time", "15", url],
                           capture_output=True, text=True, timeout=20)
        if p.returncode != 0 or not p.stdout.strip():
            return ("error:curl", None)
        data = json.loads(p.stdout)
        return ("verified", data.get("abi"))
    except Exception as e:  # noqa: BLE001
        return (f"error:{type(e).__name__}", None)


def block_ts(block):
    r = rpc("eth_getBlockByNumber", [hex(block), False])
    if isinstance(r, dict):
        ts = u256(r.get("timestamp"))
        if ts:
            return ts
    return None


def triage_nft(c):
    addr = c["address"]
    out = {"address": addr, "kind": c.get("kind"),
           "mint_count": c.get("mint_count"),
           "distinct_minters": c.get("distinct_minters"),
           "minters_sample": c.get("minters_sample"),
           "first_block": c.get("first_block"), "last_block": c.get("last_block")}
    status, abi = sourcify_abi(addr)
    out["sourcify"] = status
    fns = []
    if isinstance(abi, list):
        for it in abi:
            if it.get("type") == "function":
                fns.append(it.get("name", ""))
    out["abi_functions"] = sorted(set(fns))
    out["name"] = decode_str(call(addr, sel("name()")))
    out["symbol"] = decode_str(call(addr, sel("symbol()")))
    reg = addr_ret(call(addr, sel("agentRegistry()")))
    out["agentRegistry"] = reg
    out["registry_match"] = (reg or "").lower() == REGISTRY.lower()
    out["owner"] = addr_ret(call(addr, sel("owner()")))
    out["totalSupply"] = u256(call(addr, sel("totalSupply()")))
    out["maxSupply"] = u256(call(addr, sel("MAX_SUPPLY()")))
    # free views: from ABI first, else generic candidates
    free_views = {}
    abi_free = [f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")]
    candidates = list(dict.fromkeys(abi_free + [
        "freeSupply", "freeMinted", "freeClaimed", "freeLeft",
        "freeMintSupply", "freeSharesRemaining", "freeSharesClaimed",
        "FREE_SUPPLY", "FREE_SLOTS", "FREE_AMOUNT", "PRICE", "mintPrice",
        "price", "cost"]))
    for fn in candidates:
        # only no-arg views; skip functions with inputs (except handled below)
        sig = None
        if isinstance(abi, list):
            for it in abi:
                if it.get("type") == "function" and it.get("name") == fn:
                    if len(it.get("inputs", [])) == 0:
                        outs = it.get("outputs", [])
                        if outs and outs[0].get("type") in ("uint256", "uint8", "bool"):
                            sig = f"{fn}()"
                    break
        if sig is None and fn not in abi_free:
            sig = f"{fn}()"
        if sig is None:
            continue
        v = call(addr, sel(sig))
        if v is None:
            continue
        if v.startswith("0x") and len(v) == 66:
            free_views[fn] = u256(v)
        elif v.startswith("0x") and len(v) == 66:
            free_views[fn] = v
    out["free_views"] = free_views
    # freeClaimed(user) / freeMinted(user) style
    for fn in ["freeClaimed", "freeMinted", "freeShareClaimedBy", "hasClaimedFree",
               "claimedFree", "freeMintedBy"]:
        if fn in fns:
            v = call(addr, sel(f"{fn}(address)") + addr_arg(USER))
            if v is not None:
                out.setdefault("user_free_flags", {})[fn] = u256(v)
    # quote(user,1)
    if "quote" in fns:
        q = call(addr, sel("quote(address,uint256)") + addr_arg(USER) + format(1, "064x"))
        out["quote_user_1"] = u256(q)
    out["first_mint_ts"] = block_ts(c["first_block"])
    if out["first_mint_ts"]:
        dt = datetime.fromtimestamp(out["first_mint_ts"], WIB)
        out["first_mint_wib"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        out["age_hours"] = round((time.time() - out["first_mint_ts"]) / 3600, 2)
    return out


def shape_track_c(addr):
    """S1/S2 sale-shape from Sourcify ABI + registry bytes in code."""
    status, abi = sourcify_abi(addr)
    fns = []
    if isinstance(abi, list):
        for it in abi:
            if it.get("type") == "function":
                fns.append(it.get("name", ""))
    code = rpc("eth_getCode", [addr, "latest"])
    reg_bytes = isinstance(code, str) and REGISTRY_BYTES in code[2:].lower()
    has = lambda *names: any(f in fns for f in names)
    mint = has("mint", "mintShare", "mintFree", "mintPaid", "buyShare", "buy")
    quote = has("quote", "getPrice", "price", "cost", "mintPrice", "PRICE")
    free = [f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")]
    agent = has("agentRegistry", "agentGate", "agentId", "AgentRegistry")
    token = has("name", "symbol", "decimals", "totalSupply")
    s1 = bool(mint and quote and free and (agent or reg_bytes))
    s2 = bool(token and has("mintFree") and free and (agent or reg_bytes)
              and has("mintPaid"))
    return {"sourcify": status, "functions": sorted(set(fns)), "registry_bytes": reg_bytes,
            "mint": mint, "quote": quote, "free": free, "agent": agent or reg_bytes,
            "token": token, "S1": s1, "S2": s2}


def main():
    first_seen = []
    erc20 = {}
    for f in CHUNKS:
        d = json.load(open(os.path.join(BASE, f)))
        first_seen += d.get("first_seen", [])
        for e in d.get("erc20_mint_contracts_list", []):
            erc20[e["address"].lower()] = e
    discards = json.load(open(os.path.join(BASE, "same-owner-discards.json")))
    discard_owners = {r.get("owner", "").lower() for r in discards if r.get("owner")}

    out = {"run": RUN_TAG, "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "first_seen_triage": [], "track_c_5c": {}}
    # dedupe first_seen across chunks (same contract can appear in >1 chunk)
    _dedup = {}
    for c in first_seen:
        k = c["address"].lower()
        if k not in _dedup:
            _dedup[k] = dict(c)
            _dedup[k]["minters_sample"] = list(c.get("minters_sample") or [])
        else:
            _d = _dedup[k]
            _d["mint_count"] = (_d.get("mint_count") or 0) + (c.get("mint_count") or 0)
            _d["distinct_minters"] = len(set(_d["minters_sample"]) | set(c.get("minters_sample") or []))
            _d["minters_sample"] = list(set(_d["minters_sample"]) | set(c.get("minters_sample") or []))
            _d["first_block"] = min(_d["first_block"], c["first_block"])
            _d["last_block"] = max(_d["last_block"], c["last_block"])
    first_seen = list(_dedup.values())
    print(f"DEDUP first-seen: {len(first_seen)} unique", flush=True)
    for c in first_seen:
        t = triage_nft(c)
        t["owner_in_discards"] = (t.get("owner") or "").lower() in discard_owners
        free_ok = False
        if t.get("quote_user_1") == 0:
            free_ok = True
        for v in (t.get("free_views") or {}).values():
            if isinstance(v, int) and v > 0:
                free_ok = True
        t["agent_shaped"] = bool(t.get("registry_match") or
                                 (t.get("sourcify") == "verified" and
                                  any("agent" in f.lower() or "free" in f.lower()
                                      for f in t.get("abi_functions", []))))
        t["free_path"] = free_ok
        t["age_ok_48h"] = (t.get("age_hours") is not None and t["age_hours"] <= 48)
        t["verdict"] = ("EARLY LEAD" if (t["agent_shaped"] and t["free_path"]
                                          and t["age_ok_48h"]) else "not-agent-shaped/no-free-path")
        out["first_seen_triage"].append(t)
        print(f"TRIAGE {t['address']} name={t.get('name')} sym={t.get('symbol')} "
              f"registry_match={t.get('registry_match')} sourcify={t.get('sourcify')} "
              f"free={t.get('free_views')} quote1={t.get('quote_user_1')} "
              f"owner={t.get('owner')} discards={t['owner_in_discards']} "
              f"first={t.get('first_mint_wib')} age_h={t.get('age_hours')} "
              f"-> {t['verdict']}", flush=True)

    # Track-C 5c
    tc = json.load(open(os.path.join(BASE, "track-c-scan-checked.json")))
    checked_set = {k.lower() for k in tc if k != "checked"}
    checked_set |= {k.lower() for k in tc.get("checked", {})}
    ge10 = [e for e in erc20.values() if e["mint_count"] >= 10]
    ge10.sort(key=lambda e: -e["mint_count"])
    new20 = [e for e in ge10 if e["address"].lower() not in checked_set][:20]
    out["track_c_5c"]["candidates_ge10"] = len(ge10)
    out["track_c_5c"]["new_checked"] = []
    sale_hits = []
    for e in new20:
        s = shape_track_c(e["address"])
        rec = {"address": e["address"], "mint_count": e["mint_count"],
               "distinct_minters": e["distinct_minters"],
               "first_block": e["first_block"], **s}
        out["track_c_5c"]["new_checked"].append(rec)
        tc[e["address"]] = {
            "source": f"{RUN_TAG}-5c",
            "status": "sale-shape-hit" if (s["S1"] or s["S2"]) else "checked-not-sale-shape",
            "note": (f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} "
                     f"free={s['free']} agent={s['agent']} token={s['token']} "
                     f"sourcify={s['sourcify']} mint_count={e['mint_count']}")}
        if s["S1"] or s["S2"]:
            sale_hits.append(rec)
        print(f"5C {e['address']} mc={e['mint_count']} S1={s['S1']} S2={s['S2']} "
              f"mint={s['mint']} quote={s['quote']} free={s['free']} "
              f"agent={s['agent']} sourcify={s['sourcify']}", flush=True)
    out["track_c_5c"]["sale_hits"] = sale_hits
    with open(os.path.join(BASE, "track-c-scan-checked.json"), "w") as f:
        json.dump(tc, f, indent=1)
    with open(os.path.join(BASE, f"backfill-triage-{RUN_TAG[9:]}.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"TRIAGE DONE: {len(out['first_seen_triage'])} first-seen, "
          f"{len(new20)} track-C baru dicek, {len(sale_hits)} sale-shape hit", flush=True)


if __name__ == "__main__":
    main()
