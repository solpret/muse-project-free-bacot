#!/usr/bin/env python3
"""Pre-window + free-shape check run 2026-11-09 0931 WIB.
Pre-window: for non-discarded agent-shaped-flagged first-seen contracts,
count Transfer-from-zero mints in [132400000, 132507583] (before this run's
scan window) via ONE Ankr ankr_getLogs call per contract. 0 pre-window mints
+ totalSupply/totalMinted reads detect mature contracts predating 132400000.
Free-shape: for 0x42dBe114 (Sourcify exact_match, S1=True) read free views +
quote(agent wallet,1) + freeAvailable/freeUsed(agent wallet) + name/symbol.
Read-only; writes run-2026-11-09-0931-prewindow.json.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
FROM, TO = 132400000, 132507583
AGENT_WALLET = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

CONTRACTS = [
    "0x03ABBA3Ed9750B847a1dA717A089E1387504Fdf0",
    "0x42dBe11400A6DD3C92710FD275f8ca1193830022",
    "0x9f2ae1A752045faDF9Fe411143D618C9cC5F3db2",
    "0x3ef5ffD14568560bbdAbF8bdb3842966457c0F88",
    "0xDE3c7f3dAc07f053B5eA8421bE1B82b3bB02B1d0",
]
# owner-discarded, NOT pre-window checked (excluded from promotion regardless):
DISCARDED = [
    "0x06c7f79B54859a7a6320A0f01fd73981B50F08A1",
    "0x544ECC6E69dF47AD8cE1621f4Fe57dc9095E1A37",
]
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def eth_call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result")
            if isinstance(r, str) and r.startswith("0x"):
                return r
        except Exception:
            continue
    return None

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def enc_addr(a):
    return a[2:].lower().rjust(64, "0")

def view_int(addr, data):
    r = eth_call(addr, data)
    if r is None or len(r) < 66:
        return None
    try:
        return int(r[-64:], 16)
    except Exception:
        return None

def view_bool(addr, data):
    v = view_int(addr, data)
    return None if v is None else bool(v)

out = {"run": "2026-11-09-0931", "pre_window": [FROM, TO],
       "discarded_not_checked": DISCARDED}
for addr in CONTRACTS:
    t0 = time.time()
    try:
        res = ankr_post("ankr_getLogs", {
            "blockchain": "bsc",
            "fromBlock": str(FROM),
            "toBlock": str(TO),
            "address": addr,
            "topics": [TRANSFER, ZERO_TOPIC],
            "pageSize": 1000,
        }, timeout=55)
        logs = res.get("result", {}).get("logs", []) if isinstance(res, dict) else []
        n = len(logs)
        first_blk = min((int(l["blockNumber"], 16) for l in logs), default=None)
        entry = {"pre_window_mints": n, "first_pre_block": first_blk,
                 "truncated": n >= 1000, "seconds": round(time.time() - t0, 1)}
    except Exception as e:
        entry = {"pre_window_mints": None, "first_pre_block": None,
                 "truncated": None, "error": str(e)[:200],
                 "seconds": round(time.time() - t0, 1)}
    if entry.get("pre_window_mints") == 0:
        entry["totalSupply"] = view_int(addr, sel("totalSupply()"))
        entry["totalMinted"] = view_int(addr, sel("totalMinted()"))
    out[addr] = entry
    print(addr, entry, flush=True)

# --- free-shape for 0x42dBe114 ---
c = "0x42dBe11400A6DD3C92710FD275f8ca1193830022"
fs = {}
fs["name"] = None
fs["symbol"] = None
for fn, key in (("name()", "name"), ("symbol()", "symbol")):
    r = eth_call(c, sel(fn))
    if r and len(r) >= 130:
        try:
            ln = int(r[64:128], 16)
            fs[key] = bytes.fromhex(r[128:128 + ln * 2]).decode("utf-8", "replace")
        except Exception:
            pass
fs["FREE_SUPPLY"] = view_int(c, sel("FREE_SUPPLY()"))
fs["FREE_PER_WALLET"] = view_int(c, sel("FREE_PER_WALLET()"))
fs["MAX_SUPPLY"] = view_int(c, sel("MAX_SUPPLY()"))
fs["totalMinted"] = view_int(c, sel("totalMinted()"))
fs["freeMinted"] = view_int(c, sel("freeMinted()"))
fs["freeMintOpen"] = view_bool(c, sel("freeMintOpen()"))
fs["paidMintOpen"] = view_bool(c, sel("paidMintOpen()"))
fs["PRICE"] = view_int(c, sel("PRICE()"))
fs["freeAvailable_agent_wallet"] = view_int(c, sel("freeAvailable(address)") + enc_addr(AGENT_WALLET))
fs["freeUsed_agent_wallet"] = view_int(c, sel("freeUsed(address)") + enc_addr(AGENT_WALLET))
q = eth_call(c, sel("quote(address,uint256)") + enc_addr(AGENT_WALLET) + format(1, "064x"))
if q and len(q) >= 130:
    try:
        fs["quote_agent_wallet_1_cost"] = int(q[2:66], 16)
        fs["quote_agent_wallet_1_tokensOut"] = int(q[66:130], 16)
    except Exception:
        fs["quote_raw"] = q
fs["contractURI"] = None
r = eth_call(c, sel("contractURI()"))
if r and len(r) >= 130:
    try:
        ln = int(r[64:128], 16)
        fs["contractURI"] = bytes.fromhex(r[128:128 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        pass
out[c]["free_shape"] = fs
print(c, "free_shape:", fs, flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0931-prewindow.json", "w"), indent=1)
print("PREWINDOW DONE")
