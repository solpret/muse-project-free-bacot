#!/usr/bin/env python3
"""Run 2026-11-06 0701 WIB: verify the 3 backfill first-seen NFTs (Silent Hydra / Cipher
Wraith / Umbra Lynx). All three ABIs (curl-verified) are IDENTICAL: 29 functions incl.
AGENT_REGISTRY + mint + quote + spotsLeft + MAX_SUPPLY, no free views. The shared
classify() GATE_WORDS misses 'AGENT_REGISTRY' (underscore) - all three ARE agent-shaped
by the registry-reference prong. This script: (a) first-mint check via address-filtered
Transfer-from-zero logs 131880000..first_block-1; (b) fresh on-chain state reads
(totalSupply/totalMinted/spotsLeft/MAX_SUPPLY/PRICE/quote(user,1)/mintedBy(user)/
balanceOf(user)); (c) first-mint block timestamps for age. Read-only."""
import json, urllib.request, datetime
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0701"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
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
def call(addr, data):
    out = rpc("eth_call", [{"to": addr, "data": data}, "latest"])
    if not out or "result" not in out:
        return None
    v = out["result"]
    if not v or v == "0x":
        return None
    try:
        return int(v, 16)
    except Exception:
        return v
def block_ts(n):
    out = rpc("eth_getBlockByNumber", [hex(n), False])
    if not out or "result" not in out or not out["result"]:
        return None
    ts = int(out["result"]["timestamp"], 16)
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
def getlogs(addr, frm, to):
    out = rpc("eth_getLogs", [{"fromBlock": hex(frm), "toBlock": hex(to), "address": addr,
                               "topics": [TRANSFER, ZERO_TOPIC]}])
    if out is None or "result" not in out:
        return None
    return out["result"]

out = {}
for name, addr, fb in ITEMS:
    r = {"address": addr, "first_block": fb}
    # (a) earlier mints?
    earlier, failed = 0, False
    start = 131880000
    while start < fb:
        end = min(start + 1999, fb - 1)
        logs = getlogs(addr, start, end)
        if logs is None:
            failed = True
            break
        earlier += len(logs)
        start = end + 1
    r["earlier_mints_before_first_block"] = None if failed else earlier
    r["first_mint_verified"] = (not failed) and earlier == 0
    r["first_mint_wib"] = block_ts(fb)
    # (b) state reads
    for sig in ["totalSupply()", "totalMinted()", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "nextTokenId()"]:
        r[sig] = call(addr, sel(sig))
    r["quote_user_1"] = call(addr, sel("quote(address,uint256)") + enc(USER) + format(1, "064x"))
    r["mintedBy_user"] = call(addr, sel("mintedBy(address)") + enc(USER))
    r["balanceOf_user"] = call(addr, sel("balanceOf(address)") + enc(USER))
    r["OWNER"] = call(addr, sel("OWNER()"))
    out[name] = r
    print(name, json.dumps(r), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-early-verify.json", "w"), indent=1)
print("saved run-2026-11-06-0701-early-verify.json")
