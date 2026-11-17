#!/usr/bin/env python3
"""Verify3 run 2026-11-09 0631 WIB — split-batch reads (2 batches x ~19 calls,
timeout 40s; the 37-call single batch in verify2 timed out on every endpoint).
Plus first-mint extension for AgenticGangsterNFT (no mints in [132440000, head]).
Read-only; writes run-2026-11-09-0631-verify3.json only.
"""
import json, subprocess, sys, datetime
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

def post_rpc(ep, payload, timeout=40):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def block_ts(block):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(block), False]}, timeout=40)
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
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=40)
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

def run_batch(addr, specs, timeout=40):
    """specs: list of (key, data, kind). One batch per endpoint attempt."""
    calls = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
              "params": [{"to": addr, "data": data}, "latest"]} for i, (_, data, _) in enumerate(specs)]
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=timeout)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, (key, _, kind) in zip(res, specs):
                if not isinstance(item, dict) or "error" in item or item.get("result") is None:
                    outd[key] = None; continue
                r = item.get("result")
                if kind == "int": outd[key] = to_int(r)
                elif kind == "addr":
                    outd[key] = ("0x" + r[-40:]) if isinstance(r, str) and len(r) >= 42 else None
                elif kind == "str": outd[key] = decode_str(r)
                else: outd[key] = r
            return outd, True
        except Exception:
            continue
    return {}, False

def read_contract(name, addr):
    specs1, specs2 = [], []
    for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                "freeLeft()", "FREE_CAP()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
                "mintStart()", "mintEnd()", "remainingFree()", "freeCount()", "paidMinted()",
                "paidMintedCount()", "totalPaid()", "FREE_PER_WALLET()", "freePerWallet()"]:
        specs1.append((sig.split("(")[0], sel(sig), "int"))
    for sig in ["balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
                "freeMintedBy(address)", "mintedBy(address)", "claimedFree(address)",
                "mintedPerWallet(address)", "freeFor(address)"]:
        specs1.append((sig.split("(")[0] + "_user", sel(sig) + enc(USER), "int"))
    for sig in ["quote(address,uint256)", "costOf(address,uint256)"]:
        specs2.append((sig.split("(")[0] + "_user1", sel(sig) + enc(USER) + enc_u(1), "int"))
    for sig in ["owner()", "agentIdRegistry()", "agentRegistry()", "agentId()", "AGENT_ID()",
                "payout()", "coinContract()"]:
        specs2.append((sig.split("(")[0], sel(sig), "addr"))
    for sig in ["name()", "symbol()"]:
        specs2.append((sig.split("(")[0], sel(sig), "str"))
    outd, ok1 = run_batch(addr, specs1)
    outd2, ok2 = run_batch(addr, specs2)
    outd.update(outd2)
    outd["_batch_ok"] = ok1 and ok2
    return outd

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
TARGETS = {
  "SakuraNFT": "0xE56fD19a19E684b94db1Dd3c81896736E3631D47",
  "AgenticGangsterNFT": "0x0A2a07eF09DD7D83E2312476F0588aBaA3E34Ce3",
  "BAO-NFT": "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354",
  "GLOOP": "0x183cbb52b3c7bcb2433d50de0add99b59f4de4fe",
  "ShadowSquad": "0x0bc496BC51D14ae6C4A7003B05061323d4De9206",
  "MONEY": "0x085a493ac880188a69ad38449f505dA9E730C50B",
  "BHTB-sale": "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
  "AgentGrid-sale": "0x651302C0043040D48EaAF85605E12F0549aD6D89",
}
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

# AgenticGangsterNFT: no mints in [132440000, head]; probe 48h window [132151777, 132440000]
print("first-mint AgenticGangsterNFT (48h window)", flush=True)
out["first_mint"] = {"AgenticGangsterNFT_48h": first_mint(TARGETS["AgenticGangsterNFT"], 132151777, 132440000)}
print(" ->", out["first_mint"]["AgenticGangsterNFT_48h"], flush=True)

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

json.dump(out, open(f"{HF}/run-2026-11-09-0631-verify3.json", "w"), indent=1)
print("VERIFY3 DONE", flush=True)
