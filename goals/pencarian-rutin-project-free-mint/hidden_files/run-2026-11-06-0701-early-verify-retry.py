#!/usr/bin/env python3
"""Run 2026-11-06 0701 WIB: RETRY the failed first-mint checks for the 3 backfill NFTs,
via Ankr ankr_getLogs (address-filtered) with 30s timeout, plus retry of the two failed
first-mint block timestamps and quote(user,1) reads. Read-only."""
import json, sys, time, urllib.request, datetime
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0701"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
ITEMS = [
    ("Silent Hydra Agent", "0x56C7776351BaDf99D33A602026aAAD7Afc5E4dF4", 131896042),
    ("Cipher Wraith Agent", "0x50e9958a50B239f96fC64b9e1A06A3850D24063a", 131896743),
    ("Umbra Lynx Agent", "0x1062c963F5F11A5A55831B7e818E55b052B59947", 131897443),
]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def rpc(method, params, timeout=15):
    for rpc_url in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc_url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception:
            continue
    return None
def ankr_addr_logs(addr, frm, to):
    params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
              "address": addr, "pageSize": 1000, "decodeLogs": False,
              "topics": [TRANSFER, ZERO_TOPIC]}
    try:
        body = ankr_post("ankr_getLogs", params, timeout=30)
    except Exception as e:
        if "429" in str(e) or "rate" in str(e).lower():
            time.sleep(30)
            body = ankr_post("ankr_getLogs", params, timeout=30)
        else:
            raise
    result = body.get("result", {}) if isinstance(body, dict) else {}
    return result.get("logs", [])

out = {}
for name, addr, fb in ITEMS:
    r = {"address": addr, "first_block": fb}
    earlier, failed, err = 0, False, None
    start = 131880000
    while start < fb:
        end = min(start + 1999, fb - 1)
        try:
            logs = ankr_addr_logs(addr, start, end)
            earlier += len(logs)
        except Exception as e:
            failed = True
            err = str(e)[:200]
            break
        start = end + 1
        time.sleep(0.5)
    r["earlier_mints_before_first_block"] = None if failed else earlier
    r["first_mint_verified"] = (not failed) and earlier == 0
    r["earlier_check_error"] = err
    # retry first-mint block timestamp
    b = rpc("eth_getBlockByNumber", [hex(fb), False])
    if b and b.get("result"):
        ts = int(b["result"]["timestamp"], 16)
        r["first_mint_wib"] = datetime.datetime.fromtimestamp(
            ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    else:
        r["first_mint_wib"] = None
    # retry quote(user,1)
    q = rpc("eth_call", [{"to": addr, "data": sel("quote(address,uint256)") + enc(USER) + format(1, "064x")}, "latest"])
    r["quote_user_1_retry"] = None
    if q and q.get("result") and q["result"] != "0x":
        try:
            r["quote_user_1_retry"] = int(q["result"], 16)
        except Exception:
            r["quote_user_1_retry"] = q["result"]
    out[name] = r
    print(name, json.dumps(r), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-early-verify-retry.json", "w"), indent=1)
print("saved run-2026-11-06-0701-early-verify-retry.json")
