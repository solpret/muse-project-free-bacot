#!/usr/bin/env python3
"""Read-only decode of in-window txs for the 9 active wallets (pagination + PCS path parse)."""
import json, sys, time, datetime
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

SEL_BUY = sel("swapExactETHForTokensSupportingFeeOnTransferTokens(uint256,address[],address,uint256)")
SEL_SELL = sel("swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)")
SEL_APPROVE = sel("approve(address,uint256)")
print("SEL_BUY", SEL_BUY, "SEL_SELL", SEL_SELL, "SEL_APPROVE", SEL_APPROVE, flush=True)

jak = datetime.timezone(datetime.timedelta(hours=7))
start_ts = 1793667900
active = ["0x2325f175975abdbcde555c79cc8e63381d28551b",
          "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
          "0x3628764a6576b8dfb31fba0aac6a333b64851423",
          "0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
          "0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74",
          "0xad94ee77d0e868d299fb3e92b9d67560257f656d",
          "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
          "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650",
          "0x355ea9e542b36c645a2dee63b9df079ccb9bf3db"]

def parse_path(data_hex, sel_expected):
    """data_hex without 0x, after 4-byte selector. Returns path list or None."""
    b = bytes.fromhex(data_hex[8:])
    def u256(off): return int.from_bytes(b[off:off+32], "big")
    def addr(off): return "0x" + b[off+12:off+32].hex()
    if sel_expected == SEL_BUY:
        path_off = u256(32)
        n = u256(path_off)
        return [addr(path_off + 32 + i*32) for i in range(n)]
    if sel_expected == SEL_SELL:
        path_off = u256(64)
        n = u256(path_off)
        return [addr(path_off + 32 + i*32) for i in range(n)]
    return None

out = {}
for w in active:
    txs, page_token = [], None
    while True:
        params = {"blockchain": "bsc", "address": w, "pageSize": 50}
        if page_token:
            params["pageToken"] = page_token
        data = ankr_mod.ankr_post("ankr_getTransactionsByAddress", params)
        res = data.get("result") or {}
        batch = res.get("transactions") or []
        txs.extend(batch)
        page_token = res.get("nextPageToken")
        if not batch or not page_token:
            break
        # stop when oldest in batch is before window
        try:
            oldest = int(batch[-1].get("timestamp", "0"), 16)
        except Exception:
            oldest = 0
        if oldest < start_ts:
            break
        time.sleep(2.0)
    inw = []
    for t in txs:
        try:
            ts = int(t.get("timestamp", "0"), 16)
        except Exception:
            continue
        if ts < start_ts:
            continue
        inp = (t.get("input") or "")
        s = inp[:10]
        kind, detail = "other", {}
        if s == SEL_BUY:
            try:
                path = parse_path(inp[2:], SEL_BUY)
                kind, detail = "pcs_buy", {"path": path, "bought": path[-1] if path else None,
                                            "bnb": int(t.get("value", "0"), 16) / 1e18}
            except Exception as e:
                detail = {"parse_error": str(e)[:200]}
        elif s == SEL_SELL:
            try:
                path = parse_path(inp[2:], SEL_SELL)
                amount_in = int.from_bytes(bytes.fromhex(inp[2:][8:8+64]), "big")
                kind, detail = "pcs_sell", {"path": path, "sold": path[0] if path else None,
                                            "amount_in_raw": str(amount_in)}
            except Exception as e:
                detail = {"parse_error": str(e)[:200]}
        elif s == SEL_APPROVE:
            kind = "approve"
            try:
                raw = bytes.fromhex(inp[2:][8:])
                detail = {"spender": "0x" + raw[12:32].hex(),
                          "amount_raw": str(int.from_bytes(raw[32:64], "big"))}
            except Exception as e:
                detail = {"parse_error": str(e)[:200]}
        inw.append({"hash": t.get("hash"), "block": int(t.get("blockNumber"), 16),
                    "to": t.get("to"), "value": t.get("value"), "status": t.get("status"),
                    "ts": ts, "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M WIB"),
                    "selector": s, "kind": kind, "detail": detail})
        time.sleep(0.05)
    out[w] = inw
    import collections
    print(f"{w[:10]} total_in_window={len(inw)} kinds={dict(collections.Counter(x['kind'] for x in inw))}", flush=True)
    time.sleep(2.0)
json.dump(out, open("/tmp/tracked-scan-decoded.json", "w"), indent=1)
print("saved /tmp/tracked-scan-decoded.json", flush=True)
