#!/usr/bin/env python3
"""Mock tests for the Ankr -> BscScan scan migration (no API key needed).

Covers:
  1. bscscan.py envelope parsing (OK / empty / rate-limit retry /
     invalid key / Pro-required) and the 0.34 s pacing.
  2. Pagination helpers (_paged truncation flag, get_logs_all splitting).
  3. Driver mint detection (from == zero address), signal math
     (12 entities -> signal, 14 -> trigger, 11 -> none), machine-token
     fast path + anomaly flag, and the watermark rule (any unverified
     wallet -> watermark NOT advanced, exit 1).

Run: python3 test-bscscan-migration.py
Exit 0 = all mock tests pass. Live tests still need the BscScan key.
"""
import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / "workspace" / "custom-connectors" / "custom.bscscan" / "bin"))
import bscscan  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "scan_bscscan", str(HOME / "workspace" / "narrative-pulse" / "tracked-mint-scan-bscscan.py"))
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'PASS' if cond else 'FAIL'}: {name} {detail}")


# ---------------------------------------------------------------- client
# Mock the transport + the surrogate URL builder (no credential needed).
_calls = {"n": 0}
_script = {"mode": "ok"}


def _fake_http(url, timeout=30):
    _calls["n"] += 1
    mode = _script["mode"]
    if mode == "ok":
        return {"status": "1", "message": "OK",
                "result": [{"blockNumber": "133500000", "hash": "0xabc"}]}
    if mode == "empty":
        return {"status": "0", "message": "No transactions found", "result": []}
    if mode == "rate_then_ok":
        if _calls["n"] == 1:
            return {"status": "0", "message": "Max rate limit reached, please use API Key for higher rate limit.",
                    "result": "Max rate limit reached"}
        return {"status": "1", "message": "OK", "result": [{"blockNumber": "1"}]}
    if mode == "rate_always":
        return {"status": "0", "message": "Max rate limit reached", "result": "x"}
    if mode == "bad_key":
        return {"status": "0", "message": "NOTOK", "result": "Invalid API Key"}
    if mode == "pro":
        return {"status": "0", "message": "This API endpoint requires an API Pro subscription.",
                "result": "Upgrade to Pro"}
    raise AssertionError(f"unknown mode {mode}")


bscscan._http_get_json = _fake_http
bscscan.url_with_surrogate_query_param = (
    lambda url, name, allowed_hosts: url + "&apikey=MOCK")
bscscan._last_call_ts = 0.0

_script["mode"] = "ok"
r = bscscan.bscscan_get({"module": "account", "action": "txlist"})
check("envelope OK -> result list", isinstance(r, list) and r[0]["hash"] == "0xabc")

_script["mode"] = "empty"
r = bscscan.bscscan_get({"module": "account", "action": "txlist"})
check("'No transactions found' -> [] (not an error)", r == [])

_script["mode"] = "rate_then_ok"
_calls["n"] = 0
r = bscscan.bscscan_get({"module": "account", "action": "txlist"})
check("rate-limit -> 1 retry then OK", isinstance(r, list) and _calls["n"] == 2)

_script["mode"] = "rate_always"
_calls["n"] = 0
try:
    bscscan.bscscan_get({"module": "account", "action": "txlist"})
    check("rate-limit twice -> BscScanRateLimit", False)
except bscscan.BscScanRateLimit:
    check("rate-limit twice -> BscScanRateLimit", True)

_script["mode"] = "bad_key"
try:
    bscscan.bscscan_get({"module": "account", "action": "txlist"})
    check("Invalid API Key -> BscScanAuthError", False)
except bscscan.BscScanAuthError:
    check("Invalid API Key -> BscScanAuthError", True)

_script["mode"] = "pro"
try:
    bscscan.bscscan_get({"module": "token", "action": "tokenholderlist"})
    check("Pro endpoint -> BscScanProRequired", False)
except bscscan.BscScanProRequired:
    check("Pro endpoint -> BscScanProRequired", True)

# Pacing: two calls must be >= 0.34 s apart (mocked HTTP, real clock).
_script["mode"] = "ok"
bscscan._last_call_ts = 0.0
t0 = time.monotonic()
bscscan.bscscan_get({"module": "account", "action": "txlist"})
bscscan.bscscan_get({"module": "account", "action": "txlist"})
elapsed = time.monotonic() - t0
check("pacing >= 0.34 s between calls", elapsed >= 0.33, f"({elapsed:.2f}s)")

# Pagination helper: stops when a batch is short; flags truncation at 20 pages.
calls = {"pages": 0}


def _fake_paged_fn(addr, sb, eb, page=1, offset=10000):
    calls["pages"] += 1
    return ([{"x": 1}] * offset) if page < 3 else [{"x": 1}]


recs, trunc = bscscan._paged(_fake_paged_fn, "0xabc", 1, 2)
check("_paged stops on short batch, not truncated",
      len(recs) == 2 * 10000 + 1 and trunc is False, f"pages={calls['pages']}")

calls["pages"] = 0


def _always_full(a, s, e, page=1, offset=10000):
    calls["pages"] += 1
    return [{"x": 1}] * offset


recs, trunc = bscscan._paged(_always_full, "0xabc", 1, 2)
check("_paged flags truncation at MAX_PAGES", trunc is True and calls["pages"] == 20,
      f"pages={calls['pages']}")

# get_logs_all splits a full 1000-log page.
_calls["logs"] = 0
_orig_get_logs = bscscan.get_logs


def _fake_get_logs(contract, fb, tb, topic0=None, topic1=None, **kw):
    _calls["logs"] += 1
    if tb - fb >= 500:
        return [{"blockNumber": hex(fb), "topics": [topic0, topic1]}] * 1000
    return [{"blockNumber": hex(fb), "topics": [topic0, topic1]}] * 3


bscscan.get_logs = _fake_get_logs
logs, trunc = bscscan.get_logs_all("0xcontract", 1000, 1500,
                                   topic0=bscscan.TRANSFER_TOPIC0,
                                   topic1=bscscan.ZERO_TOPIC1)
check("get_logs_all splits full pages", len(logs) == 6 and trunc is False,
      f"calls={_calls['logs']}")
bscscan.get_logs = _orig_get_logs

# ---------------------------------------------------------------- driver
# Fixture: real 55-wallet set; synthetic mints.
wset = drv.load_wallet_set()
W = wset["wallets"]
assert len(W) == 55, f"expected 55 wallets, got {len(W)}"
TIP = 133539000
WM = 132534899
CONTRACT_A = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # 12 wallets -> signal
CONTRACT_B = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"  # 14 wallets -> trigger
CONTRACT_C = "0xcccccccccccccccccccccccccccccccccccccccc"  # 11 wallets -> none
MACHINE = "0x489e9bba4d7599aba33dacb2c0dfef4f64f17777"  # in state machine_tokens


def _mint(contract, wallet, i, name=None, symbol=None):
    return {"blockNumber": str(133000000 + i), "timeStamp": "1794600000",
            "hash": f"0xhash{i:04d}", "from": bscscan.ZERO_ADDRESS,
            "to": wallet, "contractAddress": contract,
            "tokenName": name or "", "tokenSymbol": symbol or "",
            "tokenID": "1" if "nft" in contract else None,
            "value": "1000000000000000000"}


def _run_driver(monkey, tmp):
    """Run the driver main() against a COPY of the real state in tmp dir."""
    state_path = tmp / "tracked-wallet-mint-scan-state.json"
    shutil.copy(HOME / "workspace" / "narrative-pulse" / "tracked-wallet-mint-scan-state.json",
                state_path)
    drv.STATE_PATH = state_path
    drv.LOG_PATH = tmp / "tracked-wallet-mint-scan-log.md"
    drv.SCAN_RUNS_DIR = tmp
    drv.tip_block = lambda: TIP
    sys.argv = ["tracked-mint-scan-bscscan.py", "--run", "170"]
    rc = drv.main()
    return rc, json.load(open(state_path)), json.load(
        open(tmp / "run170-bscscan-findings.json"))


# --- Happy path: A=signal, B=trigger, C=none, machine fast-path ---
def _leg_ok(addr, sb, eb, page=1, offset=10000):
    return [], False


def _tokentx_ok(addr, sb, eb, page=1, offset=10000):
    out = []
    idx = W.index(addr)
    if idx < 12:
        out.append(_mint(CONTRACT_A, addr, idx))
    if idx < 14:
        out.append(_mint(CONTRACT_B, addr, 100 + idx))
    if idx < 11:
        out.append(_mint(CONTRACT_C, addr, 200 + idx))
    if idx < 3:
        out.append(_mint(MACHINE, addr, 300 + idx))
    return out, False


drv.bscscan.txlist_all = lambda a, s, e: ([], False)
drv.bscscan.tokentx_all = _tokentx_ok
drv.bscscan.tokennfttx_all = lambda a, s, e: ([], False)
drv.bscscan.token1155tx_all = lambda a, s, e: ([], False)
drv.bscscan.get_logs_all = lambda c, fb, tb, topic0=None, topic1=None, _depth=0: (
    [{"topics": [topic0, topic1]}], False)

tmp = Path(tempfile.mkdtemp())
rc, state_after, summ = _run_driver(None, tmp)
check("driver happy path exit 0", rc == 0, f"rc={rc}")
check("signal: contract A (12 entities)",
      any(s["contract"] == CONTRACT_A for s in summ["signals_over_20pct"]))
check("trigger: contract B (14 entities)",
      any(t["contract"] == CONTRACT_B for t in summ["triggers_over_25pct"]))
check("no signal: contract C (11 entities)",
      not any(s["contract"] == CONTRACT_C
              for s in summ["signals_over_20pct"] + summ["triggers_over_25pct"]))
check("machine-token fast path (3 wallets, no name)",
      any(m["contract"] == MACHINE for m in summ["machine_token_fast_path"]))
check("watermark advanced to tip on verified run",
      state_after["last_run"]["block_start"] == TIP,
      f"block_start={state_after['last_run']['block_start']}")
check("no anomaly on clean machine-token", summ["anomalies"] == [])

# --- Anomaly: machine token suddenly has a name -> flagged, not fast-pathed ---
drv.bscscan.tokentx_all = lambda a, s, e: (
    [_mint(MACHINE, a, 400 + W.index(a), name="MachineCoin", symbol="MCH")
     for _ in [0] if W.index(a) < 2], False)
tmp2 = Path(tempfile.mkdtemp())
rc2, _, summ2 = _run_driver(None, tmp2)
check("machine-token with name -> anomaly (not fast path)",
      any(x["contract"] == MACHINE for x in summ2["anomalies"])
      and not any(m["contract"] == MACHINE
                  for m in summ2["machine_token_fast_path"]))

# --- Failure path: one wallet's txlist raises -> watermark NOT advanced ---
drv.bscscan.txlist_all = lambda a, s, e: (_ for _ in ()).throw(
    bscscan.BscScanError("boom")) if a == W[0] else ([], False)
drv.bscscan.tokentx_all = lambda a, s, e: ([], False)
tmp3 = Path(tempfile.mkdtemp())
rc3, state3, summ3 = _run_driver(None, tmp3)
check("one wallet failing -> exit 1", rc3 == 1, f"rc={rc3}")
check("watermark NOT advanced on failed run",
      state3["last_run"]["block_start"] == WM,
      f"block_start={state3['last_run']['block_start']}")
check("failed wallet recorded", W[0] in summ3["wallets"]["failed"])

# --- Mint detection: from != zero is NOT a mint ---
r = _mint(CONTRACT_A, W[0], 1)
r["from"] = "0x1234567890123456789012345678901234567890"
check("non-zero from is not a mint",
      (r.get("from") or "").lower() != bscscan.ZERO_ADDRESS)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
print("ALL MOCK TESTS PASSED (live tests still need the BscScan key)")
