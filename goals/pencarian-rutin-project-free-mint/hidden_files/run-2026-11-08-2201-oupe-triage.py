#!/usr/bin/env python3
"""Parent triage run 2026-11-08 2201: OUPE slot/first-mint + Pokechain/GLOOP Transfer-to-user.
Read-only. No preview/mint/claim/sign."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as _fr_post
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-2201"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0x" + "00" * 12 + USER[2:].lower()
ZERO_PAD = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
OUPE = "0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d"
POKE = "0x4EF929aF00cB93993c3D01834C4DA79200d31e32"
GLOOP = "0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def eth_call(addr, data, ep=None):
    eps = [ep] if ep else EPS
    for e in eps:
        try:
            r = _fr_post(e, [{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}], timeout=30)
            if isinstance(r, list) and r and "result" in r[0]:
                return r[0]["result"]
            return None
        except Exception as ex:
            last = ex
    return None

def call_view(addr, sig, arg=None):
    data = sel(sig)
    if arg is not None:
        data += enc(arg)
    raw = eth_call(addr, data)
    return to_int(raw), raw

def call_str(addr, sig):
    raw = eth_call(addr, sel(sig))
    if raw is None or raw == "0x": return None
    try:
        b = bytes.fromhex(raw[2:])
        # string ABI: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None

out = {"run": TS, "ts_wib": time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(time.time()+7*3600))}

# --- head block ---
try:
    r = _fr_post(EPS[0], [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=30)
    head = int(r[0]["result"], 16)
except Exception as e:
    head = 132416272
out["head"] = head
print("HEAD", head, flush=True)

# --- 1. Transfer-to-user for Pokechain + GLOOP (from 132380000 to head) ---
for name, addr in [("Pokechain", POKE), ("GLOOP", GLOOP)]:
    found = []
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132380000),
            "toBlock": hex(head), "pageSize": 1000, "decodeLogs": False, "address": addr,
            "topics": [TRANSFER, None, USER_PAD]}, timeout=90)
        logs = body.get("result", {}).get("logs", []) or []
        for lg in logs:
            found.append({"block": int(lg.get("blockNumber"), 16), "tx": lg.get("transactionHash"),
                          "tokenId": to_int(lg.get("topics", [None]*4)[3]) if len(lg.get("topics", [])) > 3 else None,
                          "from": "0x" + lg.get("topics", ["", ""])[1][-40:] if len(lg.get("topics", [])) > 1 else None})
    except Exception as e:
        found = [{"error": f"{type(e).__name__}: {e}"}]
    out[f"transfer_to_user_{name}"] = found
    print(name, "transfers-to-user:", json.dumps(found), flush=True)

# --- 2. OUPE: Sourcify ABI fetch ---
abi = None
try:
    req = urllib.request.Request(
        f"https://sourcify.dev/server/v2/contracts/56/{OUPE}",
        headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        meta = json.load(resp)
    abi = meta.get("stdJson", {}).get("abi") or meta.get("abi")
    print("SOURCIFY OUPE: abi fns:", len(abi) if abi else None, flush=True)
except Exception as e:
    print("SOURCIFY OUPE FAIL:", type(e).__name__, e, flush=True)
out["oupe_sourcify_abi_ok"] = bool(abi)
if abi:
    fns = [f"{x.get('name')}({','.join(i.get('type','') for i in x.get('inputs',[]))})"
           for x in abi if x.get("type") == "function"]
    out["oupe_abi_functions"] = fns
    print("OUPE ABI:", json.dumps(fns), flush=True)

# --- 3. OUPE eth_call reads ---
views = ["name()", "symbol()", "totalSupply()", "startTime()", "freeClaimed()",
         "FREE_MAX()", "FREE_CLAIM()", "marketOpen()", "website()", "contractURI()",
         "MAX_SUPPLY()", "PHASE1_CAP()", "MAX_PACKS()", "phase()", "price()",
         "claimFree()", "mintPrice()", "publicPrice()"]
reads = {}
for sig in views:
    if sig in ("name()", "symbol()", "website()", "contractURI()"):
        reads[sig] = call_str(OUPE, sig)
    else:
        v, raw = call_view(OUPE, sig)
        reads[sig] = v
out["oupe_views"] = reads
print("OUPE VIEWS:", json.dumps(reads, ensure_ascii=False), flush=True)

# user-slot candidates (probe each; a clean uint return = function exists)
slot_cands = ["claimed(address)", "freeTaken(address)", "claimOf(address)",
              "remainingFor(address)", "hasClaimed(address)", "mintedBy(address)",
              "freeUsed(address)", "freeLeft(address)", "claims(address)",
              "claimedFree(address)", "freeClaimedBy(address)"]
slots = {}
for sig in slot_cands:
    v, raw = call_view(OUPE, sig, USER)
    slots[sig] = {"value": v, "raw": (raw or "")[:66]}
out["oupe_user_slot_probes"] = slots
print("OUPE SLOT PROBES:", json.dumps(slots), flush=True)

# quote for user (1 unit) candidates
for sig in ["quote(address,uint256)", "costOf(address,uint256)", "getPrice(uint256)",
            "priceOf(address,uint256)"]:
    try:
        data = sel(sig)
        if "(address,uint256)" in sig:
            data += enc(USER) + (1).to_bytes(32, "big").hex()
        else:
            data += (1).to_bytes(32, "big").hex()
        raw = eth_call(OUPE, data)
        out.setdefault("oupe_quote_probes", {})[sig] = to_int(raw)
    except Exception as e:
        out.setdefault("oupe_quote_probes", {})[sig] = f"ERR {e}"
print("OUPE QUOTES:", json.dumps(out.get("oupe_quote_probes")), flush=True)

# --- 4. OUPE first mint via Ankr (Transfer from zero), chunks of 2000 blocks from 132405000 ---
first = None
frm = 132405000
while frm <= head and first is None:
    to = min(frm + 1999, head)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
            "toBlock": hex(to), "pageSize": 1000, "decodeLogs": False, "address": OUPE,
            "topics": [TRANSFER, ZERO_PAD]}, timeout=90)
        logs = body.get("result", {}).get("logs", []) or []
        if logs:
            lg = logs[0]
            first = {"block": int(lg.get("blockNumber"), 16), "tx": lg.get("transactionHash"),
                     "count_in_chunk": len(logs)}
            # block timestamp via fast_rpc eth_getBlockByNumber
            try:
                r = _fr_post(EPS[0], [{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                       "params": [hex(first["block"]), False]}], timeout=30)
                ts = int(r[0]["result"]["timestamp"], 16)
                first["wib"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts + 7*3600))
            except Exception as e:
                first["wib"] = f"ts-err {e}"
        print(f"OUPE first-mint chunk {frm}-{to}: {len(logs)} logs", flush=True)
    except Exception as e:
        print(f"OUPE first-mint chunk {frm}-{to} ERR: {e}", flush=True)
        break
    frm = to + 1
out["oupe_first_mint"] = first
print("OUPE FIRST MINT:", json.dumps(first), flush=True)

with open(f"{BASE}/run-{TS}-oupe-triage.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("WROTE run-%s-oupe-triage.json" % TS, flush=True)
