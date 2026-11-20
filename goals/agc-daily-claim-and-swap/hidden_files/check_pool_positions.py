"""Baca poolPositions(wallet, from, count) dari AGCMinter + LOCK().
Dipakai untuk verifikasi jatuh tempo LP Mode B sebelum withdrawLP.
"""
import json, urllib.request, datetime
from eth_abi import encode, decode
from eth_hash.auto import keccak

RPCS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc.publicnode.com",
]
WALLET = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINTER = "0x6288DFe86f22B53eEB6886aE2D78941de7483743"
WIB = datetime.timezone(datetime.timedelta(hours=7))

def rpc(method, params):
    last = None
    for u in RPCS:
        try:
            req = urllib.request.Request(u, data=json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                headers={"Content-Type": "application/json"})
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

# LOCK()
lock_raw = call(MINTER, "0x" + sel("LOCK()"))
lock = decode(["uint256"], bytes.fromhex(lock_raw[2:]))[0]
print("LOCK (detik):", lock, "=", lock / 86400, "hari")

# poolPositionCount(wallet)
cnt_raw = call(MINTER, "0x" + sel("poolPositionCount(address)") + encode(["address"], [WALLET]).hex())
count = decode(["uint256"], bytes.fromhex(cnt_raw[2:]))[0]
print("poolPositionCount:", count)

# poolPositions(wallet, 0, count) -> tuple[] (time, shares, lp, reward, rewardClaimed, lpOut)
data = "0x" + sel("poolPositions(address,uint256,uint256)") + encode(
    ["address", "uint256", "uint256"], [WALLET, 0, count]).hex()
raw = call(MINTER, data)
positions = decode(["(uint256,uint256,uint256,uint256,uint256,uint256)[]"], bytes.fromhex(raw[2:]))[0]
blk_num = rpc("eth_blockNumber", [])
now = int(__import__("time").time())
print("block:", int(blk_num, 16), "| waktu WIB:",
      datetime.datetime.fromtimestamp(now, WIB))
for i, p in enumerate(positions):
    t, shares, lp, rew, claimed, lpout = p
    unlock = t + lock
    print(f"pos[{i}] mint={datetime.datetime.fromtimestamp(t, WIB)} shares={shares} "
          f"lp={lp/1e18:.4f} reward={rew/1e18:,.2f} claimed={claimed/1e18:,.2f} "
          f"sisa={rew/1e18-claimed/1e18:,.2f} lpOut={lpout/1e18:.6f} "
          f"unlock={datetime.datetime.fromtimestamp(unlock, WIB)} "
          f"MATANG={'YA' if now >= unlock else 'BELUM'}")
