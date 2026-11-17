#!/usr/bin/env python3
"""Fresh verify BRAINROT ZOO (ROT) 0x3c7d328027ca0068e7cd8709d64d9161bc35de93 — Boltbook EN/ZH front-page lead run 1831. Read-only."""
import sys, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch, _post as _fr_post
from eth_hash.auto import keccak
import onchain_nft_scan as scan

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
A = "0x3c7d328027ca0068e7cd8709d64d9161bc35de93"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

def selector(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def enc_uint(n): return format(n, "064x")
def raw_call(addr, data, block="latest", timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, block])], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last
def dec_uint(h):
    if not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_str(h):
    if not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def tc(sig, args=""):
    try: return raw_call(A, selector(sig) + args)
    except Exception as e: return "ERR:%s" % type(e).__name__

r = {}
r["name"] = dec_str(tc("name()"))
r["symbol"] = dec_str(tc("symbol()"))
r["totalMinted"] = dec_uint(tc("totalMinted()"))
r["totalSupply"] = dec_uint(tc("totalSupply()"))
r["MAX_SUPPLY"] = dec_uint(tc("MAX_SUPPLY()"))
r["FREE_SUPPLY"] = dec_uint(tc("FREE_SUPPLY()"))
r["FREE_CAP"] = dec_uint(tc("FREE_CAP()"))
r["freeClaimed"] = dec_uint(tc("freeClaimed()"))
r["freeMinted"] = dec_uint(tc("freeMinted()"))
r["mintOpen"] = dec_uint(tc("mintOpen()"))
r["price"] = dec_uint(tc("price()"))
r["mintPrice"] = dec_uint(tc("mintPrice()"))
r["owner"] = tc("owner()")
r["agentId"] = tc("agentId()")
r["agentRegistry"] = tc("agentRegistry()")
r["AGENT_ID"] = tc("AGENT_ID()")
r["contractURI_raw"] = tc("contractURI()")
r["tokenURI_1_raw"] = tc("tokenURI(uint256)", enc_uint(1))
r["freeClaimed_user"] = dec_uint(tc("freeClaimed(address)", enc_addr(AGENT)))
r["freeMinted_user"] = dec_uint(tc("freeMinted(address)", enc_addr(AGENT)))
r["balanceOf_user"] = dec_uint(tc("balanceOf(address)", enc_addr(AGENT)))
q = tc("quote(address,uint256)", enc_addr(AGENT) + enc_uint(1))
if isinstance(q, str) and q.startswith("0x") and len(q) >= 2 + 64*2:
    b = bytes.fromhex(q[2:])
    r["quote_user_1_words"] = [int.from_bytes(b[i*32:(i+1)*32], "big") for i in range(min(5, len(b)//32))]
else:
    r["quote_user_1_raw"] = q
print(json.dumps(r, indent=1), flush=True)

# eth_getCode registry-bytes check
code = None
for ep in EPS:
    try:
        code = batch([("eth_getCode", [A, "latest"])], endpoint=ep, timeout=15)[0]
        break
    except Exception:
        continue
r["code_len"] = len(code) - 2 if code else None
r["registry_bytes_in_code"] = (REG in code.lower()) if code else None
print("code_len", r["code_len"], "registry_bytes", r["registry_bytes_in_code"], flush=True)

# Sourcify
try:
    out = subprocess.run(["curl", "-s", "--max-time", "20",
        "https://sourcify.dev/server/v2/contracts/56/" + A],
        capture_output=True, text=True)
    sj = json.loads(out.stdout) if out.stdout.strip().startswith("{") else {}
    r["sourcify"] = {"match": sj.get("match"), "verifiedAt": sj.get("verifiedAt"),
                     "creationMatch": sj.get("creationMatch"), "runtimeMatch": sj.get("runtimeMatch")}
except Exception as e:
    r["sourcify"] = {"error": str(e)}
print("sourcify", r["sourcify"], flush=True)

# First-mint binary search via historical totalSupply eth_call.
# Find earliest block in [lo, hi] with totalSupply > 0. hi = current head.
head = None
for ep in EPS:
    try:
        head = int(_fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=8, retries=0)["result"], 16)
        break
    except Exception:
        continue
r["head"] = head
print("head", head, flush=True)
sel_ts = selector("totalSupply()")
def ts_at(block):
    try:
        raw = raw_call(A, sel_ts, block=hex(block), timeout=10)
    except Exception:
        return None
    if isinstance(raw, dict):
        return None  # eth_call error object
    if raw == "0x" or raw is None:
        return 0  # no code yet at that block (not deployed) -> supply 0
    return dec_uint(raw)
lo, hi = 130000000, head  # lo: safely before any plausible launch (contract likely recent; verify below)
# sanity: totalSupply at lo must be 0 or revert; if >0, extend lo backwards
v_lo = ts_at(lo)
print("totalSupply at lo", lo, "=", v_lo, flush=True)
if v_lo not in (0, None):
    lo2 = 128000000
    print("totalSupply at lo2", lo2, "=", ts_at(lo2), flush=True)
    lo = lo2
# binary search first block with totalSupply > 0
a, b = lo, head
while b - a > 1:
    m = (a + b) // 2
    v = ts_at(m)
    if v is None:
        print("ts_at None at", m, "- abort binary search", flush=True)
        a = None
        break
    if v > 0:
        b = m
    else:
        a = m
r["first_supply_block"] = b if a is not None else None
print("first block with totalSupply>0:", r["first_supply_block"], flush=True)
if r["first_supply_block"]:
    fb = r["first_supply_block"]
    # block timestamp via dataseed (Ankr returns fake timestamps - never use)
    blk = None
    for ep in EPS:
        try:
            blk = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(fb), False]}, timeout=10, retries=0)
            break
        except Exception:
            continue
    if blk and blk.get("result"):
        import datetime
        ts = int(blk["result"]["timestamp"], 16)
        r["first_mint_block_time_utc"] = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat()
        r["first_mint_block_time_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
        print("first mint time WIB:", r["first_mint_block_time_wib"], flush=True)
    # corroborate with Ankr getLogs Transfer-from-zero in 1000-block window around fb
    frm = max(fb - 500, 0)
    to = fb + 499
    logs, pages = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
    mine = [l for l in logs if l.get("address", "").lower() == A.lower()]
    r["ankr_window"] = [frm, to]
    r["ankr_logs_for_contract"] = len(mine)
    if mine:
        first = min(mine, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
        r["first_transfer_block"] = int(first.get("blockNumber", "0x0"), 16)
        r["first_transfer_tx"] = first.get("transactionHash")
        print("first Transfer-from-zero block:", r["first_transfer_block"], "tx:", r["first_transfer_tx"], flush=True)

json.dump(r, open(BASE + "/run-2026-11-08-1831-brainrot-verify.json", "w"), indent=1)
print("WROTE run-2026-11-08-1831-brainrot-verify.json")
