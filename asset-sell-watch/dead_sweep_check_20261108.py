#!/usr/bin/env python3
"""Dead-asset sweep 2026-11-08: refresh latest Transfer per pending-swap coin.

Read-only. Uses Ankr ankr_getLogs (Transfer topic) from each token's last
known activity block to latest, following nextPageToken. Writes a compact
summary JSON; prints only the summary. Never fabricates 0: a failed read
is reported as error, not as 'no activity'.
KAGENT excluded: already removed from pending-swaps.json 2026-11-08 ~01:57
(refund phase) — out of sweep scope, not a sweep discard.
"""
import json, os, sys, urllib.request

sys.path.insert(0, os.path.expanduser("~/workspace/custom-connectors/custom.ankr/bin"))
from ankr import ankr_post  # noqa: E402

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
RPC = "https://bsc-dataseed.binance.org"

TOKENS = {
    # symbol: (token, from_block = last known activity block, last_update)
    "POA": ("0x21bc810818d9c9c767ba73c543f67a989fb5a543", 131782127, "2026-11-03"),
    "BNBbaby": ("0xd0079025a9bb66a7a1de991de2e4326faba35729", 132113416, "2026-11-07"),
    "PATCH": ("0xBbA053567846842F95C060867a5C9eb6b3983c80", 132010167, "2026-11-06"),
    "QAGENT": ("0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", 132112799, "2026-11-07"),
    "YYDS": ("0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 132073059, "2026-11-07"),
    "Bianjiayou": ("0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", 132024201, "2026-11-06"),
    "PACTURE": ("0x10b80088fDAf9363d83671BE66b64f231f9e92f6", 132112929, "2026-11-07"),
    "ORBITA": ("0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", 132156462, "2026-11-07"),
    "WW3": ("0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", 132287716, "2026-11-08"),
}


def rpc(method, params):
    req = urllib.request.Request(
        RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                              "params": params}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def latest_transfer(token, frm, to):
    """Return (max_block, tx_hash, n_logs, error). Follows pagination."""
    params = {"blockchain": "bsc", "address": [token],
              "fromBlock": hex(frm), "toBlock": hex(to),
              "pageSize": 1000, "decodeLogs": False,
              "topics": [[TRANSFER_TOPIC]]}
    max_block, max_tx, n = 0, None, 0
    token_page = None
    pages = 0
    while True:
        p = dict(params)
        if token_page:
            p["pageToken"] = token_page
        try:
            body = ankr_post("ankr_getLogs", p)
        except Exception as e:  # noqa: BLE001
            return max_block, max_tx, n, f"ankr error: {e}"
        if "error" in body:
            return max_block, max_tx, n, f"ankr json error: {body['error']}"
        res = body.get("result", {})
        logs = res.get("logs", [])
        pages += 1
        for lg in logs:
            n += 1
            b = int(lg.get("blockNumber", "0x0"), 16)
            if b > max_block:
                max_block, max_tx = b, lg.get("transactionHash")
        token_page = res.get("nextPageToken")
        if not token_page or pages >= 10:
            break
    return max_block, max_tx, n, None


def block_time_wib(block):
    try:
        b = rpc("eth_getBlockByNumber", [hex(block), False])
        ts = int(b["result"]["timestamp"], 16)
        import datetime
        dt = datetime.datetime.fromtimestamp(
            ts, datetime.timezone(datetime.timedelta(hours=7)))
        return dt.strftime("%Y-%m-%d %H:%M WIB")
    except Exception as e:  # noqa: BLE001
        return f"timestamp unreadable: {e}"


def main():
    latest = int(rpc("eth_blockNumber", [])["result"], 16)
    out = {"latest_block": latest, "checked_at_wib": "2026-11-08 ~08:45",
           "tokens": {}}
    for sym, (token, frm, last_update) in TOKENS.items():
        mb, tx, n, err = latest_transfer(token, frm, latest)
        entry = {"from_block": frm, "to_block": latest,
                 "logs_in_window": n, "last_update_recorded": last_update}
        if err:
            entry["status"] = "READ FAILED — not counted as no activity"
            entry["error"] = err
        elif n == 0:
            entry["status"] = "no Transfer since from_block"
            entry["latest_transfer_block"] = None
        else:
            entry["status"] = "activity found"
            entry["latest_transfer_block"] = mb
            entry["latest_transfer_tx"] = tx
            entry["latest_transfer_time_wib"] = block_time_wib(mb)
            entry["newer_than_recorded"] = mb > frm
        out["tokens"][sym] = entry
    path = os.path.expanduser(
        "~/workspace/asset-sell-watch/dead-sweep-check-2026-11-08.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
