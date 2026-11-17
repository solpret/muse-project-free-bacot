#!/usr/bin/env python3
"""Follow-up run 1034 for Bot Fighters 0x58a704... (S1 PASS, 3/500 free):
1) first-mint time via eth_getLogs (small range, Transfer from zero)
2) website gate evidence: fetch botfighters.pages.dev + docs, grep exact contract
3) shape-check 2 new Boltbook ZH addresses.
Read-only. Writes hot-leg-2026-11-11-1034-followup.json + site fetch files."""
import json, time, subprocess, re, base64
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
CTR = "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb"
EPS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"

def curl(url, timeout=20, post=None, ep=None):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data", post]
    cmd.append(ep or url)
    pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return pr.stdout, pr.returncode

def rpc(ep, method, params, timeout=25):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    out, rc = curl(None, timeout, post=payload, ep=ep)
    return json.loads(out)

out = {"run": "2026-11-11 10:34 WIB follow-up", "contract": CTR}

# --- 1) first mint via eth_getLogs ---
block_now = None
for ep in EPS:
    try:
        r = rpc(ep, "eth_blockNumber", [])
        block_now = int(r["result"], 16)
        break
    except Exception:
        continue
out["block_now"] = block_now
first_mint = None
logs_err = None
if block_now:
    # verified 10:26:33 WIB; ~15 min before now -> ~300 blocks back; pad to 1200 blocks
    frm = block_now - 1200
    for ep in EPS:
        try:
            r = rpc(ep, "eth_getLogs", [{"fromBlock": hex(frm), "toBlock": "latest",
                                         "address": CTR, "topics": [TRANSFER, ZERO_TOPIC]}],
                    timeout=30)
            if "error" in r:
                logs_err = f"{ep}: {r['error']}"
                continue
            logs = r.get("result", [])
            if logs:
                first = logs[0]
                bn = int(first["blockNumber"], 16)
                # block timestamp
                br = rpc(ep, "eth_getBlockByNumber", [hex(bn), False], timeout=25)
                ts = int(br["result"]["timestamp"], 16)
                dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=7)))
                first_mint = {"block": bn, "tx": first.get("transactionHash"),
                              "time_wib": dt.strftime("%Y-%m-%d %H:%M:%S"),
                              "ts": ts, "log_count_in_range": len(logs)}
            else:
                first_mint = {"none_in_range": True, "from_block": frm}
            logs_err = None
            break
        except Exception as e:
            logs_err = f"{ep}: {type(e).__name__}: {e}"
out["first_mint"] = first_mint
out["logs_error"] = logs_err

# --- 2) website gate evidence ---
site = {}
for path in ["", "llms.txt", "skill.md", "launch.json"]:
    url = f"https://botfighters.pages.dev/{path}"
    try:
        body, rc = curl(url, 20)
        fn = BASE + f"botfighters-1034-{path.replace('/', '_') or 'index'}.html"
        open(fn, "w").write(body)
        site[path or "index"] = {"bytes": len(body), "rc": rc,
                                 "prints_contract": "58a704" in body.lower(),
                                 "has_free": "free" in body.lower(),
                                 "snippet_contract": [m for m in re.findall(r".{0,60}58a704.{0,60}", body, re.I)][:2]}
    except Exception as e:
        site[path or "index"] = {"error": f"{type(e).__name__}: {e}"}
out["website"] = site

# --- 3) shape-check 2 new Boltbook ZH addresses ---
REG = "0x60b9262456de011f7d15a54cdD8c48bAaa8B022F".lower()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
              "freeMinted","freePoolRemaining"]
def shape_check(addr):
    try:
        body, rc = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 20)
        d = json.loads(body)
        abi = d.get("abi") or (d.get("contract", {}) or {}).get("abi")
        if not abi:
            return {"error": "no-abi-in-response"}
        src = json.dumps(d).lower()
        fns = {f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"}
        has_mint = any(n and ("mint" in n.lower()) for n in fns)
        has_quote = any(n and ("quote" in n.lower() or "cost" in n.lower()) for n in fns)
        free_hits = [v for v in FREE_VIEWS if v in fns]
        agent = REG in src or "agentgate" in src or "agentidregistry" in src
        s1 = bool(has_mint and has_quote and free_hits and agent)
        tokenish = all(x in fns for x in ("name","symbol","decimals","totalSupply"))
        s2 = bool(tokenish and ("mintFree" in fns) and
                  (("freeClaimed" in fns and "freeMinted" in fns) and
                   ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns)) and agent)
        early = bool(agent and (has_mint or free_hits))
        return {"S1": s1, "S2": s2, "early_shape": early, "mint": has_mint,
                "quote": has_quote, "free": free_hits, "agent": agent,
                "token": tokenish, "fns": len(fns)}
    except Exception as e:
        return {"error": f"{type(e).__name__}"}

bb_new = ["0x70ab28d6d1569d35b6dcb58d0b2da0363303c9f5",
          "0xddf252ad1be2c89b69c2b068fc378daa952ba7f1"]
bb_shapes = {a: shape_check(a) for a in bb_new}
out["boltbook_zh_shape"] = bb_shapes
out["duration_sec"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-2026-11-11-1034-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
