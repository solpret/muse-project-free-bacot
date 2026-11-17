#!/usr/bin/env python3
"""Retry first-mint age lookup for the 5 S1 contracts from hot-leg run 2026-11-07 15:04 WIB.
Their age was UNVERIFIED then (public Ankr getLogs 401). Now via Ankr Advanced API get_logs.
Minted topic for the share-sale template; fallback earliest Transfer-from-zero.
Read-only. Block timestamp via dataseed."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import ankr as ankr_mod
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDRS = {
    "0x8717fc8751b8Ebd6832EA145974AA77D86bE9EaD": "WibblezapAgent",
    "0xe8b5E3ca9f4F51366f9f4860ed70b8e929e80470": "QuonkersAgent",
    "0x16A8aFdc97F8Cf48617bF15E47b4dA2217ea04A5": "DribblonAgent",
    "0xab3F2dA0b63F5A823510095263789E9e6F26329a": "HobnorbAgent",
    "0x2a71CEF7101B8b19c4ab18BeD40C3ec5EC87B9b7": "YammerjackAgent",
}
_k = keccak.new(digest_bits=256); _k.update(b"Minted(address,uint256,uint256,bool)")
MINTED = "0x" + _k.hexdigest()
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0" * 64
WIB = datetime.timezone(datetime.timedelta(hours=7))

def block_ts(blk):
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            v = _fast_single(ep, "eth_getBlockByNumber", [hex(blk), False], 8, retries=0)
            if v and v.get("timestamp"):
                return int(v["timestamp"], 16)
        except Exception:
            continue
    return None

out = {}
now = datetime.datetime.now(WIB)
for addr, name in ADDRS.items():
    r = ankr_mod.get_logs(addr, "earliest", "latest")
    logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
    minted = [l for l in logs if l["topics"] and l["topics"][0].lower() == MINTED]
    minted.sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
    entry = {"name": name, "total_logs": len(logs), "minted_events": len(minted)}
    if minted:
        f = minted[0]
        blk = int(f["blockNumber"], 16)
        ts = block_ts(blk)
        entry["first_minted"] = {"block": blk, "tx": f["transactionHash"],
                                 "logIndex": int(f["logIndex"], 16),
                                 "block_timestamp": ts}
        if ts:
            dt = datetime.datetime.fromtimestamp(ts, WIB)
            entry["first_minted"]["wib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
            entry["first_minted"]["age_hours"] = round((now.timestamp() - ts) / 3600, 2)
            entry["first_minted"]["age_le_48h"] = (now.timestamp() - ts) <= 48 * 3600
    else:
        # fallback: earliest Transfer-from-zero
        tr = [l for l in logs if l["topics"] and l["topics"][0].lower() == TRANSFER
              and len(l["topics"]) > 1 and l["topics"][1].lower() == ZERO]
        tr.sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
        entry["transfer_from_zero"] = len(tr)
        if tr:
            f = tr[0]
            blk = int(f["blockNumber"], 16)
            ts = block_ts(blk)
            entry["first_transfer_mint"] = {"block": blk, "tx": f["transactionHash"],
                                            "block_timestamp": ts}
            if ts:
                dt = datetime.datetime.fromtimestamp(ts, WIB)
                entry["first_transfer_mint"]["wib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
                entry["first_transfer_mint"]["age_hours"] = round((now.timestamp() - ts) / 3600, 2)
                entry["first_transfer_mint"]["age_le_48h"] = (now.timestamp() - ts) <= 48 * 3600
    out[addr] = entry
    json.dump({"logs": logs}, open(f"{BASE}/hot-leg-2026-11-07-1514-age-{name}.json", "w"))

json.dump(out, open(f"{BASE}/hot-leg-2026-11-07-1514-leg3-age-5.json", "w"), indent=1)
print(json.dumps(out, indent=1))
