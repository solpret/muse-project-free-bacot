import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race, call_many
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
snap = json.load(open(f"{H}/onchain-snapshot.json"))
block = int(race("eth_blockNumber", []), 16)
print("block", block, flush=True)
targets = {}
for n in ["Fangcount","Mechfarm","Threadmoth","Syntaxia","Compilur","Robogent","Glasscore","Crtdroid","Medusine","Gearpixel","Dronegent","Jelly Agent"]:
    e = snap["contracts"].get(n)
    if e and e.get("address"): targets[n] = e["address"]
targets["pollen-mint"] = snap["pending_claims"]["hive-pollen"]["mint"]
targets["AgentZero-5a67"] = "0x5A67Db8389A08762D6120903Eec43e719Cf67c43"
targets["Ihigi-sale"] = "0x3611455bE1FC2c6987FE9d016971b7E40B341684"
targets["binanceai-mint"] = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
views = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("totalMinted()", ""), ("freeMinted()", ""), ("mintedBy(address)", pad), ("freeUsed(address)", pad), ("balanceOf(address)", pad)]
calls = []; meta = []
for name, addr in targets.items():
    for sig, args in views:
        calls.append((addr, "0x" + sel(sig) + args)); meta.append((name, sig))
res = []
for i in range(0, len(calls), 80): res += call_many(calls[i:i+80])
reread = {}
for (name, sig), r in zip(meta, res):
    v = None
    if isinstance(r, str) and r.startswith("0x") and len(r) == 66:
        try: v = int(r, 16)
        except Exception: v = None
    reread.setdefault(name, {"address": targets[name]})[sig] = v
# specifics
spec = [
 ("pollen-mint", "launched()", ""), ("pollen-mint", "phase()", ""), ("pollen-mint", "pollenAgents()", ""), ("pollen-mint", "paidSold()", ""),
 ("pollen-mint", "pollenClaimed(address)", pad),
 ("AgentZero-5a67", "FREE_CAP()", ""), ("AgentZero-5a67", "poolOpened()", ""), ("AgentZero-5a67", "startTime()", ""), ("AgentZero-5a67", "quote(address,uint256)", pad + "0"*63 + "1"),
 ("Ihigi-sale", "poolOpened()", ""), ("Ihigi-sale", "phase()", ""), ("Ihigi-sale", "FREE_CAP()", ""), ("Ihigi-sale", "quote(uint256)", "0"*63 + "1"),
 ("binanceai-mint", "launched()", ""),
]
calls2 = [(targets[n], "0x" + sel(s) + a) for n, s, a in spec]
res2 = call_many(calls2)
for (name, sig, _), r in zip(spec, res2):
    v = None
    if isinstance(r, str) and r.startswith("0x") and len(r) == 66:
        try: v = int(r, 16)
        except Exception: v = None
    reread[name][sig] = v
# pollen token balance user
tok = snap["pending_claims"]["hive-pollen"]["token"]
r = call_many([(tok, "0x" + sel("balanceOf(address)") + pad)])[0]
v = int(r, 16) if isinstance(r, str) and r.startswith("0x") and len(r) == 66 else None
reread["pollen-token-bal-user"] = {"address": tok, "balanceOf(user)": v}
print(json.dumps(reread, indent=1), flush=True)
json.dump({"block": block, "reread": reread}, open(f"{H}/hot-leg-2026-11-03-1614-reread.json", "w"), indent=1)
print("DONE", block)
