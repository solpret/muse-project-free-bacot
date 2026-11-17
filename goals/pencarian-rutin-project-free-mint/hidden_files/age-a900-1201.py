import sys, json, time, datetime
sys.path.insert(0, '.')
from onchain_nft_scan import ankr_logs, rpc_call
ADDR="0xa900873E65B5F391B6E37d80a98A6b26D07613B8"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
head=int(rpc_call("eth_blockNumber", []), 16)
print("head:", head, flush=True)
# 48h cutoff at ~0.45 s/block -> ~384000 blocks; search backwards in 1000-block chunks for first mint
cutoff = head - 384000
found=None
frm=head
pages=0
while frm > cutoff:
    to=max(frm-999, cutoff)
    try:
        logs,_=ankr_logs(to, frm, [TRANSFER, ZERO])
    except Exception as e:
        print("chunk err", to, frm, e, flush=True); break
    pages+=1
    mine=[l for l in logs if l.get("address","").lower()==ADDR.lower()]
    if mine:
        # keep scanning backwards to find earliest, but record latest found in this chunk
        found=mine
        print(f"chunk {to}-{frm}: {len(mine)} mint logs for a900 (first in chunk block {min(int(l['blockNumber'],16) for l in mine)})", flush=True)
    else:
        print(f"chunk {to}-{frm}: 0", flush=True)
    if found and frm-1000 <= cutoff:
        break
    frm=to-1
    if pages>=8: break
if found:
    first=min(found, key=lambda l: int(l["blockNumber"],16))
    print("FIRST MINT in searched window:", json.dumps(first)[:400])
    blk=int(first["blockNumber"],16)
    print("first_mint_block:", blk)
    # block timestamp via eth_getBlockByNumber
    import urllib.request
    from fast_rpc import _single
    for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
        try:
            b=_single(ep,"eth_getBlockByNumber",[hex(blk),False],10,retries=0)
            ts=int(b["timestamp"],16)
            print("first_mint_wib:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
            print("age_hours:", (time.time()-ts)/3600)
            break
        except Exception as e:
            print("block ts err", ep, e)
else:
    print("NO mint logs found in searched window (head-384000..head)")
