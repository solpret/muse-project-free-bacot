import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
s = json.load(open(f"{H}/onchain-snapshot.json"))
targets = []
for k, v in s["contracts"].items():
    if isinstance(v, dict) and v.get("status", "").startswith("early-lead-reported") and (v.get("freePctVerified") or 0) >= 25:
        targets.append((k, v["address"]))
for k in ("Robogent", "Whale Agent", "Zach Xbt", "Deepvane", "Neuroveil", "Mechfarm", "Hexagent", "Dronagent", "Yydsgent"):
    if k in s["contracts"]: targets.append((k, s["contracts"][k]["address"]))
BRIDGE = [
    ("bridge-unverified-name", "0xd8e24465f2f5a8fb9b3b24e3042f26a4b10c020f"),
    ("bridge-Agent Oil Rig", "0xf00d595f9fbb8308fb03eeec7406e6883b157413"),
    ("bridge-Neonagent", "0x0d463ce4ad0c24ab902f7443ef6c725207c6eb9f"),
    ("bridge-M3MO", "0x08be8a0727b6fc801171c1f4f4dd547ea44ca339"),
    ("bridge-Agent Harvest Land", "0xacf150d9ec909e3d339bf4c6d090b18495674e66"),
    ("bridge-FLAPPY", "0x1591f1ed9f3dbec3a922dc63f5782daf17eeba1e"),
    ("bridge-Wise Owl Society", "0x1cf9e60218493149ace7dc953497c07175aa625e"),
]
targets += BRIDGE
seen = set(); tg = []
for k, a in targets:
    if a.lower() not in seen: seen.add(a.lower()); tg.append((k, a))
views = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("totalMinted()", ""), ("freeMinted()", ""), ("mintedBy(address)", pad), ("freeUsed(address)", pad), ("balanceOf(address)", pad), ("owner()", ""), ("mintOpen()", ""), ("quote(address,uint256)", pad + "0"*63 + "1")]
out = {"block": None}
try: out["block"] = int(race("eth_blockNumber", []), 16)
except Exception as e: out["block_error"] = str(e)[:120]
def one(addr, sig, args):
    try:
        r = race("eth_call", [{"to": addr, "data": "0x" + sel(sig) + args}, "latest"])
        if isinstance(r, str) and r.startswith("0x") and len(r) == 66: return int(r, 16)
        if isinstance(r, str) and r.startswith("0x") and len(r) == 130: return r[-40:]
        return None
    except Exception: return None
def txt(addr, sig):
    try:
        r = race("eth_call", [{"to": addr, "data": "0x" + sel(sig)}, "latest"])
        if isinstance(r, str) and len(r) > 130:
            b = bytes.fromhex(r[130:]) if False else None
            raw = bytes.fromhex(r[2:])
            # ABI string: offset(32)+len(32)+data
            ln = int(raw[32:64].hex(), 16)
            return raw[64:64+ln].decode(errors="ignore")
        return None
    except Exception: return None
for name, addr in tg:
    d = {sig: one(addr, sig, args) for sig, args in views}
    d["name"] = txt(addr, "name()"); d["symbol"] = txt(addr, "symbol()")
    out[name] = {"address": addr, **d}
    print(name, d, d["name"], d["symbol"], flush=True)
json.dump(out, open(f"{H}/run-2026-11-03-1331-reread.json", "w"), indent=1)
print("DONE", len(tg), "block", out["block"])
