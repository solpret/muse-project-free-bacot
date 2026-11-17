import json, time, urllib.request
from Crypto.Hash import keccak
RPC = "https://bsc-dataseed.binance.org"
ADDR = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def rpc(method, params, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
def call(data):
    for i in range(5):
        try:
            return rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
        except Exception as e:
            print("retry", i, e); time.sleep(2)
    return {"error": "all retries failed"}
o = call(sel("ownerOf(uint256)") + format(4023, "064x"))
print("ownerOf(4023):", o.get("result"), "->", ("0x" + o["result"][-40:]) if o.get("result") else o)
b = call(sel("balanceOf(address)") + "0"*24 + USER[2:].lower())
print("balanceOf(user):", int(b["result"], 16) if b.get("result") else b)
t = call(sel("tokenURI(uint256)") + format(4023, "064x"))
print("tokenURI(4023):", t.get("result", "")[:200] if t.get("result") else t)
json.dump({"ownerOf": o, "balanceOf": b, "tokenURI": t}, open("run-2026-11-07-1931-bobbie-owner.json", "w"), indent=1, default=str)
