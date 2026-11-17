#!/usr/bin/env python3
"""Method 4 screening: OKX BSC Smart Money Leaderboard top-14 (7D) wallets.
READ-ONLY. No login, no signing, no feed/tier changes.
Filters (same as m1-2): (a) independent operator, (b) active 30d,
(c) early >=3 coins (m1-2 definition: early buyer in >=3 of the 14 formed
coins; snapshot-30d breadth reported as secondary JAGENT-pattern view),
(d) realized profit on-chain verified, (e) not a dumper,
(f) not a passive fee receiver, (g) not exchange/contract.
Addresses below were transcribed from OKX profile page titles/URLs
(browser.open output) and verified: for truncated-label rows, first-4 +
last-4 match the full address; for nickname rows the profile URL itself
carries the full address. Length/hex checked in-script.
"""
import json, sys, urllib.request
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr

CAND = [
    ("87b5",   "0x87b51e0d40d413d2b7ef480e8b327a57df9769c6"),
    ("xigua-A","0x3472ccf6209925204b9cf352171ee150904fda7e"),
    ("0e1c",   "0x0e1c5ecbba12fa1cb187e3d18f1c0a58bce5ce3a"),
    ("david",  "0x7a2363a401b2340c7941dd2eeff0196a5078d2e6"),
    ("95e0",   "0x95e02ed458ba54fd640f5b3956ff4178aac809d5"),
    ("gake-okx","0x3c5083022114ea14fb3d8d06f5931c629c2bedd6"),
    ("5949",   "0x59495c0497abb3c2a60eb7df89b6ad94df8b6993"),
    ("clukz",  "0x077b9981bc8a2ca417cea41861111da63266988b"),
    ("e60e",   "0xe60e67fed34ebb3116ec03995839fdb0be2ba4be"),
    ("4a48",   "0x4a48a8ab550b936aad4f3252281acac1a717f460"),
    ("yangyang","0xa11e739adf417ffe34e1eba75df2031499192b66"),
    ("xigua-B","0x95b998b3ebc4c04fac037ff451144af5c90eda8f"),
    ("1f71",   "0x1f71ff5ead0270889d0a09badfd47ef584618d18"),
]

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "method": method,
                       "params": params, "id": 1}).encode()
    for url in ["https://bsc-dataseed.binance.org/",
                "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            req = urllib.request.Request(
                url, data=body, headers={"Content-Type": "application/json"})
            res = json.loads(urllib.request.urlopen(req, timeout=25).read())
            if "result" in res and res["result"] is not None:
                return res["result"]
        except Exception as e:
            last = str(e)
    return "ERR:" + last

def main():
    for label, a in CAND:
        assert len(a) == 42 and a.startswith("0x"), (label, a)
        int(a[2:], 16)
    latest = int(rpc("eth_blockNumber", []), 16)
    print("latest block:", latest)
    win30 = latest - 5760000
    # snapshot contract set
    s = json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
    snap = set()
    for v in s["contracts"].values():
        if v.get("address"): snap.add(v["address"].lower())
    for v in s["track_c"].values():
        if not isinstance(v, dict): continue
        for k in ("sale", "token"):
            if v.get(k): snap.add(v[k].lower())
    for v in s["pending_claims"].values():
        if not isinstance(v, dict): continue
        for k in ("mint", "token"):
            if v.get(k): snap.add(v[k].lower())
    print("snapshot contract set:", len(snap))
    out = {"latest": latest, "win30_from": win30, "results": {}}
    for label, addr in CAND:
        code = rpc("eth_getCode", [addr, "latest"])
        is_eoa = (code == "0x")
        # Ankr tx-by-address, 30d window, first page only
        try:
            r = ankr.ankr_post("ankr_getTransactionsByAddress", {
                "blockchain": "bsc", "address": [addr], "pageSize": 1000,
                "fromBlock": hex(win30), "toBlock": hex(latest)})
            txs = r.get("result", {}).get("transactions", []) if isinstance(r, dict) else []
            if not txs and isinstance(r, dict):
                txs = r.get("result", []) if isinstance(r.get("result"), list) else []
        except Exception as e:
            txs, txerr = [], f"{type(e).__name__}: {str(e)[:150]}"
        else:
            txerr = None
        tos = set()
        for t in txs:
            if isinstance(t, dict):
                for k in ("to", "contractAddress"):
                    if t.get(k): tos.add(str(t[k]).lower())
        breadth = sorted(tos & snap)
        res = {
            "address": addr,
            "code": (code[:30] + "..." if isinstance(code, str) and len(code) > 30 else code),
            "is_eoa": is_eoa,
            "tx_30d_page1": len(txs),
            "tx_30d_capped": len(txs) == 1000,
            "tx_err": txerr,
            "snapshot_breadth_30d": len(breadth),
            "snapshot_contracts_touched": breadth[:20],
            "active30d": len(txs) > 0,
        }
        out["results"][label] = res
        print(json.dumps({label: res}))
    json.dump(out, open('/home/hatch/workspace/narrative-pulse/wallet-wave-20261103/m4_screen.json', 'w'), indent=1)
    print("saved m4_screen.json")

if __name__ == "__main__":
    main()
