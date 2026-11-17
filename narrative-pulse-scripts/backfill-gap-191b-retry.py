#!/usr/bin/env python3
"""ONE retry pass over the failed getLogs legs of backfill 191b.

The main run ended PARTIAL with 12 failed legs (2 RemoteDisconnected
early, then HTTP 403 throttling + 1 RPC timeout in the tail). This is
a SINGLE spaced retry (30 s pause between calls, same 403 backoff),
run after a 4-minute cooldown so the bloXroute throttle window can
replenish. NOT a hammer loop: if a leg fails again it stays failed
and is reported as unverified — no further retries.

Reads the failed legs from run191b-backfill-gap-findings.json,
re-queries only those (chunk, topic) pairs, merges any mints found
into the progress file, and writes:
  ~/workspace/narrative-pulse/scan-runs/run191b-retry-findings.json
It also updates the main findings file's failed_chunks + status so
there is one authoritative record.
"""
import importlib.util
import json
import time
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace" / "narrative-pulse"
SCAN_RUNS_DIR = NP / "scan-runs"
PROGRESS_PATH = SCAN_RUNS_DIR / "run191b-backfill-progress.json"
FINDINGS_PATH = SCAN_RUNS_DIR / "run191b-backfill-gap-findings.json"
RETRY_FINDINGS_PATH = SCAN_RUNS_DIR / "run191b-retry-findings.json"

COOLDOWN_S = 240
PAUSE_BETWEEN_CALLS_S = 30

spec = importlib.util.spec_from_file_location(
    "b191b", str(NP / "backfill-gap-191b.py"))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def main():
    print(f"RETRY 191b: cooldown {COOLDOWN_S}s before first call "
          f"(throttle window breather)", flush=True)
    time.sleep(COOLDOWN_S)

    findings = json.load(open(FINDINGS_PATH))
    failed = findings["wallets"]["failed_chunks"]
    print(f"RETRY 191b: {len(failed)} failed legs to re-query", flush=True)

    prog = json.load(open(PROGRESS_PATH))
    mints = prog.get("mints", [])
    seen_tx = {m["tx"].lower() for m in mints if m.get("tx")}
    state = json.load(open(b.STATE_PATH))
    known = set()
    for f in state.get("reported_findings", []):
        for m in f.get("mints", []):
            if m.get("tx"):
                known.add(m["tx"].lower())

    wset = b.load_wallet_set()
    wallets = wset["wallets"]
    wtopics = ["0x000000000000000000000000" + w[2:] for w in wallets]

    block_ts_cache = {}
    tx_cache = {}

    def block_ts(block):
        if block not in block_ts_cache:
            r = b.rpc_call("eth_getBlockByNumber", [hex(block), False],
                           timeout=20, retries=1)
            block_ts_cache[block] = int(r["timestamp"], 16)
        return block_ts_cache[block]

    def tx_of(txhash):
        if txhash not in tx_cache:
            tx_cache[txhash] = b.rpc_call("eth_getTransactionByHash",
                                          [txhash], timeout=20, retries=1)
        return tx_cache[txhash]

    still_failed = []
    new_mints = 0
    first = True
    for leg in failed:
        cfrom, cto = leg["chunk"]
        kind_label = leg["topics"]
        if not first:
            time.sleep(PAUSE_BETWEEN_CALLS_S)
        first = False
        topics = ([b.TRANSFER_TOPIC0, b.ZERO_TOPIC, wtopics]
                  if kind_label == "Transfer"
                  else [b.TRANSFER_SINGLE_TOPIC0, None, b.ZERO_TOPIC,
                        wtopics])
        try:
            f = {"fromBlock": hex(cfrom), "toBlock": hex(cto),
                 "topics": topics}
            res = b.rpc_call("eth_getLogs", [f], timeout=60, retries=1)
        except Exception as e:
            still_failed.append({"chunk": [cfrom, cto],
                                 "topics": kind_label,
                                 "error": str(e)[:200]})
            print(f"  retry {cfrom}-{cto} {kind_label} FAILED again: {e}",
                  flush=True)
            continue
        n = 0
        for l in res or []:
            try:
                txh = (l.get("transactionHash") or "").lower()
                if not txh or txh in known or txh in seen_tx:
                    continue
                block = int(l["blockNumber"], 16)
                contract = (l.get("address") or "").lower()
                tps = l.get("topics") or []
                to_wallet = ("0x" + tps[2][26:].lower()
                             if kind_label == "Transfer" and len(tps) > 2
                             else "0x" + tps[3][26:].lower()
                             if len(tps) > 3 else None)
                if kind_label == "TransferSingle":
                    token_id = (int(tps[4], 16) if len(tps) > 4 else None)
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
                    "call_to": call_to, "kind": kind,
                    "mint_contract": contract,
                    "name": None, "symbol": None,
                    "time_wib": b.wib(block_ts(block)),
                    "token_id": token_id,
                    "amount": (str(amount) if amount is not None else None),
                    "tx": txh, "block": block, "wallet": to_wallet,
                    "value_bnb": (value_wei / 1e18
                                  if value_wei is not None else None),
                    "free": free,
                })
                seen_tx.add(txh)
                n += 1
            except Exception as e:
                print(f"  retry log parse failed: {e}", flush=True)
                continue
        new_mints += n
        print(f"  retry {cfrom}-{cto} {kind_label} OK: {n} new mints",
              flush=True)

    # token metadata for any new contracts found in retry
    by_contract = {}
    for m in mints:
        by_contract.setdefault(m["mint_contract"], []).append(m)
    for contract, ms in by_contract.items():
        if any(mm.get("name") is None for mm in ms):
            meta = b.token_meta(contract)
            for mm in ms:
                mm["name"] = meta["name"]
                mm["symbol"] = meta["symbol"]

    # save merged progress
    prog["mints"] = mints
    prog["mints_so_far"] = len(mints)
    prog["failed_chunks"] = still_failed
    prog["retry_done_wib"] = b.wib(int(time.time()))
    json.dump(prog, open(PROGRESS_PATH, "w"), indent=1)

    # aggregate per contract (same shape as main run)
    machine = {m["address"].lower(): m
               for m in state.get("machine_tokens", [])}
    machine_hits, anomalies, findings_mints = [], [], []
    for contract, ms in by_contract.items():
        wallets_c = sorted({m["wallet"] for m in ms if m["wallet"]})
        entities, raw, note = b.fold_entities(wallets_c)
        entry = {"contract": contract, "mints": len(ms),
                 "wallets": wallets_c, "entities": entities,
                 "raw_wallets": raw, "entity_note": note,
                 "first_seen_wib": min(
                     (m["time_wib"] for m in ms if m["time_wib"]),
                     default=None),
                 "kinds": sorted({m["kind"] for m in ms}),
                 "names": sorted({m["name"] for m in ms if m["name"]}),
                 "symbols": sorted({m["symbol"] for m in ms if m["symbol"]}),
                 "free_mints": sum(1 for m in ms if m["free"] is True),
                 "paid_mints": sum(1 for m in ms if m["free"] is False),
                 "free_unverified_mints": sum(1 for m in ms
                                              if m["free"] is None)}
        if contract in machine:
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
    signals = [e for e in findings_mints
               if b.SIGNAL_MIN_ENTITIES <= e["entities"]
               < b.AUTO_MINT_MIN_ENTITIES]
    triggers = [e for e in findings_mints
                if e["entities"] >= b.AUTO_MINT_MIN_ENTITIES]

    retry_summary = {
        "run": "191b-retry",
        "legs_retried": len(failed),
        "legs_still_failed": len(still_failed),
        "still_failed": still_failed,
        "new_mints_found": new_mints,
        "total_mints": len(mints),
        "contracts_new": len(by_contract),
        "machine_token_fast_path": machine_hits,
        "anomalies": anomalies,
        "signals_over_20pct": signals,
        "triggers_over_25pct": triggers,
    }
    json.dump(retry_summary, open(RETRY_FINDINGS_PATH, "w"), indent=1)

    # update the main findings file: authoritative record
    findings["wallets"]["failed_chunks"] = still_failed
    findings["mint_events_new"] = len(mints)
    findings["contracts_new"] = len(by_contract)
    findings["machine_token_fast_path"] = machine_hits
    findings["anomalies"] = anomalies
    findings["signals_over_20pct"] = signals
    findings["triggers_over_25pct"] = triggers
    findings["status"] = "OK" if not still_failed else "PARTIAL"
    findings["retry"] = {"legs_retried": len(failed),
                         "legs_still_failed": len(still_failed),
                         "new_mints_found": new_mints}
    json.dump(findings, open(FINDINGS_PATH, "w"), indent=1)
    print(f"RETRY 191b DONE: retried={len(failed)} "
          f"still_failed={len(still_failed)} new_mints={new_mints} "
          f"total_mints={len(mints)} contracts={len(by_contract)} "
          f"signals={len(signals)} triggers={len(triggers)}", flush=True)
    return 0 if not still_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
