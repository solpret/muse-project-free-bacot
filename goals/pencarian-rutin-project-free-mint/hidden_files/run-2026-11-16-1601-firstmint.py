#!/usr/bin/env python3
"""First-mint verification + string-view decode for free-mint-search run 2026-11-16 16:01 WIB.
Volta Gent + Punch Card: find earliest Transfer-from-zero via public BSC RPC eth_getLogs,
newest-first in 2000-block windows (bounded: max 40000 blocks back). Also decode
HARBOR website(), HEXCOVEN contractURI(), Punch contractURI() strings.
Read-only; writes run-2026-11-16-1601-firstmint2.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=90):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def rpc_call(method, params):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=90)
            if isinstance(r, dict) and "result" in r and r["result"] is not None:
                return r["result"], ep
        except Exception as e:
            continue
    return None, None
def get_logs(addr, frm, to):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                              "params": [{"address": addr, "fromBlock": hex(frm), "toBlock": hex(to),
                                          "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=90)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                return r["result"], ep
            if isinstance(r, dict) and "error" in r:
                last_err = "ERR:" + str(r["error"])[:120]
                continue
        except Exception as e:
            continue
    return ("ERR:" + last_err) if 'last_err' in dir() else None, None

head_hex, _ = rpc_call("eth_blockNumber", [])
head = int(head_hex, 16)
print("head:", head, flush=True)

def first_mint(addr, name, max_back=40000, window=500):
    """Newest-first window scan; returns (first_block, first_tx, n_calls, note)."""
    calls = 0
    end = head
    first_block = None
    while end > head - max_back:
        frm = max(end - window + 1, head - max_back)
        logs, ep = get_logs(addr, frm, end)
        calls += 1
        if logs is None:
            return None, None, calls, f"getLogs FAILED all endpoints window {frm}-{end}"
        if isinstance(logs, str):
            return None, None, calls, f"getLogs error window {frm}-{end}: {logs}"
        if not logs:
            # no mints in this window; first mint is in a NEWER window already scanned
            break
        # mints found in this window; record oldest block in window, keep scanning older
        oldest = min(int(l["blockNumber"], 16) for l in logs)
        first_block = oldest
        print(f"  {name}: window {frm}-{end} -> {len(logs)} mint logs, oldest block {oldest}", flush=True)
        end = frm - 1
    if first_block is None:
        return None, None, calls, f"no mint logs in last {max_back} blocks (or scan incomplete)"
    # narrow: find the exact first log in the window containing first_block
    logs, ep = get_logs(addr, first_block, first_block)
    calls += 1
    if isinstance(logs, list) and logs:
        tx = logs[0]["transactionHash"]
        return first_block, tx, calls, "ok"
    return first_block, None, calls, "first-block re-read empty"

def block_ts(blk):
    r, _ = rpc_call("eth_getBlockByNumber", [hex(blk), False])
    if r:
        return int(r["timestamp"], 16)
    return None

def decode_string(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"<decode fail: {e}>"

out = {"head": head, "started_wib": "2026-11-16T16:01+07:00"}
for name, addr in (("Volta Gent", "0x2703a2be75e0c470d83573badc6a1b1b86d1871e"),
                   ("Punch Card", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4")):
    print(f"{name} first-mint scan...", flush=True)
    blk, tx, calls, note = first_mint(addr, name)
    ts = block_ts(blk) if blk else None
    out[name] = {"first_mint_block": blk, "first_mint_tx": tx, "first_mint_ts": ts,
                 "calls": calls, "note": note}
    print(f"  -> {name}: block={blk} tx={tx} ts={ts} calls={calls} note={note}", flush=True)

# string views
for name, addr, fn in (("HARBOR", "0xa5844f0539e289c9a477672818ee263ef862b517", "website()"),
                       ("HEXCOVEN", "0xd3d5d57e4942cedcb6864c1dce1e9808544dd30d", "contractURI()"),
                       ("Punch Card", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4", "contractURI()")):
    data = sel(fn)
    r, ep = rpc_call("eth_call", [{"to": addr, "data": data}, "latest"])
    val = decode_string(r) if r else None
    out.setdefault("strings", {})[name] = val
    print(f"{name} {fn} -> {val}", flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-16-1601-firstmint2.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
