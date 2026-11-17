#!/usr/bin/env python3
"""Leg 3 follow-up for hot-leg 0554: slot/cost + first-mint time for 2 new S1 NFTs."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-16-0554"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
CONTRACTS = ["0x1b8894391a3DcFe7e248C321103265AB52E273e0",
             "0xdb7A8fa53F96cf4744c21BB6c78a2272ec6566e5"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10)
    return json.loads(r.stdout)

out = {"run": "hot-leg 0554 leg3-followup", "contracts": {}}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"

for a in CONTRACTS:
    rec = {}
    leg3 = json.load(open(BASE + f"hot-leg-{TAG}-leg3.json"))["contracts"][a]
    fns = set(leg3["fns"])
    # inspect ABI signatures for cost / mintedBy / quote
    import urllib.request
    try:
        raw = subprocess.run(["curl", "-s", "-m", "15",
                              f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                             capture_output=True, timeout=20).stdout
        abi = json.loads(raw.decode(errors="replace")).get("abi") or []
    except Exception:
        abi = []
    sigs = {}
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") == "function":
            nm = fn.get("name")
            if nm in ("cost", "quote", "mintedBy", "mint", "max_per_wallet", "freeClaimed",
                      "mintFree", "claimFree"):
                sigs[nm] = nm + "(" + ",".join(i.get("type", "") for i in fn.get("inputs", [])) + ")"
    rec["sigs"] = sigs
    calls, meta = [], []
    def add(key, sig, args):
        if sig.split("(")[0] in sigs or sig.split("(")[0].lower() in fns:
            calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                          "params": [{"to": a, "data": build(sig, args)}, "latest"]})
            meta.append(key)
    add("mintedBy_user", "mintedBy(address)", [USER])
    add("cost_user_1", "cost(address,uint256)", [USER, 1])
    add("cost_1", "cost(uint256)", [1])
    add("max_per_wallet", "max_per_wallet()", [])
    add("MAX_PER_WALLET", "MAX_PER_WALLET()", [])
    add("freeClaimed_total", "freeClaimed()", [])
    add("totalSupply", "totalSupply()", [])
    views = {}
    if calls:
        for ep in EPS:
            try:
                res = post_rpc(ep, calls, timeout=60)
                if not isinstance(res, list) or len(res) != len(calls):
                    continue
                for it, key in zip(res, meta):
                    if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                        views[key] = None
                    else:
                        r = it["result"]
                        views[key] = to_int(r[:66]) if len(r) >= 66 else r
                break
            except Exception as e:
                print(a, "ep exc", str(e)[:80], flush=True)
    rec["views"] = views
    # first mint: getLogs Transfer from zero address, fromBlock 0
    logs = None
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                "params": [{"address": a, "fromBlock": "0x0", "toBlock": "latest",
                                            "topics": [TRANSFER, ZERO]}]}, timeout=60)
            if isinstance(res, dict) and isinstance(res.get("result"), list):
                logs = res["result"]
                break
        except Exception as e:
            print(a, "logs exc", str(e)[:80], flush=True)
    if logs is not None:
        rec["n_mint_transfers"] = len(logs)
        if logs:
            first = logs[0]
            rec["first_mint_block"] = int(first["blockNumber"], 16)
            rec["first_mint_tx"] = first["transactionHash"]
            # block timestamp
            for ep in EPS:
                try:
                    b = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                      "params": [first["blockNumber"], False]}, timeout=60)
                    if isinstance(b, dict) and b.get("result"):
                        ts = int(b["result"]["timestamp"], 16)
                        rec["first_mint_ts"] = ts
                        from datetime import datetime, timezone, timedelta
                        rec["first_mint_wib"] = datetime.fromtimestamp(
                            ts, timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
                        break
                except Exception:
                    continue
    else:
        rec["n_mint_transfers"] = None
        rec["logs_error"] = "getLogs failed on all endpoints"
    out["contracts"][a] = rec
    print(a, json.dumps(rec, indent=1), flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-leg3-followup.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"])
