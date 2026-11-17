#!/usr/bin/env python3
"""Method 4 deep checks (bounded): funder probes for 6 wallets + exit
checks for the 2 m1-early hits. READ-ONLY. Reuses m2_funding helpers."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/narrative-pulse/wallet-wave-20261103')
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr
import m2_funding as m2
from Crypto.Hash import keccak

def topic_transfer():
    k = keccak.new(digest_bits=256)
    k.update(b"Transfer(address,address,uint256)")
    return "0x" + k.hexdigest()

def pad(a):
    return "0x" + "0" * 24 + a[2:].lower()

def exits(wallet, token, pool, buy_block):
    sig = topic_transfer()
    r = ankr.get_logs(token, buy_block, buy_block + 2000,
                      topics=[[sig], [pad(wallet)]])
    logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
    out = []
    for lg in logs:
        topics = lg.get("topics", [])
        to = ("0x" + topics[2][-40:]) if len(topics) > 2 else None
        out.append({"block": int(lg.get("blockNumber", "0x0"), 16),
                    "tx": lg.get("transactionHash"),
                    "to": to, "to_pool": (to or "").lower() == pool.lower()})
    return out

def main():
    latest = 131410983
    funders = ["87b5", "95e0", "4a48", "xigua-A", "xigua-B", "gake-okx"]
    addrs = {
        "87b5": "0x87b51e0d40d413d2b7ef480e8b327a57df9769c6",
        "95e0": "0x95e02ed458ba54fd640f5b3956ff4178aac809d5",
        "4a48": "0x4a48a8ab550b936aad4f3252281acac1a717f460",
        "xigua-A": "0x3472ccf6209925204b9cf352171ee150904fda7e",
        "xigua-B": "0x95b998b3ebc4c04fac037ff451144af5c90eda8f",
        "gake-okx": "0x3c5083022114ea14fb3d8d06f5931c629c2bedd6",
    }
    res = {}
    for label in funders:
        w = addrs[label]
        try:
            first = m2.first_tx_block(w, latest)
        except Exception as e:
            first, ferr = None, f"{type(e).__name__}: {str(e)[:150]}"
        else:
            ferr = None
        summ = None
        if first:
            try:
                summ = m2.native_summary(w, first, first + 200000, cap_pages=3)
            except Exception as e:
                summ = f"ERR {type(e).__name__}: {str(e)[:150]}"
        res[label] = {"first_tx": first, "first_err": ferr, "native_early": summ}
        print(json.dumps({label: res[label]}, default=str), flush=True)
    # exits for the 2 m1-early hits
    ex = {}
    ex["95e0-JAGENT"] = exits(
        addrs["95e0"], "0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15",
        "0xe6efcdef2b720d1eca2b69edb7ef357725680bea", 130288713)
    ex["4a48-SAFU-B13B"] = exits(
        addrs["4a48"], "0xdd806e436dda5588bf54061c11590c77ddc87777",
        "0x13b86fcf85c9c8f5c36593822d216b8893c25450", 126879531)
    for k, v in ex.items():
        print(k, "n_out_15m:", len(v), flush=True)
        for row in v[:8]:
            print("   ", row, flush=True)
    res["exits"] = ex
    json.dump(res, open('/home/hatch/workspace/narrative-pulse/wallet-wave-20261103/m4_deep.json', 'w'), indent=1, default=str)
    print("saved m4_deep.json")

if __name__ == "__main__":
    main()
