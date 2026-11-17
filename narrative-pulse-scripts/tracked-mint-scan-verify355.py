#!/usr/bin/env python3
"""Read-only verify: 0x355e mint receipts in full + on-chain name/symbol for each mint contract."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
from fast_rpc import batch

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()

W = "0x355ea9e542b36c645a2dee63b9df079ccb9bf3db"
W_PAD = "0x" + "0" * 24 + W[2:].lower()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")

d = json.load(open("/tmp/tracked-scan-decoded.json"))
txs = [t for t in d[W] if t["kind"] == "other"]
print(f"other txs for {W}: {len(txs)}", flush=True)
recs = {}
for i in range(0, len(txs), 6):
    chunk = txs[i:i+6]
    out = batch([("eth_getTransactionReceipt", [t["hash"]]) for t in chunk])
    for t, r in zip(chunk, out):
        recs[t["hash"]] = (t, r)
    time.sleep(4)

mints = []
for h, (t, r) in recs.items():
    if r is None:
        print(f"{t['time_wib']} {h[:12]} receipt NULL", flush=True); continue
    for lg in (r.get("logs") or []):
        tp = lg.get("topics") or []
        if not tp: continue
        if tp[0] == T_TRANSFER and len(tp) >= 3 and tp[1] == "0x" + "0" * 64 and tp[2].lower() == W_PAD:
            kind = "ERC721" if len(tp) == 4 else "ERC20"
            token_id = str(int(tp[3], 16)) if len(tp) == 4 else None
            amount = str(int(lg.get("data") or "0x0", 16)) if len(tp) == 3 else None
            mints.append({"time_wib": t["time_wib"], "hash": h, "call_to": t["to"],
                          "selector": t["selector"], "tx_value_bnb": int(t["value"], 16) / 1e18,
                          "mint_contract": lg.get("address"), "kind": kind,
                          "token_id": token_id, "amount_raw": amount})
        elif tp[0] == T_SINGLE and len(tp) >= 4 and tp[2] == "0x" + "0" * 64 and tp[3].lower() == W_PAD:
            mints.append({"time_wib": t["time_wib"], "hash": h, "call_to": t["to"],
                          "selector": t["selector"], "tx_value_bnb": int(t["value"], 16) / 1e18,
                          "mint_contract": lg.get("address"), "kind": "ERC1155",
                          "token_id": str(int(tp[4], 16)) if len(tp) >= 5 else None,
                          "amount_raw": None})
for m in sorted(mints, key=lambda x: x["time_wib"]):
    print(m, flush=True)
json.dump(mints, open("/tmp/tracked-scan-355-mints.json", "w"), indent=1)

# name()/symbol() for distinct mint contracts, batches of 5-6
contracts = sorted({m["mint_contract"] for m in mints})
print("distinct mint contracts:", contracts, flush=True)
SEL_NAME, SEL_SYMBOL = sel("name()"), sel("symbol()")
def dec_str(raw):
    try:
        b = bytes.fromhex(raw[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[32:64], "big"); ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception as e:
        return f"<decode err {e}>"
meta = {}
for i in range(0, len(contracts), 5):
    chunk = contracts[i:i+5]
    calls = []
    for c in chunk:
        calls.append((c, SEL_NAME)); calls.append((c, SEL_SYMBOL))
    # call_many batches eth_call; use it (max ~10 calls, split ok)
    from fast_rpc import call_many
    res = call_many(calls)
    for j, c in enumerate(chunk):
        meta[c] = {"name": dec_str(res[2*j]) if res[2*j] else None,
                   "symbol": dec_str(res[2*j+1]) if res[2*j+1] else None}
    time.sleep(4)
print(json.dumps(meta, indent=1), flush=True)
json.dump(meta, open("/tmp/tracked-scan-355-meta.json", "w"), indent=1)
