import json, time, urllib.request
from Crypto.Hash import keccak
RPC = "https://bsc-dataseed.binance.org"
ADDR = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TX = "0xf911ab16cefafec1ac6b573cfe840861a9a188e374a0cdd71414b47e889c7749"
def rpc(method, params, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
rc = None
for i in range(20):
    try:
        r = rpc("eth_getTransactionReceipt", [TX])
        if r.get("result"):
            rc = r["result"]; break
    except Exception as e:
        print("try", i, "ERR", e)
    time.sleep(3)
print("receipt:", "FOUND" if rc else "NOT FOUND")
if rc:
    print("status:", int(rc["status"], 16), "block:", int(rc["blockNumber"], 16), "gasUsed:", int(rc["gasUsed"], 16))
    for lg in rc.get("logs", []):
        print("  log topics:", len(lg["topics"]), "topic0:", lg["topics"][0][:18], "data words:", [int(lg["data"][2+j:2+j+64], 16) for j in range(0, len(lg["data"])-2, 64)] if lg.get("data") else [])
    json.dump(rc, open("run-2026-11-07-1931-bobbie-settle-receipt.json", "w"), indent=1)
def call(data):
    return rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
def u(fn):
    try:
        res = call(sel(fn))
        return int(res["result"], 16) if res.get("result") else ("ERR", res.get("error"))
    except Exception as e:
        return ("EXC", str(e))
print("balanceOf(user):", call(sel("balanceOf(address)") + "0"*24 + USER[2:].lower()))
print("ownerOf(4023):", call(sel("ownerOf(uint256)") + format(4023, "064x")))
print("freeAllocated:", u("freeAllocated()"), "totalMinted:", u("totalMinted()"))
print("mintedBy(user):", call(sel("mintedBy(address)") + "0"*24 + USER[2:].lower()))
print("freeUsed(user):", call(sel("freeUsed(address)") + "0"*24 + USER[2:].lower()))
print("head:", int(rpc("eth_blockNumber", [])["result"], 16))
