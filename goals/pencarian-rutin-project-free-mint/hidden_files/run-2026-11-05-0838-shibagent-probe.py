import json, urllib.request, datetime
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.ninicoin.io", "https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SHIB = "0x016a148e728b8d61b2440ed311946ac06d4b5648"
IDENTITY = "0x9cc4d56e6ce5c0ddade134b932023b5cab2458d8"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
WBNB = "0xbb4cdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def raw(to, data):
    for rpc in RPCS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return {"error": "all RPCs failed"}
def call(to, sig, args=""):
    return raw(to, sel(sig) + args)
def u256(h):
    return int(h, 16) if isinstance(h, str) and len(h) >= 66 else h
def wib(ts):
    return (datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
            + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S WIB")
res = {}
addr_arg = USER[2:].lower().rjust(64, "0")
res["owner()"] = raw(SHIB, sel("owner()"))
res["FREE_SHARES()"] = u256(call(SHIB, "FREE_SHARES()"))
res["freeClaimed()"] = u256(call(SHIB, "freeClaimed()"))
res["sold()"] = u256(call(SHIB, "sold()"))
res["phase()"] = u256(call(SHIB, "phase()"))
res["startedAt()"] = u256(call(SHIB, "startedAt()"))
res["TOKENS_PER_SHARE()"] = u256(call(SHIB, "TOKENS_PER_SHARE()"))
res["decimals()"] = u256(call(SHIB, "decimals()"))
info = raw(SHIB, sel("info()"))
if isinstance(info, str) and len(info) >= 2 + 64*5:
    words = [int(info[2+i*64:2+(i+1)*64], 16) for i in range(5)]
    res["info_decoded"] = {"phase": words[0], "sold": words[1], "freeClaimed": words[2],
                           "deadline": words[3], "raised": words[4]}
    res["deadline_wib"] = wib(words[3])
    res["startedAt_wib"] = wib(res["startedAt()"])
res["balanceOf(user)"] = u256(call(SHIB, "balanceOf(address)", addr_arg))
# user identity id, then free slot
uid = raw(IDENTITY, sel("identityOf(address)") + addr_arg)
res["identityOf(user)_on_identity_contract"] = uid
if isinstance(uid, str) and len(uid) == 66:
    res["freeClaimedById(userId)"] = raw(SHIB, sel("freeClaimedById(bytes32)") + uid[2:])
uid2 = raw(REGISTRY, sel("identityOf(address)") + addr_arg)
res["identityOf(user)_on_registry"] = uid2
res["handleOf(user)_on_shib"] = raw(SHIB, sel("handleOf(address)") + addr_arg)
# PCS pair check
pair = raw(FACTORY, sel("getPair(address,address)") + SHIB[2:].lower().rjust(64, "0") + WBNB[2:].lower().rjust(64, "0"))
res["pcs_pair(SHIB,WBNB)"] = pair
if isinstance(pair, str) and len(pair) == 66 and int(pair, 16) != 0:
    pair_addr = "0x" + pair[2:].rjust(40, "0")[-40:]
    res["pair_token0()"] = raw(pair_addr, sel("token0()"))
    res["pair_token1()"] = raw(pair_addr, sel("token1()"))
    res["pair_getReserves()"] = raw(pair_addr, sel("getReserves()"))
blk = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            blk = int(json.load(r)["result"], 16)
        break
    except Exception:
        continue
res["block"] = blk
print(json.dumps(res, indent=1, default=str))
with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0838-shibagent-probe.json", "w") as f:
    json.dump(res, f, indent=1, default=str)
