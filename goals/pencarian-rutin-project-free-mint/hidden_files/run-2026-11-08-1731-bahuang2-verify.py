#!/usr/bin/env python3
"""Fresh verify BAHUANG2 0x57CC350b844484Eac0DE444526d295C90F9cCbB5 (hot-leg 17:19 find). Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak
import onchain_nft_scan as scan

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
A = "0x57CC350b844484Eac0DE444526d295C90F9cCbB5"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def selector(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def enc_uint(n): return format(n, "064x")
def raw_call(addr, data, timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last
def dec_uint(h):
    if not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_bool(h):
    v = dec_uint(h); return None if v is None else bool(v)
def dec_str(h):
    if not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def tc(sig, args=""):
    try: return raw_call(A, selector(sig) + args)
    except Exception as e: return f"ERR:{type(e).__name__}"

r = {}
r["name"] = dec_str(tc("name()"))
r["symbol"] = dec_str(tc("symbol()"))
r["totalMinted"] = dec_uint(tc("totalMinted()"))
r["totalSupply"] = dec_uint(tc("totalSupply()"))
r["FREE_CAP"] = dec_uint(tc("FREE_CAP()"))
r["FREE_PER_WALLET"] = dec_uint(tc("FREE_PER_WALLET()"))
r["freeMinted"] = dec_uint(tc("freeMinted()"))
r["freeCount_agent"] = dec_uint(tc("freeCount(address)", enc_addr(AGENT)))
r["mintOpen"] = dec_uint(tc("mintOpen()"))
r["mintStart"] = dec_uint(tc("mintStart()"))
r["mintEnd"] = dec_uint(tc("mintEnd()"))
r["agentId"] = tc("agentId()")
r["owner"] = tc("owner()")
r["costWei_1"] = dec_uint(tc("costWei(uint256)", enc_uint(1)))
# quote(user,1): returns tuple; decode first 5 words
q = tc("quote(address,uint256)", enc_addr(AGENT) + enc_uint(1))
if isinstance(q, str) and q.startswith("0x") and len(q) >= 2 + 64*5:
    b = bytes.fromhex(q[2:])
    r["quote_user_1_words"] = [int.from_bytes(b[i*32:(i+1)*32], "big") for i in range(5)]
else:
    r["quote_user_1_raw"] = q
print(json.dumps(r, indent=1), flush=True)
# First-mint re-verification via Ankr getLogs: Transfer from 0x0 to anyone, contract A, blocks 132375700-132375760
logs, pages = scan.ankr_logs(132375700, 132375760, [scan.TRANSFER, scan.ZERO_TOPIC])
mine = [l for l in logs if l.get("address", "").lower() == A.lower()]
print(f"ankr getLogs 132375700-132375760: {len(logs)} logs total, {len(mine)} for BAHUANG2", flush=True)
for l in mine[:5]:
    print("  block", int(l.get("blockNumber","0x0"),16), "tx", l.get("transactionHash"), "topics", l.get("topics",[])[:3], flush=True)
r["first_mint_logs_in_132375700_132375760"] = len(mine)
r["first_mint_block_from_hotleg"] = 132375730
json.dump(r, open("run-2026-11-08-1731-bahuang2-verify.json", "w"), indent=1)
print("WROTE bahuang2-verify.json")
