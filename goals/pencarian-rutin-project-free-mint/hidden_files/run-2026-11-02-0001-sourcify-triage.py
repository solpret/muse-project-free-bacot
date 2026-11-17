#!/usr/bin/env python3
"""00:01 run: triage 2 Sourcify S1 passes. Read-only."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:150]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        sig = name.replace("quote1(", "quote(").replace("quote0(", "quote(")
        val, err = call(to, sel(sig) + arg)
        try: iv = int(val, 16) if val else None
        except Exception: iv = None
        out[name] = {"int": iv, "raw": val, "error": err if val is None else None}
    return out
def words(val):
    if not val: return None
    b = bytes.fromhex(val[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
def block_ts(b):
    blk = _single("https://bsc-dataseed.binance.org/", "eth_getBlockByNumber", [hex(b), False], 10, retries=0)
    ts = int(blk["timestamp"], 16)
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
def first_mints(addr, topics):
    logs = []; tok = None; pages = 0
    while True:
        p = {"blockchain": "bsc", "fromBlock": hex(130900000), "toBlock": "latest", "pageSize": 1000, "decodeLogs": False, "topics": topics, "address": addr}
        if tok: p["pageToken"] = tok
        body = ankr_post("ankr_getLogs", p, timeout=30)
        r = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(r.get("logs", [])); tok = r.get("nextPageToken"); pages += 1
        if not tok or pages >= 20: break
    if not logs: return {"count": 0, "pages": pages}
    bs = sorted(int(l["blockNumber"], 16) for l in logs)
    minters = {"0x" + l["topics"][2][-40:] for l in logs if len(l.get("topics", [])) >= 3}
    return {"count": len(logs), "pages": pages, "first_block": bs[0], "first_ts": block_ts(bs[0]), "last_block": bs[-1], "distinct_minters_topic2": len(minters)}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
MINTED_BABY = "0x19f5f791ee407773427bf7b970bbbc3375065c32edd1ab142e23a84f94b0719b"
res = {}
GAME = "0x3815A26a6981BAAd0b850f7522B7a8BDDdB6B70C"
res["game"] = collect(GAME, [("totalSupply()", ""), ("maxSupply()", ""), ("freeClaimed()", ""), ("mintedCount()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeCount()", ""), ("paused()", ""), ("quote(uint256)", enc_uint(1)[2:]), ("currentDay()", ""), ("name()", ""), ("symbol()", "")])
aid, _ = call(GAME, sel("agentId(address)") + enc_addr(USER)[2:])
res["game_agentId_user"] = {"raw": aid}
try: res["game_first_mints"] = first_mints(GAME, [TRANSFER, ZERO])
except Exception as e: res["game_first_mints_error"] = str(e)[:200]
CARD = "0xe15e68C9198ee0A5780fba96016e1780204aF3B4"
res["card"] = collect(CARD, [("totalCards()", ""), ("cardsSold()", ""), ("cardsRemaining()", ""), ("freeCardCap()", ""), ("freeCardsRemaining()", ""), ("freeGiven()", ""), ("gateOn()", ""), ("paused()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("quotaLeft(address)", enc_addr(USER)[2:]), ("pricePerShare()", ""), ("tokensPerShare()", ""), ("token()", "")])
q1, _ = call(CARD, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
res["card_quote_user_1"] = {"words": words(q1), "raw": q1}
try: res["card_first_minted"] = first_mints(CARD, [MINTED_BABY])
except Exception as e: res["card_first_minted_error"] = str(e)[:200]
# card token reads
tok_raw = res["card"]["token()"]["raw"]
if tok_raw:
    tok = "0x" + tok_raw[-40:]
    res["card_token_addr"] = tok
    res["card_token"] = collect(tok, [("name()", ""), ("symbol()", ""), ("decimals()", ""), ("totalSupply()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
print(json.dumps(res, indent=1))
json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0001-sourcify-triage.json", "w"), indent=1)
