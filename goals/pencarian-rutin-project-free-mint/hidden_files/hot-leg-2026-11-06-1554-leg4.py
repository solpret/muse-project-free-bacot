import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1554"
T0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
print("LEG4-ONLY start", flush=True)
# ---------- Leg 4: targeted snapshot re-read (read-only) ----------
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
DL4 = time.time() + 50
def raw(to, data):
    for rpc in RPCS:
        if time.time() > DL4:
            return "deadline"
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

ITEMS = {
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "mintedBy(address)",
    "claimedFree(address)", "freeClaimed()"]),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
   ["totalSupply()", "freeMinted()", "freeClaimed()", "balanceOf(address)", "claimedFree(address)"]),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "claimedFree(address)"]),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "claimedFree(address)"]),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "claimedFree(address)"]),
 "PassAgentX": ("0x08b1A979Dd997492EEcc010fe986eA2e2925e620",
   ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)", "freeUsed(address)"]),
 "MILLION": ("0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4",
   ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)"]),
 "AgentGlyph": ("0x3ef2a97abf2e43182eacae323b82d2cac2132c6a",
   ["freeClaimed()", "totalSupply()", "FREE_SUPPLY()"]),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132",
   ["totalSupply()", "freeQuota()", "remainingFree()", "mintedBy(address)", "balanceOf(address)", "mintOpen()"]),
 "DROID": ("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
   ["opened()", "freeMinted()", "totalMinted()"]),
 "IMARS": ("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
   ["opened()", "freeMinted()", "totalMinted()"]),
 "OSK": ("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
   ["opened()", "totalMinted()"]),
 "Tacotron": ("0x05debe4445232205ae7e79d02cb5de5aa0641eff",
   ["totalSupply()", "freeClaimed()", "freeLeft(address)", "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]),
 "Candlix": ("0x263d87e3b4a284b6e4b0b80f7945b6095113ffe6",
   ["totalSupply()", "freeClaimed()", "freeLeft(address)", "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "FANBEIMAO": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "LuckyBox": ("0xd08ef372B52C29255fEd7004f59bF41571451894",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Predictagent": ("0x8fF4bd65584882324c44Ee794a23E7791820189b",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "FABE": ("0xFabE022a5943462fee1Bd221791945DA57510BE8",
   ["freeSharesRemaining()", "freeSharesClaimed(address)", "launched()", "balanceOf(address)"]),
 "Agentidbsc": ("0x716BFaB3B7b0301D17Af0fF4c50a880C7721F39C",
   ["totalSupply()", "freeClaimed()", "freeAvailable()", "balanceOf(address)"]),
 "Crack-live": ("0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09",
   ["totalSupply()", "publicRemaining()", "mintOpen()", "mintCost(address,uint256)",
    "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]),
 "Neurolucha": ("0x56eBED63452Bb02B975ceE02949DA3C02466725b",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "claimedFree(address)",
    "canFreeMint(address)"]),
}
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("mintCost"):
            v = call(addr, sig, enc(USER) + "0" * 63 + "1"); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d

blk = block()
print("BLOCK", blk, flush=True)
out = {"block": blk, "reread": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_item, list(ITEMS.items())):
        out["reread"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-targeted.json", "w"), indent=1)
print("LEG4 done in %.1fs block %s" % (time.time() - T0, blk), flush=True)

# ---------- Bridge (read-only) ----------
try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap},
              open(f"{BASE}/hot-leg-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
print("DONE total %.1fs" % (time.time() - T0), flush=True)
