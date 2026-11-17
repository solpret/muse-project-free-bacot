import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1434-spotcheck.json"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    last = None
    for rpc in RPCS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                out = json.load(r)
            break
        except Exception as e:
            last = e; continue
    else:
        return {"error": "rpc-fail: " + str(last)[:60]}
    if "error" in out: return {"error": str(out["error"])[:80]}
    v = out["result"]
    if not v or v == "0x": return None
    try: return int(v, 16)
    except Exception: return v
def call(to, sig, args=""):
    return raw(to, sel(sig) + args)
def block():
    for rpc in RPCS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return int(json.load(r)["result"], 16)
        except Exception:
            continue
    return None
res = {"block": block()}
CJ = "0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5"
LL = "0x1B72ceC52A74537b06F713FCebA0e491f53679aE"
TB = "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17"
AM = "0x8670e99062ead2cE5402754aeDE769602FDf38b8"
WAGA = "0x06a6f51D30556f4262e38485C09556fE81e6A984"
SEN = "0xb21583A08581278BcF925351a99C61A4562C62f0"
AFROG = "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"
for name, addr in [("Cachejack", CJ), ("Layerloom", LL), ("Tumblebots", TB)]:
    res[name] = {"totalSupply()": call(addr, "totalSupply()"),
                 "freeMinted()": call(addr, "freeMinted()"),
                 "claimedFree(user)": call(addr, "claimedFree(address)", enc_addr(USER)),
                 "canFreeMint(user)": call(addr, "canFreeMint(address)", enc_addr(USER))}
res["AgentMiner"] = {"totalSupply()": call(AM, "totalSupply()"),
                     "freeFor(user,1)": call(AM, "freeFor(address,uint256)", enc_addr(USER) + enc_uint(1)),
                     "quote(user,1)": call(AM, "quote(address,uint256)", enc_addr(USER) + enc_uint(1)),
                     "mintedBy(user)": call(AM, "mintedBy(address)", enc_addr(USER))}
res["WAGA"] = {"totalMints()": call(WAGA, "totalMints()"),
               "quote(user,1)": call(WAGA, "quote(address,uint256)", enc_addr(USER) + enc_uint(1)),
               "mintOpen()": call(WAGA, "mintOpen()")}
res["SENBAZURU"] = {"freeClaimed()": call(SEN, "freeClaimed()"),
                    "paidSold()": call(SEN, "paidSold()"),
                    "hasFreeShare(user)": call(SEN, "hasFreeShare(address)", enc_addr(USER))}
res["AFROG"] = {"totalSupply()": call(AFROG, "totalSupply()"),
                "freeClaimed()": call(AFROG, "freeClaimed()"),
                "FREE_SUPPLY()": call(AFROG, "FREE_SUPPLY()")}
print(json.dumps(res, indent=1))
json.dump(res, open(OUT, "w"), indent=1)
