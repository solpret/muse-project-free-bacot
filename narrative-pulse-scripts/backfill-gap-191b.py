#!/usr/bin/env python3
"""One-off backfill scan tracked-wallet (BSC) for the gap skipped by
run 191: blocks 133700627..133746748 (46,121 blocks, ~15:11-21:00 WIB
15 Nov 2026). User-approved 2026-11-15 ~21:16 WIB.

Standalone copy of the canonical driver logic
(~/workspace/narrative-pulse/tracked-mint-scan-rpc.py) WITHOUT the
gap policy (that policy is what skipped this window) and WITHOUT
writing to the routine state file (last_run/watermark belong to run
191, already advanced to 133748748).

READ-ONLY + flag only: NEVER previews, mints, approves, signs or
buys. A >25% trigger (>=14 entities) is FLAGGED in the findings
JSON only — no execution.

RPC: bloXroute public https://bsc.rpc.blxrbdn.com, plain urllib.
Slow mode: 2000-block chunks, 10 s pause between getLogs calls,
403 backoff 30 s then 60 s (max 2 retries). A chunk failing after
retry is recorded as failed/unverified — NEVER treated as 0 mints.

Checkpoint after every chunk:
  ~/workspace/narrative-pulse/scan-runs/run191b-backfill-progress.json
Findings:
  ~/workspace/narrative-pulse/scan-runs/run191b-backfill-gap-findings.json

Usage: python3 backfill-gap-191b.py [--from-block B] [--to-block B]
Resume: re-running picks up completed chunks from the progress file.
"""
import ast
import datetime
import json
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace" / "narrative-pulse"
STATE_PATH = NP / "tracked-wallet-mint-scan-state.json"
TIER_AB_PATH = NP / "tier-ab-watch-state.json"
WALLET_CONF_PATH = HOME / "workspace" / "ponyin-tools" / "live-executor-draft" / "wallet_confirmation.py"
SCAN_RUNS_DIR = NP / "scan-runs"
PROGRESS_PATH = SCAN_RUNS_DIR / "run191b-backfill-progress.json"
FINDINGS_PATH = SCAN_RUNS_DIR / "run191b-backfill-gap-findings.json"

RPC_URL = "https://bsc.rpc.blxrbdn.com"
USER_WALLETS = {
    "0xeb237f6f9fb4e826739f0954e9768914f28b2c2e",
    "0xcf3c6fc1bf670a8d3f03436395286f86dbee7418",
}
SIGNAL_MIN_ENTITIES = 12
AUTO_MINT_MIN_ENTITIES = 14
MAX_GETLOGS_CONTRACTS = 5
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
TRANSFER_TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TRANSFER_SINGLE_TOPIC0 = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
CHUNK_BLOCKS = 2000
SLOW_DELAY_S = 10
SLOW_403_BACKOFF_S = (30, 60)

ENTITY_CLUSTERS = {}
JAK = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 133700627
TO_BLOCK = 133746748


def wib(ts):
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(int(ts), tz=JAK).strftime(
        "%Y-%m-%d %H:%M:%S WIB")


class RpcError(Exception):
    pass


def rpc_call(method, params, timeout=60, retries=1):
    """Slow-mode call: up to 3 attempts; 403 backoff 30 s then 60 s."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    last_err = None
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            req = urllib.request.Request(
                RPC_URL, data=body,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            if "error" in d:
                raise RpcError(json.dumps(d["error"])[:300])
            return d.get("result")
        except RpcError as e:
            last_err = e
            if attempt < max_attempts - 1:
                time.sleep(SLOW_403_BACKOFF_S[min(
                    attempt, len(SLOW_403_BACKOFF_S) - 1)]
                    if "403" in str(e) else 2)
        except Exception as e:
            last_err = RpcError(f"{type(e).__name__}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(SLOW_403_BACKOFF_S[min(
                    attempt, len(SLOW_403_BACKOFF_S) - 1)]
                    if "403" in str(last_err) else 2)
    raise last_err


def load_wallet_set():
    tier = json.load(open(TIER_AB_PATH))
    tier_wallets = [w.lower() for w in tier["wallets"].keys()]
    tree = ast.parse(open(WALLET_CONF_PATH).read())
    feed = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TRACKED_WALLETS":
                    feed = [e.value.lower() for e in node.value.elts
                            if isinstance(e, ast.Constant)]
    uniq, overlap = [], 0
    for w in tier_wallets + feed:
        if w in uniq:
            overlap += 1
            continue
        uniq.append(w)
    uniq = [w for w in uniq if w not in USER_WALLETS]
    return {"wallets": uniq, "tier_ab_count": len(tier_wallets),
            "feed_count": len(feed), "overlap": overlap,
            "total_unique": len(uniq)}


def fold_entities(wallets):
    if not ENTITY_CLUSTERS:
        return len(wallets), len(wallets), "linkage belum diverifikasi"
    remaining = set(wallets)
    entities = 0
    for members in ENTITY_CLUSTERS.values():
        hit = remaining.intersection({m.lower() for m in members})
        if hit:
            entities += 1
            remaining -= hit
    entities += len(remaining)
    return entities, len(wallets), "cluster folding applied"


def eth_call(to, data):
    try:
        return rpc_call("eth_call", [{"to": to, "data": data}, "latest"],
                        timeout=20, retries=0)
    except Exception:
        return None


def _decode_string(hexdata):
    try:
        raw = bytes.fromhex(hexdata[2:])
        if len(raw) < 64:
            return None
        off = int.from_bytes(raw[0:32], "big")
        ln = int.from_bytes(raw[off:off + 32], "big")
        return raw[off + 32:off + 32 + ln].decode("utf-8", errors="replace")
    except Exception:
        return None


def token_meta(address):
    name = _decode_string(eth_call(address, "0x06fdde03") or "")
    symbol = _decode_string(eth_call(address, "0x95d89b41") or "")
    dec_raw = eth_call(address, "0x313ce567")
    decimals = None
    try:
        if dec_raw:
            decimals = int(dec_raw, 16)
    except Exception:
        decimals = None
    return {"name": name, "symbol": symbol, "decimals": decimals}


def get_logs_chunked(from_block, to_block, topics, address=None):
    cb = CHUNK_BLOCKS
    logs = []
    cur = from_block
    first = True
    while cur <= to_block:
        end = min(cur + cb - 1, to_block)
        if not first:
            time.sleep(SLOW_DELAY_S)
        first = False
        f = {"fromBlock": hex(cur), "toBlock": hex(end), "topics": topics}
        if address:
            f["address"] = address
        res = rpc_call("eth_getLogs", [f], timeout=60, retries=1)
        if res:
            logs.extend(res)
        cur = end + 1
    return logs


def save_progress(progress):
    json.dump(progress, open(PROGRESS_PATH, "w"), indent=1)


def main():
    from_block, to_block = FROM_BLOCK, TO_BLOCK
    if "--from-block" in sys.argv:
        from_block = int(sys.argv[sys.argv.index("--from-block") + 1])
    if "--to-block" in sys.argv:
        to_block = int(sys.argv[sys.argv.index("--to-block") + 1])

    state = json.load(open(STATE_PATH))
    known = set()
    for f in state.get("reported_findings", []):
        for m in f.get("mints", []):
            if m.get("tx"):
                known.add(m["tx"].lower())
    machine = {m["address"].lower(): m
               for m in state.get("machine_tokens", [])}

    wset = load_wallet_set()
    wallets = wset["wallets"]
    wtopics = ["0x000000000000000000000000" + w[2:] for w in wallets]
    print(f"BACKFILL 191b wallets={len(wallets)} "
          f"(tier-ab {wset['tier_ab_count']} + feed {wset['feed_count']}, "
          f"overlap {wset['overlap']}) window={from_block}-{to_block} "
          f"({to_block - from_block + 1} blocks) known_tx={len(known)} "
          f"machine_tokens={len(machine)}", flush=True)

    chunks = []
    cur = from_block
    while cur <= to_block:
        end = min(cur + CHUNK_BLOCKS - 1, to_block)
        chunks.append((cur, end))
        cur = end + 1
    print(f"BACKFILL 191b chunks={len(chunks)}", flush=True)

    # Resume from progress file if present.
    mints = []
    failed_chunks = []
    done_chunks = set()
    if PROGRESS_PATH.exists():
        try:
            prog = json.load(open(PROGRESS_PATH))
            done_chunks = {tuple(c) for c in prog.get("chunks_done", [])}
            mints = prog.get("mints", [])
            failed_chunks = prog.get("failed_chunks", [])
            print(f"BACKFILL 191b RESUME: {len(done_chunks)} chunks done, "
                  f"{len(mints)} mints so far, "
                  f"{len(failed_chunks)} failed chunks recorded",
                  flush=True)
        except Exception as e:
            print(f"BACKFILL 191b progress unreadable ({e}) — fresh start",
                  flush=True)

    block_ts_cache = {}
    tx_cache = {}

    def block_ts(block):
        if block not in block_ts_cache:
            r = rpc_call("eth_getBlockByNumber", [hex(block), False],
                         timeout=20, retries=1)
            block_ts_cache[block] = int(r["timestamp"], 16)
        return block_ts_cache[block]

    def tx_of(txhash):
        if txhash not in tx_cache:
            tx_cache[txhash] = rpc_call("eth_getTransactionByHash",
                                        [txhash], timeout=20, retries=1)
        return tx_cache[txhash]

    first_log_call = True
    for ci, (cfrom, cto) in enumerate(chunks):
        if (cfrom, cto) in done_chunks:
            continue
        chunk_failed = False
        for topics, kind_label in (
                ([TRANSFER_TOPIC0, ZERO_TOPIC, wtopics], "Transfer"),
                ([TRANSFER_SINGLE_TOPIC0, None, ZERO_TOPIC, wtopics],
                 "TransferSingle")):
            if not first_log_call:
                time.sleep(SLOW_DELAY_S)
            first_log_call = False
            try:
                f = {"fromBlock": hex(cfrom), "toBlock": hex(cto),
                     "topics": topics}
                res = rpc_call("eth_getLogs", [f], timeout=60, retries=1)
            except Exception as e:
                failed_chunks.append(
                    {"chunk": [cfrom, cto], "topics": kind_label,
                     "error": str(e)[:200]})
                print(f"  chunk {cfrom}-{cto} {kind_label} FAILED: {e}",
                      flush=True)
                chunk_failed = True
                continue
            for l in res or []:
                try:
                    txh = (l.get("transactionHash") or "").lower()
                    if not txh or txh in known:
                        continue
                    block = int(l["blockNumber"], 16)
                    contract = (l.get("address") or "").lower()
                    tps = l.get("topics") or []
                    to_wallet = ("0x" + tps[2][26:].lower()
                                 if kind_label == "Transfer" and len(tps) > 2
                                 else "0x" + tps[3][26:].lower()
                                 if len(tps) > 3 else None)
                    if kind_label == "TransferSingle":
                        token_id = (int(tps[4], 16)
                                    if len(tps) > 4 else None)
                        data = l.get("data") or "0x"
                        amount = (int(data, 16) if len(data) > 2 else None)
                        kind = "ERC1155"
                    elif len(tps) > 3:
                        token_id = int(tps[3], 16)
                        amount = None
                        kind = "ERC721"
                    else:
                        token_id = None
                        data = l.get("data") or "0x"
                        amount = (int(data, 16) if len(data) > 2 else None)
                        kind = "ERC20"
                    tx = tx_of(txh)
                    if tx is None:
                        value_wei = None
                        call_to = ""
                        free = None
                    else:
                        value_wei = int(tx.get("value", "0x0"), 16)
                        call_to = (tx.get("to") or "").lower()
                        free = value_wei == 0
                    mints.append({
                        "call_to": call_to,
                        "kind": kind,
                        "mint_contract": contract,
                        "name": None, "symbol": None,
                        "time_wib": wib(block_ts(block)),
                        "token_id": token_id,
                        "amount": (str(amount) if amount is not None
                                   else None),
                        "tx": txh,
                        "block": block,
                        "wallet": to_wallet,
                        "value_bnb": (value_wei / 1e18
                                      if value_wei is not None else None),
                        "free": free,
                    })
                except Exception as e:
                    print(f"  log parse failed: {e}", flush=True)
                    continue
        done_chunks.add((cfrom, cto))
        save_progress({
            "run": "191b",
            "window": {"from": from_block, "to": to_block},
            "chunks_total": len(chunks),
            "chunks_done": sorted([list(c) for c in done_chunks]),
            "chunks_done_count": len(done_chunks),
            "mints_so_far": len(mints),
            "mints": mints,
            "failed_chunks": failed_chunks,
            "updated_wib": wib(int(time.time())),
        })
        print(f"  [{len(done_chunks)}/{len(chunks)}] chunk {cfrom}-{cto} "
              f"done (failed={chunk_failed}), mints so far={len(mints)}",
              flush=True)

    all_verified = not failed_chunks

    # ---- token metadata (best-effort) + aggregate per contract
    by_contract = {}
    for m in mints:
        by_contract.setdefault(m["mint_contract"], []).append(m)
    for contract in by_contract:
        meta = token_meta(contract)
        for m in by_contract[contract]:
            m["name"] = meta["name"]
            m["symbol"] = meta["symbol"]
    machine_hits, anomalies = [], []
    findings_mints = []
    for contract, ms in by_contract.items():
        wallets_c = sorted({m["wallet"] for m in ms if m["wallet"]})
        entities, raw, note = fold_entities(wallets_c)
        entry = {"contract": contract, "mints": len(ms),
                 "wallets": wallets_c, "entities": entities,
                 "raw_wallets": raw, "entity_note": note,
                 "first_seen_wib": min((m["time_wib"] for m in ms if m["time_wib"]),
                                 default=None),
                 "kinds": sorted({m["kind"] for m in ms}),
                 "names": sorted({m["name"] for m in ms if m["name"]}),
                 "symbols": sorted({m["symbol"] for m in ms if m["symbol"]}),
                 "free_mints": sum(1 for m in ms if m["free"] is True),
                 "paid_mints": sum(1 for m in ms if m["free"] is False),
                 "free_unverified_mints": sum(1 for m in ms
                                              if m["free"] is None)}
        if contract in machine:
            mt = machine[contract]
            named = bool(entry["names"] or entry["symbols"])
            free_path = any(m["free"] is True for m in ms)
            if named or free_path:
                anomalies.append({**entry, "anomaly":
                                  "name/symbol appeared" if named
                                  else "free-mint path appeared"})
            else:
                machine_hits.append(entry)
                continue
        findings_mints.append(entry)

    signals, triggers = [], []
    for e in findings_mints:
        if e["entities"] >= AUTO_MINT_MIN_ENTITIES:
            triggers.append(e)
        elif e["entities"] >= SIGNAL_MIN_ENTITIES:
            signals.append(e)

    # ---- Leg D: targeted getLogs verification for candidates (max 5)
    verify = {}
    for e in (triggers + signals + anomalies)[:MAX_GETLOGS_CONTRACTS]:
        try:
            logs = get_logs_chunked(
                from_block, to_block, [TRANSFER_TOPIC0, ZERO_TOPIC],
                address=e["contract"])
            first_mints = [l for l in logs
                           if (l.get("topics") or [None, None])[1] == ZERO_TOPIC]
            verify[e["contract"]] = {
                "logs_returned": len(logs),
                "first_mint_logs": len(first_mints),
                "verified": len(first_mints) > 0}
        except Exception as ex:
            verify[e["contract"]] = {"error": str(ex)[:200], "verified": False}

    # ---- Paid trend (mint-tx values only; swap/buy trend UNVERIFIED)
    paid = {}
    tx_lookup_failed = 0
    for m in mints:
        if m["free"] is None:
            tx_lookup_failed += 1
            continue
        if m["free"]:
            continue
        to = m["call_to"] or m["mint_contract"]
        agg = paid.setdefault(to, {"wallets": set(), "txs": 0,
                                   "total_bnb_wei": 0})
        agg["wallets"].add(m["wallet"])
        agg["txs"] += 1
        agg["total_bnb_wei"] += int(m["value_bnb"] * 1e18)
    paid_trend = []
    for to, agg in sorted(paid.items(), key=lambda kv: -len(kv[1]["wallets"])):
        paid_trend.append({"contract": to, "wallets": len(agg["wallets"]),
                           "txs": agg["txs"],
                           "total_bnb": agg["total_bnb_wei"] / 1e18})

    summary = {
        "run": "191b",
        "status": "OK" if all_verified else "PARTIAL",
        "rpc": RPC_URL,
        "window": {"from": from_block, "to": to_block,
                   "blocks": to_block - from_block + 1},
        "gap_backfilled": {"from": FROM_BLOCK, "to": TO_BLOCK,
                           "blocks": TO_BLOCK - FROM_BLOCK + 1,
                           "reason": "one-off user-approved backfill of "
                                     "the gap skipped by run 191 "
                                     "(>40k blocks)"},
        "wallets": {"checked": len(wallets), "tier_ab": wset["tier_ab_count"],
                    "feed": wset["feed_count"], "unique": wset["total_unique"],
                    "failed_chunks": failed_chunks},
        "mint_events_new": len(mints),
        "tx_lookup_failed": tx_lookup_failed,
        "contracts_new": len(by_contract),
        "machine_token_fast_path": machine_hits,
        "anomalies": anomalies,
        "signals_over_20pct": signals,
        "triggers_over_25pct": triggers,
        "getlogs_verification": verify,
        "paid_trend_top": paid_trend[:10],
        "paid_trend_note": ("mint-tx values only; pure-buy (swap) trend "
                            "UNVERIFIED via public RPC (no txlist method)"),
        "note": ("Routine state file NOT touched (watermark stays at "
                 "133748748 per run 191); this backfill is a standalone "
                 "one-off. Triggers are FLAGGED only — no execution."),
    }
    json.dump(summary, open(FINDINGS_PATH, "w"), indent=1)
    print(f"BACKFILL 191b {'OK' if all_verified else 'PARTIAL'}: "
          f"mints={len(mints)} contracts={len(by_contract)} "
          f"signals={len(signals)} triggers={len(triggers)} "
          f"machine={len(machine_hits)} anomalies={len(anomalies)} "
          f"failed_chunks={len(failed_chunks)}", flush=True)
    print(json.dumps(summary, indent=1)[:4000], flush=True)
    return 0 if all_verified else 1


if __name__ == "__main__":
    sys.exit(main())
