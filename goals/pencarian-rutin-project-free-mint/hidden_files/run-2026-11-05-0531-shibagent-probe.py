import json, urllib.request, datetime
from Crypto.Hash import keccak
RPC = "https://bsc-dataseed.bnbchain.org"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0531-shibagent-probe.json"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def raw(to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            out = json.load(r)
    except Exception as e:
        return {"error": str(e)}
    if "error" in out: return {"error": out["error"]}
    return out["result"]
def call(to, sig, args=""):
    return raw(to, sel(sig) + args)
def u256(hexv):
    if not isinstance(hexv, str) or len(hexv) < 66: return hexv
    return int(hexv, 16)
SHIB = "0x016a148e728b8d61b2440ed311946ac06d4b5648"
res = {}
res["name()"] = raw(SHIB, sel("name()"))
res["symbol()"] = raw(SHIB, sel("symbol()"))
res["decimals()"] = call(SHIB, "decimals()")
res["totalSupply()"] = call(SHIB, "totalSupply()")
for fn in ["FREE_SHARES()","PAID_SHARES()","TOKENS_PER_SHARE()","BASE_QUOTA()","MAX_SUPPLY()",
           "price()","startedAt()","freeClaimed()","sold()","phase()","launched()","finalized()",
           "MINT_DURATION()","POOL_TOKENS()"]:
    res[fn] = call(SHIB, fn)
info = raw(SHIB, sel("info()"))
res["info_raw"] = info
if isinstance(info, str) and len(info) >= 2 + 64*5:
    words = [int(info[2+i*64:2+(i+1)*64], 16) for i in range(5)]
    res["info_decoded"] = {"phase": words[0], "sold": words[1], "freeClaimed": words[2],
                           "deadline": words[3], "raised": words[4]}
    for label, ts in (("startedAt", res.get("startedAt()")), ("deadline", words[3])):
        if isinstance(ts, int) and ts > 0:
            res[label+"_wib"] = (datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
                                 + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S WIB")
res["identity()"] = call(SHIB, "identity()")
res["balanceOf(user)"] = call(SHIB, "balanceOf(address)", USER[2:].lower().rjust(64, "0"))
res["quote()"] = call(SHIB, "quote()")
# QAGENT free pool check
QAG = "0xE3a4f3099a2136e0e66202A665815caB8FFA2704"
res["QAGENT_freeMinted()"] = call(QAG, "freeMinted()")
res["QAGENT_sharesMinted()"] = call(QAG, "sharesMinted()")
print(json.dumps(res, indent=1, default=str))
with open(OUT, "w") as f:
    json.dump(res, f, indent=1, default=str)
