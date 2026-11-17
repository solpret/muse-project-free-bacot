import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def read(addr, sig, tries=3):
    data = sel(sig) + enc(USER) if "(address)" in sig else sel(sig)
    for _ in range(tries):
        try: return to_int(race("eth_call", [{"to": addr, "data": data}, "latest"]))
        except Exception: time.sleep(2)
    return None
def read_str(addr, sig, tries=3):
    data = sel(sig)
    for _ in range(tries):
        try:
            raw = race("eth_call", [{"to": addr, "data": data}, "latest"])
            if not raw or len(raw) < 130: return None
            b = bytes.fromhex(raw[2:]); ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
        except Exception: time.sleep(2)
    return None
out = {}
for name, addr in [("DYOR_token_A","0x9791d92B63a566AC578e6070ee1F8546C8b2153B"),
                   ("DYOR_token_B","0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7")]:
    d = {}
    for sig in ["PER_NFT()","nft()","LIQUIDITY()","MINTER_POOL()","TEAM()","VEST_DAYS()",
                "lockedOf(address)","nextUnlock(address)","transferableOf(address)",
                "claimableNfts(address)","claimedNfts(address)","totalSupply()","decimals()"]:
        d[sig] = read(addr, sig)
    d["name()"] = read_str(addr, "name()")
    d["symbol()"] = read_str(addr, "symbol()")
    # hex forms of address-valued views
    for k in ("nft()","LIQUIDITY()","MINTER_POOL()","TEAM()"):
        v = d.get(k)
        d[k+"_hex"] = ("0x"+format(v,"040x")) if isinstance(v,int) else None
    out[name] = d
    print(name, json.dumps(d, indent=1), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-0931-dyor2.json","w"), indent=1)
print("DONE", flush=True)
