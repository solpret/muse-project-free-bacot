import sys, json
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from onchain_nft_scan import rpc_call
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
def call(addr, sig, args=""):
    try:
        r = rpc_call("eth_call", [{"to": addr, "data": "0x" + sel(sig) + args}, "latest"])
        if isinstance(r, str) and len(r) == 66: return int(r, 16)
        if isinstance(r, str) and len(r) == 130: return "0x" + r[-40:]
        return r
    except Exception as e: return f"ERR:{type(e).__name__}:{str(e)[:80]}"
def txt(addr, sig):
    try:
        r = rpc_call("eth_call", [{"to": addr, "data": "0x" + sel(sig)}, "latest"])
        raw = bytes.fromhex(r[2:]); ln = int(raw[32:64].hex(), 16)
        return raw[64:64+ln].decode(errors="ignore")
    except Exception: return None
BRIDGE = [
    ("bridge-unverified-name", "0xd8e24465f2f5a8fb9b3b24e3042f26a4b10c020f"),
    ("bridge-Agent Oil Rig", "0xf00d595f9fbb8308fb03eeec7406e6883b157413"),
    ("bridge-Neonagent", "0x0d463ce4ad0c24ab902f7443ef6c725207c6eb9f"),
    ("bridge-M3MO", "0x08be8a0727b6fc801171c1f4f4dd547ea44ca339"),
    ("bridge-Agent Harvest Land", "0xacf150d9ec909e3d339bf4c6d090b18495674e66"),
    ("bridge-FLAPPY", "0x1591f1ed9f3dbec3a922dc63f5782daf17eeba1e"),
    ("bridge-Wise Owl Society", "0x1cf9e60218493149ace7dc953497c07175aa625e"),
    ("Yydsgent", "0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61"),
]
for name, addr in BRIDGE:
    vals = {}
    for sig, args in [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("totalMinted()", ""), ("freeMinted()", ""), ("mintOpen()", ""), ("mintedBy(address)", pad), ("freeUsed(address)", pad), ("balanceOf(address)", pad), ("owner()", ""), ("quote(address,uint256)", pad + "0"*63 + "1")]:
        vals[sig] = call(addr, sig, args)
    vals["name"] = txt(addr, "name()"); vals["symbol"] = txt(addr, "symbol()")
    print(name, vals, flush=True)
# Pollen pending claim
POLLEN = "0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"
p = {}
for sig, args in [("launched()", ""), ("phase()", ""), ("pollenAgents()", ""), ("paidSold()", "")]:
    p[sig] = call(POLLEN, sig, args)
print("Pollen", p, flush=True)
# Agent Zero
AZ = "0x5A67Db8389A08762D6120903Eec43e719Cf67c43"
a = {}
for sig, args in [("freeMinted()", ""), ("paidMinted()", ""), ("phase()", ""), ("poolOpened()", ""), ("startTime()", ""), ("FREE_CAP()", ""), ("quote(address,uint256)", pad + "0"*63 + "1")]:
    a[sig] = call(AZ, sig, args)
print("AgentZero", a, flush=True)
print("DONE")
