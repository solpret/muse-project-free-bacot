#!/usr/bin/env python3
"""Run 66: verify the two 27-wallet paid tokens (read-only eth_call + receipt log reads)."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak

def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
ZERO_PAD = "0x" + "0" * 64

def call(addr, data):
    try:
        return fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
    except Exception as e:
        return f"ERROR:{e}"

def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def read_str(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR") or len(r) < 130:
        return f"unreadable({str(r)[:60]})"
    try:
        ln = int(r[130:194], 16)
        raw = bytes.fromhex(r[194:194 + ln * 2])
        return raw.decode("utf-8", "replace")
    except Exception as e:
        return f"decode-error {e}"

def read_uint(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:60]})"
    try:
        return int(r, 16)
    except Exception:
        return f"raw:{r[:80]}"

def read_addr(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:60]})"
    try:
        return "0x" + r[-40:]
    except Exception:
        return f"raw:{r[:80]}"

TOKENS = ["0x19b7fd3ae4234e4e632ff0b0f01f62a5340d7777",
          "0x540df48115f469c4083ba7a6d03255ea5f6f7777"]
out = {}
for t in TOKENS:
    out[t] = {
        "name": read_str(t, "name()"),
        "symbol": read_str(t, "symbol()"),
        "decimals": read_uint(t, "decimals()"),
        "totalSupply": read_uint(t, "totalSupply()"),
        "owner": read_addr(t, "owner()"),
    }
    print(t, out[t], flush=True)

# earliest sample buy per token: scan receipts for Transfer (from != zero) to tracked wallet
rec = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run67-receipts.json"))
sent = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run67-sent.json"))
tier = json.load(open(Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}

# need raw receipts again for Transfer logs (run67-receipts.json only kept mint_logs);
# re-fetch receipts for txs touching each token is expensive; instead use sent tx list:
# find earliest in-window tx per token via Ankr-free approach: scan receipts json for paid info is not stored.
# Fallback: getLogs per token address-filtered via Ankr for Transfer to tracked wallets.
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
for t in TOKENS:
    try:
        data = ankr_mod.get_logs(t, 131870175, 131870174, topics=[T_TRANSFER, None, sorted(tracked_padded)])
        logs = ((data.get("result") or {}).get("logs") or [])
        print(t, "ankr topic-filtered Transfer-to-tracked logs:", len(logs), flush=True)
        # earliest by block
        if logs:
            logs_sorted = sorted(logs, key=lambda l: (int(l.get("blockNumber","0x0"),16), int(l.get("logIndex","0x0"),16)))
            first = logs_sorted[0]
            print("  first:", first.get("transactionHash"), "block", int(first.get("blockNumber","0x0"),16),
                  "from", first.get("topics")[1], "amount_raw", int(first.get("data","0x0"),16), flush=True)
            out[t]["first_tracked_transfer_tx"] = first.get("transactionHash")
            out[t]["first_tracked_transfer_block"] = int(first.get("blockNumber","0x0"),16)
            out[t]["first_tracked_transfer_from"] = first.get("topics")[1]
            out[t]["first_tracked_transfer_amount_raw"] = int(first.get("data","0x0"),16)
            out[t]["tracked_transfer_log_count"] = len(logs)
    except Exception as e:
        print(t, "ankr ERROR", e, flush=True)

# pair verification for the first-transfer 'from' (pair) of each token
for t in TOKENS:
    pair_padded = out[t].get("first_tracked_transfer_from")
    if not pair_padded or not pair_padded.startswith("0x"):
        continue
    pair = "0x" + pair_padded[-40:]
    t0 = read_addr(pair, "token0()")
    t1 = read_addr(pair, "token1()")
    print(t, "pair", pair, "token0", t0, "token1", t1, flush=True)
    out[t]["pair"] = pair
    out[t]["pair_token0"] = t0
    out[t]["pair_token1"] = t1

json.dump(out, open(Path.home() / "workspace/narrative-pulse/scan-runs/run67-token-verify.json", "w"), indent=1)
print("saved run67-token-verify.json", flush=True)
