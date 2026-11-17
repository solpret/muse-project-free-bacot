#!/usr/bin/env python3
"""Zorrie deep first-mint walk-back + bytecode selector check, run 1901. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
A = "0x47feee72353358a61618cE640265F9f406f88E47"

# owner vs same-owner discards
discards = json.load(open(BASE + "/same-owner-discards.json"))
owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}
print("owner 0x394f6bade236789d0a060e4bfd40501cd95345a5 in discards:", "0x394f6bade236789d0a060e4bfd40501cd95345a5" in owners)

# bytecode selectors
code = batch([("eth_getCode", [A, "latest"])], endpoint="https://bsc-dataseed.binance.org/", timeout=15)[0]
code_l = str(code).lower()
def sel(sig): return keccak(sig.encode()).hex()[:8]
for sig in ["mintFree((address,uint256,uint256,bool),bytes)",
            "mintPaid((address,uint256,uint256,bool),bytes)",
            "freeMintedPerWallet(address)", "totalMinted()", "maxSupply()",
            "agentRegistry()", "AGENT_ID()", "hasAgentId(address)", "isAgent(address)"]:
    print(sig, "->", sel(sig), "in code:", sel(sig) in code_l)

# first mint walk-back: up to 60 chunks of 1000 blocks from head
head = int(scan.rpc_call("eth_blockNumber", []), 16)
print("head:", head, flush=True)
first = None
to_b = head
for i in range(60):
    frm = max(0, to_b - 999)
    try:
        logs, _ = scan.ankr_logs(frm, to_b, [scan.TRANSFER, scan.ZERO_TOPIC])
    except Exception as e:
        print(f"chunk {frm}-{to_b} ERROR {e}", flush=True); break
    mine = [l for l in logs if l.get("address", "").lower() == A.lower()]
    print(f"chunk {i} {frm}-{to_b}: {len(logs)} logs, {len(mine)} zorrie mints", flush=True)
    if mine:
        first = min(int(l["blockNumber"], 16) for l in mine)
        to_b = first - 1
        continue
    to_b = frm - 1  # empty chunk: keep walking back
print("earliest zorrie mint block:", first)
ts = None
if first:
    blk = batch([("eth_getBlockByNumber", [hex(first), False])], endpoint="https://bsc-dataseed.binance.org/", timeout=15)[0]
    ts = blk.get("timestamp") if isinstance(blk, dict) else None
    print("first mint block timestamp (dataseed):", ts, int(ts, 16) if ts else None)
    import datetime
    if ts:
        print("first mint WIB:", datetime.datetime.fromtimestamp(int(ts, 16), datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"))
json.dump({"first_mint_block": first, "first_mint_ts": ts, "head": head},
          open(BASE + "/run-2026-11-08-1901-zorrie-firstmint.json", "w"), indent=1)
print("DONE")
