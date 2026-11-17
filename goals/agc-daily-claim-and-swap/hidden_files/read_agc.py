import json, urllib.request, sys
from eth_abi import encode
from eth_hash.auto import keccak

RPC = "https://bsc-dataseed.binance.org"
WALLET = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINTER = "0x6288DFe86f22B53eEB6886aE2D78941de7483743"
AGC = "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def call(to, data):
    res = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    if "error" in res:
        raise RuntimeError(f"eth_call error: {res['error']}")
    return res["result"]

def sel(sig):
    return keccak(sig.encode())[:4].hex()

# freePositions(address,uint256,uint256)
data = "0x" + sel("freePositions(address,uint256,uint256)") + encode(
    ["address", "uint256", "uint256"], [WALLET, 0, 10]).hex()
raw = call(MINTER, data)
print("freePositions raw:", raw)
b = bytes.fromhex(raw[2:])
words = [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
print("word count:", len(words))
for i, w in enumerate(words):
    print(f"word[{i}] = {w} (hex 0x{w:064x})")

blk = rpc("eth_getBlockByNumber", ["latest", False])["result"]
print("block:", blk["number"], "timestamp:", int(blk["timestamp"], 16), blk["timestamp"])

bal = rpc("eth_getBalance", [WALLET, "latest"])["result"]
print("BNB wei:", int(bal, 16))

baldata = "0x" + sel("balanceOf(address)") + encode(["address"], [WALLET]).hex()
agc = call(AGC, baldata)
print("AGC raw balance:", int(agc, 16))
