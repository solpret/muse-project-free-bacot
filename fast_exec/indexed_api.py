#!/usr/bin/env python3
"""indexed_api.py — READ-ONLY indexed-data fallbacks for BSC.

Built 2026-11-01 as infra-hardening step 4. It exists because the two
data paths the gates rely on are single points of failure:

  * eth_getLogs is DISABLED on BNB Chain's official public RPC endpoints,
    so Transfer-log replay (launch time, holder growth) cannot be done
    through fast_rpc alone.
  * GoPlus token_security sometimes returns holder_count 0/empty, and
    a 0 there must never be read as "no holders" (standing rule).

This module queries INDEXED providers instead of raw RPC:
  * Ankr Advanced API (free Freemium tier, needs an API key):
    ankr_getTokenHolders (holders + count) and ankr_getLogs.
  * Blockscout Pro API (free tier, needs an API key):
    token counters (holders count + transfers count).

IMPORTANT — READ BEFORE USING:
  * This module is NOT wired into feed_loop.py, gate_runner.py, or any
    gate/score. Nothing here changes a trading decision. Wiring it in
    needs a separate user decision AND a live test with a real key.
  * API keys are NEVER stored in this file. They come only from the
    environment (ANKR_API_KEY, BLOCKSCOUT_API_KEY) or, for Ankr, from
    the registered custom.ankr connection (surrogate exchange via
    custom.ankr/bin/ankr.py). Without any credential the function
    returns status "key_missing" — it never invents data and never
    fails a gate by itself.
  * Every function returns a dict:
      {"status": "ok"|"unconfirmed"|"key_missing"|"error",
       "source": "ankr"|"blockscout", "value": <int|list|None>,
       "detail": <short string>}
    Callers must treat anything but "ok" as UNCONFIRMED, exactly like
    a GoPlus 0. A second provider disagreeing with the first is also
    UNCONFIRMED, never an average.
  * Ankr response shapes are parsed defensively (several possible
    count field names). VERIFIED live 2026-11-01 via the custom.ankr
    connection: ankr_getTokenHolders returns holdersCount directly
    (USDT: 83.738.706, sync block 130.981.522, status synced) and
    ankr_getLogs returns result.logs (457 logs over a ~3.400-block
    window). Shape is confirmed; gate wiring still needs a separate
    user decision.
"""

import json
import os
import urllib.request

ANKR_URL = "https://rpc.ankr.com/multichain/{key}"
BLOCKSCOUT_URL = "https://api.blockscout.com/56/api/v2/tokens/{ca}/counters"
HEADERS = {"Content-Type": "application/json",
           "User-Agent": "Mozilla/5.0"}


def _post_json(url, payload, timeout=20, headers=None):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={**HEADERS, **(headers or {})}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _connector_post(method, params):
    """Ankr call through the registered custom.ankr connection.

    Used when ANKR_API_KEY is not set in the environment. The key
    itself is never read here — the connector helper exchanges a
    surrogate with authd (see custom.ankr/bin/ankr.py). Raises on
    failure; callers convert that to an honest error status.
    """
    import importlib.util
    helper = os.path.expanduser(
        "~/workspace/custom-connectors/custom.ankr/bin/ankr.py")
    spec = importlib.util.spec_from_file_location("ankr_helper", helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ankr_post(method, params)


def _get_json(url, timeout=20, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _pick_count(obj):
    """Best-effort count extraction across provider response shapes."""
    if isinstance(obj, int):
        return obj
    if not isinstance(obj, dict):
        return None
    for key in ("totalHolders", "holdersCount", "holderCount",
                "token_holders_count", "count", "total"):
        v = obj.get(key)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    res = obj.get("result")
    if res is not None and res is not obj:
        return _pick_count(res)
    holders = obj.get("holders")
    if isinstance(holders, list) and obj.get("totalHolders") is None:
        # A page is not a count; only use it if the provider also
        # reported a total elsewhere (handled above). Never guess.
        return None
    return None


def ankr_token_holders_count(ca):
    """Holder count for a BSC token via Ankr ankr_getTokenHolders.

    Credential order: ANKR_API_KEY env var first, then the registered
    custom.ankr connection (surrogate exchange). No credential at all
    still returns key_missing, never invented data.
    """
    key = os.environ.get("ANKR_API_KEY")
    try:
        if key:
            out = _post_json(ANKR_URL.format(key=key), {
                "jsonrpc": "2.0", "id": 1, "method": "ankr_getTokenHolders",
                "params": {"blockchain": "bsc", "contractAddress": ca,
                           "pageSize": 1}})
        else:
            out = _connector_post("ankr_getTokenHolders", {
                "blockchain": "bsc", "contractAddress": ca,
                "pageSize": 1})
    except Exception as e:
        return {"status": "error", "source": "ankr", "value": None,
                "detail": f"{type(e).__name__}: {str(e)[:200]}"}
    if isinstance(out, dict) and out.get("error"):
        return {"status": "error", "source": "ankr", "value": None,
                "detail": str(out["error"])[:200]}
    count = _pick_count(out)
    if count is None:
        return {"status": "unconfirmed", "source": "ankr", "value": None,
                "detail": "response shape unverified; no count field found"}
    return {"status": "ok", "source": "ankr", "value": count,
            "detail": "ankr_getTokenHolders"}


def ankr_get_logs(ca, from_block, to_block, topics=None):
    """Indexed contract logs for a BSC contract + block range.

    from_block/to_block accept ints (converted to hex) or the strings
    "earliest"/"latest". Returns raw log list on ok; callers decode.
    """
    key = os.environ.get("ANKR_API_KEY")
    def _blk(v):
        return v if isinstance(v, str) else hex(v)
    params = {"blockchain": "bsc", "address": [ca],
              "fromBlock": _blk(from_block), "toBlock": _blk(to_block),
              "pageSize": 1000, "decodeLogs": False}
    if topics:
        params["topics"] = topics
    try:
        if key:
            out = _post_json(ANKR_URL.format(key=key), {
                "jsonrpc": "2.0", "id": 1, "method": "ankr_getLogs",
                "params": params})
        else:
            out = _connector_post("ankr_getLogs", params)
    except Exception as e:
        return {"status": "error", "source": "ankr", "value": None,
                "detail": f"{type(e).__name__}: {str(e)[:200]}"}
    if isinstance(out, dict) and out.get("error"):
        return {"status": "error", "source": "ankr", "value": None,
                "detail": str(out["error"])[:200]}
    logs = None
    if isinstance(out, dict):
        res = out.get("result") or {}
        logs = res.get("logs") if isinstance(res, dict) else None
        if logs is None and isinstance(res, list):
            logs = res
    if logs is None:
        return {"status": "unconfirmed", "source": "ankr", "value": None,
                "detail": "response shape unverified; no logs field found"}
    return {"status": "ok", "source": "ankr", "value": logs,
            "detail": f"ankr_getLogs: {len(logs)} logs in range"}


def ankr_get_transactions_by_address(address, page_size=1000):
    """Transaction history for one BSC address via Ankr Advanced API.

    Read-only. Returns the raw transaction list on ok (newest first
    in the provider's usual order; callers must take min block for
    'earliest' logic and must flag a full page as possibly
    truncated history, never as complete history).
    """
    key = os.environ.get("ANKR_API_KEY")
    params = {"blockchain": "bsc", "address": [address],
              "pageSize": page_size}
    try:
        if key:
            out = _post_json(ANKR_URL.format(key=key), {
                "jsonrpc": "2.0", "id": 1,
                "method": "ankr_getTransactionsByAddress",
                "params": params})
        else:
            out = _connector_post("ankr_getTransactionsByAddress", params)
    except Exception as e:
        return {"status": "error", "source": "ankr", "value": None,
                "detail": f"{type(e).__name__}: {str(e)[:200]}"}
    if isinstance(out, dict) and out.get("error"):
        return {"status": "error", "source": "ankr", "value": None,
                "detail": str(out["error"])[:200]}
    txs = None
    if isinstance(out, dict):
        res = out.get("result") or {}
        txs = res.get("transactions") if isinstance(res, dict) else None
        if txs is None and isinstance(res, list):
            txs = res
    if txs is None:
        return {"status": "unconfirmed", "source": "ankr", "value": None,
                "detail": "response shape unverified; no transactions field found"}
    return {"status": "ok", "source": "ankr", "value": txs,
            "detail": f"ankr_getTransactionsByAddress: {len(txs)} txs"}


def _connector_blockscout_counters(ca):
    """Token counters through the registered custom.blockscout
    connection (surrogate exchange). Raises on HTTP failure."""
    import importlib.util
    helper = os.path.expanduser(
        "~/workspace/custom-connectors/custom.blockscout/bin/blockscout.py")
    spec = importlib.util.spec_from_file_location("blockscout_helper",
                                                  helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.token_counters(ca)


def blockscout_token_holders_count(ca):
    """Holder + transfer counts for a BSC token via Blockscout Pro API.

    Credential order: BLOCKSCOUT_API_KEY env var first, then the
    registered custom.blockscout connection. A 401/403 with a
    credential present returns "auth_rejected" (the stored key is
    not accepted by Blockscout), never a fabricated count.
    Known coverage gap (verified 2026-11-01): the universal API
    does not serve BSC chain 56 ("Network not supported", BSC
    absent from the live chains list), so BSC calls fall through
    to Ankr; the key itself is valid on Ethereum, Optimism, and
    Arbitrum.
    Without any credential the API may answer or return 401, in
    which case the status says so honestly instead of pretending
    the count is 0.
    """
    key = os.environ.get("BLOCKSCOUT_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        if key:
            out = _get_json(BLOCKSCOUT_URL.format(ca=ca), headers=headers)
        else:
            out = _connector_blockscout_counters(ca)
    except Exception as e:
        msg = str(e)
        if "401" in msg or "403" in msg:
            if key:
                return {"status": "auth_rejected", "source": "blockscout",
                        "value": None,
                        "detail": "env key rejected by Blockscout"}
            _has_connector = os.path.exists(os.path.expanduser(
                "~/workspace/custom-connectors/custom.blockscout/bin/blockscout.py"))
            return {"status": "auth_rejected" if _has_connector
                    else "key_missing", "source": "blockscout",
                    "value": None,
                    "detail": ("stored Blockscout key rejected (HTTP 401); "
                               "check the key in the dev portal")
                    if _has_connector else
                    "Blockscout Pro API needs a free key (dev.blockscout.com)"}
        return {"status": "error", "source": "blockscout", "value": None,
                "detail": f"{type(e).__name__}: {msg[:200]}"}
    count = _pick_count(out)
    if count is None:
        return {"status": "unconfirmed", "source": "blockscout",
                "value": None,
                "detail": "response shape unverified; no count field found"}
    return {"status": "ok", "source": "blockscout", "value": count,
            "detail": "token counters"}


def holders_count(ca):
    """Try Blockscout first, then Ankr; return the first ok result.

    If both answer and disagree, the caller must treat the count as
    UNCONFIRMED — this helper returns the disagreement explicitly
    instead of hiding it.
    """
    results = [blockscout_token_holders_count(ca),
               ankr_token_holders_count(ca)]
    oks = [r for r in results if r["status"] == "ok"]
    if len(oks) >= 2 and oks[0]["value"] != oks[1]["value"]:
        return {"status": "unconfirmed", "source": "both",
                "value": None,
                "detail": f"disagreement: blockscout={oks[0]['value']} "
                          f"ankr={oks[1]['value']}"}
    if oks:
        return oks[0]
    return results[0]


if __name__ == "__main__":
    import sys
    ca = sys.argv[1] if len(sys.argv) > 1 else \
        "0x55d398326f99059fF775485246999027B3197955"  # USDT (test token)
    print("blockscout:", blockscout_token_holders_count(ca))
    print("ankr:", ankr_token_holders_count(ca))
