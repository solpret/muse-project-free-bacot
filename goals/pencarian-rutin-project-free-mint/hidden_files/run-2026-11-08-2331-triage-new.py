#!/usr/bin/env python3
"""Run 2331 triage for Boltbook-new contracts (route 2/3) + Vesperfang mint-revert verify.
Read-only: Sourcify ABI fetch, fast_rpc eth_calls, Ankr getLogs (module, proxy env).
Never previews/mints. Writes run-2026-11-08-2331-triage-new.json + .log via stdout."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

TARGETS = {
    "FrankensteinFriends": "0xedfd9e6517ad4491ac6c7c98508566e2490ce708",
    "VampireVibes": "0xa5fb4e0e83837e9c7035b47c2f02d7db075563de",
    "BNBirds": "0x5d6967fe8400c4504c5035e1fb834967da7efbde",
    "MiChan": "0x669cb75f51b5d23f4b42fc1522b653d7b88e608d",
    "OPEC": "0x88311E8fA4ab792CA72acaf6f8AD4B391cc56713",
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def raw_call(addr, sig, arg=None, timeout=30):
    data = sel(sig) + (enc(arg) if arg else "")
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=timeout, retries=0)
            if isinstance(out, dict) and "error" in out: return None, out["error"]
            return (to_int(out.get("result")) if isinstance(out, dict) else None), None
        except Exception:
            continue
    return None, "all-endpoints-failed"

def raw_call_str(addr, sig, timeout=30):
    data = sel(sig)
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=timeout, retries=0)
            if isinstance(out, dict) and "error" in out: return None
            r = out.get("result") if isinstance(out, dict) else None
            if not r or r == "0x": return None
            try:
                b = bytes.fromhex(r[2:])
                # string: offset(32) + len(32) + data
                ln = int.from_bytes(b[32:64], "big")
                return b[64:64+ln].decode("utf-8", "replace")
            except Exception:
                return None
        except Exception:
            continue
    return None

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run2331"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        return None, f"fetch-error: {e}"
    abi = data.get("abi")
    if abi:
        return abi, data.get("match", "")
    try:
        url2 = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run2331"})
        with urllib.request.urlopen(req2, timeout=30) as r:
            data2 = json.load(r)
        return data2.get("abi"), data2.get("match", "")
    except Exception as e:
        return None, f"abi-fetch-error: {e}"

FREE_VIEWS = ["freeclaimed", "freeleft", "freesupply", "freefor", "freeused", "freeavailable",
              "freesharesremaining", "freesharesclaimed", "freesharepoolexhausted", "freeminted",
              "free", "free_count", "freecount", "freeskunksremaining", "free_pool", "freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]

def shape(abi):
    if not abi:
        return {"shape": "UNKNOWN-abi-unavailable"}
    names = [e["name"] for e in abi if isinstance(e, dict) and e.get("name")]
    low = [n.lower() for n in names]
    has_mint = any("mint" in n for n in low)
    free_views = sorted({n for n in names if n.lower() in FREE_VIEWS or "free" in n.lower()})
    quote_fns = sorted({n for n in names if n.lower() in QUOTE_FNS})
    has_quote = bool(quote_fns)
    is_token = all(x in low for x in ("name", "symbol", "decimals", "totalsupply"))
    raw = json.dumps(abi).lower()
    registry_ref = REGISTRY.lower() in raw or "agentid" in raw or "agentregistry" in raw or "agentgate" in raw
    gate_fn = any("agent" in n for n in low)
    s1 = has_mint and has_quote and bool(free_views) and (registry_ref or gate_fn)
    s2 = is_token and any(n.lower() == "mintfree" for n in names) and bool(free_views) and (registry_ref or gate_fn)
    mint_shape = has_mint and (bool(free_views) or "free" in raw)
    return {"functions": names, "has_mint": has_mint, "free_views": free_views,
            "quote_fns": quote_fns, "is_token": is_token,
            "registry_ref_or_gate": bool(registry_ref or gate_fn),
            "S1": s1, "S2": s2, "mint_shape": mint_shape,
            "shape": ("SALE-S1" if s1 else "SALE-S2" if s2 else "MINT-SHAPE" if mint_shape else "NOT-AGENT-SHAPED")}

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "mintedBy(address)", "freeUsed(address)",
         "freeLeft(address)", "quote(address,uint256)"]

def first_mint(addr, frm, to):
    """First Transfer-from-zero in [frm,to], chunked 1000 blocks. Returns (block, ts) or (None, note)."""
    lo, hi = frm, to
    first = None
    chunk = lo
    while chunk <= hi:
        cto = min(chunk + 999, hi)
        try:
            logs, _ = scan.ankr_logs(chunk, cto, [scan.TRANSFER, scan.ZERO_TOPIC])
        except Exception as e:
            return None, f"getLogs-error {chunk}-{cto}: {e}"
        for log in logs:
            if log.get("address", "").lower() != addr.lower():
                continue
            topics = log.get("topics", [])
            if len(topics) in (3, 4):
                blk = int(log.get("blockNumber", "0x0"), 16)
                if first is None or blk < first:
                    first = blk
        print(f"  firstmint chunk {chunk}-{cto}: first so far {first}", flush=True)
        chunk = cto + 1
        time.sleep(1.0)
    if first is None:
        return None, f"no Transfer-from-zero in {frm}-{to}"
    # block timestamp via fast_rpc
    ts = None
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(first), False]}, timeout=30, retries=0)
            ts = int(out["result"]["timestamp"], 16)
            break
        except Exception:
            continue
    return first, ts

out = {"run": "2331", "targets": {}}
for name, addr in TARGETS.items():
    print(f"== {name} {addr}", flush=True)
    rec = {"address": addr}
    abi, note = fetch_abi(addr)
    rec["sourcify"] = note if isinstance(note, str) else str(note)
    s = shape(abi) if abi else {"shape": "UNKNOWN-abi-unavailable", "note": note}
    rec.update(s)
    print(f"  shape={rec['shape']} S1={s.get('S1')} S2={s.get('S2')} registry/gate={s.get('registry_ref_or_gate')} free={s.get('free_views')} quote={s.get('quote_fns')}", flush=True)
    reads = {}
    for sig in VIEWS:
        if sig == "quote(address,uint256)":
            # quote(user,1): encode address + uint256 1
            data = sel(sig) + enc(USER) + "0" * 63 + "1"
            v = None
            for ep in EPS:
                try:
                    o = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                      "params": [{"to": addr, "data": data}, "latest"]},
                                 timeout=30, retries=0)
                    if isinstance(o, dict) and "error" not in o:
                        v = to_int(o.get("result")); break
                except Exception:
                    continue
            reads["quote_user_1"] = v
            continue
        v, err = raw_call(addr, sig, USER if "(address)" in sig else None)
        reads[sig.split("(")[0] + ("_user" if "(address)" in sig else "")] = v
    reads["name"] = raw_call_str(addr, "name()")
    reads["symbol"] = raw_call_str(addr, "symbol()")
    rec["reads"] = reads
    print(f"  reads={json.dumps(reads)}", flush=True)
    out["targets"][name] = rec

# Vesperfang mint(1) value-0 sim verify
print("== Vesperfang mint-revert verify", flush=True)
vesp = "0x2a91b304ee74162007730cf1da24c1d8c137c627"
data = sel("mint(uint256)") + "0" * 63 + "1"
err = None; res = None
for ep in EPS:
    try:
        o = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"from": USER, "to": vesp, "data": data, "value": "0x0"}, "latest"]},
                     timeout=30, retries=0)
        if isinstance(o, dict) and "error" in o:
            err = o["error"]; break
        res = o.get("result"); break
    except Exception as e:
        err = str(e); continue
print(f"  Vesperfang mint(1) sim: result={res} error={json.dumps(err)[:300]}", flush=True)
out["vesperfang_mint_sim"] = {"result": res, "error": err}

# First-mint verification for the two fresh NFT names (Boltbook: minted ~23:10-23:15 WIB)
head = int(scan.rpc_call("eth_blockNumber", []), 16)
print(f"head={head}", flush=True)
for name in ("FrankensteinFriends", "VampireVibes"):
    addr = TARGETS[name]
    print(f"== first-mint {name}", flush=True)
    blk, ts = first_mint(addr, head - 9000, head)
    rec = {"first_mint_block": blk, "first_mint_ts": ts}
    if ts:
        import datetime
        rec["first_mint_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    print(f"  {rec}", flush=True)
    out["targets"][name]["first_mint"] = rec

json.dump(out, open(BASE + "/run-2026-11-08-2331-triage-new.json", "w"), indent=1)
print("saved", BASE + "/run-2026-11-08-2331-triage-new.json", flush=True)
