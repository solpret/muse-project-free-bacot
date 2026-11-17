import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1439-panda-probe.json"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
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
PANDA = "0x7561C414A7a6Ff44Fc81e9BFC2eda8F57C3EC61e"
res["AgentPanda"] = {
    "totalMinted()": call(PANDA, "totalMinted()"),
    "mintOpen()": call(PANDA, "mintOpen()"),
    "freeRemainingFor(user)": call(PANDA, "freeRemainingFor(address)", enc_addr(USER)),
    "freeMintedBy(user)": call(PANDA, "freeMintedBy(address)", enc_addr(USER)),
    "mintedBy(user)": call(PANDA, "mintedBy(address)", enc_addr(USER)),
    "balanceOf(user)": call(PANDA, "balanceOf(address)", enc_addr(USER)),
    "remainingFor(user)": call(PANDA, "remainingFor(address)", enc_addr(USER)),
}
F928 = "0xf928177124616A101a13BdE334Dfd85Df62b837d"
def cstr(v):
    if isinstance(v, dict) or not v or v == "0x": return v
    try:
        h = v[2:]; ln = int(h[64:128], 16); return bytes.fromhex(h[128:128 + ln * 2]).decode(errors="replace")
    except Exception: return v
res["F928"] = {
    "name()": cstr(raw(F928, sel("name()"))),
    "symbol()": cstr(raw(F928, sel("symbol()"))),
    "PRICE()": call(F928, "PRICE()"),
    "spotsLeft()": call(F928, "spotsLeft()"),
    "totalSpotsMinted()": call(F928, "totalSpotsMinted()"),
    "MAX_SPOTS()": call(F928, "MAX_SPOTS()"),
    "WEBSITE()": cstr(raw(F928, sel("WEBSITE()"))),
    "TWITTER()": cstr(raw(F928, sel("TWITTER()"))),
}
print(json.dumps(res, indent=1))
json.dump(res, open(OUT, "w"), indent=1)
