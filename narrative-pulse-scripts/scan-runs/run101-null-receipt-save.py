#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
TX = "0x62fb2bb4c86600a50a5f3170a40ea4fcd3156764b5bab268494a0dbfc771fccb"
r = fast_rpc.race("eth_getTransactionReceipt", [TX])
json.dump(r, open("/home/hatch/workspace/narrative-pulse/scan-runs/run101-null-receipt.json", "w"), indent=1)
print("status", r.get("status"), "block", int(r.get("blockNumber"), 16), "n_logs", len(r.get("logs") or []), "gasUsed", r.get("gasUsed"))
from Crypto.Hash import keccak
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
ZERO = "0x" + "0"*64
for lg in r.get("logs") or []:
    topics = lg.get("topics") or []
    if topics and topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO:
        print("MINT LOG:", lg.get("address"), "to", topics[2][-40:], "data", lg.get("data"))
print("saved run101-null-receipt.json")
