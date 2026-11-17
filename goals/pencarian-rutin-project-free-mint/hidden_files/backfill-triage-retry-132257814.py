#!/usr/bin/env python3
"""Retry 429'd ZSEAT selectors + sample mint tx values (paid vs free).
Read-only. 8s pause between eth_calls; Ankr via proxy (ankr_post).
Appends to backfill-triage-132257814-132260648.json under 'retry' + 'mint_tx_sample'.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from eth_hash.auto import keccak
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132257814-132260648.json"
ADDR = "0xA5C09809Ada4969FBe1D67A9034Ed9633C98Ab87"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"
EPS = ["https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-rpc.publicnode.com/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

def dec_addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def dec_uint(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 2:
        try:
            return int(raw, 16)
        except Exception:
            return None
    return None

out = json.load(open(OUT))
retry = out.get("retry", {})

RETRY_SIGS = [("agentIdRegistry()", "zero", "addr"),
              ("AGENT_ID_REGISTRY()", "zero", "addr"),
              ("freeCount(address)", "addr", "uint"),
              ("quote(address,uint256)", "addr_uint", "uint"),
              ("minted(address)", "addr", "uint")]
for sig, kind, dec in RETRY_SIGS:
    if sig in retry and retry[sig].get("raw"):
        continue
    data = sel(sig)
    if kind == "addr":
        data += USER_PAD
    elif kind == "addr_uint":
        data += USER_PAD + ONE
    raw, e = None, None
    for attempt in (1, 2):
        raw, e = rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
        if raw or (e and "429" not in str(e)):
            break
        print(f"{sig} attempt {attempt}: 429, waiting 20s...", flush=True)
        time.sleep(20)
    row = {"raw": (raw or "")[:130], "error": e}
    if dec == "addr":
        row["addr"] = dec_addr(raw) if raw else None
    elif dec == "uint":
        row["uint"] = dec_uint(raw) if raw else None
    retry[sig] = row
    print(f"RETRY {sig}: raw={(raw or '')[:66]} -> {row.get('addr') or row.get('uint')} err={str(e)[:80] if e else None}", flush=True)
    out["retry"] = retry
    json.dump(out, open(OUT, "w"), indent=1)
    time.sleep(8)

# Sample mint tx values via Ankr getLogs (Transfer from zero address, this contract)
print("fetching mint logs via Ankr...", flush=True)
params = {"blockchain": "bsc", "fromBlock": hex(132259700), "toBlock": hex(132260648),
          "address": [ADDR.lower()], "pageSize": 1000, "decodeLogs": False,
          "topics": [TRANSFER, ZERO_TOPIC]}
try:
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = (body.get("result", {}) or {}).get("logs", [])
except Exception as e:
    print(f"ankr_getLogs failed: {e}", flush=True)
    logs = []
print(f"mint logs found: {len(logs)}", flush=True)
txs = []
seen_tx = set()
for lg in logs:
    h = lg.get("transactionHash")
    if h and h not in seen_tx:
        seen_tx.add(h)
        txs.append(h)
    if len(txs) >= 5:
        break
sample = []
for h in txs:
    tx, e = rpc("eth_getTransactionByHash", [h], timeout=10)
    val = None
    fn = None
    if isinstance(tx, dict):
        v = tx.get("value")
        val = int(v, 16) if isinstance(v, str) else v
        inp = tx.get("input", "")
        fn = inp[:10] if isinstance(inp, str) and len(inp) >= 10 else None
    sample.append({"tx": h, "value_wei": val, "value_bnb": (val / 1e18 if val is not None else None), "fn_selector": fn, "error": e})
    print(f"tx {h[:18]}... value={sample[-1]['value_bnb']} BNB fn={fn} err={e}", flush=True)
    time.sleep(4)
out["mint_tx_sample"] = {"logs": len(logs), "sampled": sample}
json.dump(out, open(OUT, "w"), indent=1)
print("RETRY+DONE", flush=True)
