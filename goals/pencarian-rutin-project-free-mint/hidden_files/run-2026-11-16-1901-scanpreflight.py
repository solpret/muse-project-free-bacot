import sys, time, json
sys.path.insert(0, '.')
from onchain_nft_scan import ankr_logs, rpc_call
t0=time.time()
head=int(rpc_call("eth_blockNumber", []), 16)
print("head:", head, flush=True)
logs, pages = ankr_logs(head-49, head, ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", "0x0000000000000000000000000000000000000000000000000000000000000000"])
print("PREFLIGHT OK in %.1fs: %d logs, %d pages" % (time.time()-t0, len(logs), pages), flush=True)
