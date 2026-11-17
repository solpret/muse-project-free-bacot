#!/usr/bin/env python3
"""Triage scan first-seen registry=True contracts, run 0101 (2026-11-06). Read-only.
For each: (a) earliest-mint check via Ankr logs (existence before window
first_block, back to block 130000000); (b) generic free views for the user;
(c) value of 1-2 sample mint txs (proves mint value 0 like Moonfall).
A failed read is None / error, never zero."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_bool(out):
    v = dec_uint(out)
    return None if v is None else bool(v)

def dec_addr(out):
    if not isinstance(out, str) or len(out) < 66:
        return None
    return "0x" + out[26:66]

def call(addr, data, timeout=7):
    try:
        return rpc_call("eth_call", [{"to": addr, "data": data}, "latest"], timeout)
    except Exception as e:
        return {"_error": str(e)[:100]}

def logs_in(addr, frm, to, page=1000):
    logs = []
    tok = None
    n = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "address": [addr], "pageSize": page, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        if tok:
            params["pageToken"] = tok
        body = ankr_post("ankr_getLogs", params, timeout=30)
        res = body.get("result", {})
        logs.extend(res.get("logs", []))
        n += 1
        tok = res.get("nextPageToken")
        if not tok or n >= 15:
            break
    return logs

def ts_wib(b):
    ts = int(rpc_call("eth_getBlockByNumber", [hex(b), False], 10)["timestamp"], 16)
    return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))

def main():
    scan = json.load(open("onchain-scan-2026-11-06-0101.json"))
    seen = json.load(open("onchain-scan-seen.json"))["contracts"]
    seen_lower = {k.lower() for k in seen}
    snap = json.load(open("onchain-snapshot.json"))["contracts"]
    snap_lower = {v.get("address", "").lower() for v in snap.values() if v.get("address")}
    head = int(rpc_call("eth_blockNumber", [], 10), 16)
    ua = "000000000000000000000000" + USER[2:].lower()
    out = {"block": head, "triage": {}}
    for c in scan["contracts"]:
        a = c["address"]
        if a.lower() in seen_lower or a.lower() in snap_lower or not c.get("registry_bytes_hit"):
            continue
        r = {"address": a, "name": c.get("name"), "symbol": c.get("symbol"),
             "kind": c.get("kind"), "window_mints": c.get("mint_count"),
             "window_minters": c.get("distinct_minters"),
             "window_first_block": c.get("first_block")}
        logs = logs_in(a, 130000000, head)
        if logs:
            fb = min(int(x["blockNumber"], 16) for x in logs)
            r["earliest_block"] = fb
            r["earliest_wib"] = ts_wib(fb)
            r["log_count"] = len(logs)
            r["minters"] = len({x["topics"][2] for x in logs if len(x.get("topics", [])) > 2})
            sample_txs = []
            for x in logs[:2]:
                txh = x.get("transactionHash")
                try:
                    tx = rpc_call("eth_getTransactionByHash", [txh], 10)
                    sample_txs.append({"tx": txh, "value": tx.get("value"), "from": tx.get("from")})
                except Exception as e:
                    sample_txs.append({"tx": txh, "error": str(e)[:80]})
            r["sample_mint_txs"] = sample_txs
        else:
            r["earliest_block"] = None
        views = {
            "totalSupply": (sel("totalSupply()"), dec_uint),
            "totalMinted": (sel("totalMinted()"), dec_uint),
            "freeClaimed": (sel("freeClaimed()"), dec_uint),
            "freeMinted": (sel("freeMinted()"), dec_uint),
            "FREE_SUPPLY": (sel("FREE_SUPPLY()"), dec_uint),
            "MAX_SUPPLY": (sel("MAX_SUPPLY()"), dec_uint),
            "mintOpen": (sel("mintOpen()"), dec_bool),
            "price": (sel("price()"), dec_uint),
            "owner": (sel("owner()"), dec_addr),
            "quote_user_1": (sel("quote(address,uint256)") + ua + format(1, "064x"), dec_uint),
            "costOf_user_1": (sel("costOf(address,uint256)") + ua + format(1, "064x"), dec_uint),
            "mintedBy_user": (sel("mintedBy(address)") + ua, dec_uint),
            "freeUsed_user": (sel("freeUsed(address)") + ua, dec_uint),
            "balanceOf_user": (sel("balanceOf(address)") + ua, dec_uint),
        }
        for k, (data, dec) in views.items():
            r[k] = dec(call(a, data))
        out["triage"][c.get("name") or a] = r
        print(r["name"], "| earliest:", r.get("earliest_block"), r.get("earliest_wib"),
              "| logs:", r.get("log_count"), "| totalSupply:", r.get("totalSupply"),
              "| freeClaimed:", r.get("freeClaimed"), "| FREE_SUPPLY:", r.get("FREE_SUPPLY"),
              "| quote(user,1):", r.get("quote_user_1"), "| costOf(user,1):", r.get("costOf_user_1"),
              "| price:", r.get("price"), "| mintedBy(user):", r.get("mintedBy_user"),
              "| tx values:", [t.get("value") for t in r.get("sample_mint_txs", [])])
    json.dump(out, open("triage-firstseen-2026-11-06-0101.json", "w"), indent=1)
    print("wrote triage-firstseen-2026-11-06-0101.json")

if __name__ == "__main__":
    main()
