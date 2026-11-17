import json, urllib.request, sys
from eth_abi import encode
from eth_hash.auto import keccak

RPC = "https://bsc-dataseed.binance.org"
WALLET = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGC = "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
DELTA = 280000 * 10**18

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def call(to, data):
    res = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    if "error" in res:
        raise RuntimeError(f"eth_call error: {res['error']}")
    return res["result"]

# getAmountsOut(uint256,address[])
data = "0x" + sel("getAmountsOut(uint256,address[])") + encode(
    ["uint256", "address[]"], [DELTA, [AGC, WBNB]]).hex()
raw = call(ROUTER, data)
b = bytes.fromhex(raw[2:])
words = [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
print("getAmountsOut words:", words)
quote = words[2]
print("quote WBNB wei:", quote, "=", quote / 1e18, "WBNB")

# allowance(owner, spender)
adata = "0x" + sel("allowance(address,address)") + encode(
    ["address", "address"], [WALLET, ROUTER]).hex()
allow = int(call(AGC, adata), 16)
print("allowance AGC->router:", allow, "=", allow / 1e18, "AGC")

blk = rpc("eth_getBlockByNumber", ["latest", False])["result"]
ts = int(blk["timestamp"], 16)
print("block timestamp:", ts, "deadline:", ts + 1200)
min_out = quote * 95 // 100
print("amountOutMin (95%):", min_out, "=", min_out / 1e18, "WBNB")

# swap calldata for gas estimate
swap = "0x" + sel("swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)") + encode(
    ["uint256", "uint256", "address[]", "address", "uint256"],
    [DELTA, min_out, [AGC, WBNB], WALLET, ts + 1200]).hex()
print("swap calldata:", swap)
est = rpc("eth_estimateGas", [{"from": WALLET, "to": ROUTER, "data": swap, "value": "0x0"}])
print("estimateGas:", est)
gp = rpc("eth_gasPrice", [])
print("gasPrice wei:", int(gp["result"], 16))
if "result" in est:
    g = int(est["result"], 16)
    print("est gas cost BNB:", g * int(gp["result"], 16) / 1e18, "2x:", 2 * g * int(gp["result"], 16) / 1e18)
