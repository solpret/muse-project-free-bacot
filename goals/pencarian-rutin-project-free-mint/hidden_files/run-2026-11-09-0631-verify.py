#!/usr/bin/env python3
"""Verify run 2026-11-09 0631 WIB — on-chain reads + first-mint search for
discovery/scan findings. Read-only; writes run-2026-11-09-0631-verify.json only.
Targets:
 - SakuraNFT 0xE56fD19a19E684b94db1Dd3c81896736E3631D47 (Sourcify agent-shaped)
 - AgenticGangsterNFT 0x0A2a07eF09DD7D83E2312476F0588aBaA3E34Ce3 (Sourcify agent-shaped)
 - BAO-NFT 0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354 (Boltbook radar post)
 - GLOOP 0x183cbb52b3c7bcb2433d50de0add99b59f4de4fe (sold-out check, Boltbook)
 - BHTB track_c freeUsed fresh + AgentGrid free views fresh
 - ShadowSquad 0x0bc496BC51D14ae6C4A7003B05061323d4De9206: freeClaimed()/totalSupply/totalMinted + per-user views
 - MONEY 0x085a493ac880188a69ad38449f505dA9E730C50B: fresh totals + per-user view attempts
First-mint: Ankr getLogs binary search (Transfer from zero), block timestamp via
dataseed eth_getBlockByNumber (NEVER Ankr for timestamps).
"""
import json, subprocess, sys, datetime, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0631"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def block_ts(block):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(block), False]}, timeout=25)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                return int(res["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def wib(ts):
    if ts is None: return None
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

def head_block():
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            if isinstance(res, dict) and res.get("result"):
                return int(res["result"], 16)
        except Exception:
            continue
    return None

def eth_call(addr, sig, arg=None):
    """Single eth_call; arg = address str or int (uint256). Returns int or None."""
    data = sel(sig)
    if arg is not None:
        data += enc(arg) if isinstance(arg, str) else enc_u(arg)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(res, dict) and "result" in res and res.get("result") not in (None, "0x"):
                return to_int(res["result"])
            if isinstance(res, dict) and res.get("result") == "0x":
                return 0
        except Exception:
            continue
    return None

def eth_call_addr(addr, sig):
    """eth_call returning an address (or None)."""
    data = sel(sig)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(res, dict) and isinstance(res.get("result"), str) and len(res["result"]) >= 42:
                v = "0x" + res["result"][-40:]
                return v if v != "0x" + "00" * 20 else "0x0000000000000000000000000000000000000000"
        except Exception:
            continue
    return None

def eth_call_str(addr, sig):
    """eth_call returning a string (name/symbol); best-effort decode."""
    data = sel(sig)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if isinstance(r, str) and len(r) > 130:
                raw = bytes.fromhex(r[2:])
                ln = int.from_bytes(raw[64:96], "big")
                if 0 < ln < 100:
                    return raw[96:96 + ln].decode("utf-8", "replace")
        except Exception:
            continue
    return None

def any_mint(addr, frm, to):
    try:
        res = ankr_post("ankr_getLogs", {"blockchain": "bsc", "address": addr,
            "fromBlock": str(frm), "toBlock": str(to),
            "topics": [TRANSFER, ZERO_TOPIC], "pageSize": 1000}, timeout=55)
        return len(res.get("result", {}).get("logs", [])) > 0, None
    except Exception as e:
        return None, str(e)[:150]

def first_mint(addr, lo, hi):
    ok, err = any_mint(addr, lo, hi)
    print(f"  first-mint probe [{lo},{hi}]: {ok} {err or ''}", flush=True)
    if ok is None: return {"first_mint_block": None, "error": err}
    if not ok: return {"first_mint_block": None, "no_mint_in_range": [lo, hi]}
    while lo < hi:
        mid = (lo + hi) // 2
        ok2, err2 = any_mint(addr, lo, mid)
        if ok2 is None:
            return {"first_mint_block": None, "error": err2, "lo": lo, "hi": hi}
        if ok2: hi = mid
        else: lo = mid + 1
    ts = block_ts(lo)
    return {"first_mint_block": lo, "timestamp": ts, "wib": wib(ts)}

HEAD = head_block()
print("HEAD:", HEAD, flush=True)
out = {"run": TS, "head": HEAD, "contracts": {}}

VIEWS_N0 = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
            "freeLeft()", "FREE_CAP()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
            "mintStart()", "mintEnd()", "remainingFree()", "freeCount()", "paidMinted()",
            "paidMintedCount()", "totalPaid()", "FREE_PER_WALLET()", "freePerWallet()"]
VIEWS_ADDR = ["balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
              "freeMintedBy(address)", "mintedBy(address)", "claimedFree(address)",
              "mintedPerWallet(address)", "freeFor(address)"]
VIEWS_U = ["quote(address,uint256)", "costOf(address,uint256)"]
ADDR_VIEWS = ["owner()", "agentIdRegistry()", "agentRegistry()", "agentId()", "AGENT_ID()",
              "payout()", "coinContract()"]
STR_VIEWS = ["name()", "symbol()"]

TARGETS = {
  "SakuraNFT": "0xE56fD19a19E684b94db1Dd3c81896736E3631D47",
  "AgenticGangsterNFT": "0x0A2a07eF09DD7D83E2312476F0588aBaA3E34Ce3",
  "BAO-NFT": "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354",
  "GLOOP": "0x183cbb52b3c7bcb2433d50de0add99b59f4de4fe",
  "ShadowSquad": "0x0bc496BC51D14ae6C4A7003B05061323d4De9206",
  "MONEY": "0x085a493ac880188a69ad38449f505dA9E730C50B",
}
# BHTB + AgentGrid addresses from snapshot track_c
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
for nm in ("BHTB", "AgentGrid"):
    a = snap.get("track_c", {}).get(nm, {}).get("address") if isinstance(snap.get("track_c", {}).get(nm), dict) else None
    if a: TARGETS[nm] = a
print("TARGETS:", TARGETS, flush=True)

for name, addr in TARGETS.items():
    d = {"address": addr}
    for sig in VIEWS_N0:
        d[sig.split("(")[0]] = eth_call(addr, sig)
    for sig in VIEWS_ADDR:
        d[sig.split("(")[0] + "_user"] = eth_call(addr, sig, USER)
    for sig in VIEWS_U:
        d[sig.split("(")[0] + "_user1"] = eth_call(addr, sig, None) if False else None
    # quote(user,1): two-arg call built manually
    for sig in ("quote(address,uint256)", "costOf(address,uint256)"):
        data = sel(sig) + enc(USER) + enc_u(1)
        v = None
        for ep in EPS:
            try:
                res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                    "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
                if isinstance(res, dict) and res.get("result") not in (None, "0x"):
                    v = to_int(res["result"]); break
            except Exception:
                continue
        d[sig.split("(")[0] + "_user1"] = v
    for sig in ADDR_VIEWS:
        d[sig.split("(")[0]] = eth_call_addr(addr, sig)
    for sig in STR_VIEWS:
        d[sig.split("(")[0]] = eth_call_str(addr, sig)
    out["contracts"][name] = d
    print(name, {k: v for k, v in d.items() if v is not None}, flush=True)

# first-mint searches (only where first mint not already verified this run)
FM = {
  "SakuraNFT": (132440000, HEAD),
  "AgenticGangsterNFT": (132440000, HEAD),
  "BAO-NFT": (131900000, HEAD),
}
out["first_mint"] = {}
for name, (lo, hi) in FM.items():
    print("first-mint", name, flush=True)
    out["first_mint"][name] = first_mint(TARGETS[name], lo, hi)
    print(" ->", out["first_mint"][name], flush=True)

# owner vs discards
disc = json.load(open(f"{HF}/same-owner-discards.json"))
owners = set()
if isinstance(disc, dict):
    for v in disc.values():
        if isinstance(v, dict):
            o = v.get("owner") or v.get("owner_address")
            if o: owners.add(o.lower())
        elif isinstance(v, str):
            owners.add(v.lower())
elif isinstance(disc, list):
    for v in disc:
        if isinstance(v, dict):
            o = v.get("owner") or v.get("owner_address") or v.get("address")
            if o: owners.add(o.lower())
        elif isinstance(v, str):
            owners.add(v.lower())
print("discard owners loaded:", len(owners), flush=True)
out["discard_check"] = {}
for name, addr in TARGETS.items():
    o = out["contracts"][name].get("owner")
    out["discard_check"][name] = {"owner": o, "in_discards": (o.lower() in owners) if o else None}
    print("discard", name, o, out["discard_check"][name]["in_discards"], flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0631-verify.json", "w"), indent=1)
print("VERIFY DONE", flush=True)
