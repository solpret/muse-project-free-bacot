#!/usr/bin/env python3
"""Salvage for hot-leg 2026-11-11 21:59 WIB (main script killed by 280s timeout
after legs 1+2; leg 3b+4 never ran). Sequential curl eth_calls only.
(1) Verify new S1 contract 0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C on-chain:
free pool, user slot, age (saleStart/saleEnd), name/symbol.
(2) AGCR 0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc: Boltbook post claims
2,367/2,400 free gone; 07:30 shape-check said agent=False but that used the
case-sensitive legs.py (agentIdRegistry bug, cf. runlog 21:14). Re-check ABI
agent refs case-insensitively; if agent-shaped, read its free state too.
(3) Decision-critical re-reads only: Stampooor + AgentPals + early leads
BUCKET/MOONDRILL/0x2e50/MECHA/CRTSAINTS (small sequential set).
Read-only; writes only hot-leg-run-2026-11-11-2159-salvage.json + runlog."""
import json, subprocess, time
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
STAMP = "2026-11-11-2159"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)

def eth_call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            j = json.loads(r.stdout.decode(errors="replace"))
            if "error" in j: continue
            raw = j.get("result")
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception:
            continue
    return {"error": "all-endpoints-failed"}

def eth_block():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            return int(json.loads(r.stdout.decode(errors="replace"))["result"], 16)
        except Exception:
            continue
    return None

def read_str(addr, sig):
    data = sel(sig)
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            j = json.loads(r.stdout.decode(errors="replace"))
            raw = j.get("result", "")
            if raw and len(raw) >= 130:
                ln = int(raw[66:130], 16)
                hx = raw[130:130 + ln * 2]
                return bytes.fromhex(hx).decode(errors="replace")
            return {"error": "short-return"}
        except Exception:
            continue
    return {"error": "all-endpoints-failed"}

def read_tuple(addr, sig, args=""):
    # returns list of up to 5 uints + bool + string tail as raw; decode first 5 uint slots
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            j = json.loads(r.stdout.decode(errors="replace"))
            raw = j.get("result", "")
            if not raw or raw == "0x": return {"error": "empty-return"}
            vals = []
            hx = raw[2:]
            for i in range(5):
                chunk = hx[i * 64:(i + 1) * 64]
                if len(chunk) < 64: break
                vals.append(int(chunk, 16))
            return {"uints": vals, "raw_tail": raw[2 + 5 * 64:2 + 5 * 64 + 200]}
        except Exception:
            continue
    return {"error": "all-endpoints-failed"}

U = enc_addr(USER)
blk = eth_block()
print("BLOCK", blk, flush=True)

# ---- (1) S1 contract ----
S1 = "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"
s1 = {}
s1["name"] = read_str(S1, "name()")
s1["symbol"] = read_str(S1, "symbol()")
for key, sig, args in [
    ("totalSupply", "totalSupply()", ""), ("totalMinted", "totalMinted()", ""),
    ("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
    ("freeRemaining", "freeRemaining()", ""), ("mintOpen", "mintOpen()", ""),
    ("saleStart", "saleStart()", ""), ("saleEnd", "saleEnd()", ""),
    ("refundOpen", "refundOpen()", ""), ("settled", "settled()", ""),
    ("PRICE", "PRICE()", ""), ("mintPrice", "mintPrice()", ""),
    ("cost", "cost()", ""), ("MAX_SUPPLY", "MAX_SUPPLY()", ""),
    ("freeAvailable_user", "freeAvailable(address)", U),
    ("freeClaimed_user", "freeClaimed(address)", U),
    ("mintedBy_user", "mintedBy(address)", U),
    ("balanceOf_user", "balanceOf(address)", U),
    ("hasAgentId_user", "hasAgentId(address)", U),
    ("AGENT_ID", "AGENT_ID()", ""),
]:
    s1[key] = eth_call(S1, sig, args)
    time.sleep(0.25)
s1["quote_user_1"] = read_tuple(S1, "quote(address,uint256)", U + enc_u(1))
print("S1", json.dumps(s1, indent=1), flush=True)

# ---- (2) AGCR agent-ref re-check ----
agcr = {}
try:
    out = subprocess.run(["curl", "-s", "-m", "20",
                          "https://sourcify.dev/server/v2/contract/56/0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc?fields=abi",
                          ], capture_output=True, timeout=25)
    abi = json.loads(out.stdout.decode(errors="replace")).get("abi", [])
    names = [e["name"] for e in abi if e.get("type") == "function"]
    low = {n.lower() for n in names}
    agcr["fn_count"] = len(names)
    agcr["agent_ref_case_insensitive"] = bool(low & {"agentid", "agent_id", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
    agcr["agent_fns"] = sorted(n for n in names if "agent" in n.lower())
    agcr["free_views"] = sorted(n for n in names if n in {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining", "freeRemaining", "freeSupply", "FREE_SUPPLY", "FREE_SLOTS"})
    agcr["has_mint"] = any(n.lower().startswith("mint") for n in names)
    agcr["has_quote"] = bool(set(names) & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice", "PRICE"})
    agcr["name_fns"] = [n for n in names if n in ("name", "symbol", "mintFree", "freeMint", "mintStart", "saleStart", "openedAt", "mintOpenedAt", "FREE_SLOTS", "FREE_SUPPLY", "firstFreeUsed", "paidMinted", "mintOpen")]
except Exception as e:
    agcr["error"] = f"{type(e).__name__}: {str(e)[:100]}"
print("AGCR-ABI", json.dumps(agcr, indent=1), flush=True)

agcr_state = {}
if agcr.get("agent_ref_case_insensitive"):
    A = "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"
    for key, sig, args in [
        ("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
        ("freeRemaining", "freeRemaining()", ""), ("mintOpen", "mintOpen()", ""),
        ("totalSupply", "totalSupply()", ""), ("totalMinted", "totalMinted()", ""),
        ("freeAvailable_user", "freeAvailable(address)", U),
        ("freeClaimed_user", "freeClaimed(address)", U),
        ("balanceOf_user", "balanceOf(address)", U),
        ("saleStart", "saleStart()", ""), ("mintStart", "mintStart()", ""),
    ]:
        agcr_state[key] = eth_call(A, sig, args)
        time.sleep(0.25)
    print("AGCR-STATE", json.dumps(agcr_state, indent=1), flush=True)

# ---- (3) Decision-critical re-reads ----
ITEMS = {
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459",
               [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
                ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""),
                ("freeAvailable_user", "freeAvailable(address)", U),
                ("balanceOf_user", "balanceOf(address)", U)]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
               [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
                ("hasFreeMinted_user", "hasFreeMinted(address)", U),
                ("balanceOf_user", "balanceOf(address)", U)]),
 "BUCKET": ("0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
            [("totalSupply", "totalSupply()", ""), ("totalFreeCount", "totalFreeCount()", ""),
             ("freeUsed_user", "freeUsed(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "MOONDRILL": ("0x87b354E2014D2e418927A1105dD219A2e7b063b0",
               [("totalSupply", "totalSupply()", ""), ("firstFreeUsed", "firstFreeUsed()", ""),
                ("paidMinted", "paidMinted()", ""), ("mintOpen", "mintOpen()", ""),
                ("balanceOf_user", "balanceOf(address)", U)]),
 "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
            [("totalSupply", "totalSupply()", ""), ("firstFreeUsed", "firstFreeUsed()", ""),
             ("paidMinted", "paidMinted()", ""), ("mintOpen", "mintOpen()", ""),
             ("balanceOf_user", "balanceOf(address)", U)]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
           [("totalMinted", "totalMinted()", ""), ("freeClaimed", "freeClaimed()", ""),
            ("balanceOf_user", "balanceOf(address)", U)]),
 "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
               [("totalSupply", "totalSupply()", ""), ("paidMinted", "paidMinted()", ""),
                ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
}
reread = {}
for name, (addr, calls) in ITEMS.items():
    reread[name] = {}
    for key, sig, args in calls:
        reread[name][key] = eth_call(addr, sig, args)
        time.sleep(0.25)
print("REREAD", json.dumps(reread, indent=1), flush=True)

# Stampooor site gate live
site_gate = {}
for _u in ("https://stampooor.com/packs/", "https://stampooor.com/"):
    try:
        _r = subprocess.run(["curl", "-s", "-m", "15", "-o", "/dev/null", "-w", "%{http_code}:%{size_download}", "-A", "hot-leg/1.0", _u],
                            capture_output=True, timeout=20)
        site_gate[_u] = _r.stdout.decode(errors="replace")
    except Exception as e:
        site_gate[_u] = f"ERROR {type(e).__name__}: {str(e)[:80]}"
print("STAMPOOR-SITE", site_gate, flush=True)

out = {
 "run": "free-mint-hot-leg 2026-11-11 21:59 WIB (salvage: main script killed by 280s timeout after legs 1+2)",
 "started_wib": NOW_ISO,
 "block": blk,
 "leg1_feed_new_s1": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
 "s1_onchain": s1,
 "agcr_abi": agcr,
 "agcr_state": agcr_state,
 "reread": reread,
 "stampooor_site_gate_live": site_gate,
 "elapsed_s": round(time.time() - T0, 1),
}
json.dump(out, open(BASE + f"hot-leg-run-{STAMP}-salvage.json", "w"), indent=1)
print("ELAPSED", round(time.time() - T0, 1))
