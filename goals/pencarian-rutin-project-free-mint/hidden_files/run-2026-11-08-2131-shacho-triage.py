"""Parent triage run 2131: SHACHO CLUB 0x26E009350Ef80cb542785d57c27c686a582bf605
(Sale-S1 candidate from Sourcify feed; backfill triaged agent-shaped but first
mint UNVERIFIED due to dataseed failures) + Jinchan free-pool check.
Reads via fast_rpc (eth_call) + Ankr get_logs module (first mint).
No preview/mint/claim/sign. No shared-state writes."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as fr_post
from ankr import ankr_post

EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SHACHO = "0x26E009350Ef80cb542785d57c27c686a582bf605"
JINCHAN = "0xccc127D1A7Ef1e385757784a9878F7279BF3B19D"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

# keccak selectors via eth_utils if available, else hardcoded map
try:
    from eth_utils import keccak
    def sel(sig):
        return keccak(sig.encode()).hex()[:8]
except Exception:
    import sha3
    def sel(sig):
        return sha3.keccak_256(sig.encode()).hexdigest()[:8]

def call(addr, fn, args=b""):
    data = "0x" + sel(fn) + args.hex()
    for ep in EPS:
        try:
            out = fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                          timeout=12, retries=0)
            r = out.get("result")
            if r and r != "0x":
                return r
        except Exception:
            continue
    return None

def u(r):
    return int(r, 16) if r else None

def addr_of(r):
    return "0x" + r[-40:] if r else None

def s(r):
    if not r:
        return None
    try:
        b = bytes.fromhex(r[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode()
    except Exception:
        return r

def uaddr(a):
    return bytes.fromhex(a[2:])

res = {"shacho": {}, "jinchan": {}}
sh = res["shacho"]
sh["address"] = SHACHO
sh["owner"] = addr_of(call(SHACHO, "owner()"))
sh["name"] = s(call(SHACHO, "name()"))
sh["symbol"] = s(call(SHACHO, "symbol()"))
sh["totalSupply"] = u(call(SHACHO, "totalSupply()"))
sh["freeLeft"] = u(call(SHACHO, "freeLeft()"))
sh["freeSupply"] = u(call(SHACHO, "freeSupply()"))
sh["price"] = u(call(SHACHO, "price()"))
sh["agentIds"] = addr_of(call(SHACHO, "agentIds()"))
sh["agentIds_is_registry"] = (sh["agentIds"] or "").lower() == REGISTRY
sh["freeOf_user"] = u(call(SHACHO, "freeOf(address)", uaddr(USER)))
sh["costOf_user_1"] = u(call(SHACHO, "costOf(address,uint256)", uaddr(USER) + (1).to_bytes(32, "big")))
sh["mintedBy_user"] = u(call(SHACHO, "mintedBy(address)", uaddr(USER)))
sh["mintsLeft_user"] = u(call(SHACHO, "mintsLeft(address)", uaddr(USER)))
print("SHACHO:", json.dumps(sh, indent=1), flush=True)

# first mint via Ankr getLogs: Transfer from zero, chunked 1000 blocks backwards
# from head; search back up to ~2 days (~400k blocks at 0.45s/blk is too much;
# contract verified 21:14 WIB today, so search back from head ~6h = ~48k blocks)
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
head = None
for ep in EPS:
    try:
        out = fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=10, retries=0)
        head = int(out["result"], 16)
        break
    except Exception:
        continue
print("head:", head, flush=True)
first = None
if head:
    frm = head - 60000
    while frm <= head and first is None:
        to = min(frm + 999, head)
        try:
            body = ankr_post("ankr_getLogs", {"fromBlock": hex(frm), "toBlock": hex(to),
                                              "address": SHACHO,
                                              "topics": [TRANSFER, ZERO]}, timeout=30)
            logs = body.get("result", []) or []
            print(f"chunk {frm}-{to}: {len(logs)} logs", flush=True)
            if logs:
                first = min(logs, key=lambda l: int(l["blockNumber"], 16))
                break
        except Exception as e:
            print(f"chunk {frm}-{to} ERROR: {e}", flush=True)
        frm = to + 1
if first:
    blk = int(first["blockNumber"], 16)
    ts = None
    for ep in EPS:
        try:
            out = fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(blk), False]}, timeout=10, retries=0)
            ts = int(out["result"]["timestamp"], 16)
            break
        except Exception:
            continue
    from datetime import datetime, timezone, timedelta
    wib = datetime.fromtimestamp(ts, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
    sh["first_mint_block"] = blk
    sh["first_mint_tx"] = first["transactionHash"]
    sh["first_mint_ts"] = ts
    sh["first_mint_wib"] = wib
    print("FIRST MINT:", blk, first["transactionHash"], wib, flush=True)
else:
    sh["first_mint"] = "NOT FOUND in last 60000 blocks"
    print("FIRST MINT: not found in last 60000 blocks", flush=True)

# Jinchan free pool
jc = res["jinchan"]
jc["address"] = JINCHAN
jc["totalMinted"] = u(call(JINCHAN, "totalMinted()"))
jc["FREE_SUPPLY"] = u(call(JINCHAN, "FREE_SUPPLY()"))
jc["freeMinted"] = u(call(JINCHAN, "freeMinted()"))
jc["freeClaimed"] = u(call(JINCHAN, "freeClaimed()"))
jc["freeLeft"] = u(call(JINCHAN, "freeLeft()"))
jc["freeSupply"] = u(call(JINCHAN, "freeSupply()"))
jc["mintOpen"] = u(call(JINCHAN, "mintOpen()"))
print("JINCHAN:", json.dumps(jc, indent=1), flush=True)

json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-2131-shacho-triage.json", "w"), indent=1)
print("WROTE run-2026-11-08-2131-shacho-triage.json", flush=True)
