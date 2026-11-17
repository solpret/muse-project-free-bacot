#!/usr/bin/env python3
"""Run 1631 track-C extra checks (read-only, curl transport).
- Cheems 0x00b4: mintStart/totalMinted/totalFreeMinted/currentState/tradingOpen (launch 17:00 WIB today)
- PESI sale 0xe82B: freeShares/freeRemaining/freeCap/paidShares/lpCreated
- NUSA sale 0x7D08: freeMinted/freeRemaining/sharesMinted/soldOut/closed
- WNO: PCS V2 factory getPair(WNO, WBNB) — pending-swaps pair check
- CLEPSYDRA 0x9e27 + MoonAgent 0xc469: free views (gate-blocked leads, change-only)
Writes run-2026-11-10-1631-trackc-extra.json; prints human-readable lines.
"""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
WNO = "0xc6D4ec8CB889aFBa9f251606001457644E260f7D"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, views, extra_args=None):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        data = sel(sig)
        if "(address)" in sig:
            data += enc(USER); key = base + "_user"
        elif "(address,address)" in sig:
            a1, a2 = (extra_args or {}).get(sig, (USER, USER))
            data += enc(a1) + enc(a2); key = base
        else:
            key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

out = {"block": get_block(), "checks": {}}
print("BLOCK", out["block"], flush=True)

checks = [
    ("Cheems Agent", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2",
     ["mintStart()", "totalMinted()", "totalFreeMinted()", "currentState()", "tradingOpen()", "freeClaimedByWallet(address)"]),
    ("PESI", "0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD",
     ["freeShares()", "freeRemaining()", "freeCap()", "paidShares()", "lpCreated()"]),
    ("NUSA", "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
     ["freeMinted()", "freeRemaining()", "sharesMinted()", "soldOut()", "closed()"]),
    ("CLEPSYDRA", "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
     ["freeMinted()", "freeSharesRemaining()", "totalSupply()"]),
    ("MoonAgent-MOAGT", "0xc4695f19dE428EA37169bBD058463588D511554a",
     ["freeMinted()", "freeSharesRemaining()", "totalSupply()"]),
]
for name, addr, views in checks:
    t = time.time()
    got = raw_batch(addr, views)
    out["checks"][name] = {"address": addr, "views": got}
    print(f"{name}: {got} ({time.time()-t:.1f}s)", flush=True)

# WNO pair via PCS V2 factory getPair(WNO, WBNB)
pair = raw_batch(FACTORY, ["getPair(address,address)"],
                 extra_args={"getPair(address,address)": (WNO, WBNB)})
pair_addr = None
if pair and pair.get("getPair") is not None:
    pair_addr = "0x" + format(pair["getPair"], "040x")
out["checks"]["WNO-pair"] = {"factory": FACTORY, "token": WNO, "pair": pair_addr,
                             "pair_int": pair.get("getPair") if pair else None}
print(f"WNO PCS V2 pair: {pair_addr}", flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-1631-trackc-extra.json", "w"), indent=1)
print("TRACKC-EXTRA DONE", flush=True)
