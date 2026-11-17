#!/usr/bin/env python3
"""Dead-asset sweep 2026-11-16: refresh activity signals per pending-swap coin.

Read-only. Methods:
  1. Latest block via fast_rpc.race (eth_blockNumber).
  2. Tail-window Transfer scan: eth_getLogs (Transfer topic) over
     latest-2000..latest for all 18 tokens, as ONE batch raced across
     endpoints. A success proves (no) activity only inside that window;
     it does NOT prove no activity since last_update.
  3. DexScreener token endpoint for all 18 tokens: pair existence +
     reserves is the market-activity signal (pair formation would be a
     last-update event for these no-pair coins).
  4. POA channel check (poagi.top DNS + HTTP) is done separately in the
     run shell, not here.
Never fabricates 0: a failed read is reported as error, not as 'no activity'.
"""
import json, os, sys, urllib.request

sys.path.insert(0, os.path.expanduser("~/workspace/fast_exec"))
import fast_rpc  # noqa: E402

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

TOKENS = {
    "POA": ("0x21bc810818d9c9c767ba73c543f67a989fb5a543", 131782127, "2026-11-03"),
    "BNBbaby": ("0xd0079025a9bb66a7a1de991de2e4326faba35729", 132493851, "2026-11-09"),
    "PATCH": ("0xBbA053567846842F95C060867a5C9eb6b3983c80", 132010167, "2026-11-06"),
    "QAGENT": ("0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", 132480308, "2026-11-09"),
    "YYDS": ("0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 132480278, "2026-11-09"),
    "Bianjiayou": ("0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", 132188533, "2026-11-07"),
    "PACTURE": ("0x10b80088fDAf9363d83671BE66b64f231f9e92f6", 132424186, "2026-11-08"),
    "ORBITA": ("0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", 132419616, "2026-11-08"),
    "WW3": ("0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", 132492474, "2026-11-12"),
    "POSTAGE": ("0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", 132506559, "2026-11-09"),
    "MALTA": ("0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0", 132590151, "2026-11-09"),
    "JINMA": ("0xe4517E6718b24D5725956ac7A90686592a7b1539", 132595827, "2026-11-09"),
    "THYRK": ("0x3b8747D067B2Ed8565330667128260C2a4954300", 132687553, "2026-11-10"),
    "LUCKY777": ("0xc6D4ec8CB889aFBa9f251606001457644E260f7D", 132719624, "2026-11-10"),
    "WNO": ("0x8C969a4CD49E4774908e667702C3d7C3ece164D0", 132743227, "2026-11-10"),
    "AMBR": ("0x88B06f59BdB54039AEBf1d308d8B9181a90385c1", 132755995, "2026-11-10"),
    "CHEEMSA": ("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", 132764116, "2026-11-10"),
    "NEB": ("0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68", 132851962, "2026-11-11"),
}

TAIL = 2000


def main():
    out = {"checked_at_wib": "2026-11-16 ~08:37", "tokens": {}, "discarded": []}
    try:
        latest_hex = fast_rpc.race("eth_blockNumber", [])
        latest = int(latest_hex, 16)
        out["latest_block"] = latest
        out["latest_block_source"] = "fast_rpc.race eth_blockNumber"
    except Exception as e:  # noqa: BLE001
        out["latest_block"] = None
        out["latest_block_error"] = f"{type(e).__name__}: {e}"
        latest = None

    # --- Tail-window Transfer scan (one batch, raced) ---
    if latest is not None:
        frm = hex(latest - TAIL)
        to = hex(latest)
        calls = []
        for sym, (token, _anchor, _lu) in TOKENS.items():
            calls.append({"method": "eth_getLogs", "params": [{
                "fromBlock": frm, "toBlock": to, "address": token,
                "topics": [TRANSFER_TOPIC]}]})
        try:
            results = fast_rpc.batch_race(calls, timeout=15)
            for (sym, (_t, _a, lu)), res in zip(TOKENS.items(), results):
                entry = {"from_block": latest - TAIL, "to_block": latest,
                         "window_blocks": TAIL, "last_update_recorded": lu}
                if isinstance(res, dict) and "error" in res:
                    entry["status"] = "READ FAILED — not counted as no activity"
                    entry["error"] = str(res["error"])
                elif isinstance(res, list):
                    entry["logs_in_tail_window"] = len(res)
                    if len(res) == 0:
                        entry["status"] = "no Transfer in tail window (does NOT prove no activity since last_update)"
                    else:
                        mb = max(int(lg.get("blockNumber", "0x0"), 16) for lg in res)
                        entry["status"] = "ACTIVITY FOUND in tail window"
                        entry["latest_transfer_block"] = mb
                        entry["latest_transfer_tx"] = next(
                            (lg.get("transactionHash") for lg in res
                             if int(lg.get("blockNumber", "0x0"), 16) == mb), None)
                else:
                    entry["status"] = "READ FAILED — unexpected shape"
                    entry["error"] = repr(res)[:300]
                out["tokens"][sym] = entry
            out["tail_scan"] = "batch_race ok"
        except Exception as e:  # noqa: BLE001
            out["tail_scan"] = f"FAILED: {type(e).__name__}: {e}"
            for sym, (_t, _a, lu) in TOKENS.items():
                out["tokens"][sym] = {
                    "status": "READ FAILED — not counted as no activity",
                    "error": out["tail_scan"], "last_update_recorded": lu}

    # --- DexScreener pair check (market activity signal) ---
    addrs = ",".join(t[0] for t in TOKENS.values())
    url = f"https://api.dexscreener.com/tokens/v1/bsc/{addrs}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            pairs = json.load(r)
        by_token = {}
        for p in pairs or []:
            by_token.setdefault(p.get("baseToken", {}).get("address", "").lower(),
                                []).append(p)
        dex = {}
        for sym, (token, _a, _lu) in TOKENS.items():
            ps = by_token.get(token.lower(), [])
            if not ps:
                dex[sym] = {"pairs": 0, "status": "no pair on DexScreener"}
            else:
                dex[sym] = {"pairs": len(ps), "status": "PAIR EXISTS",
                            "pairs_detail": [
                                {"dex": p.get("dexId"), "pair": p.get("pairAddress"),
                                 "liq_usd": (p.get("liquidity") or {}).get("usd"),
                                 "pair_created_at": p.get("pairCreatedAt")}
                                for p in ps]}
        out["dexscreener"] = dex
    except Exception as e:  # noqa: BLE001
        out["dexscreener"] = {"status": "READ FAILED", "error": f"{type(e).__name__}: {e}"}

    path = os.path.expanduser(
        "~/workspace/asset-sell-watch/dead-sweep-check-2026-11-16.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
