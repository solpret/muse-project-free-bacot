#!/usr/bin/env python3
"""Registry watch for FREE BACOT — READ-ONLY, keyless.

Polls the Agent ID registry contract (ERC721) for NEW mints: Transfer
events from the zero address. Resolves tokenURI -> metadata (name, links,
candidate NFT contract) best-effort. Never previews, mints, claims,
approves, signs, swaps, or executes anything.

Replaces the discovery function of Boltbook (boltbook.com died 2026-11-07,
parked on HugeDomains). Registry mints run ~3 per ~50 minutes, so a
15-minute cadence catches them promptly.

Logs pattern 2026-11-17 (12 consecutive failures on bloXroute):
eth_getLogs via bloXroute died (HTTP 403 "administrative rules" +
timeouts) and every other public endpoint refuses the method
(dataseeds/nodereal -32005 "limit exceeded" even on 10-block ranges,
publicnode/onfinality/drpc HTTP 429) — the shared egress IP is
rate-limited for this heavy method. Logs now come from plain
eth_getLogs in 500-block chunks via fetch_logs(): primary
https://rpc-bsc.48.club (proven 2026-11-17: 500-block calls OK and
deterministic; a 2000-block single call times out), fallback
https://1rpc.io/bnb (max 50-block range, sub-chunked; flaky 429),
then bloXroute/dataseeds/nodereal/publicnode/onfinality/drpc as last
resort. bsc.publicnode.com is EXCLUDED: it answered OK with 0 logs for
a window where 48.club returned 13 — silently dropping mints.
eth_call via fast_rpc._single over public BSC endpoints (unchanged).

State: registry-watch-state.json {last_block, seen: {tokenId: {...}}}
Run output: registry-watch-<from>-<to>.json {from_block, to_block,
new_mints: [...], reresolved: [...], unresolved: [tokenId, ...]}
(reresolved = previously unresolved mints whose metadata now reads;
unresolved mints are retried on later runs until resolved.)
Lock: registry-watch.lock (fcntl, non-blocking) — exit 3 if held.
Watermark advances ONLY over the verified fetched prefix: a chunk
that fails on all endpoints stops the run (exit 1) after advancing
over the chunks already fetched; next run resumes after the last
verified block, so no block is ever skipped.

Usage:
  python3 -u registry-watch.py [--from-block N] [--to-block N] [--dry-run]
  (no args: from = state last_block+1, to = head, cap 2000 blocks/run;
   no state file: seed from = head - 500)
Exit codes: 0 = ok; 1 = getLogs failed (watermark unchanged);
            3 = lock held by another run.
"""
import argparse
import fcntl
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single  # noqa: E402

REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
TOKENURI_SEL = "0xc87b56dd"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"}
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")


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


LOG_CHUNK = 500  # blocks per eth_getLogs call (was: one 2000-block call)
LOG_MAX_RANGE = {"https://1rpc.io/bnb": 50}  # per-endpoint range caps
LOG_ENDPOINTS = [
    "https://rpc-bsc.48.club",           # primary (proven 2026-11-17)
    "https://1rpc.io/bnb",              # fallback, max 50-block range
    "https://bsc.rpc.blxrbdn.com",      # ex-primary, now 403/timeout
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed3.bnbchain.org/",
    "https://bsc-dataseed-public.bnbchain.org/",
    "https://bsc.nodereal.io/",
    "https://bsc-rpc.publicnode.com/",
    "https://bnb.api.onfinality.io/public/",
    "https://bsc.drpc.org/",
]


def _logs_one_endpoint(ep, from_block, to_block):
    """eth_getLogs on one endpoint for [from_block, to_block].

    Splits into <=50-block pieces on endpoints that cap the range
    (1rpc). Returns a list of log dicts; raises on any failure.
    """
    cap = LOG_MAX_RANGE.get(ep)
    out = []
    frm = from_block
    while frm <= to_block:
        to = frm + (cap - 1 if cap else to_block - frm)
        if to > to_block:
            to = to_block
        filt = {"address": REGISTRY,
                "fromBlock": hex(frm), "toBlock": hex(to),
                "topics": [TRANSFER, ZERO_TOPIC]}
        res = _single(ep, "eth_getLogs", [filt], 12, retries=0)
        out.extend(res or [])
        frm = to + 1
    return out


class PartialLogsError(Exception):
    """Raised when some chunks fetched OK but a later chunk failed.

    Carries the logs fetched so far and the last fully-fetched block,
    so the caller can advance the watermark over the verified prefix
    instead of discarding all progress.
    """
    def __init__(self, logs, last_good_block, message):
        super().__init__(message)
        self.logs = logs
        self.last_good_block = last_good_block


def fetch_logs(from_block, to_block):
    """Registry Transfer-from-zero logs in [from_block, to_block].

    Requests are chunked into LOG_CHUNK-block pieces; each piece is
    tried on LOG_ENDPOINTS in order until one returns, with one retry
    after a short pause (transient flakes on the primary are common).
    If a piece still fails on every endpoint, raises PartialLogsError
    with the logs fetched so far (caller advances over that prefix).
    """
    out = []
    frm = from_block
    last_good = from_block - 1
    while frm <= to_block:
        to = min(frm + LOG_CHUNK - 1, to_block)
        chunk = None
        last_err = None
        for _attempt in range(2):
            for ep in LOG_ENDPOINTS:
                try:
                    chunk = _logs_one_endpoint(ep, frm, to)
                    break
                except Exception as e:  # noqa: BLE001
                    last_err = e
            if chunk is not None:
                break
            time.sleep(5)
        if chunk is None:
            raise PartialLogsError(
                out, last_good,
                f"getLogs {frm}-{to} failed on all endpoints: {last_err}")
        out.extend(chunk)
        last_good = to
        frm = to + 1
    return out


def decode_abi_string(hexdata):
    """Decode an eth_call return that is a dynamic string."""
    if not isinstance(hexdata, str) or not hexdata.startswith("0x"):
        return None
    try:
        raw = bytes.fromhex(hexdata[2:])
    except Exception:  # noqa: BLE001
        return None
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


def token_uri(token_id):
    data = TOKENURI_SEL + token_id.to_bytes(32, "big").hex()
    raw = rpc_call("eth_call", [{"to": REGISTRY, "data": "0x" + data},
                                "latest"], timeout=8)
    return decode_abi_string(raw)


def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def fetch_metadata(uri):
    """Return (metadata_dict_or_None, fetched_url_or_None)."""
    if not uri:
        return None, None
    candidates = []
    if uri.startswith("ipfs://"):
        rest = uri[len("ipfs://"):]
        candidates.append("https://ipfs.io/ipfs/" + rest)
        candidates.append("https://gateway.pinata.cloud/ipfs/" + rest)
    elif uri.startswith("http://") or uri.startswith("https://"):
        candidates.append(uri)
    else:
        return None, None
    last_err = None
    for url in candidates:
        try:
            return fetch_json(url), url
        except Exception as e:  # noqa: BLE001
            last_err = e
    log(f"  metadata fetch FAILED for {uri}: {last_err}")
    return None, None


def _resolve(token_id, rec):
    """Best-effort tokenURI + metadata resolution into rec.

    Returns True when metadata was read (rec['resolved']=True), False
    otherwise. RPC/HTTP failure never raises — the mint stays unresolved
    and is retried on a later run.
    """
    try:
        uri = token_uri(token_id)
    except Exception as e:  # noqa: BLE001
        log(f"  tokenId {token_id}: tokenURI FAILED ({type(e).__name__}) — "
            "unresolved, retry next run")
        uri = None
    if not uri:
        return False
    rec["uri"] = uri
    md, fetched_url = fetch_metadata(uri)
    if not isinstance(md, dict):
        log(f"  tokenId {token_id}: uri={uri} metadata unreadable")
        return False
    rec["metadata"] = {k: md.get(k) for k in
                       ("name", "description", "image",
                        "external_url", "external_link",
                        "website") if k in md}
    rec["name"] = md.get("name")
    rec["resolved"] = True
    blob = json.dumps(md)
    for cand in ADDR_RE.findall(blob):
        if cand.lower() != REGISTRY.lower():
            rec["candidate_nft_contract"] = cand
            break
    return True


def atomic_write_json(path, obj):
    tmp = path + ".tmp-regwatch"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def load_state(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"last_block": None, "seen": {}}


def head_block():
    try:
        return int(rpc_call("eth_blockNumber", [], timeout=5), 16)
    except Exception as e:  # noqa: BLE001
        log(f"head block UNVERIFIED (read failed): {e}")
        return None


def scan_state_head():
    try:
        with open(os.path.join(BASE, "onchain-scan-state.json")) as f:
            return json.load(f).get("last_scanned_block")
    except Exception:  # noqa: BLE001
        return None


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-block", type=int, default=None)
    ap.add_argument("--to-block", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    state_path = os.path.join(BASE, "registry-watch-state.json")
    lock_path = os.path.join(BASE, "registry-watch.lock")
    lock_f = None
    if not args.dry_run:
        lock_f = open(lock_path, "w")
        try:
            fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log("LOCKED: another registry-watch run holds the lock — exiting")
            return 3

    state = load_state(state_path)
    seen = state.get("seen", {})

    head = head_block()
    if args.from_block is not None:
        from_block = args.from_block
    elif state.get("last_block") is not None:
        from_block = state["last_block"] + 1
    elif head is not None:
        from_block = head - 500
    else:
        fallback = scan_state_head()
        from_block = fallback if fallback is not None else 0
    if args.to_block is not None:
        to_block = args.to_block
    elif head is not None:
        to_block = head
    else:
        to_block = from_block + 1999
    # Cap window at 2000 blocks per run.
    if to_block - from_block + 1 > 2000:
        to_block = from_block + 1999
    if to_block < from_block:
        log(f"nothing to scan (from {from_block} > to {to_block})")
        return 0

    log(f"REGISTRY-WATCH {from_block}..{to_block} "
        f"({to_block - from_block + 1} blocks)"
        f"{' DRY-RUN' if args.dry_run else ''}")

    partial = False
    try:
        logs = fetch_logs(from_block, to_block)
    except PartialLogsError as e:
        if e.last_good_block < from_block:
            log(f"ERROR getLogs {from_block}-{to_block}: {e} — "
                "watermark unchanged")
            return 1
        log(f"PARTIAL getLogs: {e} — processing verified prefix "
            f"{from_block}..{e.last_good_block}, watermark advances there")
        logs = e.logs
        to_block = e.last_good_block
        partial = True
    except Exception as e:  # noqa: BLE001
        log(f"ERROR getLogs {from_block}-{to_block}: {e} — watermark unchanged")
        return 1
    log(f"getLogs returned {len(logs)} Transfer-from-zero logs")

    mints = []
    for lg in logs:
        addr = (lg.get("address") or "").lower()
        if addr != REGISTRY.lower():
            continue
        topics = lg.get("topics", [])
        if len(topics) < 3 or topics[1].lower() != ZERO_TOPIC:
            continue
        minter = "0x" + topics[2][-40:]
        token_id = None
        if len(topics) == 4:
            try:
                token_id = int(topics[3], 16)
            except Exception:  # noqa: BLE001
                token_id = None
        if token_id is None:
            data = lg.get("data") or ""
            try:
                token_id = int(data, 16)
            except Exception:  # noqa: BLE001
                continue
        blk = int(lg.get("blockNumber", "0x0"), 16)
        mints.append({"tokenId": token_id, "minter": minter, "block": blk,
                      "tx": lg.get("transactionHash")})
    log(f"registry mints in window: {len(mints)}")

    new_mints = []
    reresolved = []
    unresolved = []
    run_tag = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    for m in sorted(mints, key=lambda x: x["tokenId"]):
        tid = str(m["tokenId"])
        existing = seen.get(tid)
        if existing and existing.get("resolved"):
            continue  # already known + resolved
        if existing and not existing.get("resolved"):
            # Retry resolution for a previously unresolved mint; keep the
            # original record (block/tx/minter/first_seen_run).
            rec = dict(existing)
            resolved_now = _resolve(m["tokenId"], rec)
            if resolved_now:
                reresolved.append(rec)
            else:
                unresolved.append(m["tokenId"])
            if not args.dry_run:
                seen[tid] = rec
            continue
        rec = {"block": m["block"], "tx": m["tx"], "minter": m["minter"],
               "name": None, "uri": None, "metadata": None,
               "candidate_nft_contract": None, "resolved": False,
               "first_seen_run": run_tag}
        if _resolve(m["tokenId"], rec):
            log(f"  tokenId {tid}: name={rec['name']!r} "
                f"candidate={rec['candidate_nft_contract']}")
        else:
            unresolved.append(m["tokenId"])
        if not args.dry_run:
            seen[tid] = rec
        new_mints.append(rec)

    out = {"from_block": from_block, "to_block": to_block,
           "new_mints": new_mints,
           "reresolved": reresolved,
           "unresolved": unresolved,
           "run_at": run_tag}
    out_path = os.path.join(
        BASE, f"registry-watch-{from_block}-{to_block}.json")
    if not args.dry_run:
        atomic_write_json(out_path, out)
        state["last_block"] = to_block
        state["seen"] = seen
        atomic_write_json(state_path, state)
        log(f"state updated: last_block={to_block}, seen={len(seen)}")
    else:
        log(f"DRY-RUN: would write {out_path} (not written); "
            f"state NOT mutated")
    log(f"done in {time.time() - t0:.1f}s: "
        f"{len(new_mints)} new, {len(reresolved)} re-resolved, "
        f"{len(unresolved)} unresolved")
    return 1 if partial else 0


if __name__ == "__main__":
    sys.exit(main())
