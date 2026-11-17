#!/usr/bin/env python3
"""Lean verification of 3 Boltbook leads (run 0301) via OnFinality single
eth_call (dataseeds down this run; batches 429) + Ankr getLogs first-mint
+ Sourcify ABI via curl. Writes JSON per contract as it completes."""
import json, sys, time, subprocess, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EP = "https://bnb.api.onfinality.io/public"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
WIB = timezone(timedelta(hours=7))

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def eth_call_single(to, data, timeout=25):
    """One eth_call via OnFinality. Returns raw result hex or None."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(EP, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    time.sleep(3.5)  # OnFinality public rate limit: single calls only, spaced
    if d.get("error"):
        return None
    return d.get("result")

def eth_block_ts(blocknum, timeout=25):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                       "params": [hex(blocknum), False]}).encode()
    req = urllib.request.Request(EP, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    time.sleep(3.5)
    b = d.get("result") or {}
    ts = b.get("timestamp")
    return int(ts, 16) if ts else None

def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None

def call_view(addr, sig, arg=None):
    data = sel(sig)
    if arg == "user":
        data += enc(USER)
    elif arg is not None:
        data += format(int(arg), "064x")
    raw = eth_call_single(addr, data)
    return to_int(raw), raw

def call_addr(addr, sig):
    raw = eth_call_single(addr, sel(sig))
    if raw and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def sourcify_abi(addr):
    try:
        out = subprocess.run(["curl", "-s", "-m", "20",
                              f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                              "-H", "User-Agent: Mozilla/5.0"],
                             capture_output=True, text=True, timeout=30)
        d = json.loads(out.stdout)
        abi = d.get("abi") or []
        fns = sorted({f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function" and f.get("name")})
        return {"verified": True, "fns": fns}
    except Exception as e:
        return {"verified": False, "error": str(e)[:120]}

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32

def first_mint(addr, head):
    to_blk = head
    for _ in range(14):
        frm = max(to_blk - 999, 0)
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
                                              "toBlock": hex(to_blk), "pageSize": 1000,
                                              "decodeLogs": False, "address": addr,
                                              "topics": [TRANSFER, ZERO]}, timeout=30)
            logs = body.get("result", {}).get("logs", [])
        except Exception as e:
            print(f"  walkback {frm}-{to_blk} ERROR {e}", flush=True); logs = []
        print(f"  walkback {frm}-{to_blk}: {len(logs)} mint logs", flush=True)
        if logs:
            first = min(logs, key=lambda l: int(l["blockNumber"], 16))
            return int(first["blockNumber"], 16), len(logs)
        to_blk = frm - 1
        if to_blk <= 0:
            break
    return None, 0

TARGETS = [
    ("ALL ACCESS", "0xc3ce00677dad113f5d466d46c8c7b3a227855a5b",
     ["totalSupply()", "MAX_SUPPLY()", "freeLeft()", "freeOf(address,uint256)",
      "mintOpen()", "price()", "costOf(address,uint256)", "mintedBy(address)",
      "balanceOf(address)", "mintsLeft(address)", "MAX_PER_WALLET()", "bogo()"]),
    ("Hexrotta", "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9",
     ["totalSupply()", "MAX_SUPPLY()", "freeClaimed()", "freeMinted()", "freeLeft()",
      "mintOpen()", "price()", "costOf(address,uint256)", "mintedBy(address)",
      "balanceOf(address)", "mintsLeft(address)"]),
    ("AgentPad Pass", "0x01c106835091c09d5c69737631af133530093c89",
     ["totalSupply()", "MAX_SUPPLY()", "freeClaimed()", "freeMinted()", "freeLeft()",
      "mintOpen()", "price()", "costOf(address,uint256)", "mintedBy(address)",
      "balanceOf(address)", "mintsLeft(address)"]),
]

# head via OnFinality single call
body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
req = urllib.request.Request(EP, data=body, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=25) as r:
    head = int(json.load(r)["result"], 16)
print("HEAD (onfinality):", head, flush=True)
time.sleep(3.5)

out = {}
for name, addr, views in TARGETS:
    print(f"== {name} {addr} ==", flush=True)
    e = {"address": addr}
    for sig in views:
        base = sig.split("(")[0]
        arg = None
        if "(address" in sig:
            arg = "user"
            key = base + "_user"
        else:
            key = base
        if sig.startswith("freeOf") or sig.startswith("costOf"):
            # freeOf(address,uint256)/costOf(address,uint256): address + qty=1
            data = sel(sig) + enc(USER) + format(1, "064x")
            raw = eth_call_single(addr, data)
            val = to_int(raw)
            e[key] = val
            print(f"  {sig} -> {val}", flush=True)
            continue
        val, raw = call_view(addr, sig, arg)
        e[key] = val
        print(f"  {sig} -> {val}", flush=True)
    e["agentIds"] = call_addr(addr, "agentIds()")
    e["owner"] = call_addr(addr, "owner()")
    print("  agentIds() ->", e["agentIds"], "| registry match:", (e["agentIds"] or "").lower() == REGISTRY.lower(), flush=True)
    print("  owner() ->", e["owner"], flush=True)
    abi = sourcify_abi(addr)
    e["sourcify"] = abi
    print("  sourcify verified:", abi.get("verified"), "fns:", len(abi.get("fns", [])), flush=True)
    fb, nlogs = first_mint(addr, head)
    e["first_mint_block"] = fb
    e["first_mint_window_logs"] = nlogs
    print("  first mint block:", fb, flush=True)
    if fb:
        ts = eth_block_ts(fb)
        e["first_mint_ts"] = ts
        if ts:
            e["first_mint_wib"] = datetime.fromtimestamp(ts, WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
            print("  first mint time:", e["first_mint_wib"], flush=True)
    out[name] = e
    json.dump(out, open(f"{BASE}/run-2026-11-09-0301-leads.json", "w"), indent=1)
    print(f"  saved {name}", flush=True)
print("DONE")
