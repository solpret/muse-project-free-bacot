#!/usr/bin/env python3
"""Parallel backfill driver for the FREE BACOT on-chain scan gap.

READ-ONLY scan + one serial state merge. Spawns K backfill-scan.py --worker
processes over K consecutive chunk-size-block chunks starting at the shared
watermark, waits for all of them, then merges ONCE under backfill.lock:
  * first-seen from every completed chunk is appended to seen (deduped by
    lowercase address, earliest first_block kept)
  * the watermark advances only over the contiguous successfully-scanned
    prefix (a failed chunk leaves a hole; later chunks' data is still kept
    and their first-seen is still recorded, exactly like the single-chunk
    script's partial behaviour — the hole itself is retried next run)
  * per-chunk state notes keep the same format as backfill-scan.py

Workers never touch state/seen (their --worker flag skips flock and
mutation), so concurrent workers cannot lose each other's first-seen
appends — the race the exclusive flock in backfill-scan.py was guarding.
The driver holds backfill.lock for the whole run, so a second driver (or
a standalone backfill-scan.py run) exits 3 instead of overlapping.

Ankr cost: ~80 ankr_getLogs calls per 2.000-block chunk (~240/run at K=3).
Shape-check failures (e.g. Sourcify throttling under 3x load) degrade
gracefully to shape_pending / error status in the chunk JSON; the cron
worker's triage re-verifies first-seen contracts with direct calls anyway.

Usage:
  python3 -u backfill-parallel.py --chunks 3
  python3 -u backfill-parallel.py --chunks 2 --chunk-size 200 --dry-run

Exit codes: 0 = all chunks fully scanned; 2 = partial (some chunk failed
or partial, watermark advanced over the contiguous prefix);
            1 = total failure (no chunk completed);
            3 = lock held by another backfill run.
"""
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single  # noqa: E402

EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
WORKER = os.path.join(BASE, "backfill-scan.py")


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


def atomic_write_json(path, obj):
    tmp = path + ".tmp-backfill-parallel"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", type=int, default=3,
                    help="parallel workers / consecutive chunks per run")
    ap.add_argument("--chunk-size", type=int, default=2000)
    ap.add_argument("--deadline-secs", type=int, default=600,
                    help="shape-phase soft deadline passed to each worker")
    ap.add_argument("--workers-timeout", type=int, default=1800,
                    help="max seconds to wait for one worker before killing it")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--state", default=os.path.join(BASE, "onchain-scan-state.json"))
    ap.add_argument("--seen", default=os.path.join(BASE, "onchain-scan-seen.json"))
    args = ap.parse_args()

    lock_path = os.path.join(BASE, "backfill.lock")
    lock_f = open(lock_path, "w")
    try:
        fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("LOCKED: another backfill run holds backfill.lock — exiting")
        return 3

    with open(args.state) as f:
        state = json.load(f)
    watermark = int(state.get("last_scanned_block", 0))

    head = None
    try:
        head = int(rpc_call("eth_blockNumber", [], timeout=5), 16)
        log(f"head block (best-effort): {head}")
    except Exception as e:  # noqa: BLE001
        log(f"head block UNVERIFIED (read failed, continuing): {e}")
    log(f"watermark: {watermark}; gap to head: "
        f"{(head - watermark) if head is not None else 'unknown'} blocks"
        f"{' DRY-RUN' if args.dry_run else ''}")

    ranges = []
    start = watermark + 1
    for i in range(args.chunks):
        frm = start + i * args.chunk_size
        to = frm + args.chunk_size - 1
        if head is not None and frm > head:
            break
        if head is not None:
            to = min(to, head)
        ranges.append((frm, to))
    if not ranges:
        log("CAUGHT UP: watermark already at/above head — nothing to scan")
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()
        return 0
    log(f"spawning {len(ranges)} workers: "
        + ", ".join(f"{a}-{b}" for a, b in ranges))

    procs = []
    for frm, to in ranges:
        out_json = os.path.join(BASE, f"backfill-{frm}-{to}.json")
        log_path = os.path.join(BASE, f"backfill-{frm}-{to}.worker.log")
        cmd = [sys.executable, "-u", WORKER, "--worker",
               "--from-block", str(frm), "--to-block", str(to),
               "--out", out_json, "--deadline-secs", str(args.deadline_secs)]
        if args.dry_run:
            cmd.append("--dry-run")
        log_f = open(log_path, "w")
        p = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT)
        procs.append({"from": frm, "to": to, "out": out_json,
                      "log": log_path, "proc": p, "log_f": log_f})

    results = []
    for w in procs:
        try:
            rc = w["proc"].wait(timeout=args.workers_timeout)
        except subprocess.TimeoutExpired:
            log(f"TIMEOUT worker {w['from']}-{w['to']} "
                f"after {args.workers_timeout}s — killing")
            w["proc"].kill()
            w["proc"].wait()
            rc = 1
        w["log_f"].close()
        report = None
        try:
            with open(w["out"]) as f:
                report = json.load(f)
        except Exception as e:  # noqa: BLE001
            log(f"worker {w['from']}-{w['to']}: no readable report ({e})")
        results.append({"from": w["from"], "to": w["to"], "rc": rc,
                        "out": w["out"], "log": w["log"], "report": report})
        n_contracts = len(report["contracts"]) if report else 0
        n_first = report.get("first_seen_count", 0) if report else 0
        log(f"worker {w['from']}-{w['to']}: rc={rc}, "
            f"contracts={n_contracts}, first-seen={n_first}")

    completed = [r for r in results if r["report"] is not None
                 and r["rc"] in (0, 2)]
    failed = [r for r in results if r not in completed]

    new_watermark = watermark
    first_seen_all = {}
    notes = {}
    # First-seen dedupe + contiguous-prefix watermark are pure computation
    # (identical in dry-run, so the summary shows what WOULD happen);
    # only the file writes below are gated on not dry-run.
    with open(args.seen) as f:
        seen = json.load(f)
    seen_contracts = seen.get("contracts", {})
    seen_lower = {k.lower() for k in seen_contracts}
    for r in completed:
        rep = r["report"]
        for c in rep.get("first_seen", []):
            key = c["address"].lower()
            if key in seen_lower:
                continue
            prev = first_seen_all.get(key)
            if prev is None or c["first_block"] < prev["first_block"]:
                first_seen_all[key] = c
        notes[f"note_backfill_{r['from']}_{r['to']}"] = (
            f"Backfill chunk {r['from']}-{r['to']}: "
            f"{len(rep.get('contracts', []))} NFT + "
            f"{rep.get('erc20_mint_contracts', 0)} ERC20-mint contracts, "
            f"{rep.get('first_seen_count', 0)} first-seen, "
            f"{rep.get('ankr_calls', 0)} Ankr calls, "
            f"{len(rep.get('errors', []))} errors, "
            f"failed chunks {rep.get('failed_chunks') or 'none'}, "
            f"watermark -> "
            f"{rep.get('watermark_advanced_to') if rep.get('watermark_advanced_to') is not None else 'unchanged'}."
        )
    # Watermark advances only over the contiguous prefix, in order.
    for r in completed:
        rep = r["report"]
        adv = rep.get("watermark_advanced_to")
        if r["from"] == new_watermark + 1 and adv is not None:
            new_watermark = int(adv)
        else:
            break
    if not args.dry_run and completed:
        for addr, c in first_seen_all.items():
            seen_contracts[c["address"]] = c["first_block"]
        first = ranges[0][0]
        last = ranges[-1][1]
        suffix = f".bak-backfill-parallel-{first}-{last}"
        shutil.copy(args.seen, args.seen + suffix)
        shutil.copy(args.state, args.state + suffix)
        atomic_write_json(args.seen, seen)
        with open(args.state) as f:
            state = json.load(f)
        if new_watermark > watermark:
            state["last_scanned_block"] = new_watermark
            state["last_scan_window_from"] = ranges[0][0]
            state["last_scan_window_to"] = new_watermark
        state["last_scan_wib"] = f"backfill-parallel {first}-{last}"
        state.update(notes)
        state[f"note_backfill_parallel_{first}_{last}"] = (
            f"Parallel backfill {first}-{last} ({len(ranges)} workers): "
            f"{len(completed)}/{len(ranges)} chunks completed, "
            f"{len(first_seen_all)} first-seen (deduped), "
            f"failed {[f'{r['from']}-{r['to']}' for r in failed] or 'none'}, "
            f"watermark {watermark} -> {new_watermark}."
        )
        atomic_write_json(args.state, state)
        log(f"state/seen updated (backups *{suffix}); "
            f"watermark {watermark} -> {new_watermark}; "
            f"first-seen appended: {len(first_seen_all)}")
    elif args.dry_run:
        log(f"DRY-RUN: no state/seen mutation; watermark would advance "
            f"{watermark} -> {new_watermark}; "
            f"first-seen would be {len(first_seen_all)}")

    # FIX 2026-11-07 (merge-defect): a worker with rc=2 (partial) used to
    # leave the summary's failed_chunks empty — only whole-chunk failures
    # were counted — so failed sub-chunks were invisible at merge level.
    # The worker now also stops watermark_advanced_to at the first failed
    # sub-chunk; the driver surfaces every failed sub-chunk here so the
    # hole is visible in the summary and retried via the watermark.
    failed_sub_chunks = [
        {"chunk": f"{r['from']}-{r['to']}", **fc}
        for r in completed for fc in (r["report"] or {}).get("failed_chunks", [])
    ]
    summary = {
        "parallel": True,
        "chunk_id": f"{ranges[0][0]}-{ranges[-1][1]}",
        "watermark_before": watermark,
        "watermark_after": new_watermark,
        "head_block": head,
        "chunks": [{"from": r["from"], "to": r["to"], "rc": r["rc"],
                    "out": r["out"], "log": r["log"],
                    "first_seen_count":
                        (r["report"] or {}).get("first_seen_count", 0),
                    "watermark_advanced_to":
                        (r["report"] or {}).get("watermark_advanced_to")}
                   for r in results],
        "first_seen_total": len(first_seen_all),
        "failed_chunks": [f"{r['from']}-{r['to']}" for r in failed],
        "failed_sub_chunks": failed_sub_chunks,
        "elapsed_secs": round(time.time() - t0, 1),
    }
    summary_path = os.path.join(
        BASE, f"backfill-parallel-{ranges[0][0]}-{ranges[-1][1]}.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=1)
    log(f"wrote {summary_path}")
    log(f"RESULT: {len(completed)}/{len(ranges)} chunks, "
        f"watermark {watermark} -> "
        f"{new_watermark if not args.dry_run else '(dry-run, unchanged)'}, "
        f"first-seen {len(first_seen_all)}, "
        f"failed {[f'{r['from']}-{r['to']}' for r in failed] or 'none'}, "
        f"failed sub-chunks {len(failed_sub_chunks)}, "
        f"elapsed {summary['elapsed_secs']}s")
    fcntl.flock(lock_f, fcntl.LOCK_UN)
    lock_f.close()

    if not completed:
        return 1
    if failed or any(r["rc"] == 2 for r in completed):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
