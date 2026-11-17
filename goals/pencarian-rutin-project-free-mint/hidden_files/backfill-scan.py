#!/usr/bin/env python3
"""Backfill scanner for the FREE BACOT on-chain scan gap — READ-ONLY, keyless.

Scans ONE explicit 2.000-block window (default chunk = next window after the
watermark in onchain-scan-state.json) using Ankr ankr_getLogs DIRECTLY
(no_proxy for rpc.ankr.com — the route-4 stall in runs 0431/0531/0601 was
specific to the scan process's proxied connection, while direct Ankr
getLogs answered in 0,7-1,4 dtk). Same log topics + output shape as
onchain_nft_scan.py (route 4), so the main 30-minute run's triage works
unchanged on the chunk JSON.

Hardening vs route 4:
  * explicit --from-block/--to-block (never "latest N")
  * all prints flush=True; run with python3 -u (no 0-byte-log mystery)
  * per-chunk continue-on-error (route 4 BREAKS the whole scan on one
    Transfer chunk error — a 2000-block scan died after ~300 blocks)
  * watermark advances only over the contiguous successfully-scanned
    prefix; failed chunk ranges are recorded as residual gaps and retried
    by the next run (never silently skipped)
  * soft deadline on the shape-check phase (rest marked shape_pending)
  * exclusive flock so two backfill runs never mutate state/seen at once

Parallel mode (2026-11-06, user: "jalankan saja paralel"): the driver
backfill-parallel.py spawns K workers with --worker over K consecutive
2.000-block chunks. A worker skips the flock (the driver holds it for the
whole run) and skips state/seen mutation (the driver merges once, serially,
after all workers finish) — so concurrent workers cannot lose each
other's first-seen appends, the race the exclusive flock was guarding.
Workers still write their own chunk JSON (same shape) with first_seen
computed read-only against the seen snapshot at their start; the driver
dedupes first-seen across chunks by lowercase address (earliest
first_block kept) and advances the watermark only over the contiguous
successfully-scanned prefix.

Mutations (skipped with --dry-run): appends first-seen contracts to
onchain-scan-seen.json and advances last_scanned_block in
onchain-scan-state.json. Backups (.bak-backfill-<from>-<to>) are written
first; writes are atomic (temp + os.replace). Triage / verification /
snapshot / reporting is the CRON WORKER's job, from the chunk JSON —
this script never previews, mints, claims, or executes anything.

Usage:
  python3 -u backfill-scan.py --from-block 131895549 --to-block 131897548 \
      --out backfill-131895549-131897548.json
  python3 -u backfill-scan.py --from-block 131895549 --to-block 131897548 \
      --out /tmp/test.json --dry-run

Exit codes: 0 = chunk fully scanned, watermark -> to_block;
            2 = partial (some chunks failed, watermark -> contiguous prefix);
            1 = total failure (no chunk scanned, watermark unchanged);
            3 = lock held by another backfill run.
"""
import argparse
import fcntl
import json
import os
import shutil
import sys
import time
import urllib.request

# Ankr via the egress proxy (urllib default): direct egress is BLOCKED in
# this sandbox — setting no_proxy for rpc.ankr.com makes urllib speak TLS
# to the transparent middlebox and fails with SSL WRONG_VERSION_NUMBER
# (verified in the 06:47 smoke test). The proxy path is REQUIRED; the
# route-4 stall was not the proxy being used, it was per-call slowness
# plus the script breaking on the first chunk error (fixed below).

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single  # noqa: E402
from ankr import ankr_post  # noqa: E402

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TS_SINGLE = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ZERO_TOPIC = "0x" + "00" * 32
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
HIVE_AGENTS = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
NAME_SEL = "0x06fdde03"
SYMBOL_SEL = "0x95d89b41"


def log(*a):
    print(*a, flush=True)


def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def ankr_logs(from_block, to_block, topics, max_pages=10):
    logs = []
    page_token = None
    pages = 0
    while True:
        params = {"blockchain": "bsc",
                  "fromBlock": hex(from_block), "toBlock": hex(to_block),
                  "pageSize": 1000, "decodeLogs": False, "topics": topics}
        if page_token:
            params["pageToken"] = page_token
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                time.sleep(30)
                body = ankr_post("ankr_getLogs", params, timeout=30)
            else:
                raise
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(result.get("logs", []))
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or pages >= max_pages:
            break
        time.sleep(2.2)  # stay under 30 req/min
    return logs, pages


def decode_str_or_bytes32(hexdata):
    if not isinstance(hexdata, str) or not hexdata.startswith("0x"):
        return None
    raw = bytes.fromhex(hexdata[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64 + ln].decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None


def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
            return ("verified", data.get("abi"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("not_verified", None)
        return (f"http_{e.code}", None)
    except Exception as e:  # noqa: BLE001
        return (f"error:{type(e).__name__}", None)


def atomic_write_json(path, obj):
    tmp = path + ".tmp-backfill"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-block", type=int, required=True)
    ap.add_argument("--to-block", type=int, required=True)
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-secs", type=int, default=900,
                    help="soft deadline (from start) for the shape phase")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--worker", action="store_true",
                    help="parallel-worker mode (spawned by backfill-parallel.py): "
                    "skip flock (the driver holds backfill.lock for the whole "
                    "run) and skip state/seen mutation (the driver merges once, "
                    "serially, after all workers finish)")
    ap.add_argument("--state", default=os.path.join(BASE, "onchain-scan-state.json"))
    ap.add_argument("--seen", default=os.path.join(BASE, "onchain-scan-seen.json"))
    args = ap.parse_args()
    from_block, to_block = args.from_block, args.to_block
    log(f"BACKFILL chunk {from_block}..{to_block} "
        f"({to_block - from_block + 1} blocks, chunks of {args.chunk})"
        f"{' DRY-RUN' if args.dry_run else ''}")

    lock_path = os.path.join(BASE, "backfill.lock")
    lock_f = None
    if not args.worker:
        lock_f = open(lock_path, "w")
        try:
            fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log("LOCKED: another backfill run holds backfill.lock — exiting")
            return 3

    # Best-effort head (window is watermark-determined; never fatal).
    latest = None
    try:
        latest = int(rpc_call("eth_blockNumber", [], timeout=5), 16)
        log(f"head block (best-effort): {latest}")
    except Exception as e:  # noqa: BLE001
        log(f"head block UNVERIFIED (read failed, continuing): {e}")

    erc721, erc1155, erc20 = {}, {}, {}
    calls = 0
    errors = []
    failed_chunks = []

    def add(store, addr, blk):
        e = store.setdefault(addr, {"mint_count": 0, "minters": set(),
                                    "first_block": None, "last_block": None})
        e["mint_count"] += 1
        e["first_block"] = blk if e["first_block"] is None else min(e["first_block"], blk)
        e["last_block"] = blk if e["last_block"] is None else max(e["last_block"], blk)
        return e

    chunk_from = from_block
    contiguous_end = from_block - 1
    # FIX 2026-11-07 (merge-defect): contiguous_end must stop at the FIRST
    # failed sub-chunk. Previously it was overwritten by every later
    # successful sub-chunk, so watermark_advanced_to jumped past failed
    # sub-chunks and the driver advanced the watermark over the hole
    # (failed_chunks recorded, never retried). prefix_broken latches on
    # the first failure and never lets contiguous_end advance again.
    prefix_broken = False
    while chunk_from <= to_block:
        chunk_to = min(chunk_from + args.chunk - 1, to_block)
        chunk_ok = True
        try:
            logs, _ = ankr_logs(chunk_from, chunk_to, [TRANSFER, ZERO_TOPIC])
            calls += 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"Transfer chunk {chunk_from}-{chunk_to}: {e}")
            log(f"ERROR Transfer chunk {chunk_from}-{chunk_to}: {e} — continuing")
            failed_chunks.append((chunk_from, chunk_to, "Transfer"))
            chunk_ok = False
            logs = []
        for lg in logs:
            topics = lg.get("topics", [])
            addr = lg.get("address", "")
            blk = int(lg.get("blockNumber", "0x0"), 16)
            if len(topics) == 4:
                e = add(erc721, addr, blk)
                e["minters"].add("0x" + topics[2][-40:])
            elif len(topics) == 3:
                e = add(erc20, addr, blk)
                e["minters"].add("0x" + topics[2][-40:])
        time.sleep(2.2)
        ts_logs = None
        for topic_filter in ([TS_SINGLE, None, ZERO_TOPIC], [TS_SINGLE]):
            try:
                ts_logs, _ = ankr_logs(chunk_from, chunk_to, topic_filter)
                calls += 1
                break
            except Exception as e:  # noqa: BLE001
                if len(topic_filter) > 1 and topic_filter[1] is None:
                    continue
                errors.append(f"TransferSingle chunk {chunk_from}-{chunk_to}: {e}")
                log(f"ERROR TransferSingle chunk {chunk_from}-{chunk_to}: {e} — continuing")
                failed_chunks.append((chunk_from, chunk_to, "TransferSingle"))
                chunk_ok = False
                ts_logs = []
        for lg in (ts_logs or []):
            topics = lg.get("topics", [])
            if len(topics) >= 3 and topics[2].lower() == ZERO_TOPIC:
                blk = int(lg.get("blockNumber", "0x0"), 16)
                e = add(erc1155, lg.get("address", ""), blk)
                e["minters"].add("0x" + topics[3][-40:] if len(topics) >= 4 else "?")
        time.sleep(2.2)
        if not chunk_ok:
            prefix_broken = True
        if chunk_ok and not prefix_broken:
            contiguous_end = chunk_to
        log(f"chunk {chunk_from}-{chunk_to}: ERC721 {len(erc721)}, "
            f"ERC1155 {len(erc1155)}, ERC20-mint {len(erc20)}"
            f"{'' if chunk_ok else ' (FAILED — residual gap)'}"
            f"{' (contiguous prefix broken — watermark stops before here)' if prefix_broken and chunk_ok else ''}")
        chunk_from = chunk_to + 1

    # Shape checks (cheap agent-shape flags), bounded by the soft deadline.
    contracts = []
    shape_pending = 0
    for kind, store in (("ERC721", erc721), ("ERC1155", erc1155)):
        for addr, e in sorted(store.items(), key=lambda kv: -kv[1]["mint_count"]):
            if time.time() - t0 > args.deadline_secs:
                shape_pending += 1
                contracts.append({
                    "address": addr, "kind": kind,
                    "mint_count": e["mint_count"],
                    "distinct_minters": len(e["minters"]),
                    "minters_sample": sorted(e["minters"])[:5],
                    "first_block": e["first_block"], "last_block": e["last_block"],
                    "shape_pending": True,
                })
                continue
            code = None
            try:
                code = rpc_call("eth_getCode", [addr, "latest"], timeout=5)
            except Exception as ex:  # noqa: BLE001
                errors.append(f"getCode {addr}: {ex}")
            registry_hit = None
            if isinstance(code, str) and len(code) > 2:
                registry_hit = REGISTRY_BYTES in code[2:].lower()
            status, abi = sourcify_abi(addr)
            free_funcs, mint_funcs = [], []
            if isinstance(abi, list):
                for item in abi:
                    if item.get("type") != "function":
                        continue
                    nm = item.get("name", "")
                    if "free" in nm.lower() and not nm.lower().startswith("freeze"):
                        free_funcs.append(nm)
                    if "mint" in nm.lower():
                        mint_funcs.append(nm)
            name = symbol = None
            for sel, slot in ((NAME_SEL, "name"), (SYMBOL_SEL, "symbol")):
                try:
                    out = rpc_call("eth_call", [{"to": addr, "data": sel}, "latest"], timeout=5)
                    val = decode_str_or_bytes32(out)
                    if slot == "name":
                        name = val
                    else:
                        symbol = val
                except Exception:  # noqa: BLE001
                    pass
            contracts.append({
                "address": addr, "kind": kind,
                "mint_count": e["mint_count"],
                "distinct_minters": len(e["minters"]),
                "minters_sample": sorted(e["minters"])[:5],
                "first_block": e["first_block"], "last_block": e["last_block"],
                "registry_bytes_hit": registry_hit,
                "sourcify": status,
                "free_shaped": sorted(set(free_funcs))[:10],
                "mint_funcs": sorted(set(mint_funcs))[:10],
                "name": name, "symbol": symbol,
            })
    if shape_pending:
        log(f"shape phase hit soft deadline ({args.deadline_secs}s): "
            f"{shape_pending} contracts marked shape_pending")

    hive = [c for c in contracts if c["address"].lower() == HIVE_AGENTS.lower()]
    report = {
        "backfill": True,
        "chunk_id": f"{from_block}-{to_block}",
        "latest_block": latest, "from_block": from_block, "to_block": to_block,
        "ankr_calls": calls, "errors": errors,
        "failed_chunks": [{"from": a, "to": b, "topic": t} for a, b, t in failed_chunks],
        "watermark_advanced_to": contiguous_end if contiguous_end >= from_block else None,
        "erc20_mint_contracts": len(erc20),
        "erc20_mint_contracts_list": [
            {"address": addr, "mint_count": e["mint_count"],
             "distinct_minters": len(e["minters"]),
             "first_block": e["first_block"], "last_block": e["last_block"]}
            for addr, e in sorted(erc20.items(), key=lambda kv: -kv[1]["mint_count"])
        ],
        "contracts": contracts,
        "hive_agents_found": bool(hive),
        "hive_agents": hive[0] if hive else None,
    }

    # First-seen detection + state/seen mutation (skipped on dry-run and
    # in --worker mode, where the driver merges once after all workers).
    first_seen = []
    if not args.dry_run and not args.worker:
        with open(args.seen) as f:
            seen = json.load(f)
        seen_contracts = seen.get("contracts", {})
        seen_lower = {k.lower(): k for k in seen_contracts}
        for c in contracts:
            if c["address"].lower() not in seen_lower:
                first_seen.append(c)
        for c in first_seen:
            seen_contracts[c["address"]] = c["first_block"]
        # ERC20-mint first-seen is tracked by the worker's 5c triage, not here.
        suffix = f".bak-backfill-{from_block}-{to_block}"
        shutil.copy(args.seen, args.seen + suffix)
        shutil.copy(args.state, args.state + suffix)
        atomic_write_json(args.seen, seen)
        with open(args.state) as f:
            state = json.load(f)
        if contiguous_end >= from_block:
            state["last_scanned_block"] = contiguous_end
            state["last_scan_window_from"] = from_block
            state["last_scan_window_to"] = contiguous_end
        state["last_scan_wib"] = f"backfill {from_block}-{to_block}"
        state[f"note_backfill_{from_block}_{to_block}"] = (
            f"Backfill chunk {from_block}-{to_block}: {len(contracts)} NFT + "
            f"{len(erc20)} ERC20-mint contracts, {len(first_seen)} first-seen, "
            f"{calls} Ankr calls, {len(errors)} errors, "
            f"failed chunks {failed_chunks or 'none'}, "
            f"watermark -> {contiguous_end if contiguous_end >= from_block else 'unchanged'}."
        )
        atomic_write_json(args.state, state)
        log(f"state/seen updated (backups *{suffix}); "
            f"watermark -> {contiguous_end if contiguous_end >= from_block else 'unchanged'}; "
            f"first-seen: {len(first_seen)}")
    else:
        with open(args.seen) as f:
            seen = json.load(f)
        seen_lower = {k.lower() for k in seen.get("contracts", {})}
        first_seen = [c for c in contracts if c["address"].lower() not in seen_lower]
        mode = "WORKER" if args.worker else "DRY-RUN"
        log(f"{mode}: no state/seen mutation; first-seen would be {len(first_seen)}")

    report["first_seen"] = first_seen
    report["first_seen_count"] = len(first_seen)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=1)
    log(f"wrote {args.out}")
    log(f"RESULT: {len(contracts)} NFT contracts, "
        f"{sum(c['mint_count'] for c in contracts)} NFT mints, "
        f"{len(erc20)} ERC-20 mint contracts, {len(first_seen)} first-seen")
    for c in first_seen:
        log(f"  FIRST-SEEN {c['kind']} {c['address']} mints={c['mint_count']} "
            f"minters={c['distinct_minters']} name={c.get('name')} "
            f"symbol={c.get('symbol')} registry={c.get('registry_bytes_hit')} "
            f"sourcify={c.get('sourcify')} free={c.get('free_shaped')}")
    if lock_f is not None:
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()

    if contiguous_end < from_block:
        return 1  # nothing scanned
    if failed_chunks:
        return 2  # partial
    return 0


if __name__ == "__main__":
    sys.exit(main())
