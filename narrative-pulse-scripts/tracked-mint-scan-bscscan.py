#!/usr/bin/env python3
"""Canonical hourly tracked-wallet mint scan — BscScan leg.

Replaces the Ankr legs (dead: freemium exhausted, HTTP 401 since
2026-11-09; 29 consecutive failed runs 141-169). BscScan API is the
data source; the signal definitions, thresholds, guards and state
format are UNCHANGED from the Ankr era.

Legs (per run, BSC only, read-only — this script NEVER previews,
mints, approves, signs or buys):
  A. Sent pass:  `txlist` per wallet over [watermark, tip].
  B. Inbound/mint leg: `tokentx` + `tokennfttx` + `token1155tx` per
     wallet over [watermark, tip]. A transfer whose `from` is the zero
     address is a mint (ERC-20 share sale / ERC-721 / ERC-1155).
  C. Paid trend: sent txs with value > 0 aggregated per `to` contract.
  D. Targeted verification: `getLogs` (topic0 = Transfer) for signal /
     trigger candidates only, max 5 contracts/run.
  E. Signal math: distinct participating wallets per contract, folded
     through ENTITY_CLUSTERS (recorded strong-linkage clusters count
     as ONE entity). Signal >20% = >= 12 entities; auto-mint trigger
     >25% = >= 14 entities (of 55). A trigger candidate is only
     FLAGGED here — the guards (website gate, age <24h, free quota,
     audit, clean preview, same-owner discard) are checked by the
     cron worker afterwards; this script executes NOTHING.

Failure semantics (same as the Ankr era): any leg failing for a
wallet, or any pagination truncated, means that wallet/leg is
UNVERIFIED — never 0. The watermark advances ONLY when every wallet
is verified in every leg. Otherwise the state records FAILED, the
watermark stays, and the exit code is 1 (2 = invalid API key).

Usage:
  python3 tracked-mint-scan-bscscan.py [--run N] [--from-block B]
      [--dry-run] [--max-wallets K] [--out-dir DIR]
Defaults: run = last_run.run + 1; from-block = state watermark
(132534899 at migration time — do NOT reset it); out = scan-runs/.
"""
import argparse
import ast
import datetime
import json
import os
import sys
import time
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace" / "narrative-pulse"
sys.path.insert(0, str(HOME / "workspace" / "custom-connectors" / "custom.bscscan" / "bin"))
sys.path.insert(0, str(HOME / "workspace" / "fast_exec"))
import bscscan  # noqa: E402
import fast_rpc  # noqa: E402

STATE_PATH = NP / "tracked-wallet-mint-scan-state.json"
TIER_AB_PATH = NP / "tier-ab-watch-state.json"
WALLET_CONF_PATH = HOME / "workspace" / "ponyin-tools" / "live-executor-draft" / "wallet_confirmation.py"
LOG_PATH = NP / "tracked-wallet-mint-scan-log.md"
SCAN_RUNS_DIR = NP / "scan-runs"

USER_WALLETS = {
    "0xeb237f6f9fb4e826739f0954e9768914f28b2c2e",
    "0xcf3c6fc1bf670a8d3f03436395286f86dbee7418",
}
SIGNAL_MIN_ENTITIES = 12   # strictly >20% of 55
AUTO_MINT_MIN_ENTITIES = 14  # strictly >25% of 55
MAX_GETLOGS_CONTRACTS = 5
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Recorded strong-linkage clusters count as ONE entity. There is NO
# machine-readable cluster map in state today (the TRIO reference in
# the cron body is historical); entries are added here ONLY when a
# cluster is recorded by the worker in state/log. Empty = count per
# wallet + note "linkage belum diverifikasi".
ENTITY_CLUSTERS = {}

JAK = datetime.timezone(datetime.timedelta(hours=7))


def wib(ts):
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(int(ts), tz=JAK).strftime(
        "%Y-%m-%d %H:%M:%S WIB")


def load_wallet_set():
    """Fresh wallet set: tier-ab (54) + feed TRACKED_WALLETS (6)."""
    tier = json.load(open(TIER_AB_PATH))
    tier_wallets = [w.lower() for w in tier["wallets"].keys()]
    # Parse TRACKED_WALLETS via AST (no import side effects, always fresh).
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


def tip_block():
    """Chain tip via fast_rpc eth_blockNumber (race, first success)."""
    try:
        r = fast_rpc.batch_race("eth_blockNumber", [])
        if isinstance(r, str) and r.startswith("0x"):
            return int(r, 16)
        if isinstance(r, dict) and isinstance(r.get("result"), str):
            return int(r["result"], 16)
    except Exception:
        pass
    # Direct single-endpoint fallback via fast_rpc internals.
    for ep in fast_rpc.healthy_endpoints():
        try:
            r = fast_rpc._single(ep, "eth_blockNumber", [], timeout=5,
                                 retries=0)
            if isinstance(r, str) and r.startswith("0x"):
                return int(r, 16)
            if isinstance(r, dict) and isinstance(r.get("result"), str):
                return int(r["result"], 16)
        except Exception:
            continue
    raise RuntimeError("tip block unreadable from all fast_rpc endpoints")


def fold_entities(wallets):
    """Fold wallets through ENTITY_CLUSTERS; return (entity_count,
    raw_wallet_count, note)."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, default=None)
    ap.add_argument("--from-block", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-wallets", type=int, default=0)
    ap.add_argument("--out-dir", default=str(SCAN_RUNS_DIR))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    state = load_state()
    run_no = args.run or (int(state.get("last_run", {}).get("run", 169)) + 1)
    wset = load_wallet_set()
    wallets = wset["wallets"]
    if args.max_wallets:
        wallets = wallets[: args.max_wallets]
        print(f"WARNING: --max-wallets {args.max_wallets} (DEV ONLY, "
              f"not a production run)", flush=True)
    watermark = args.from_block or int(
        state.get("last_run", {}).get("block_start", 132534899))
    known = known_tx_hashes(state)
    machine = {m["address"].lower(): m
               for m in state.get("machine_tokens", [])}

    print(f"RUN {run_no} wallets={len(wallets)} "
          f"(tier-ab {wset['tier_ab_count']} + feed {wset['feed_count']}, "
          f"overlap {wset['overlap']}) watermark={watermark}", flush=True)

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

    failed_wallets, failed_legs = {}, []
    sent, mints, paid = {}, [], {}
    max_block = watermark
    auth_error = False

    def note_failure(wallet, leg, err):
        failed_wallets.setdefault(wallet, []).append(f"{leg}: {str(err)[:200]}")

    # ---- Leg A: sent pass (txlist) + Leg B: inbound (token transfers)
    for i, w in enumerate(wallets):
        try:
            txs, trunc = bscscan.txlist_all(w, watermark, tip)
            if trunc:
                note_failure(w, "txlist", "pagination truncated at 20 pages")
                continue
            in_win = []
            for t in txs:
                try:
                    b = int(t.get("blockNumber", "0"))
                except Exception:
                    continue
                if b <= watermark or b > tip:
                    continue
                max_block = max(max_block, b)
                in_win.append(t)
                # Leg C: paid trend (sent value > 0 to a contract)
                try:
                    val = int(t.get("value", "0"))
                except Exception:
                    val = 0
                if val > 0 and (t.get("to") or "").lower() != w:
                    to = (t.get("to") or "").lower()
                    agg = paid.setdefault(to, {"wallets": set(), "txs": 0,
                                               "total_bnb_wei": 0})
                    agg["wallets"].add(w)
                    agg["txs"] += 1
                    agg["total_bnb_wei"] += val
            sent[w] = in_win
        except bscscan.BscScanAuthError as e:
            print(f"RUN {run_no} AUTH ERROR: {e}", flush=True)
            auth_error = True
            break
        except Exception as e:
            note_failure(w, "txlist", e)
            continue
        for fn, kind in ((bscscan.tokentx_all, "ERC20"),
                         (bscscan.tokennfttx_all, "ERC721"),
                         (bscscan.token1155tx_all, "ERC1155")):
            try:
                recs, trunc = fn(w, watermark, tip)
                if trunc:
                    note_failure(w, f"{kind}-transfers",
                                 "pagination truncated at 20 pages")
                    continue
                for r in recs:
                    try:
                        b = int(r.get("blockNumber", "0"))
                    except Exception:
                        continue
                    if b <= watermark or b > tip:
                        continue
                    if (r.get("from") or "").lower() != ZERO_ADDRESS:
                        continue
                    txh = (r.get("hash") or "").lower()
                    if txh in known:
                        continue
                    max_block = max(max_block, b)
                    mints.append({
                        "call_to": (r.get("to") or "").lower(),
                        "kind": kind,
                        "mint_contract": (r.get("contractAddress") or "").lower(),
                        "name": r.get("tokenName") or None,
                        "symbol": r.get("tokenSymbol") or None,
                        "time_wib": wib(r.get("timeStamp")),
                        "token_id": r.get("tokenID"),
                        "amount": r.get("value"),
                        "tx": txh,
                        "block": b,
                        "wallet": w,
                    })
            except bscscan.BscScanAuthError as e:
                print(f"RUN {run_no} AUTH ERROR: {e}", flush=True)
                auth_error = True
                break
            except Exception as e:
                note_failure(w, f"{kind}-transfers", e)
        if auth_error:
            break
        if (i + 1) % 10 == 0:
            print(f"  [{i + 1}/{len(wallets)}] wallets done, "
                  f"mints so far={len(mints)}", flush=True)

    if auth_error:
        _write_failed_run(state, run_no, watermark, tip, wset,
                          "AUTH ERROR: Invalid API Key", out_dir, args.dry_run)
        return 2

    # ---- Aggregate mints per contract; machine-token fast path; signals
    by_contract = {}
    for m in mints:
        by_contract.setdefault(m["mint_contract"], []).append(m)
    machine_hits, anomalies = [], []
    findings_mints = []
    for contract, ms in by_contract.items():
        wallets_c = sorted({m["wallet"] for m in ms})
        entities, raw, note = fold_entities(wallets_c)
        entry = {"contract": contract, "mints": len(ms),
                 "wallets": wallets_c, "entities": entities,
                 "raw_wallets": raw, "entity_note": note,
                 "first_seen_wib": min((m["time_wib"] for m in ms if m["time_wib"]),
                                 default=None),
                 "kinds": sorted({m["kind"] for m in ms}),
                 "names": sorted({m["name"] for m in ms if m["name"]}),
                 "symbols": sorted({m["symbol"] for m in ms if m["symbol"]})}
        if contract in machine:
            mt = machine[contract]
            # Anomaly checks: name/symbol appeared, or a zero-value
            # free-mint path appeared (machine tokens have no free path).
            named = bool(entry["names"] or entry["symbols"])
            free_path = any(m["kind"] == "ERC20" and m["amount"] in (None, "0")
                            for m in ms)
            if named or free_path:
                anomalies.append({**entry, "anomaly":
                                  "name/symbol appeared" if named
                                  else "free-mint path appeared"})
            else:
                machine_hits.append(entry)
                continue  # fast path: no full verification, no signal
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
            logs, trunc = bscscan.get_logs_all(
                e["contract"], watermark, tip,
                topic0=bscscan.TRANSFER_TOPIC0,
                topic1=bscscan.ZERO_TOPIC1)
            first_mints = [l for l in logs
                           if (l.get("topics") or [None, None])[1] ==
                           bscscan.ZERO_TOPIC1] if logs else []
            verify[e["contract"]] = {
                "logs_returned": len(logs), "first_mint_logs": len(first_mints),
                "truncated": trunc,
                "verified": len(first_mints) > 0 and not trunc}
        except Exception as ex:
            verify[e["contract"]] = {"error": str(ex)[:200], "verified": False}

    # ---- Paid trend summary
    paid_trend = []
    for to, agg in sorted(paid.items(), key=lambda kv: -len(kv[1]["wallets"])):
        paid_trend.append({"contract": to, "wallets": len(agg["wallets"]),
                           "txs": agg["txs"],
                           "total_bnb": agg["total_bnb_wei"] / 1e18})

    all_verified = not failed_wallets
    summary = {
        "run": run_no, "status": "OK" if all_verified else "FAILED",
        "window": {"from": watermark, "to": tip, "blocks": tip - watermark},
        "wallets": {"checked": len(wallets), "tier_ab": wset["tier_ab_count"],
                    "feed": wset["feed_count"], "unique": wset["total_unique"],
                    "failed": sorted(failed_wallets.keys())},
        "sent_txs_in_window": sum(len(v) for v in sent.values()),
        "mint_events_new": len(mints),
        "contracts_new": len(by_contract),
        "machine_token_fast_path": machine_hits,
        "anomalies": anomalies,
        "signals_over_20pct": signals,
        "triggers_over_25pct": triggers,
        "getlogs_verification": verify,
        "paid_trend_top": paid_trend[:10],
        "max_block_seen": max_block,
    }
    findings_path = out_dir / f"run{run_no}-bscscan-findings.json"
    json.dump(summary, open(findings_path, "w"), indent=1)
    print(f"RUN {run_no} summary: {json.dumps(summary, indent=1)[:3000]}",
          flush=True)

    if args.dry_run:
        print(f"RUN {run_no} DRY RUN: state/log NOT written", flush=True)
        return 0 if all_verified else 1

    # ---- State + log write (watermark advances ONLY if all verified)
    backup = out_dir / f"tracked-wallet-mint-scan-state.json.bak-run{run_no}-pre"
    json.dump(state, open(backup, "w"), indent=1)
    if all_verified:
        state["last_run"] = {
            "run": run_no, "status": "OK - BscScan leg",
            "block_start": tip, "block_end": tip,
            "window_wib": f"{wib(watermark)} - {wib(tip)} (verified)",
            "wallets_checked": (
                f"tier-ab {wset['tier_ab_count']} + feed {wset['feed_count']} "
                f"= {wset['total_unique']} unik; 0 failed"),
            "method_note": (
                f"BscScan leg: txlist + tokentx/tokennfttx/token1155tx; "
                f"sent={summary['sent_txs_in_window']} txs, "
                f"mints baru={len(mints)}, kontrak baru={len(by_contract)}, "
                f"sinyal={len(signals)}, trigger={len(triggers)}"),
        }
        if mints:
            state.setdefault("reported_findings", []).append({
                "run": run_no,
                "counts": (f"{len(mints)} mint events, "
                           f"{len(by_contract)} distinct mint contracts"),
                "free_vs_paid": "per-mint value read from transfer data; "
                                "free/paid label is per tx value, not a quote read",
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
            "status": f"FAILED - BscScan leg incomplete "
                      f"({len(failed_wallets)} wallets unverified)",
            "block_start": watermark, "block_end": None,
            "window_wib": (f"window {watermark}-{tip} NOT advanced; "
                           f"run {run_no + 1} MUST rescan from {watermark}"),
            "wallets_checked": f"{len(failed_wallets)} wallets unverified; "
                               f"see {findings_path.name}",
            "method_note": "BscScan leg partial failure; do NOT treat as "
                           "zero-mint run.",
        }
        state[f"failed_wallets_run{run_no}"] = {
            w: legs for w, legs in failed_wallets.items()}
    state["next_run_note"] = (
        f"(Run {run_no}: {'OK' if all_verified else 'FAILED'} - BscScan leg; "
        f"watermark {'advanced to ' + str(tip) if all_verified else 'NOT advanced, stays ' + str(watermark)}; "
        f"sinyal={len(signals)} trigger={len(triggers)} machine-fast-path={len(machine_hits)} "
        f"anomali={len(anomalies)}.)")
    json.dump(state, open(STATE_PATH, "w"), indent=1)
    with open(LOG_PATH, "a") as f:
        f.write(f"\n## Run {run_no} — {wib(int(time.time()))} "
                f"(jendela blok {watermark}–{tip}, "
                f"{'TERVERIFIKASI' if all_verified else 'TIDAK TERVERIFIKASI'})\n")
        f.write(f"- Set segar: tier-ab {wset['tier_ab_count']} + feed "
                f"{wset['feed_count']} = {wset['total_unique']} unik; "
                f"wallet user tidak ada di set.\n")
        f.write(f"- Sent pass: {summary['sent_txs_in_window']} txs in-window; "
                f"mint baru: {len(mints)} events / {len(by_contract)} kontrak; "
                f"sinyal >20%: {len(signals)}; trigger >25%: {len(triggers)}; "
                f"machine fast-path: {len(machine_hits)}; anomali: {len(anomalies)}.\n")
        if triggers:
            f.write(f"- TRIGGER AUTO-MINT >25% (PERLU GUARD CHECK worker, "
                    f"BUKAN eksekusi driver): "
                    f"{', '.join(t['contract'] for t in triggers)}.\n")
        if signals:
            f.write(f"- SINYAL >20%: "
                    f"{', '.join(s['contract'] for s in signals)}.\n")
        if not all_verified:
            f.write(f"- GAGAL: {len(failed_wallets)} wallet tidak terverifikasi "
                    f"— watermark TIDAK maju; run {run_no + 1} harus rescan "
                    f"dari blok {watermark}.\n")
        f.write(f"- Bukti: scan-runs/run{run_no}-bscscan-findings.json. "
                f"State: tracked-wallet-mint-scan-state.json "
                f"(backup .bak-run{run_no}-pre).\n")
    print(f"RUN {run_no} {'OK' if all_verified else 'FAILED'}; "
          f"watermark={'advanced to ' + str(tip) if all_verified else 'NOT advanced'}",
          flush=True)
    return 0 if all_verified else 1


def _write_failed_run(state, run_no, watermark, tip, wset, reason,
                      out_dir, dry_run):
    print(f"RUN {run_no} FAILED: {reason}; watermark stays {watermark}",
          flush=True)
    if dry_run:
        return
    backup = out_dir / f"tracked-wallet-mint-scan-state.json.bak-run{run_no}-pre"
    json.dump(state, open(backup, "w"), indent=1)
    state["last_run"] = {
        "run": run_no, "status": f"FAILED - {reason}",
        "block_start": watermark, "block_end": None,
        "window_wib": f"window {watermark}-{tip} NOT advanced",
        "wallets_checked": "0 wallets verified (auth failure)",
        "method_note": reason,
    }
    json.dump(state, open(STATE_PATH, "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
