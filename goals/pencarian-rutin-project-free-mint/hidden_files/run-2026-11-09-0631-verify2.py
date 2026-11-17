#!/usr/bin/env python3
"""Verify2 run 2026-11-09 0631 WIB — LEAN batched reads (one JSON-RPC batch per
contract, curl transport, ThreadPoolExecutor), plus Ankr first-mint search.
Read-only; writes run-2026-11-09-0631-verify2.json only.
Fixes verify.py: sequential per-view calls were far too slow under dataseed
latency (killed mid-run with no output).
"""
import json, subprocess, sys, datetime, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
from concurrent.futures import ThreadPoolExecutor

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

def decode_str(hexstr):
    try:
        if not isinstance(hexstr, str) or len(hexstr) < 130: return None
        raw = bytes.fromhex(hexstr[2:])
        ln = int.from_bytes(raw[64:96], "big")
        if 0 < ln < 100:
            return raw[96:96 + ln].decode("utf-8", "replace")
    except Exception:
        pass
    return None

def read_contract(name, addr):
    """One batched eth_call per endpoint attempt. Returns dict of decoded values."""
    calls, keys, kinds = [], [], []
    def add(key, sig, arg=None, kind="int"):
        data = sel(sig)
        if arg == "USER": data += enc(USER)
        elif arg == "USER1":
            data += enc(USER) + enc_u(1)
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key); kinds.append(kind)
    for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                "freeLeft()", "FREE_CAP()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
                "mintStart()", "mintEnd()", "remainingFree()", "freeCount()", "paidMinted()",
                "paidMintedCount()", "totalPaid()", "FREE_PER_WALLET()", "freePerWallet()"]:
        add(sig.split("(")[0], sig)
    for sig in ["balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
                "freeMintedBy(address)", "mintedBy(address)", "claimedFree(address)",
                "mintedPerWallet(address)", "freeFor(address)"]:
        add(sig.split("(")[0] + "_user", sig, arg="USER")
    for sig in ["quote(address,uint256)", "costOf(address,uint256)"]:
        add(sig.split("(")[0] + "_user1", sig, arg="USER1")
    for sig in ["owner()", "agentIdRegistry()", "agentRegistry()", "agentId()", "AGENT_ID()",
                "payout()", "coinContract()"]:
        add(sig.split("(")[0], sig, kind="addr")
    for sig in ["name()", "symbol()"]:
        add(sig.split("(")[0], sig, kind="str")
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key, kind in zip(res, keys, kinds):
                if not isinstance(item, dict) or "error" in item or item.get("result") is None:
                    outd[key] = None; continue
                r = item.get("result")
                if kind == "int": outd[key] = to_int(r)
                elif kind == "addr":
                    outd[key] = ("0x" + r[-40:]) if isinstance(r, str) and len(r) >= 42 else None
                elif kind == "str": outd[key] = decode_str(r)
                else: outd[key] = r
            outd["_batch_ok"] = True
            return outd
        except Exception:
            continue
    return {"_batch_ok": False}

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
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
def tc_addr(nm):
    v = snap.get("track_c", {}).get(nm)
    if isinstance(v, dict): return v.get("address")
    return None
TARGETS = {
  "SakuraNFT": "0xE56fD19a19E684b94db1Dd3c81896736E3631D47",
  "AgenticGangsterNFT": "0x0A2a07eF09DD7D83E2312476F0588aBaA3E34Ce3",
  "BAO-NFT": "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354",
  "GLOOP": "0x183cbb52b3c7bcb2433d50de0add99b59f4de4fe",
  "ShadowSquad": "0x0bc496BC51D14ae6C4A7003B05061323d4De9206",
  "MONEY": "0x085a493ac880188a69ad38449f505dA9E730C50B",
}
for nm in ("BHTB", "AgentGrid"):
    a = tc_addr(nm)
    print("track_c", nm, "->", a, flush=True)
    if a: TARGETS[nm] = a
print("TARGETS:", TARGETS, flush=True)

out = {"run": TS, "head": HEAD, "contracts": {}}
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(read_contract, nm, ad): nm for nm, ad in TARGETS.items()}
    for f in futs:
        nm = futs[f]
        try:
            d = f.result()
        except Exception as e:
            d = {"_batch_ok": False, "error": str(e)[:200]}
        d["address"] = TARGETS[nm]
        out["contracts"][nm] = d
        print(nm, {k: v for k, v in d.items() if v is not None}, flush=True)

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
out["discard_check"] = {}
for name, addr in TARGETS.items():
    o = out["contracts"][name].get("owner")
    out["discard_check"][name] = {"owner": o, "in_discards": (o.lower() in owners) if o else None}
    print("discard", name, o, out["discard_check"][name]["in_discards"], flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0631-verify2.json", "w"), indent=1)
print("VERIFY2 DONE", flush=True)
