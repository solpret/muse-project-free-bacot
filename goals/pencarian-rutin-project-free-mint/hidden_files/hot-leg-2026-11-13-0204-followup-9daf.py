#!/usr/bin/env python3
"""Hot-leg 0204 follow-up: targeted OUTY-family view read for new S1+S2 0x9daf + OUTY.
Single raced batch per contract; read-only; writes only own follow-up json + seen notes.
0x9daf: S1+S2 flipped true on deferred retry this run; leg3 used wrong view names
(freeMinted/freeClaimed) for this family -> age/pool/slot UNVERIFIED. OUTY-family views:
minted/freeSold/paidSold/FREE_SUPPLY/PAID_CAP/START/FREE_END/FREE_FEE/PRICE/phase/
freeQuotaOf/quotaOf/balanceOf/freeOpen. OUTY itself returned null on SMALL_VIEWS for the
same reason (its interface has minted/freeSold/phase/START, not freeMinted/mintOpen).
"""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-13-0204"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
out = {"run": "hot-leg 0204 follow-up (OUTY-family views)", "started_epoch": T0}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None

FAMILY = ["minted()", "freeSold()", "paidSold()", "FREE_SUPPLY()", "PAID_CAP()",
          "START()", "FREE_END()", "FREE_FEE()", "PRICE()", "phase()",
          "freeQuotaOf(address)", "quotaOf(address)", "balanceOf(address)", "freeOpen()",
          "freeByAgent(address)", "freePerAgent()", "saleStart()", "freeSold(address)"]
def fam_batch(addr):
    calls, keys = [], []
    for i, sig in enumerate(FAMILY):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res = post_rpc_race(calls, timeout=12)
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}

def str_call(addr, sig):
    data = sel(sig)
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            off = int.from_bytes(b[32:64], "big")
            ln = int.from_bytes(b[off:off + 32], "big")
            return b[off + 32:off + 32 + ln].decode(errors="replace")
        except Exception as e:
            return f"<decode-error {e}>"
    return None

def quote_call(addr):
    data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
            tail = None
            if len(words) >= 5 and words[4] < len(b):
                off = words[4]
                ln = int.from_bytes(b[off:off + 32], "big")
                tail = b[off + 32:off + 32 + ln].decode(errors="replace")
            return {"words": words, "tail_string": tail}
        except Exception as e:
            return {"decode_error": str(e)[:100]}
    return None

TARGETS = {
    "0x9dafe93975203dafa6956bc70B7526644Db2504f": "NEW-S1S2",
    "0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412": "OUTY",
}
seen = json.load(open(BASE + "hot-leg-seen.json"))
for addr, nm in TARGETS.items():
    r = None
    for _attempt in range(2):
        r = fam_batch(addr)
        if r is not None and any(v is not None for v in r.values()):
            break
        time.sleep(1)
    nm_str = str_call(addr, "name()") if time.time() - T0 < 60 else None
    sym_str = str_call(addr, "symbol()") if time.time() - T0 < 70 else None
    q = quote_call(addr) if time.time() - T0 < 80 else None
    out[nm] = {"address": addr, "views": r,
               "summary": {k: v for k, v in r.items() if v is not None} if r else None,
               "name_str": nm_str, "symbol_str": sym_str, "quote_user_1": q}
    if isinstance(seen.get(addr), dict) and r:
        ssum = out[nm]["summary"] or {}
        old = seen[addr].get("note", "")
        old = old[-400:] if len(old) > 400 else old
        seen[addr]["note"] = (old + f" | FAM-0204: " +
                              ", ".join(f"{k}={v}" for k, v in ssum.items())[:300] +
                              (f" | name={nm_str} symbol={sym_str}" if nm_str else "") +
                              (f" | quote1={q}" if q else "")).strip()[:900]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-followup-9daf.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
