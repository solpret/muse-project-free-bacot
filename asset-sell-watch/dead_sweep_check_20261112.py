#!/usr/bin/env python3
"""Dead-asset sweep 2026-11-12: refresh latest Transfer per pending-swap coin.

Read-only. Uses Ankr ankr_getLogs (Transfer topic) from each token's last
known activity block to latest, following nextPageToken. Writes a compact
summary JSON; prints only the summary. Never fabricates 0: a failed read
is reported as error, not as 'no activity'.
New entries vs yesterday: BITCAT, LUCKY777, WNO, AMBR, CSAGENT, CHEEMSA, NEB.
CHEEMSA from-block resolved via eth_getTransactionReceipt of its mint tx.
"""
import json, os, sys, urllib.request, datetime

sys.path.insert(0, os.path.expanduser("~/workspace/custom-connectors/custom.ankr/bin"))
from ankr import ankr_post  # noqa: E402

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
RPC = "https://bsc-dataseed.binance.org"

TOKENS = {
    # symbol: (token, from_block = last known activity block, last_update)
    "POA": ("0x21bc810818d9c9c767ba73c543f67a989fb5a543", 131782127, "2026-11-03"),
    "BNBbaby": ("0xd0079025a9bb66a7a1de991de2e4326faba35729", 132493851, "2026-11-09"),
    "PATCH": ("0xBbA053567846842F95C060867a5C9eb6b3983c80", 132010167, "2026-11-06"),
    "QAGENT": ("0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", 132480308, "2026-11-09"),
    "YYDS": ("0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 132480278, "2026-11-09"),
    "Bianjiayou": ("0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", 132188533, "2026-11-07"),
    "PACTURE": ("0x10b80088fDAf9363d83671BE66b64f231f9e92f6", 132424186, "2026-11-08"),
    "ORBITA": ("0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", 132419616, "2026-11-08"),
    "WW3": ("0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", 132492474, "2026-11-09"),
    "POSTAGE": ("0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", 132506559, "2026-11-09"),
    "MALTA": ("0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0", 132590151, "2026-11-09"),
    "JINMA": ("0xe4517E6718b24D5725956ac7A90686592a7b1539", 132595827, "2026-11-09"),
    "THYRK": ("0x3b8747D067B2Ed8565330667128260C2a4954300", 132687553, "2026-11-10"),
    "BITCAT": ("0x8708EE82fa34c58431532323530592ee3953e9d5", 132720605, "2026-11-10"),
    "LUCKY777": ("0xc6D4ec8CB889aFBa9f251606001457644E260f7D", 132719624, "2026-11-10"),
    "WNO": ("0x8C969a4CD49E4774908e667702C3d7C3ece164D0", 132743227, "2026-11-10"),
    "AMBR": ("0x88B06f59BdB54039AEBf1d308d8B9181a90385c1", 132755995, "2026-11-10"),
    "CSAGENT": ("0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D", 132760929, "2026-11-10"),
    "CHEEMSA": ("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", None, "2026-11-10"),
    "NEB": ("0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68", 132851962, "2026-11-11"),
}
CHEEMSA_MINT_TX = "0xbfc5a0482699ea2eae61954e81b03e7202df4966b7174b9dedaea3b90611d939"


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
        dt = datetime.datetime.fromtimestamp(
            ts, datetime.timezone(datetime.timedelta(hours=7)))
        return dt.strftime("%Y-%m-%d %H:%M WIB")
    except Exception as e:  # noqa: BLE001
        return f"timestamp unreadable: {e}"


def main():
    latest = int(rpc("eth_blockNumber", [])["result"], 16)
    out = {"latest_block": latest, "checked_at_wib": "2026-11-12 ~08:45",
           "tokens": {}}
    # Resolve CHEEMSA from-block from its mint tx receipt.
    cheemsa_from = TOKENS["CHEEMSA"][1]
    if cheemsa_from is None:
        try:
            r = rpc("eth_getTransactionReceipt", [CHEEMSA_MINT_TX])
            cheemsa_from = int(r["result"]["blockNumber"], 16)
            out["cheemsa_from_block_resolved"] = cheemsa_from
        except Exception as e:  # noqa: BLE001
            out["cheemsa_from_block_error"] = str(e)
            cheemsa_from = latest  # fall back: empty window, read will still be attempted
    TOKENS["CHEEMSA"] = (TOKENS["CHEEMSA"][0], cheemsa_from, TOKENS["CHEEMSA"][2])
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
        "~/workspace/asset-sell-watch/dead-sweep-check-2026-11-12.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
