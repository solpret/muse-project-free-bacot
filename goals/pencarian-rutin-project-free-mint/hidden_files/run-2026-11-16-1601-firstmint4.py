#!/usr/bin/env python3
"""First-mint bracket scan v4 for free-mint-search run 2026-11-16 16:01 WIB.
Uses ONLY https://bsc-rpc.publicnode.com/ (the one endpoint that answers eth_getLogs
right now; Binance dataseeds rate-limit getLogs -32005). Sparse probes to bracket the
first mint, then linear newest-first 500-block windows inside the bracket.
Read-only. No preview/mint."""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EP = "https://bsc-rpc.publicnode.com/"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
t0 = time.time()
OUTF = BASE + "run-2026-11-16-1601-firstmint4.json"

def post_rpc(payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", EP,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def rpc_one(method, params):
    r = post_rpc({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    return r.get("result") if isinstance(r, dict) else None
def get_logs(addr, frm, to, tries=3):
    last_err = None
    for _ in range(tries):
        try:
            r = post_rpc({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                          "params": [{"address": addr, "fromBlock": hex(frm), "toBlock": hex(to),
                                      "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                return r["result"]
            last_err = str(r.get("error", r))[:150]
        except Exception as e:
            last_err = str(e)[:150]
        time.sleep(5)
    return "ERR:" + (last_err or "?")

head = int(rpc_one("eth_blockNumber", []), 16)
print("head:", head, flush=True)
out = {"head": head, "started_wib": "2026-11-16T16:01+07:00", "endpoint": EP}

def scan(name, addr):
    # sparse probes: 500-block windows ending at head-offset
    probes = [3000, 6000, 12000, 18000, 24000, 36000, 48000]
    res = {}
    for off in probes:
        end = head - off
        frm = end - 499
        logs = get_logs(addr, frm, end)
        if isinstance(logs, str):
            res.setdefault("probes", {})[off] = "ERR:" + logs[:120]
            print(f"  {name} probe -{off} ERR {logs[:100]}", flush=True)
            out[name] = {"status": "incomplete-probe-error", "probes": res["probes"]}
            json.dump(out, open(OUTF, "w"), indent=1)
            return
        res.setdefault("probes", {})[off] = len(logs)
        print(f"  {name} probe -{off} blocks [{frm}-{end}]: {len(logs)} mints", flush=True)
        time.sleep(2)
    # bracket: oldest probe WITH mints, and next older probe WITHOUT (empty)
    with_mints = [o for o in probes if isinstance(res["probes"][o], int) and res["probes"][o] > 0]
    if not with_mints:
        out[name] = {"status": "no-mints-in-probes", "probes": res["probes"],
                     "note": "no mint logs in any probe window up to -48000 blocks"}
        json.dump(out, open(OUTF, "w"), indent=1)
        return
    oldest_with = max(with_mints)
    # linear scan newest-first from head down to (head - oldest_with - 500)
    end = head
    first_block = None
    stop_at = head - oldest_with - 500
    while end > stop_at:
        frm = max(end - 499, stop_at)
        logs = get_logs(addr, frm, end)
        if isinstance(logs, str):
            out[name] = {"status": "incomplete-linear-error", "probes": res["probes"],
                         "first_mint_block": first_block,
                         "note": f"stopped at window {frm}-{end}: {logs[:120]}"}
            json.dump(out, open(OUTF, "w"), indent=1)
            print(f"  {name} linear STOP {frm}-{end}: {logs[:100]}", flush=True)
            return
        if not logs:
            print(f"  {name} linear window {frm}-{end} empty -> first mint newer than {frm}", flush=True)
            break
        oldest = min(int(l["blockNumber"], 16) for l in logs)
        first_block = oldest
        print(f"  {name} linear window {frm}-{end}: {len(logs)} mints, oldest {oldest}", flush=True)
        end = frm - 1
        time.sleep(2)
    if first_block is None:
        out[name] = {"status": "incomplete", "probes": res["probes"],
                     "note": "no first mint found in linear scan"}
    else:
        logs = get_logs(addr, first_block, first_block)
        tx = logs[0]["transactionHash"] if isinstance(logs, list) and logs else None
        blk = rpc_one("eth_getBlockByNumber", [hex(first_block), False])
        ts = int(blk["timestamp"], 16) if blk else None
        out[name] = {"status": "verified", "first_mint_block": first_block,
                     "first_mint_tx": tx, "first_mint_ts": ts, "probes": res["probes"]}
        print(f"  {name}: FIRST MINT block {first_block} tx {tx} ts {ts}", flush=True)
    json.dump(out, open(OUTF, "w"), indent=1)

scan("Volta Gent", "0x2703a2be75e0c470d83573badc6a1b1b86d1871e")
scan("Punch Card", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4")
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(OUTF, "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
