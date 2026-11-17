import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EP = "https://bsc-dataseed1.defibit.io/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(to, data):
    p = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                    "params": [{"to": to, "data": data}, "latest"]}).encode()
    try:
        req = urllib.request.Request(EP, data=p, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=8) as r:
            j = json.load(r)
        v = j.get("result")
        return v if v and v != "0x" else None
    except Exception:
        return None
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
u = USER[2:].lower().rjust(64, "0"); one = "0" * 63 + "1"
FEED = ["0x52Ea279BF4013Dc3eeA7Cd5A639E7b517E500f4E","0x4368D7047d3DE03D088460A7AfF437f017e3B22F",
"0x83648dD42722Fb24Bf04c887EBB023C1849c1D71","0xC8f664A922DCC33ebB7858958599454F8369d45F",
"0xf7fF99bd6bd739A27e3511E96c7ABB8ffF460267","0xd1D90f968bCbbdEa49520Fde5b71bBeb9555738b",
"0x273fc2C7705B23eb129E35aC8Da26348E6Fc4980","0xCA0D24D4Aee7a9855ea33e27fbAA2f8545013aD2",
"0x32CD875BC8289EC648d53AeB4Ba1688e7e79a0D2","0x4Bb7f2d9fdE2E6ff48337e6ad2E6e837e0e67777",
"0x6F066D0604f0cB8A9b32dFc525Ec25D1a1671eB2","0x22ad1E0B9aDC23C2FB8c2aBBAf3E5Fee22BB6f73",
"0x8b9403566c811C8844f8b8cF9Bf61ee38463D612","0x6B7619c7F3ca816D6E5C00fa6c79D99caCa9Ef01",
"0x3B843b46CDFa173e947E1d662629933af1D94231","0xb4AC39E5040D4CC8E1f58fc8Ba8743A41cC09Def",
"0x6F8815CD3c1B0895814A2d4911492e4FF5a5Ef86","0xa422fbf16E0e2f81A38f74B1be8b770B97575529",
"0xBC3C55a7b69C7c75b44bfEF11302E9f64bD3Cf0d","0xDF4B0b420F0684E654931Bc37b2f230dF8e81704"]
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], 'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
VIEWS = [("name()", ""), ("symbol()", ""), ("decimals()", ""), ("totalSupply()", ""),
         ("freeClaimed(address)", u), ("freeMinted()", ""), ("FREE_SUPPLY()", ""), ("FREE_SLOTS()", ""),
         ("freeSharesRemaining()", ""), ("freeSharesClaimed()", ""), ("freeLeft()", ""),
         ("freeUsed(address)", u), ("freeAvailable(address)", u), ("freeFor(address,uint256)", u + one),
         ("quote(address,uint256)", u + one), ("agentRegistry()", ""), ("registry()", ""),
         ("AGENT_REGISTRY()", ""), ("freeSharePoolExhausted()", "")]
def probe(a):
    o = {}
    for name, arg in VIEWS:
        v = call(a, sel(name) + arg)
        if name in ("name()", "symbol()"):
            o[name] = dec_str(v) if v else None
        elif name in ("agentRegistry()", "registry()", "AGENT_REGISTRY()"):
            o[name] = ("0x" + v[-40:]) if v and len(v) >= 42 else v
        else:
            o[name] = iv(v)
    return o
out = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    for a, o in zip(FEED, ex.map(probe, FEED)):
        out[a] = o; print("PROBE", a, o, flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0309-shape.json", "w"), indent=1)
print("DONE")
