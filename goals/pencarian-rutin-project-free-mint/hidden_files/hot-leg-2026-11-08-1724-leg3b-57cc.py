#!/usr/bin/env python3
"""Hot-leg 1724 leg3b: fast on-chain verify of NEW S1 NFT 0x57CC350b844484Eac0DE444526d295C90F9cCbB5
(fresh Sourcify feed, S1=True, ownerOf -> ERC-721 NFT, NOT a track-C fungible share sale).
Read-only; no preview, no mint. Per body leg (3): free pool, user slot, launch age.
Age: first Transfer-from-zero via Ankr getLogs (address-filtered), timestamp via dataseed
eth_getBlockByNumber (Ankr returns fake 'now' timestamps - NEVER use for block time)."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1724"
ADDR = "0x57CC350b844484Eac0DE444526d295C90F9cCbB5"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
t0 = time.time()
out = {"addr": ADDR, "wib": "2026-11-08T17:24:38+07:00"}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def rpc(method, params, timeout=15):
    body = [{"jsonrpc": "2.0", "id": 1, "method": method, "params": params}]
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)[0].get("result")
        except Exception:
            continue
    return None

def call(data):
    res = rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
    return res

def u256(sig, arg=None):
    data = sel(sig)
    if arg == "USER": data += enc(USER)
    elif arg == "QTY1": data += format(1, "064x")
    elif arg == "USERQTY1": data += enc(USER) + format(1, "064x")
    return to_int(call(data))

def decode_str(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        off = int.from_bytes(b[32:64], "big"); ln = int.from_bytes(b[64+off-32:64+off], "big") if False else None
        # standard ABI string: offset(32) len(32) data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception as ex:
        return f"ERR {ex}"

views = {}
for sig in ["FREE_CAP()", "FREE_PER_WALLET()", "freeMinted()", "totalMinted()",
            "mintStart()", "mintEnd()", "mintPriceWei()", "epicMinted()", "fusedMinted()"]:
    views[sig[:-2]] = u256(sig)
views["freeCount_user"] = u256("freeCount(address)", "USER")
views["costWei_1"] = u256("costWei(uint256)", "QTY1")
q = call(sel("quote(address,uint256)") + enc(USER) + format(1, "064x"))
if q and q != "0x":
    b = bytes.fromhex(q[2:])
    views["quote_user1_raw"] = [int.from_bytes(b[i*32:(i+1)*32], "big") for i in range(5)] if len(b) >= 160 else q
else:
    views["quote_user1_raw"] = q
views["name"] = decode_str(call(sel("name()")) or "0x")
views["symbol"] = decode_str(call(sel("symbol()")) or "0x")
ag = call(sel("agentId()"))
views["agentId"] = ("0x" + ag[-40:]) if ag and len(ag) >= 42 else ag
out["views"] = views

head = rpc("eth_blockNumber", [])
head_n = int(head, 16) if head else None
out["head_block"] = head_n

# first mint: Transfer from zero, address-filtered, window last 300k blocks (BSC ~0.45s/block -> ~37h)
first = None
if head_n:
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
            "fromBlock": hex(head_n - 300000), "toBlock": hex(head_n),
            "address": ADDR.lower(), "pageSize": 1000, "decodeLogs": False,
            "topics": [TRANSFER, ZERO_TOPIC]}, timeout=30)
        logs = (body.get("result", {}) or {}).get("logs", [])
        out["ankr_logs_n"] = len(logs)
        if logs:
            first = min(logs, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
            out["first_mint_block"] = int(first["blockNumber"], 16)
            out["first_mint_tx"] = first.get("transactionHash")
            ts = rpc("eth_getBlockByNumber", [hex(out["first_mint_block"]), False])
            if ts:
                out["first_mint_ts"] = int(ts.get("timestamp", "0x0"), 16)
                import datetime
                out["first_mint_wib"] = datetime.datetime.fromtimestamp(
                    out["first_mint_ts"], datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                out["age_hours"] = round((time.time() - out["first_mint_ts"]) / 3600, 2)
    except Exception as ex:
        out["ankr_error"] = f"{type(ex).__name__}: {str(ex)[:160]}"
out["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + TAG + "-leg3b-57cc.json", "w"), indent=1)
print(json.dumps(out, indent=1))
