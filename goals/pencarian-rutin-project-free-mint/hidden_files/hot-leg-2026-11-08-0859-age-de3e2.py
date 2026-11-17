import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs
ADDR="0xde3e3e9e2f87f285f0f26ea54923a933b10df140"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
FROM=131925267  # ~48h ago
res=get_logs(ADDR, FROM, "latest", topics=[TRANSFER, ZERO])
logs=res.get("result",{}).get("logs",[])
out={"from_block":FROM,"n_mint_logs_in_48h_window":len(logs),
     "nextPageToken":res.get("result",{}).get("nextPageToken"),
     "totalSupply_now":444}
if logs:
    blocks=[int(l["blockNumber"],16) for l in logs]
    out["earliest_mint_block"]=min(blocks)
    out["latest_mint_block"]=max(blocks)
    out["earliest_mint_tx"]=sorted(logs, key=lambda l:int(l["blockNumber"],16))[0].get("transactionHash")
if len(logs)==444:
    out["verdict"]="VERIFIED <=48h - all 444 mints occurred within the 48h window (freeClaimed was 0 at 48h-ago block)"
elif len(logs)<444:
    out["verdict"]=f"AGE-EXCLUDED >48h - only {len(logs)} of 444 mints in 48h window; first mint predates the window"
else:
    out["verdict"]="INCONCLUSIVE - more mint logs than totalSupply; check pagination"
json.dump(out, open("hot-leg-2026-11-08-0859-age-de3e2.json","w"), indent=1)
json.dump(logs, open("hot-leg-2026-11-08-0859-age-de3e-mints-full.json","w"), indent=1)
print(json.dumps(out, indent=1))
