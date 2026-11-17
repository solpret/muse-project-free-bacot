#!/usr/bin/env python3
"""First-mint corroboration for AgentBook 0xEECaCBE6 + userInfo probe fab7dd20.
Backward 1000-block Ankr chunks, stop at first empty chunk after mints found (cap 24)."""
import sys, json, time, datetime
sys.path.insert(0, ".")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from onchain_nft_scan import ankr_logs, rpc_call
from fast_rpc import _single
ADDR = "0xeecacbe6eac6d6f2a38e8daa9049c7aa08ad43b0"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
WIB = datetime.timezone(datetime.timedelta(hours=7))
head = int(rpc_call("eth_blockNumber", []), 16)
print("head:", head)
found = None; pages = 0; frm = head; empty_after_found = False
while pages < 24:
    to = max(frm - 999, head - 384000)
    try:
        logs, _ = ankr_logs(to, frm, [TRANSFER, ZERO])
    except Exception as e:
        print("chunk err", to, frm, e); break
    pages += 1
    mine = [l for l in logs if l.get("address", "").lower() == ADDR.lower()]
    print(f"chunk {to}-{frm}: {len(mine)} AgentBook mint logs", flush=True)
    if mine:
        found = mine if found is None else found + mine
    elif found:
        empty_after_found = True; break
    if to <= head - 384000: break
    frm = to - 1
if found:
    first = min(found, key=lambda l: int(l["blockNumber"], 16))
    blk = int(first["blockNumber"], 16)
    print("first_mint_block:", blk, "total mint logs found:", len(found))
    for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org/"]:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(blk), False], 10, retries=0)
            ts = int(b["timestamp"], 16)
            print("first_mint_wib:", datetime.datetime.fromtimestamp(ts, WIB).isoformat())
            print("age_hours:", round((time.time() - ts) / 3600, 2))
            break
        except Exception as e:
            print("block ts err", ep, e)
else:
    print("NO AgentBook mint logs in searched window (up to 24 chunks back)")
# fab7dd20 userInfo + startTime conversion
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/"]:
    try:
        r = _single(ep, "eth_call", [{"to": "0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72", "data": sel("userInfo(address)") + enc(USER)}, "latest"], 8, retries=0)
        print("fab7dd20 userInfo(user) raw:", r); break
    except Exception as e:
        print("userInfo err", ep, e)
print("fab7dd20 startTime WIB:", datetime.datetime.fromtimestamp(1794061611, WIB).isoformat())
print("fab7dd20 deadline WIB:", datetime.datetime.fromtimestamp(1794320811, WIB).isoformat())
print("now WIB:", datetime.datetime.fromtimestamp(time.time(), WIB).isoformat())
