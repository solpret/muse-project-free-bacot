import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc.publicnode.com","https://bsc-dataseed1.defibit.io","https://bsc-dataseed1.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def call(to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    last=None
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                out = json.load(r)
            if "error" in out: return {"error": out["error"]}
            v = out["result"]
            return int(v, 16) if v and v != "0x" else 0
        except Exception as e:
            last=str(e); continue
    return {"error": last}
def block():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    last=None
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return int(json.load(r)["result"], 16)
        except Exception as e:
            last=str(e); continue
    raise RuntimeError(last)
blk = block()
res = {"block": blk}
res["OSK"] = {"opened()": call("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", sel("opened()")),
               "totalMinted()": call("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", sel("totalMinted()"))}
res["NIULAI"] = {"launched()": call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", sel("launched()")), "phase()": call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", sel("phase()"))}
res["KillZero"] = {"launched()": call("0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97", sel("launched()"))}
res["DROID"] = {"opened()": call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", sel("opened()")),
                "freeMinted()": call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", sel("freeMinted()")),
                "totalMinted()": call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", sel("totalMinted()"))}
res["IMARS"] = {"opened()": call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", sel("opened()")),
                "freeMinted()": call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", sel("freeMinted()")),
                "totalMinted()": call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", sel("totalMinted()"))}
res["ASOC"] = {"freeClaimed(address)": call("0x43cEef9313CB8c4ca3757bA841C44DF40A223205", sel("freeClaimed(address)") + enc_addr(USER)[2:]),
               "saleEnded()": call("0x43cEef9313CB8c4ca3757bA841C44DF40A223205", sel("saleEnded()"))}
print(json.dumps(res, indent=1))
with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0744-reread.json", "w") as f:
    json.dump(res, f, indent=1)
