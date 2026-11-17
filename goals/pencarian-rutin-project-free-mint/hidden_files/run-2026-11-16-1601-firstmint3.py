#!/usr/bin/env python3
"""First-mint verification v3 for free-mint-search run 2026-11-16 16:01 WIB.
Volta Gent + Punch Card: earliest Transfer-from-zero via public BSC RPC eth_getLogs,
newest-first in 500-block windows, 3s pacing, retry-on-rate-limit (max 3 tries/window),
endpoint rotation. Progress saved incrementally to run-2026-11-16-1601-firstmint4.json.
Read-only. No preview/mint."""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/",
       "https://rpc.ankr.com/bsc", "https://binance.llamarpc.com/",
       "https://bsc-dataseed3.bnbchain.org/", "https://bsc-dataseed4.bnbchain.org/",
       "https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed2.defibit.io/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
t0 = time.time()
OUTF = BASE + "run-2026-11-16-1601-firstmint4.json"

def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def rpc_one(method, params):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=60)
            if isinstance(r, dict) and r.get("result") is not None:
                return r["result"]
        except Exception:
            continue
    return None
def get_logs(addr, frm, to, tries=3):
    last_err = None
    for attempt in range(tries):
        ep = EPS[(attempt) % len(EPS)]
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                              "params": [{"address": addr, "fromBlock": hex(frm), "toBlock": hex(to),
                                          "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                return r["result"], ep
            last_err = str(r.get("error", r))[:150]
        except Exception as e:
            last_err = str(e)[:150]
        time.sleep(4)
    return ("ERR:" + (last_err or "?")), None

head = int(rpc_one("eth_blockNumber", []), 16)
print("head:", head, flush=True)
out = {"head": head, "started_wib": "2026-11-16T16:01+07:00"}

def scan(name, addr, max_back=40000, window=500):
    end = head
    first_block = None
    scanned_windows = 0
    deepest_empty = None
    while end > head - max_back:
        frm = max(end - window + 1, head - max_back)
        logs, ep = get_logs(addr, frm, end)
        scanned_windows += 1
        if isinstance(logs, str):
            out[name] = {"status": "incomplete-rate-limit", "first_mint_block": first_block,
                         "deepest_empty_window": deepest_empty, "scanned_windows": scanned_windows,
                         "note": f"stopped at window {frm}-{end}: {logs}"}
            json.dump(out, open(OUTF, "w"), indent=1)
            print(f"  {name}: STOP window {frm}-{end}: {logs}", flush=True)
            return
        if not logs:
            deepest_empty = [frm, end]
            print(f"  {name}: window {frm}-{end} empty -> first mint is newer than {frm}", flush=True)
            break
        oldest = min(int(l["blockNumber"], 16) for l in logs)
        first_block = oldest
        print(f"  {name}: window {frm}-{end} -> {len(logs)} mints, oldest {oldest}", flush=True)
        end = frm - 1
        time.sleep(3)
    if first_block is None and deepest_empty is None:
        out[name] = {"status": "incomplete-no-mints-found", "scanned_windows": scanned_windows,
                     "note": f"no mint logs in last {max_back} blocks scanned"}
    elif first_block is not None:
        # exact first log in first_block
        logs, ep = get_logs(addr, first_block, first_block)
        tx = logs[0]["transactionHash"] if isinstance(logs, list) and logs else None
        ts_hex = rpc_one("eth_getBlockByNumber", [hex(first_block), False])
        ts = int(ts_hex["timestamp"], 16) if ts_hex else None
        out[name] = {"status": "verified", "first_mint_block": first_block,
                     "first_mint_tx": tx, "first_mint_ts": ts,
                     "scanned_windows": scanned_windows, "note": "ok"}
        print(f"  {name}: FIRST MINT block {first_block} tx {tx} ts {ts}", flush=True)
    else:
        out[name] = {"status": "incomplete", "first_mint_block": None,
                     "deepest_empty_window": deepest_empty, "scanned_windows": scanned_windows,
                     "note": "scan ended without finding first mint"}
    json.dump(out, open(OUTF, "w"), indent=1)

scan("Volta Gent", "0x2703a2be75e0c470d83573badc6a1b1b86d1871e")
scan("Punch Card", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4")
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(OUTF, "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
