#!/usr/bin/env python3
"""Run 1531: verify 0x4540... (S1 shape-hit, hot-leg 15:29) + feed new-vs-seen.
Read-only; writes run-2026-11-14-1531-verify4540.json. No preview/mint."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF"
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

calls = [
 ("name", "name()", []), ("symbol", "symbol()", []),
 ("totalSupply", "totalSupply()", []), ("totalPaid", "totalPaid()", []),
 ("freeMinted", "freeMinted()", []), ("freeLeft", "freeLeft()", []),
 ("FREE_CAP", "FREE_CAP()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
 ("PRICE", "PRICE()", []), ("mintOpen", "mintOpen()", []),
 ("mintStart", "mintStart()", []), ("mintEnd", "mintEnd()", []),
 ("agentId", "agentId()", []), ("poolBalance", "poolBalance()", []),
 ("claimDeadline", "claimDeadline()", []), ("claimTimeLeft", "claimTimeLeft()", []),
 ("remaining", "remaining()", []), ("quote_1", "quote(uint256)", [1]),
 ("quoteFor_user_1", "quoteFor(address,uint256)", [USER, 1]),
 ("freeClaimed_user", "freeClaimed(address)", [USER]),
 ("claimable_user", "claimable(address)", [USER]),
 ("paidLeftFor_user", "paidLeftFor(address)", [USER]),
 ("tokenURI_1", "tokenURI(uint256)", [1]),
]
import subprocess
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
def post_rpc(ep, payload, timeout=150):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def eth_call(ep, to, data):
    r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                      "params": [{"to": to, "data": data}, "latest"]})
    if "result" in r: return r["result"]
    raise Exception(str(r)[:200])
res = []
batch_ok = True
for _, sig, args in calls:
    data = build(sig, args)
    val = None
    for ep in EPS:
        try:
            val = eth_call(ep, ADDR, data); break
        except Exception:
            continue
    res.append({"result": val} if val is not None else None)
    if val is None: batch_ok = False

views = {}
for (name, sig, args), r in zip(calls, res):
    if r is None or (isinstance(r, dict) and "error" in r):
        views[name] = None; continue
    raw = r.get("result") if isinstance(r, dict) else r
    if not raw or raw == "0x":
        views[name] = None; continue
    if name in ("name", "symbol"):
        try:
            body = raw[2:]
            ln = int(body[64:128], 16)
            views[name] = bytes.fromhex(body[128:128 + ln * 2]).decode(errors="replace")
        except Exception:
            views[name] = raw
    elif name == "tokenURI_1":
        try:
            body = raw[2:]
            ln = int(body[64:128], 16)
            views[name] = bytes.fromhex(body[128:128 + ln * 2]).decode(errors="replace")
        except Exception:
            views[name] = raw
    elif name == "agentId":
        try: views[name] = "0x" + raw[2:][-40:]
        except Exception: views[name] = raw
    elif name == "quoteFor_user_1":
        try:
            body = raw[2:]
            vals = [int(body[i:i+64], 16) for i in range(0, min(len(body), 7*64), 64)]
            views[name] = {"raw_words": vals}
        except Exception:
            views[name] = raw
    else:
        views[name] = to_int(raw)

# head block
head = None
try:
    h = fast_rpc.batch_race([{"to": "0x0000000000000000000000000000000000000000", "data": "0x"} ], timeout=5)
except Exception:
    pass
# eth_blockNumber via direct race
try:
    import urllib.request
    for ep in fast_rpc.ENDPOINTS[:4]:
        try:
            req = urllib.request.Request(ep, data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode(), headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                head = int(json.load(resp)["result"], 16); break
        except Exception:
            continue
except Exception as e:
    print("head read failed:", e)

# feed new vs hot-leg seen
feed = json.load(open("/tmp/feed-1531.json"))
feed_addrs = [c["address"] for c in feed.get("results", [])]
seen = {}
try: seen = json.load(open(BASE + "hot-leg-seen.json"))
except Exception as e: print("seen load fail:", e)
new_feed = [a for a in feed_addrs if a.lower() not in {k.lower() for k in seen}]
out = {
 "run": "free-mint-search 2026-11-14 15:31 WIB",
 "contract": ADDR,
 "batch_ok": batch_ok,
 "views": views,
 "head_block": head,
 "elapsed_s": round(time.time() - t0, 1),
 "feed_total": len(feed_addrs),
 "feed_top": feed_addrs[0] if feed_addrs else None,
 "feed_new_vs_hotleg_seen": new_feed,
 "feed_new_detail": {c["address"]: c.get("verifiedAt") for c in feed.get("results", []) if c["address"] in new_feed},
}
json.dump(out, open(BASE + "run-2026-11-14-1531-verify4540.json", "w"), indent=1)
print(json.dumps(out, indent=1))
