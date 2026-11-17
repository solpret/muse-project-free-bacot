import json, time, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def post_rpc(ep, payload, timeout=30):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + format(1, "064x"); key = base + "_user1"
        elif "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=30)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {key: (None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, key in zip(res, keys)}
        except Exception:
            continue
    return None
FIELD_TO_SIG = {
    "freeMinted": "freeMinted()", "FREE_CAP": "FREE_CAP()", "freeCount_user": "freeCount(address)",
    "mintOpen": "mintOpen()", "balanceOf_user": "balanceOf(address)", "totalSupply": "totalSupply()",
    "FREE_SUPPLY": "FREE_SUPPLY()", "mintedBy_user": "mintedBy(address)", "FREE_SHARES": "FREE_SHARES()",
    "totalMinted": "totalMinted()", "finalized": "finalized()", "freeClaimed_user": "freeClaimed(address)",
    "freeClaimed": "freeClaimed()", "freeLeft": "freeLeft()", "remainingFree": "remainingFree()",
    "FREE_QUOTA": "FREE_QUOTA()", "freeUsed": "freeUsed()", "freeTakenBy_user": "freeTakenBy(address)",
    "MAX_SUPPLY": "MAX_SUPPLY()", "totalMints": "totalMints()", "mintActive": "mintActive()",
    "freeMintedTotal": "freeMintedTotal()", "quote_user1": "quote(address,uint256)",
    "freeLeft_user": "freeLeft(address)", "freeUsed_user": "freeUsed(address)",
    "freeFor_user1": "freeFor(address,uint256)", "priceFor_user": "priceFor(address)",
    "FREE_PER_WALLET": "FREE_PER_WALLET()", "mintedCount_user": "mintedCount(address)",
    "freeMinted_user": "freeMinted(address)", "phase": "phase()", "launched": "launched()",
    "sold": "sold()", "MAX_FREE": "MAX_FREE()", "sharesMinted": "sharesMinted()",
    "soldOut": "soldOut()", "closed": "closed()", "freeAvailable_user": "freeAvailable(address)",
    "hasMinted_user": "hasMinted(address)", "quotaOf_user": "quotaOf(address)",
}
rr = json.load(open(f"{BASE}/hot-leg-2026-11-09-0359-reread.json"))
prev = json.load(open(f"{BASE}/hot-leg-2026-11-09-0344-reread.json"))
failed = [k for k, v in rr["items"].items() if v.get("_batch_fail")]
def read_item(name):
    pd = prev["items"][name]
    views = [FIELD_TO_SIG[f] for f in pd if f in FIELD_TO_SIG]
    got = raw_batch(pd["address"], views)
    d = {"address": pd["address"]}
    if got is None:
        d["_batch_fail"] = True
        for f in pd:
            if f != "address": d[f] = None
    else:
        d.update(got)
    return name, d
with ThreadPoolExecutor(max_workers=4) as ex:
    for name, d in ex.map(read_item, failed):
        rr["items"][name] = d
# block probe
block = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=20)
        block = int(r["result"], 16); break
    except Exception:
        continue
rr["block"] = block
rr["retry_duration_sec"] = round(time.time() - T0, 1)
still_fail = [k for k, v in rr["items"].items() if v.get("_batch_fail")]
if still_fail:
    rr["FAILED"] = True
    rr["FAILED_reason"] = f"{len(still_fail)} items still batch-failed after retry: {still_fail}; block={block}"
json.dump(rr, open(f"{BASE}/hot-leg-2026-11-09-0359-reread.json", "w"), indent=1)
# recompute diff vs 0344 on retried data
prev_items = prev["items"]
changes = []
for name, d in rr["items"].items():
    pd = prev_items.get(name)
    if not pd: continue
    for f, v in d.items():
        if f in ("address", "_batch_fail"): continue
        ov = pd.get(f)
        if v != ov and not (v is None and ov is None):
            changes.append({"item": name, "field": f, "old": ov, "new": v})
json.dump({"block": block, "changes": changes, "still_failed": still_fail, "duration_sec": rr["retry_duration_sec"]},
          open(f"{BASE}/hot-leg-2026-11-09-0359-leg4retry.json", "w"), indent=1)
print(json.dumps({"block": block, "still_failed": still_fail, "changes": changes, "duration": rr["retry_duration_sec"]}, indent=1))
