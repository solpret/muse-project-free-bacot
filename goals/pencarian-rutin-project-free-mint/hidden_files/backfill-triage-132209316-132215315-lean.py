#!/usr/bin/env python3
"""Lean triage v2 2026-11-07 ~22:3x WIB run backfill 132209316-132215315.
Menggantikan triase v1 yang dibunuh di tengah badai 429 dataseed.
Pendekatan: Sourcify ABI dulu (curl, cepat); eth_call HANYA untuk fungsi
yang ADA di ABI; sleep 5 dtk; retry 2x dengan backoff bila 429/error.
Kontrak 1 (SQV) sudah lengkap di JSON v1 -> dilewati.
Read-only. Block timestamp via dataseed eth_getBlockByNumber.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132209316-132215315.json"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]

FIRST_SEEN = [
    ("0x3B2676eD85c4456a339D4FBAe2245BdF39d07A4f", 5, 1, 132209417),
    ("0x58F69Dea09cF0dE2D69e284FeF1969b1a75E5b43", 5, 1, 132210975),
    ("0x6Fb5be6E880a104007144FA5bf3672f96917a288", 4, 2, 132211133),
    ("0x152c47649846934cee5785986De397fABb53b827", 2, 2, 132211217),
    ("0x062008b5F50de0D2bC0b16a9cBc35a7aB5506f88", 5, 1, 132211894),
    ("0x7F0f964d05AF482a898438EE00bbe23975f63E78", 2, 2, 132212533),
    ("0x824Bc0219b586580Bfd2D4A72EE537d3ce3bF626", 5, 1, 132214409),
    ("0x4ec8df4060a6365Fd8d44A3C8c73CD7138Cc0006", 5, 1, 132214405),
]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc(method, params, timeout=12):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

def call_retry(to, data, tries=3):
    last = None
    for i in range(tries):
        r, e = rpc("eth_call", [{"to": to, "data": data}, "latest"])
        if r is not None:
            return r, None
        last = e
        if "429" in (e or ""):
            time.sleep(15)
        else:
            break
    return None, last

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

def dec_str(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 130:
        try:
            b = bytes.fromhex(raw[2:])
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
        except Exception:
            return None
    return None

def sourcify_abi(address):
    try:
        p = subprocess.run(["curl", "-s", "-m", "20",
            f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"],
            capture_output=True, text=True, timeout=25)
        if p.returncode != 0 or not p.stdout.strip():
            return ("curl_error", None)
        d = json.loads(p.stdout)
        if d.get("match") is None and d.get("abi") is None:
            return ("not_verified", None)
        return ("verified", d.get("abi"))
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

discard_owners = set()
try:
    d = json.load(open(f"{BASE}/same-owner-discards.json"))
    items = d if isinstance(d, list) else d.get("discards", d.get("records", []))
    for it in items:
        if isinstance(it, dict):
            for k in ("owner", "owner_address", "address"):
                if isinstance(it.get(k), str) and it[k].startswith("0x"):
                    discard_owners.add(it[k].lower())
except Exception as e:
    print("discards load error:", e, flush=True)
print(f"discard owners loaded: {len(discard_owners)}", flush=True)

# muat hasil v1 (kontrak 1 lengkap), lanjutkan
try:
    prev = json.load(open(OUT))
    results = prev.get("results", [])
except Exception:
    results = []
done = {r["address"].lower() for r in results}
print(f"already triaged: {len(results)}", flush=True)

# kandidat fungsi yang dicoba HANYA bila ada di ABI (case-insensitive)
CANDS = [
    ("agentRegistry()", "zero", "uint_addr"),
    ("name()", "zero", "str"),
    ("symbol()", "zero", "str"),
    ("quote(uint256)", "uint", "uint"),
    ("quoteFor(address,uint256)", "addr_uint", "uint"),
    ("currentPrice()", "zero", "uint"),
    ("mintPrice()", "zero", "uint"),
    ("price()", "zero", "uint"),
    ("PRICE()", "zero", "uint"),
    ("cost(uint256)", "uint", "uint"),
    ("totalMinted()", "zero", "uint"),
    ("totalSupply()", "zero", "uint"),
    ("maxSupply()", "zero", "uint"),
    ("remaining()", "zero", "uint"),
    ("freeClaimed(address)", "addr", "uint"),
    ("freeMinted()", "zero", "uint"),
    ("freeSupply()", "zero", "uint"),
    ("freeLeft()", "zero", "uint"),
    ("FREE_SLOTS()", "zero", "uint"),
    ("FREE_SUPPLY()", "zero", "uint"),
    ("FREE_AMOUNT()", "zero", "uint"),
    ("owner()", "zero", "uint_addr"),
]

for addr, mc, dm, fb in FIRST_SEEN:
    if addr.lower() in done:
        print(f"skip {addr} (done)", flush=True)
        continue
    out = {"address": addr, "first_block": fb, "mint_count": mc,
           "distinct_minters": dm, "calls": {}}
    status, abi = sourcify_abi(addr)
    fns = [i.get("name") for i in abi if isinstance(abi, list) and i.get("type") == "function"] if isinstance(abi, list) else []
    low = [f.lower() for f in fns]
    out["sourcify"] = status
    out["abi_functions"] = fns
    out["abi_has_agentRegistry"] = "agentregistry" in low
    out["abi_has_free_view"] = any(f in low for f in ("freeclaimed", "freeminted", "freesupply", "freeleft", "free_slots", "free_supply", "freeamount", "free_amount"))
    print(f"\n== {addr} mc={mc} first={fb} sourcify={status} fns={len(fns)} agentRegABI={out['abi_has_agentRegistry']} freeViewABI={out['abi_has_free_view']}", flush=True)
    print("   fns:", ", ".join(fns), flush=True)
    for sig, kind, dec in CANDS:
        fname = sig.split("(")[0]
        if fname.lower() not in low:
            continue
        data = sel(sig)
        if kind == "addr":
            data += USER_PAD
        elif kind == "uint":
            data += ONE
        elif kind == "addr_uint":
            data += USER_PAD + ONE
        raw, e = call_retry(addr, data)
        time.sleep(5)
        row = {"raw": (raw or "")[:130], "error": e}
        if dec == "uint":
            row["uint"] = dec_uint(raw) if raw else None
        elif dec == "uint_addr":
            row["uint"] = dec_uint(raw) if raw else None
            row["addr"] = dec_addr(raw) if raw else None
        elif dec == "str":
            row["str"] = dec_str(raw) if raw else None
        out["calls"][sig] = row
        print(f"  {sig}: {row}", flush=True)
    reg = out["calls"].get("agentRegistry()", {}).get("addr")
    out["agent_shaped"] = (reg or "").lower() == REGISTRY
    own = out["calls"].get("owner()", {}).get("addr")
    out["owner"] = own
    out["same_owner_discard"] = bool(own and own.lower() in discard_owners)
    blk, e = rpc("eth_getBlockByNumber", [hex(fb), False])
    out["block_error"] = e
    if blk and isinstance(blk, dict):
        ts = blk.get("timestamp")
        out["first_mint_timestamp"] = int(ts, 16) if ts else None
    print(f"  agent_shaped={out['agent_shaped']} owner={own} same_owner_discard={out['same_owner_discard']} ts={out.get('first_mint_timestamp')}", flush=True)
    results.append(out)
    json.dump({"run": "backfill-132209316-132215315", "results": results},
              open(OUT, "w"), indent=1)

print("saved", OUT)
