#!/usr/bin/env python3
"""Deep triage round 2 run 1301: first-mint block via binary search + extra views. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak

RPC = "https://bsc-dataseed.binance.org/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = USER[2:].lower().rjust(64, "0")

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def post(payload):
    req = urllib.request.Request(RPC, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def call(to, data, block="latest"):
    r = post({"jsonrpc": "2.0", "id": 0, "method": "eth_call",
              "params": [{"to": to, "data": data}, block]})
    if "error" in r: return None
    return r.get("result")

def dec(h):
    if not h: return None
    try: return int(h, 16)
    except Exception: return None

def dec_str(h):
    if not h or len(h) < 130: return None
    try:
        b = bytes.fromhex(h[2:])
        off = int.from_bytes(b[0:32], "big"); ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="ignore")
    except Exception: return None

def block_ts(n):
    r = post({"jsonrpc": "2.0", "id": 0, "method": "eth_getBlockByNumber",
              "params": [hex(n), False]})
    res = r.get("result") or {}
    return int(res.get("timestamp", "0"), 16)

head = int(post({"jsonrpc": "2.0", "id": 0, "method": "eth_blockNumber", "params": []})["result"], 16)
print("head:", head)

def first_mint_block(addr):
    # totalSupply() at block; binary search first block with supply > 0
    lo, hi = 0, head
    if dec(call(addr, sel("totalSupply()"), hex(hi))) in (None, 0):
        return None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = dec(call(addr, sel("totalSupply()"), hex(mid)))
        if v and v > 0: hi = mid
        else: lo = mid
    return hi

out = {}
for name, addr in [("PICK", "0x2296367f74b2ec266cf4667d98501ae7110f5a58"),
                   ("GearMachine", "0x391a13af7819e36a84f16754c133ca39d08d273d"),
                   ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d")]:
    fb = first_mint_block(addr)
    ts = block_ts(fb) if fb else None
    out[name] = {"first_mint_block": fb, "first_mint_ts": ts}
    print(name, "first_mint_block:", fb, "ts:", ts)

# extra views
def views(addr, items):
    res = {}
    for label, sig, arg in items:
        v = call(addr, sel(sig) + arg)
        res[label] = v
    return res

pick = views("0x2296367f74b2ec266cf4667d98501ae7110f5a58", [
    ("maxSupply", "maxSupply()", ""), ("publicSupplyLeft", "publicSupplyLeft()", ""),
    ("mintMode", "mintMode()", ""), ("mintStatus", "mintStatus()", ""),
    ("siteURL", "siteURL()", ""), ("xURL", "xURL()", ""), ("contractURI", "contractURI()", ""),
    ("mintedBy_user", "mintedBy(address)", PAD), ("maxPerWallet", "maxPerWallet()", ""),
    ("devMinted", "devMinted()", ""), ("devReserve", "devReserve()", ""),
])
out["PICK"].update({k: (dec_str(v) if k in ("siteURL", "xURL", "contractURI") else dec(v)) for k, v in pick.items()})
print("PICK extra:", json.dumps(out["PICK"], indent=1))

azen = views("0x699b6397986cc6c444069efe692023b1253dc26d", [
    ("AGENT_ID", "AGENT_ID()", ""), ("freeMintedPerWallet_user", "freeMintedPerWallet(address)", PAD),
    ("mintedPerWallet_user", "mintedPerWallet(address)", PAD),
    ("TOKEN_PRICE", "TOKEN_PRICE()", ""), ("TOKENS_PER_FREE_MINT", "TOKENS_PER_FREE_MINT()", ""),
    ("MAX_FREE_PER_WALLET", "MAX_FREE_PER_WALLET()", ""), ("zenToken", "zenToken()", ""),
    ("zenReserve", "zenReserve()", ""),
])
out["AZEN"].update({k: dec(v) for k, v in azen.items()})
print("AZEN extra:", json.dumps(out["AZEN"], indent=1))

gear = views("0x391a13af7819e36a84f16754c133ca39d08d273d", [
    ("costOf_user1", "costOf(address,uint256)", PAD + "0" * 63 + "1"),
    ("mintsLeft_user", "mintsLeft(address)", PAD),
    ("mintedBy_user", "mintedBy(address)", PAD),
    ("agentIds_user", "agentIds(address)", PAD),
])
out["GearMachine"].update({k: dec(v) for k, v in gear.items()})
print("Gear extra:", json.dumps(out["GearMachine"], indent=1))

# KIJIN claim
kij = views("0x94534656fc286e86c6a04a1fc19724e4da6264ed", [
    ("nft", "nft()", ""), ("token", "token()", ""), ("claimsOpen", "claimsOpen()", ""),
    ("deadline", "deadline()", ""), ("amountPerNft", "amountPerNft()", ""),
    ("bucketBalance", "bucketBalance()", ""), ("totalClaimedCount", "totalClaimedCount()", ""),
    ("totalClaimedAmount", "totalClaimedAmount()", ""),
])
out["KIJIN"] = {}
for k, v in kij.items():
    if k in ("nft", "token") and v:
        out["KIJIN"][k] = "0x" + v[-40:]
    else:
        out["KIJIN"][k] = dec(v)
print("KIJIN claim:", json.dumps(out["KIJIN"], indent=1))
nft = out["KIJIN"].get("nft")
if nft:
    bal = dec(call(nft, sel("balanceOf(address)") + PAD))
    out["KIJIN"]["user_nft_balance"] = bal
    print("user balance of KIJIN NFT:", bal)
    # canClaim(address) attempt
    cc = call("0x94534656fc286e86c6a04a1fc19724e4da6264ed", sel("canClaim(address)") + PAD)
    out["KIJIN"]["canClaim_user"] = dec(cc)
    print("canClaim(user):", dec(cc))

json.dump(out, open("run-2026-11-15-1301-triage2.json", "w"), indent=1)
