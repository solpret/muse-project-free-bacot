#!/usr/bin/env python3
"""Read-only run 5 paid-trend detail: re-fetch sent txs for the active wallets and
parse PCS buy/sell paths (programmatic selectors) to count wallets per token."""
import json, sys, time, datetime, collections
sys.path.insert(0, str(__import__('pathlib').Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
SEL_BUY = sel("swapExactETHForTokensSupportingFeeOnTransferTokens(uint256,address[],address,uint256)")
SEL_SELL = sel("swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)")
FROM = 131422074
wallets = ["0x3628764a6576b8dfb31fba0aac6a333b64851423","0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
           "0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74","0xad94ee77d0e868d299fb3e92b9d67560257f656d",
           "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a","0x7488d5da6a6097de0ff88c7492c62c2fd1e56650",
           "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0xbf004bff64725914ee36d03b87d6965b0ced4903"]
def parse_path(inp, buy):
    b = bytes.fromhex(inp[2:][8:])
    def u256(o): return int.from_bytes(b[o:o+32], "big")
    def addr(o): return "0x" + b[o+12:o+32].hex()
    if buy:
        off = u256(32); n = u256(off); return [addr(off+32+i*32) for i in range(n)]
    off = u256(64); n = u256(off); return [addr(off+32+i*32) for i in range(n)]
out = {}
for w in wallets:
    txs, pt = [], None
    while True:
        p = {"blockchain": "bsc", "address": w, "pageSize": 50}
        if pt: p["pageToken"] = pt
        d = ankr_mod.ankr_post("ankr_getTransactionsByAddress", p)
        r = d.get("result") or {}; batch = r.get("transactions") or []; txs.extend(batch); pt = r.get("nextPageToken")
        if not batch or not pt: break
        try: oldest = int(batch[-1].get("blockNumber", "0"), 16)
        except Exception: oldest = 0
        if oldest <= FROM: break
        time.sleep(1)
    inw = []
    for t in txs:
        try: bn = int(t.get("blockNumber"), 16)
        except Exception: continue
        if bn <= FROM or bn > 131430250: continue
        inp = t.get("input") or ""; s = inp[:10]; kind = "other"; path = None
        if s == SEL_BUY:
            try: path = parse_path(inp, True); kind = "pcs_buy"
            except Exception as e: kind = "pcs_buy_parse_error"
        elif s == SEL_SELL:
            try: path = parse_path(inp, False); kind = "pcs_sell"
            except Exception as e: kind = "pcs_sell_parse_error"
        elif s == "0x095ea7b3": kind = "approve"
        elif s == "0x791ac947": kind = "pcs_sell_791ac947"
        elif s == "0xb6f9de95": kind = "pcs_buy_b6f9de95"
        inw.append({"hash": t.get("hash"), "to": t.get("to"), "value_bnb": int(t.get("value", "0"), 16)/1e18,
                    "selector": s, "kind": kind, "path": path})
    out[w] = inw
    print(w[:10], len(inw), dict(collections.Counter(x["kind"] for x in inw)), flush=True)
    time.sleep(1)
# wallets per bought token (PCS buys, path last element)
tok_wallets = collections.defaultdict(set)
for w, txs in out.items():
    for t in txs:
        if t["kind"] in ("pcs_buy", "pcs_buy_b6f9de95") and t.get("path"):
            tok_wallets[t["path"][-1]].add(w)
print("bought tokens:", len(tok_wallets), "max wallets per token:", max((len(v) for v in tok_wallets.values()), default=0), flush=True)
for tok, ws in sorted(tok_wallets.items(), key=lambda kv: -len(kv[1]))[:15]:
    print(tok, len(ws), [x[:10] for x in ws], flush=True)
json.dump(out, open("/tmp/tracked-scan-run11-paid.json", "w"), indent=1)
# bf00 detail
for t in out.get("0xbf004bff64725914ee36d03b87d6965b0ced4903", []):
    print("bf00", t, flush=True)
