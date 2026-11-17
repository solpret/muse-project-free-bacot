#!/usr/bin/env python3
"""Hot-leg 22:29 supplementary leg-4 retry. Background curl showed bsc-dataseed.binance.org DID answer
eth_blockNumber (0x7deaadb) ~22:31 WIB, after the run script's 3s-timeout probe recorded all 5 endpoints
failed. Retry the 19-item re-read with longer timeouts, that endpoint first. Read-only; never writes snapshot."""
import json, time
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2229-retry"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc.publicnode.com", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
out = {"run": "free-mint-hot-leg 2026-11-06 22:29 supplementary leg-4 retry (~22:35 WIB)"}
t0 = time.time()

def rpc_json(method, params, timeout=8):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o:
                continue
            return o.get("result"), rpc
        except Exception:
            continue
    return None, None

blk, blk_rpc = rpc_json("eth_blockNumber", [], timeout=8)
out["rpc_probe_retry"] = {"block": int(blk, 16) if blk else None, "via": blk_rpc}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    v, _ = rpc_json("eth_call", [{"to": to, "data": data}, "latest"], timeout=8)
    if not v or v == "0x":
        return None
    try:
        return int(v, 16)
    except Exception:
        return v
def call(to, sig, args=""): return raw(to, sel(sig) + args)

GENERIC = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)",
           "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)",
           "quote(address,uint256)", "costOf(address,uint256)", "freeQuota()", "remainingFree()",
           "FREE_SUPPLY()", "freeSharesRemaining()", "freeAvailable()", "mintOpen()"]
EXTRA = {
 "0x2A2463d243E5c4dF850e48f350392AD23B494132": ["agentGateOn()"],
 "0x25F3EFb465685692EF3DdC47Ed040baF216B5D38": ["freePodsClaimed()", "freeClaimedBy(address)"],
 "0xD7B3FD33e0b465B0e374906F60567D317b758FD8": ["mintsLeft(address)", "price()"],
}
ITEMS = {
 "KING Agent": "0x2A2463d243E5c4dF850e48f350392AD23B494132",
 "MERGEBORN": "0x348455be18b700cae8aa425bd84e456e47f16e8b",
 "Driftnauts": "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Hashseers": "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
 "Layerloom": "0x1B72ceC52A74537b06F713FCebA0e491f53679aE",
 "Smeltbots": "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
 "Tumblebots": "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17",
 "Forklings": "0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
 "Neurolucha": "0x56eBED63452Bb02B975ceE02949DA3C02466725b",
 "BNB CACHE Server": "0x1989058Da9eb7F36E69779fCda0EA04578528570",
 "Qilingentle-423d": "0x423d25764E4D3D792C08e04C759cE3b0FcDE8596",
 "Hivejupiter-8DF7": "0x8DF74cBe998F8d447E7c77dD5117aFB940605400",
 "Saturnswarm-238c": "0x238C995A1376e08395b970870A546C57aE184434",
 "Boohiveling-c1da": "0xC1dAf114e377242eEB76d180B24b491758Acb4f7",
 "Neidroidjuan-758c": "0x758c9665747466Ff4CBa2a3714CC4e9F7C9324b6",
 "Servofarmix-f636": "0xf63623136e5f2a6CD8cE85d9F22Ac46744DF39b6",
 "PeaFunPod-1901": "0x25F3EFb465685692EF3DdC47Ed040baF216B5D38",
}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
if blk is None:
    out["leg4_retry"] = {"block": None,
        "status": "STILL SKIPPED - all 5 endpoints failed even with 8s timeout on retry. Outage persists; retry next run."}
else:
    def read_item(name_addr):
        name, addr = name_addr
        sigs = list(GENERIC) + EXTRA.get(addr, [])
        def one(sig):
            if sig.endswith("(address)"): args = enc(USER)
            elif sig.endswith("(address,uint256)"): args = enc(USER) + enc_uint(1)
            else: args = ""
            return call(addr, sig, args)
        with ThreadPoolExecutor(max_workers=8) as ex:
            vals = list(ex.map(one, sigs))
        res = dict(zip(sigs, vals))
        snap_v = snap.get("contracts", {}).get(name, {})
        return {"name": name, "address": addr, "reads": res,
                "snap_freeClaimed": snap_v.get("freeClaimed"),
                "snap_FREE_SUPPLY": snap_v.get("FREE_SUPPLY") or snap_v.get("freeSupply"),
                "snap_totalSupply": snap_v.get("totalSupply"), "snap_status": snap_v.get("status")}
    with ThreadPoolExecutor(max_workers=10) as ex:
        leg4_items = list(ex.map(read_item, ITEMS.items()))
    out["leg4_retry"] = {"block": int(blk, 16), "via": blk_rpc, "items": leg4_items}
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
blk_v = out["leg4_retry"].get("block")
print(json.dumps({"block": blk_v, "via": out["leg4_retry"].get("via"), "duration_s": out["duration_s"]}, indent=1))
if blk_v:
    for it in out["leg4_retry"]["items"]:
        r = it["reads"]
        print(it["name"], "| totalSupply:", r.get("totalSupply()"), "| freeClaimed:", r.get("freeClaimed()"),
              "| freeMinted:", r.get("freeMinted()"), "| FREE_SUPPLY:", r.get("FREE_SUPPLY()"),
              "| mintedBy(user):", r.get("mintedBy(address)"), "| balanceOf(user):", r.get("balanceOf(address)"),
              "| snap_status:", it.get("snap_status"))
