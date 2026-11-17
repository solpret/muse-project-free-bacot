"""Re-probe 5 first-seen contracts with raw JSON-RPC (to distinguish revert vs
network error) + retries. READ-ONLY. Writes run-2026-11-05-1831-reprobe.json."""
import json, time, urllib.request
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def raw_call(ep, method, params, timeout=12):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def call(addr, data, tries=3):
    """Returns ('ok', value) or ('revert', msg) or ('neterr', msg)."""
    for ep in EPS:
        for t in range(tries):
            try:
                res = raw_call(ep, "eth_call", [{"to": addr, "data": data}, "latest"])
                if "error" in res:
                    return ("revert", str(res["error"].get("message", res["error"]))[:160])
                out = res.get("result", "")
                if isinstance(out, str) and len(out) >= 66:
                    return ("ok", int(out[2:66], 16))
                return ("ok-empty", out)
            except Exception as e:
                last = f"{type(e).__name__}:{str(e)[:120]}"
                time.sleep(2)
    return ("neterr", last)

UP = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"

TARGETS = {
 "0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0": {  # Kitebots
   "noarg": ["FREE_CAP()", "FREE_PCT()", "freeMinted()", "totalSupply()", "paidMinted()", "totalMinted()", "MAX_SUPPLY()", "maxSupply()"],
   "user": ["canFreeMint(address)", "claimedFree(address)", "freeMintedBy(address)", "mintedBy(address)", "balanceOf(address)"],
   "one": ["quote(uint256)"]},
 "0x1877aA8d3Aa233058404094d4705484FF6BC1FdA": {  # AgentFounder
   "noarg": ["FREE_SUPPLY()", "freeMinted()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()", "maxSupply()", "freeRemaining()", "freeLeft()", "mintOpen()"],
   "user": ["freeMintedBy(address)", "freeClaimed(address)", "mintedBy(address)", "balanceOf(address)", "canFreeMint(address)"],
   "one": ["quote(uint256)", "costOf(uint256)"]},
 "0xDd3cb42166ECd5A42911490B67B602D56d0B13eb": {  # AgentPass
   "noarg": ["FREE_SUPPLY()", "freeMinted()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()", "maxSupply()", "freeRemaining()", "freeLeft()", "mintOpen()"],
   "user": ["freeMintedBy(address)", "freeClaimed(address)", "mintedBy(address)", "balanceOf(address)", "canFreeMint(address)"],
   "one": ["quote(uint256)", "costOf(uint256)"]},
 "0x1318EdD7408e7520761586a152BFff5F07605d7F": {  # ANGLER
   "noarg": ["FREE_SUPPLY()", "freeMinted()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()", "maxSupply()", "freeRemaining()", "freeLeft()", "mintOpen()", "FREE_CAP()", "price()", "PRICE()"],
   "user": ["freeMintedBy(address)", "freeClaimed(address)", "mintedBy(address)", "balanceOf(address)", "canFreeMint(address)"],
   "one": ["quote(uint256)", "costOf(uint256)"]},
 "0x622c41902107e43bba06C865086A449777240D7A": {  # AGENT GLYPHS
   "noarg": ["MINT_START()", "MINT_END()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()", "maxSupply()", "PRICE()", "freeMinted()", "FREE_SUPPLY()"],
   "user": ["mintedBy(address)", "balanceOf(address)", "freeClaimed(address)"],
   "one": ["quote(uint256)", "costOf(uint256)"]},
}
OUT = {}
for addr, groups in TARGETS.items():
    rec = {}
    for sig in groups["noarg"]:
        rec[sig] = call(addr, sel(sig))
    for sig in groups["user"]:
        rec[sig] = call(addr, sel(sig) + UP)
    for sig in groups["one"]:
        rec[sig] = call(addr, sel(sig) + ONE)
    OUT[addr] = rec
    print("==", addr, flush=True)
    for k, v in rec.items():
        print("  ", k, v, flush=True)
    time.sleep(1)
json.dump(OUT, open(HF + "run-2026-11-05-1831-reprobe.json", "w"), indent=1)
print("WROTE run-2026-11-05-1831-reprobe.json")
