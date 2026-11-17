"""Orin Agent — bounded read-only verify (leg 2, run 1801)."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from ankr import ankr_post

ADDR = "0xa04513d85e02e1a1623a985269b3ebd46fa76b98"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def dec(b):
    if isinstance(b, str) and b.startswith("0x"):
        try: return int(b, 16)
        except Exception: return b
    return b

out = {}
for name, sel in [('totalSupply', '0x18160ddd'), ('name', '0x06fdde03'), ('symbol', '0x95d89b41')]:
    try:
        r = race("eth_call", [{"to": ADDR, "data": sel}, "latest"], timeout=10)
        out[name] = r
    except Exception as e:
        out[name] = f"ERR {type(e).__name__}: {e}"
print("CALLS:", json.dumps(out), flush=True)
try:
    head_n = int(race("eth_blockNumber", [], timeout=10), 16)
except Exception as e:
    head_n = None
    print("head ERR", e, flush=True)
print("head:", head_n, flush=True)

def ankr_logs(frm, to, page=1, desc=False):
    params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
              "address": [ADDR], "topics": [TRANSFER, ZERO], "pageSize": page, "descOrder": desc}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    return (body.get("result", {}) or {}).get("logs", []) or []

if head_n:
    # recent mints: last 2000 blocks
    try:
        recent = ankr_logs(head_n - 2000, head_n, page=5, desc=True)
        print("recent mints last 2000 blocks:", len(recent),
              [int(l["blockNumber"], 16) for l in recent], flush=True)
    except Exception as e:
        print("recent ERR", e, flush=True); recent = []
    # earliest mint in a wide window (last ~1.5M blocks ~ 8 days at 0.45s/blk) — single call, pageSize 1 asc
    try:
        earliest = ankr_logs(head_n - 1500000, head_n, page=1, desc=False)
        if earliest:
            blk = int(earliest[0]["blockNumber"], 16)
            b = race("eth_getBlockByNumber", [hex(blk), False], timeout=10)
            print("earliest mint in window: block", blk, "ts", int(b["timestamp"], 16), "tx", earliest[0].get("transactionHash"), flush=True)
        else:
            print("no mint logs in last 1.5M blocks", flush=True)
    except Exception as e:
        print("earliest ERR", e, flush=True)
json.dump({"calls": out, "head": head_n}, open("orin-1801-verify.json", "w"), indent=1)
print("DONE", flush=True)
