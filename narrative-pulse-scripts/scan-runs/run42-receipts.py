#!/usr/bin/env python3
"""Read-only run 42 receipt phase (SUBSTITUTION, disclosed): fast_rpc's race
failed ALL its endpoints (timeouts) at 02:25-03:0x WIB, so receipts are
fetched by direct JSON-RPC batch calls to the same class of free public BSC
endpoints (publicnode primary, drpc fallback), batch 20, timeout 60s.
Same mint-log parse as run41 (Transfer / TransferSingle from zero address
to a tracked wallet). Window capped at retry-pass max_block 131682618;
mop-up txs above that block are left for next run (re-fetched + deduped).
No preview/mint/sign/login."""
import json, sys, time, urllib.request
from pathlib import Path
from Crypto.Hash import keccak

HOME = Path.home()
SENT = HOME / "workspace/narrative-pulse/scan-runs/run42-sent.json"
OUT = HOME / "workspace/narrative-pulse/scan-runs/run42-receipts.json"
WINDOW_END = 131682618

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
APPROVE = sel("approve(address,uint256)")
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64

sent = json.load(open(SENT))
cands = []
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        if t["block"] > WINDOW_END:
            continue
        if t["input_prefix"] == APPROVE:
            continue
        cands.append((w, t))
print(f"receipt candidates={len(cands)} (non-approve, block <= {WINDOW_END})", flush=True)

ENDPOINTS = ["https://bsc-rpc.publicnode.com/", "https://bsc.drpc.org/"]

def fetch_batch(chunk):
    """chunk: list of tx hashes. Returns list of receipts (or None)."""
    payload = json.dumps([{"jsonrpc": "2.0", "id": i + 1, "method": "eth_getTransactionReceipt",
                           "params": [h]} for i, h in enumerate(chunk)]).encode()
    last_err = None
    for url in ENDPOINTS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, data=payload,
                                             headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = json.loads(resp.read().decode())
                by_id = {item.get("id"): item.get("result") for item in body}
                return [by_id.get(i + 1) for i in range(len(chunk))]
            except Exception as e:
                last_err = str(e)[:200]
                time.sleep(3.0)
    print(f"  batch FAILED ({chunk[0][:12]}...): {last_err}", flush=True)
    return [None] * len(chunk)

receipts = {}
for j in range(0, len(cands), 20):
    chunk = cands[j:j + 20]
    res = fetch_batch([t["hash"] for _, t in chunk])
    for (w, t), r in zip(chunk, res):
        receipts[t["hash"]] = r
    if (j + 20) % 200 == 0:
        print(f"  {j + 20}/{len(cands)}", flush=True)
    time.sleep(2.0)

parsed = {}
for w, t in cands:
    r = receipts.get(t["hash"])
    if r is None:
        parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                             "value": t["value"], "time_wib": t["time_wib"], "status": "receipt_null"}
        continue
    logs = r.get("logs") or []
    mint_logs = []
    for lg in logs:
        topics = lg.get("topics") or []
        if not topics:
            continue
        if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[2], "data": lg.get("data")})
        elif topics[0] in (T_SINGLE, T_BATCH) and len(topics) >= 4 and topics[2] == ZERO_PAD:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[3], "data": lg.get("data"), "batch": True})
    parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                         "value": t["value"], "time_wib": t["time_wib"],
                         "receipt_status": r.get("status"), "n_logs": len(logs), "mint_logs": mint_logs}
json.dump(parsed, open(OUT, "w"), indent=1)
n_mint = sum(1 for v in parsed.values() if v.get("mint_logs"))
n_null = sum(1 for v in parsed.values() if v.get("status") == "receipt_null")
n_s1 = sum(1 for v in parsed.values() if v.get("receipt_status") == "0x1")
n_s0 = sum(1 for v in parsed.values() if v.get("receipt_status") == "0x0")
print(f"RECEIPTS DONE total={len(parsed)} with_mint_logs={n_mint} null={n_null} status1={n_s1} status0={n_s0}", flush=True)
for h, v in parsed.items():
    if v.get("mint_logs"):
        print(f"MINT {h} wallet={v['wallet'][:10]} to={v['to']} sel={v['selector']} val={v['value']} time={v['time_wib']} logs={v['mint_logs']}", flush=True)
