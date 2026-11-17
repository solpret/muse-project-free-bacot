#!/usr/bin/env python3
"""Canonical hourly tracked-wallet mint scan — public-RPC leg (bloXroute).

Replaces the Ankr legs (dead: freemium exhausted, HTTP 401 since
2026-11-09) AND the BscScan leg (dead: free Etherscan V2 plan does not
cover BSC chain 56, verified 2026-11-14 19:35 WIB). Data source is the
free public BSC RPC https://bsc.rpc.blxrbdn.com (bloXroute), verified
2026-11-14 ~20:35 WIB: eth_getLogs 1000-block windows OK (~18-26 s),
multi-wallet topic arrays OK, TransferSingle OK, eth_call OK,
eth_getBlockByNumber OK. NO key, NO signup, NO payment.

What was tested and FAILED (same day, same filter, verbatim in
~/workspace/narrative-pulse/rpc-scan-endpoint-tests-2026-11-14.md):
  - All 8 Binance dataseeds: eth_getLogs -32005 "limit exceeded" even
    at 1-block windows, even WITH an address filter. getLogs is dead.
  - 1rpc.io, meowrpc, blastapi, blockpi, drpc, publicnode: HTTP 403
    Cloudflare (error 1010) from this VM.
  - OnFinality: HTTP 429, needs API key. Nodies: paid plan required.
  - LlamaRPC, Omniatech, blastapi bnb-mainnet: connection closed.
  - 48.club: serves getLogs only at <=20-block windows + HTTP 429s
    easily — unusable as primary (backup only, not wired).
  - Ankr public endpoint: 401, needs API key (stored key exhausted).

Legs (per run, BSC only, read-only — this script NEVER previews,
mints, approves, signs or buys):
  I. Inbound/mint discovery: eth_getLogs, chunked 1000 blocks, with a
     multi-wallet topic array — Transfer topic0 + from=zero topic1 +
     to=[55 tracked wallets] topic2 — plus TransferSingle (ERC-1155)
     with the same wallet array at topic3. A from-zero transfer TO a
     tracked wallet IS a mint (ERC-20 share sale / ERC-721 / ERC-1155).
     Per mint: eth_getTransactionByHash gives the tx value (0 = free,
     >0 = paid) and the called contract; eth_getBlockByNumber gives
     the block timestamp; eth_call reads name/symbol/decimals
     (best-effort: unreadable = unverified name, never a failure).
  D. Targeted verification: eth_getLogs address=contract,
     topic0=Transfer, topic1=zero for signal/trigger candidates only,
     max 5 contracts/run.
  P. Paid trend: aggregated from MINT tx values only (value > 0).
     The old sent-pass (txlist per wallet) CANNOT be replicated by
     any free RPC — there is no txlist method. Pure-buy (swap) trend
     is therefore UNVERIFIED, never 0; this is a documented
     limitation, not a leg failure.

Signal math (UNCHANGED): distinct participating wallets per contract,
folded through ENTITY_CLUSTERS (empty today). Signal >20% = >= 12
entities; auto-mint trigger >25% = >= 14 entities (of 55). A trigger
candidate is only FLAGGED here — the guards (website gate, age <24h,
free quota, audit, clean preview, same-owner discard) are checked by
the cron worker afterwards; this script executes NOTHING.

Gap policy: if tip - watermark > MAX_BACKFILL_BLOCKS (40_000, ~5 h of
chain time — the bloXroute tx-index only serves ~7 h back, verified
2026-11-14: a ~7.4 h-old tx resolves, a ~11.4 h-old tx returns null;
older mint txs would get free/paid UNVERIFIED), the run starts at
tip - RESUME_WINDOW (2000) and records the skipped gap loudly in
state + log + findings (history lost; mints in the gap are mostly
aged out under the <24 h rule). Gaps <= 40k blocks are fully scanned
(catch-up). NEVER attempt a giant backfill.

Failure semantics (same as the Ankr/BscScan era): any chunk failing
after 1 retry means that leg is UNVERIFIED — never 0. The watermark
advances ONLY when every chunk is verified. Otherwise the state
records FAILED, the watermark stays, and the exit code is 1.

Usage:
  python3 tracked-mint-scan-rpc.py [--run N] [--from-block B]
      [--dry-run] [--max-chunks K] [--out-dir DIR] [--slow]
Slow mode (--slow, user decision 2026-11-15): 2000-block chunks,
10 s pause between getLogs calls, 403 backoff 30 s then 60 s.
Defaults: run = last_run.run + 1; from-block = state watermark
(132534899 at migration time — the gap policy clamps it on run 170);
out = scan-runs/.
"""
import argparse
import ast
import datetime
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace" / "narrative-pulse"
STATE_PATH = NP / "tracked-wallet-mint-scan-state.json"
TIER_AB_PATH = NP / "tier-ab-watch-state.json"
WALLET_CONF_PATH = HOME / "workspace" / "ponyin-tools" / "live-executor-draft" / "wallet_confirmation.py"
LOG_PATH = NP / "tracked-wallet-mint-scan-log.md"
SCAN_RUNS_DIR = NP / "scan-runs"

RPC_URL = "https://bsc.rpc.blxrbdn.com"
USER_WALLETS = {
    "0xeb237f6f9fb4e826739f0954e9768914f28b2c2e",
    "0xcf3c6fc1bf670a8d3f03436395286f86dbee7418",
}
SIGNAL_MIN_ENTITIES = 12   # strictly >20% of 55
AUTO_MINT_MIN_ENTITIES = 14  # strictly >25% of 55
MAX_GETLOGS_CONTRACTS = 5
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
TRANSFER_TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TRANSFER_SINGLE_TOPIC0 = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
CHUNK_BLOCKS = 1000
MAX_BACKFILL_BLOCKS = 40_000
RESUME_WINDOW = 2000

# Slow mode (user decision 2026-11-15 ~09:29 WIB, "Pelankan scan di
# bloXroute", after runs 181-183 failed 3x in a row on bloXroute
# HTTP 403 for eth_getLogs): fewer, larger chunks + a pause between
# getLogs calls + long backoff on 403 instead of the 2 s retry.
# Enabled with --slow; the default path is untouched.
SLOW = False
SLOW_DELAY_S = 10
SLOW_CHUNK_BLOCKS = 2000
SLOW_403_BACKOFF_S = (30, 60)

ENTITY_CLUSTERS = {}

JAK = datetime.timezone(datetime.timedelta(hours=7))


def wib(ts):
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(int(ts), tz=JAK).strftime(
        "%Y-%m-%d %H:%M:%S WIB")


# ---------------- RPC client (plain urllib, no proxy tricks) ----------------

class RpcError(Exception):
    pass


def _retry_sleep(attempt, err_str):
    """Backoff between retries: 2 s normally; in slow mode, a long
    backoff after HTTP 403 (rate limit) so the quota window can
    replenish instead of hammering a blocked endpoint."""
    if SLOW and "403" in err_str:
        return SLOW_403_BACKOFF_S[min(attempt,
                                      len(SLOW_403_BACKOFF_S) - 1)]
    return 2


def rpc_call(method, params, timeout=60, retries=1):
    """Single JSON-RPC call to bloXroute. Retries once after 2 s; in
    slow mode, up to 2 retries with a long backoff after HTTP 403."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    last_err = None
    max_attempts = retries + 1
    if SLOW and retries > 0:
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
                time.sleep(_retry_sleep(attempt, str(e)))
        except Exception as e:
            last_err = RpcError(f"{type(e).__name__}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(_retry_sleep(attempt, str(last_err)))
    raise last_err


def tip_block():
    r = rpc_call("eth_blockNumber", [])
    return int(r, 16)


# ---------------- wallet set (same sources as the BscScan driver) ----------------

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


def load_state():
    return json.load(open(STATE_PATH))


def known_tx_hashes(state):
    known = set()
    for f in state.get("reported_findings", []):
        for m in f.get("mints", []):
            if m.get("tx"):
                known.add(m["tx"].lower())
    return known


# ---------------- eth_call helpers (best-effort) ----------------

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
    """name/symbol/decimals via eth_call; None fields = unverified."""
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


# ---------------- getLogs chunked ----------------

def get_logs_chunked(from_block, to_block, topics, address=None,
                     chunk_blocks=None):
    """Yield logs over [from_block, to_block] in chunk_blocks pieces.
    Raises RpcError if any chunk fails after retry."""
    cb = chunk_blocks or CHUNK_BLOCKS
    logs = []
    cur = from_block
    first = True
    while cur <= to_block:
        end = min(cur + cb - 1, to_block)
        if SLOW and not first:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, default=None)
    ap.add_argument("--from-block", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-chunks", type=int, default=0)
    ap.add_argument("--out-dir", default=str(SCAN_RUNS_DIR))
    ap.add_argument("--slow", action="store_true",
                    help="Slow mode (user 2026-11-15): 2000-block chunks, "
                         "10 s pause between getLogs calls, long 403 backoff")
    args = ap.parse_args()
    global SLOW
    SLOW = args.slow
    chunk_blocks = SLOW_CHUNK_BLOCKS if SLOW else CHUNK_BLOCKS

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    state = load_state()
    run_no = args.run or (int(state.get("last_run", {}).get("run", 169)) + 1)
    wset = load_wallet_set()
    wallets = wset["wallets"]
    wtopics = ["0x000000000000000000000000" + w[2:] for w in wallets]
    watermark = args.from_block or int(
        state.get("last_run", {}).get("block_start", 132534899))
    known = known_tx_hashes(state)
    machine = {m["address"].lower(): m
               for m in state.get("machine_tokens", [])}

    print(f"RUN {run_no} wallets={len(wallets)} "
          f"(tier-ab {wset['tier_ab_count']} + feed {wset['feed_count']}, "
          f"overlap {wset['overlap']}) watermark={watermark} "
          f"slow={SLOW} chunk_blocks={chunk_blocks}", flush=True)

    try:
        tip = tip_block()
    except Exception as e:
        print(f"RUN {run_no} FAILED: tip unreadable: {e}", flush=True)
        return 1
    print(f"RUN {run_no} tip={tip} window={watermark}-{tip} "
          f"({tip - watermark} blocks)", flush=True)
    if watermark >= tip:
        print(f"RUN {run_no} nothing to scan (watermark at tip)", flush=True)
        return 0

    # ---- Gap policy: clamp to tip-RESUME_WINDOW when backfill infeasible
    gap_skipped = None
    start = watermark
    if tip - watermark > MAX_BACKFILL_BLOCKS:
        gap_skipped = {"from": watermark, "to": tip - RESUME_WINDOW,
                       "blocks": tip - RESUME_WINDOW - watermark,
                       "reason": (f"gap {tip - watermark} blocks > "
                                  f"MAX_BACKFILL_BLOCKS {MAX_BACKFILL_BLOCKS}; "
                                  f"history lost, mints in gap mostly aged out "
                                  f"(<24h rule)")}
        start = tip - RESUME_WINDOW
        print(f"RUN {run_no} GAP SKIPPED: {gap_skipped['blocks']} blocks "
              f"({watermark}..{tip - RESUME_WINDOW}); resuming from {start}",
              flush=True)

    # ---- Leg I: inbound/mint discovery (multi-wallet topic arrays)
    mints = []
    failed_chunks = []
    chunks = []
    cur = start
    while cur <= tip:
        end = min(cur + chunk_blocks - 1, tip)
        chunks.append((cur, end))
        cur = end + 1
    if args.max_chunks:
        chunks = chunks[: args.max_chunks]
        print(f"WARNING: --max-chunks {args.max_chunks} (DEV ONLY, "
              f"not a production run)", flush=True)
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
        for topics, kind_label in (
                ([TRANSFER_TOPIC0, ZERO_TOPIC, wtopics], "Transfer"),
                ([TRANSFER_SINGLE_TOPIC0, None, ZERO_TOPIC, wtopics],
                 "TransferSingle")):
            if SLOW and not first_log_call:
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
                        # bloXroute tx-index depth is limited (proven:
                        # ~3h-old tx OK, ~19h-old tx NULL). A null lookup
                        # means free/paid is UNVERIFIED — NEVER default to
                        # free. The mint itself is still real (log is the
                        # source of truth); only value/call_to are unknown.
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
        print(f"  [{ci + 1}/{len(chunks)}] chunks done, "
              f"mints so far={len(mints)}", flush=True)

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
                start, tip, [TRANSFER_TOPIC0, ZERO_TOPIC],
                address=e["contract"], chunk_blocks=chunk_blocks)
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
        "run": run_no, "status": "OK" if all_verified else "FAILED",
        "rpc": RPC_URL,
        "window": {"from": start, "to": tip, "blocks": tip - start},
        "gap_skipped": gap_skipped,
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
    }
    findings_path = out_dir / f"run{run_no}-rpc-findings.json"
    json.dump(summary, open(findings_path, "w"), indent=1)
    print(f"RUN {run_no} summary: {json.dumps(summary, indent=1)[:3000]}",
          flush=True)

    if args.dry_run:
        print(f"RUN {run_no} DRY RUN: state/log NOT written", flush=True)
        return 0 if all_verified else 1

    backup = out_dir / f"tracked-wallet-mint-scan-state.json.bak-run{run_no}-pre"
    json.dump(state, open(backup, "w"), indent=1)
    if all_verified:
        try:
            window_wib = (f"{wib(block_ts(start))} - {wib(block_ts(tip))} "
                          f"(verified)")
        except Exception:
            window_wib = f"blok {start}-{tip} (timestamp unverified)"
        state["last_run"] = {
            "run": run_no, "status": "OK - public-RPC leg (bloXroute)",
            "block_start": tip, "block_end": tip,
            "window_wib": window_wib,
            "wallets_checked": (
                f"tier-ab {wset['tier_ab_count']} + feed {wset['feed_count']} "
                f"= {wset['total_unique']} unik; 0 failed"),
            "method_note": (
                f"Public-RPC leg (bloXroute eth_getLogs, multi-wallet topic "
                f"arrays): mints baru={len(mints)}, kontrak baru="
                f"{len(by_contract)}, sinyal={len(signals)}, "
                f"trigger={len(triggers)}; "
                f"gap_skipped={gap_skipped['blocks'] if gap_skipped else 0} "
                f"blocks; paid trend = mint-tx values only"),
        }
        if gap_skipped:
            state["last_run"]["gap_skipped"] = gap_skipped
        if mints:
            state.setdefault("reported_findings", []).append({
                "run": run_no,
                "counts": (f"{len(mints)} mint events, "
                           f"{len(by_contract)} distinct mint contracts"),
                "free_vs_paid": "per-mint tx value (0 = free, >0 = paid)",
                "mints": [{k: m[k] for k in (
                    "call_to", "kind", "mint_contract", "name", "symbol",
                    "time_wib", "token_id", "tx") if k in m}
                    for m in mints],
            })
        for e in signals + triggers:
            state.setdefault("signaled_projects_over_20pct", []).append({
                "contract": e["contract"], "run": run_no,
                "entities": e["entities"], "wallets": e["wallets"],
                "first_seen_wib": e["first_seen_wib"]})
        for e in machine_hits:
            mt = machine[e["contract"]]
            mt["last_seen_run"] = run_no
            mt["last_seen_wib"] = e["first_seen_wib"]
    else:
        state["last_run"] = {
            "run": run_no,
            "status": f"FAILED - public-RPC leg incomplete "
                      f"({len(failed_chunks)} chunks unverified)",
            "block_start": watermark, "block_end": None,
            "window_wib": (f"window {start}-{tip} NOT advanced; "
                           f"run {run_no + 1} MUST rescan from {watermark}"),
            "wallets_checked": f"{len(failed_chunks)} chunks unverified; "
                               f"see {findings_path.name}",
            "method_note": "Public-RPC leg partial failure; do NOT treat as "
                           "zero-mint run.",
        }
        state[f"failed_chunks_run{run_no}"] = failed_chunks
    state["next_run_note"] = (
        f"(Run {run_no}: {'OK' if all_verified else 'FAILED'} - public-RPC leg; "
        f"watermark {'advanced to ' + str(tip) if all_verified else 'NOT advanced, stays ' + str(watermark)}; "
        f"sinyal={len(signals)} trigger={len(triggers)} machine-fast-path={len(machine_hits)} "
        f"anomali={len(anomalies)}.)")
    json.dump(state, open(STATE_PATH, "w"), indent=1)
    with open(LOG_PATH, "a") as f:
        f.write(f"\n## Run {run_no} — {wib(int(time.time()))} "
                f"(jendela blok {start}–{tip}, "
                f"{'TERVERIFIKASI' if all_verified else 'TIDAK TERVERIFIKASI'})\n")
        if gap_skipped:
            f.write(f"- GAP SKIPPED: {gap_skipped['blocks']} blok "
                    f"({gap_skipped['from']}..{gap_skipped['to']}) — riwayat "
                    f"hilang; mint di gap sebagian besar aged-out (<24 jam).\n")
        f.write(f"- Set segar: tier-ab {wset['tier_ab_count']} + feed "
                f"{wset['feed_count']} = {wset['total_unique']} unik; "
                f"wallet user tidak ada di set.\n")
        f.write(f"- RPC leg (bloXroute): mint baru: {len(mints)} events / "
                f"{len(by_contract)} kontrak; sinyal >20%: {len(signals)}; "
                f"trigger >25%: {len(triggers)}; machine fast-path: "
                f"{len(machine_hits)}; anomali: {len(anomalies)}.\n")
        if triggers:
            f.write(f"- TRIGGER AUTO-MINT >25% (PERLU GUARD CHECK worker, "
                    f"BUKAN eksekusi driver): "
                    f"{', '.join(t['contract'] for t in triggers)}.\n")
        if signals:
            f.write(f"- SINYAL >20%: "
                    f"{', '.join(s['contract'] for s in signals)}.\n")
        if not all_verified:
            f.write(f"- GAGAL: {len(failed_chunks)} chunk tidak terverifikasi "
                    f"— watermark TIDAK maju; run {run_no + 1} harus rescan "
                    f"dari blok {watermark}.\n")
        f.write(f"- Bukti: scan-runs/run{run_no}-rpc-findings.json. "
                f"State: tracked-wallet-mint-scan-state.json "
                f"(backup .bak-run{run_no}-pre).\n")
    print(f"RUN {run_no} {'OK' if all_verified else 'FAILED'}; "
          f"watermark={'advanced to ' + str(tip) if all_verified else 'NOT advanced'}",
          flush=True)
    return 0 if all_verified else 1


if __name__ == "__main__":
    sys.exit(main())
