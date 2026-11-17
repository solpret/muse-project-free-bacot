#!/usr/bin/env python3
"""Hot-leg 2026-11-07 01:44 leg-4 retry (RPC recovered after transient probe failure). Read-only."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
def rpc_json(method, params, timeout=6):
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
blk, blk_rpc = rpc_json("eth_blockNumber", [], timeout=6)
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
# ---------- Leg 4: targeted re-read (read-only, 90s deadline) ----------
DEADLINE = time.time() + 90
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    for rpc in RPCS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
            if not v or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()"]
ITEMS = {
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", NFT_VIEWS),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", NFT_VIEWS),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", NFT_VIEWS),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", NFT_VIEWS),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", NFT_VIEWS),
 "Layerloom": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", NFT_VIEWS),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", NFT_VIEWS),
 "Tumblebots": ("0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", NFT_VIEWS),
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8", NFT_VIEWS),
 "Neurolucha": ("0x56eBED63452Bb02B975ceE02949DA3C02466725b", NFT_VIEWS),
 "Driftnauts": ("0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", NFT_VIEWS),
 "BNB CACHE Server": ("0x1989058Da9eb7F36E69779fCda0EA04578528570", NFT_VIEWS),
 "Qilingentle-423d": ("0x423d25764E4D3D792C08e04C759cE3b0FcDE8596", NFT_VIEWS),
 "Hivejupiter-8DF7": ("0x8DF74cBe998F8d447E7c77dD5117aFB940605400", NFT_VIEWS),
 "Saturnswarm-238c": ("0x238C995A1376e08395b970870A546C57aE184434", NFT_VIEWS),
 "Boohiveling-c1da": ("0xC1dAf114e377242eEB76d180B24b491758Acb4f7", NFT_VIEWS),
 "Neidroidjuan-758c": ("0x758c9665747466Ff4CBa2a3714CC4e9F7C9324b6", NFT_VIEWS),
 "Servofarmix-f636": ("0xf63623136e5f2a6CD8cE85d9F22Ac46744DF39b6", NFT_VIEWS),
 "PeaFunPod-1901": ("0x25F3EFb465685692EF3DdC47Ed040baF216B5D38", NFT_VIEWS),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", SALE_VIEWS),
 "FANBEIMAO-824d": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", SALE_VIEWS),
 "LuckyBox-LUCK": ("0xd08ef372B52C29255fEd7004f59bF41571451894", SALE_VIEWS),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985", SALE_VIEWS),
 "Predictagent-PRDICT": ("0x8fF4bd65584882324c44Ee794a23E7791820189b", SALE_VIEWS),
 "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b", SALE_VIEWS),
 "BOMB-sale": ("0xC3f847430D660e5AAbE8D4b2B5792d6Fcbb171F9", SALE_VIEWS),
 "ChimpAgent": ("0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689", SALE_VIEWS),
}
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("quote("):
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    snap_v = snap.get("contracts", {}).get(name, {}) or snap.get("track_c", {}).get(name, {})
    d["snap"] = {k: snap_v.get(k) for k in ("freeClaimed", "FREE_SUPPLY", "freeSupply", "totalSupply", "status", "freeMinted", "totalMinted") if snap_v.get(k) is not None}
    return name, d
if blk is None:
    out4 = {"block": None, "status": "SKIPPED - RPC still unreachable on retry; no conclusion drawn. Retry next run.", "items_attempted": len(ITEMS)}
else:
    with ThreadPoolExecutor(max_workers=10) as ex:
        leg4 = dict(ex.map(read_item, list(ITEMS.items())))
    out4 = {"block": int(blk, 16), "via": blk_rpc, "items": leg4, "retry_note": "leg-4 retry after transient RPC probe failure in main script run"}
json.dump(out4, open(f"{BASE}/hot-leg-run-2026-11-07-0149-leg4.json", "w"), indent=1)
print(json.dumps({"block": out4.get("block"), "via": out4.get("via"), "status": out4.get("status", "ok"), "n_items": len(out4.get("items", {}))}, indent=1))
