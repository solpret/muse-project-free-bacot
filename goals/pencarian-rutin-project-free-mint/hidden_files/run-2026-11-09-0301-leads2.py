#!/usr/bin/env python3
"""Lean verification of 3 Boltbook leads (run 0301, v2 with retries).
OnFinality single eth_call (dataseeds down; batches 429; proxy flaps, so
every call retries). Ankr getLogs first-mint + Sourcify ABI via curl.
Writes JSON per contract as it completes; a failed view is None (UNVERIFIED),
never zero."""
import json, sys, time, subprocess, urllib.request, urllib.error
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

def post_rpc(method, params, timeout=25, attempts=3):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(EP, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.load(r)
            time.sleep(3.5)
            if d.get("error"):
                return None
            return d.get("result")
        except Exception as e:
            last = e
            print(f"  rpc {method} attempt {i+1} fail: {str(e)[:90]}", flush=True)
            time.sleep(6)
    print(f"  rpc {method} FAILED after {attempts} attempts: {str(last)[:90]}", flush=True)
    return None

def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None

def call_view(addr, sig, arg=None):
    data = sel(sig)
    if arg == "user":
        data += enc(USER)
    elif arg is not None:
        data += format(int(arg), "064x")
    return to_int(post_rpc("eth_call", [{"to": addr, "data": data}, "latest"]))

def call_addr(addr, sig):
    raw = post_rpc("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])
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

head_raw = post_rpc("eth_blockNumber", [], attempts=5)
head = int(head_raw, 16) if head_raw else None
print("HEAD (onfinality):", head, flush=True)
if head is None:
    print("HEAD UNAVAILABLE - first-mint walkback skipped, views still attempted", flush=True)

out = {}
try:
    out = json.load(open(f"{BASE}/run-2026-11-09-0301-leads.json"))
except Exception:
    out = {}
for name, addr, views in TARGETS:
    if name in out and out[name].get("done"):
        print(f"== {name}: already done, skip ==", flush=True)
        continue
    print(f"== {name} {addr} ==", flush=True)
    e = out.get(name, {"address": addr})
    for sig in views:
        base = sig.split("(")[0]
        key = base + "_user" if "(address" in sig else base
        if key in e and e[key] is not None:
            continue
        if sig.startswith("freeOf") or sig.startswith("costOf"):
            data = sel(sig) + enc(USER) + format(1, "064x")
            val = to_int(post_rpc("eth_call", [{"to": addr, "data": data}, "latest"]))
            e[key] = val
        else:
            arg = "user" if "(address" in sig else None
            e[key] = call_view(addr, sig, arg)
        print(f"  {sig} -> {e[key]}", flush=True)
        json.dump(out | {name: e}, open(f"{BASE}/run-2026-11-09-0301-leads.json", "w"), indent=1)
    if "agentIds" not in e:
        e["agentIds"] = call_addr(addr, "agentIds()")
    if "owner" not in e:
        e["owner"] = call_addr(addr, "owner()")
    print("  agentIds() ->", e["agentIds"], "| registry match:", (e["agentIds"] or "").lower() == REGISTRY.lower(), flush=True)
    print("  owner() ->", e["owner"], flush=True)
    if "sourcify" not in e:
        e["sourcify"] = sourcify_abi(addr)
        print("  sourcify verified:", e["sourcify"].get("verified"), "fns:", len(e["sourcify"].get("fns", [])), flush=True)
    if head and "first_mint_block" not in e:
        fb, nlogs = first_mint(addr, head)
        e["first_mint_block"] = fb
        e["first_mint_window_logs"] = nlogs
        print("  first mint block:", fb, flush=True)
        if fb:
            ts_raw = post_rpc("eth_getBlockByNumber", [hex(fb), False], attempts=3)
            ts = None
            if ts_raw and isinstance(ts_raw, dict):
                ts = to_int(ts_raw.get("timestamp"))
            e["first_mint_ts"] = ts
            if ts:
                e["first_mint_wib"] = datetime.fromtimestamp(ts, WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
                print("  first mint time:", e["first_mint_wib"], flush=True)
    e["done"] = True
    out[name] = e
    json.dump(out, open(f"{BASE}/run-2026-11-09-0301-leads.json", "w"), indent=1)
    print(f"  saved {name}", flush=True)
print("DONE")
