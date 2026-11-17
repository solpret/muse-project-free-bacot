import json, urllib.request, sys
from eth_abi import encode, decode
from eth_hash.auto import keccak

RPCS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc-dataseed3.binance.org",
    "https://bsc-dataseed1.defibit.io",
    "https://bsc.publicnode.com",
]
WALLET = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINTER = "0x6288DFe86f22B53eEB6886aE2D78941de7483743"
AGC = "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6"

def rpc(method, params):
    last = None
    for rpc_url in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc_url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.loads(r.read())
            if "error" in res:
                raise RuntimeError(res["error"])
            return res["result"]
        except Exception as e:
            last = e
            continue
    raise RuntimeError(f"all RPCs failed: {last}")

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])

# pending(address) -> (uint256 freeBnb, uint256 freeAgc, uint256 rewardVested, uint256 lpWithdrawable)
data = "0x" + sel("pending(address)") + encode(["address"], [WALLET]).hex()
raw = call(MINTER, data)
vals = decode(["uint256", "uint256", "uint256", "uint256"], bytes.fromhex(raw[2:]))
print("freeBnb:", vals[0] / 1e18)
print("freeAgc:", vals[1] / 1e18)
print("rewardVested:", vals[2] / 1e18)
print("lpWithdrawable:", vals[3] / 1e18)

baldata = "0x" + sel("balanceOf(address)") + encode(["address"], [WALLET]).hex()
agc = call(AGC, baldata)
print("AGC balance:", int(agc, 16) / 1e18)

blk = rpc("eth_getBlockByNumber", ["latest", False])
print("block:", int(blk["number"], 16))
