import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
t0 = time.time()
head = None
try:
    r = ankr_post("eth_blockNumber", [], timeout=30)
    head = int(r.get("result"), 16)
    print(f"head via ankr eth_blockNumber: {head}", flush=True)
except Exception as e:
    print(f"ankr eth_blockNumber failed: {e}", flush=True)
if head is None:
    sys.path.insert(0, "/home/hatch/workspace/fast_exec")
    from fast_rpc import race
    head = int(race("eth_blockNumber", []), 16)
    print(f"head via fast_rpc race: {head}", flush=True)
END = head
body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(END-49), "toBlock": hex(END), "pageSize": 1000, "decodeLogs": False, "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", "0x"+"00"*32]}, timeout=30)
n = len(body.get("result", {}).get("logs", []))
print(f"PREFLIGHT OK end={END} logs50={n} total={time.time()-t0:.1f}s", flush=True)
json.dump({"end": END, "head": END, "logs50": n, "elapsed_s": round(time.time()-t0, 1), "status": "PASS"}, open("run-2026-11-07-0131-preflight.json", "w"), indent=1)
