#!/usr/bin/env python3
"""Read-only run 5 detail: full receipt topics for the 7 mint txs + name/symbol/owner
via fast_rpc eth_call (programmatic selectors, correct ABI string decode)."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64

parsed = json.load(open("/tmp/tracked-scan-run6-receipts.json"))
mint_hashes = [h for h, v in parsed.items() if v.get("mint_logs")]
print("mint txs:", len(mint_hashes), flush=True)
recs = fast_rpc.batch([("eth_getTransactionReceipt", [h]) for h in mint_hashes])
detail = {}
for h, r in zip(mint_hashes, recs):
    if r is None:
        detail[h] = {"error": "receipt_null"}; continue
    events = []
    for lg in r.get("logs") or []:
        topics = lg.get("topics") or []
        if not topics: continue
        if topics[0] == T_TRANSFER and len(topics) >= 4 and topics[1] == ZERO_PAD:
            events.append({"kind": "ERC721 Transfer", "contract": lg.get("address"),
                           "to": "0x" + topics[2][-40:], "token_id": int(topics[3], 16)})
        elif topics[0] == T_SINGLE and len(topics) >= 5 and topics[2] == ZERO_PAD:
            data = bytes.fromhex((lg.get("data") or "0x")[2:])
            events.append({"kind": "ERC1155 TransferSingle", "contract": lg.get("address"),
                           "to": "0x" + topics[3][-40:], "token_id": int(topics[4], 16),
                           "value": int.from_bytes(data[32:64], "big") if len(data) >= 64 else None})
        elif topics[0] == T_BATCH and len(topics) >= 4 and topics[2] == ZERO_PAD:
            events.append({"kind": "ERC1155 TransferBatch", "contract": lg.get("address"),
                           "to": "0x" + topics[3][-40:]})
    detail[h] = {"wallet": parsed[h]["wallet"], "to": parsed[h]["to"], "selector": parsed[h]["selector"],
                 "value": parsed[h]["value"], "time_wib": parsed[h]["time_wib"],
                 "receipt_status": r.get("status"), "block": r.get("blockNumber"),
                 "events": events}
    print(h, detail[h], flush=True)

# name/symbol/owner for each distinct mint contract
contracts = sorted({e["contract"] for d in detail.values() for e in d.get("events", [])})
print("contracts:", contracts, flush=True)
def decode_str(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception:
        return None
meta = {}
for c in contracts:
    res = []
    for fn in ("name()", "symbol()", "owner()"):
        for attempt in range(3):
            try:
                res.append(fast_rpc.race("eth_call", [{"to": c, "data": sel(fn)}, "latest"]))
                break
            except Exception as e:
                if attempt == 2:
                    res.append(None); print(c, fn, "ERROR", str(e)[:200], flush=True)
                time.sleep(8)
        time.sleep(6)
    name = decode_str(res[0]) if res and res[0] else None
    sym = decode_str(res[1]) if len(res) > 1 and res[1] else None
    owner = ("0x" + res[2][-40:]) if len(res) > 2 and res[2] else None
    meta[c] = {"name": name, "symbol": sym, "owner": owner}
    print(c, meta[c], flush=True)
    time.sleep(6)
json.dump({"detail": detail, "meta": meta}, open("/tmp/tracked-scan-run6-detail.json", "w"), indent=1)
print("saved /tmp/tracked-scan-run6-detail.json", flush=True)
