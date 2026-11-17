#!/usr/bin/env python3
"""Salvage for hot-leg 0214: full run killed by 270s timeout (RPC slow).
Fast, trimmed: Sourcify feed (n=20) + re-read of priority items only,
chunked <=24 calls, 12s timeouts. Read-only except seen.json additions."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def curl(url, data=None, timeout=12):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None: cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception: return None
def rpc_chunked(calls, timeout=12):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i+24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        if not body: body = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(chunk), timeout=timeout)
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]; continue
        try:
            resp = json.loads(body); items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            for c in chunk:
                it = by_id.get(c["id"], {}); out.append((c["id"], it.get("result"), it.get("error")))
        except Exception as e:
            out += [(c["id"], None, f"parse-failed: {e}") for c in chunk]
    return out
def now_wib(): return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600))
t0 = time.time(); out = {"run": "free-mint-hot-leg 2026-11-14 02:14 WIB SALVAGE", "started_wib": now_wib()}
seen = json.load(open(f"{HF}/hot-leg-seen.json")); seen_lower = {k.lower() for k in seen}
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"}
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
# Leg 1 feed
feed_new = []
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=12)
    parsed = json.loads(body) if body else {}
    feed = parsed.get("results", []) if isinstance(parsed, dict) else parsed
    out["feed"] = {"n": len(feed), "newest_verifiedAt": feed[0].get("verifiedAt") if feed else None,
                   "oldest_verifiedAt": feed[-1].get("verifiedAt") if feed else None}
    for item in feed:
        a = item.get("address", "")
        if a and a.lower() not in seen_lower and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED and a not in feed_new:
            feed_new.append(a)
except Exception as e: out["feed"] = {"error": str(e)}
out["feed_new"] = feed_new
# Leg 2 boltbook quick
bb = {}
for lang, url in (("en","https://boltbook.fun/?lang=en"),("zh","https://boltbook.fun/?lang=zh")):
    b = curl(url, timeout=12)
    bb[lang] = {"bytes": len(b)} if b else {"error": "fetch-failed"}
out["boltbook"] = bb
# Priority re-read (trimmed PLAN)
PLAN = [
 ("Agentx","0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",[("freeMinted",False),("FREE_CAP",False),("freeClaimed",True),("mintOpen",False)]),
 ("CRACE","0x7B1ca439312368dE8652b9B5d7A54cA74A884680",[("freeMinted",False),("FREE_QUOTA",False),("mintOpen",False),("totalSupply",False),("freeClaimed",True)]),
 ("OLIVER","0xad86e4d52e55709d1bda08f922853d4b109e0810",[("freeMinted",False),("FREE_MAX",False),("freeRemaining",False),("mintOpen",False)]),
 ("Zero","0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",[("freeMinted",False),("FREE_CAP",False),("mintOpen",False),("freeClaimed",True)]),
 ("OBFG","0x5314071bba19943f58347ba5dec423e5032a6818",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("freeAvailable",True)]),
 ("MECHA","0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",[("freeClaimed",False)]),
 ("AgentMuse","0x779fa133848d23052B7345F63B3b2E5309cd13ed",[("freeClaimed",False),("FREE_SHARES",False)]),
 ("2e34","0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",[("freeMinted",False),("FREE_MAX",False),("mintOpen",False)]),
 ("binanceai-mint","0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched",False),("claimable",True)]),
 ("NOTV","0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",[("totalMinted",False)]),
 ("JNTM","0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",[("freeClaimed",False),("FREE_LOTS_CAP",False),("opened",False),("freeLeft",False)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn+("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc":"2.0","id":len(reqs),"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append((name, fn+("_user" if uarg else "")))
reads = {}
for cid, r, err in rpc_chunked(reqs, timeout=12):
    name, fn = keys[cid]
    v = None
    if r and r != "0x" and len(r) >= 66:
        try: v = int(r[-64:], 16)
        except Exception: v = None
    reads.setdefault(name, {})[fn] = v
out["reads"] = reads
out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
# feed_new shape probe (max 8 contracts, 12 selectors each = 96 calls -> cap 8*12=96 too many; use 6 selectors x 8 = 48, chunked 24)
PROBE = ["freeSharesRemaining","freeClaimed","freeMinted","freeLeft","FREE_SLOTS","FREE_SUPPLY"]
probe_status = {}
if feed_new:
    pcalls, pkeys = [], []
    for a in feed_new[:8]:
        for fn in PROBE:
            pcalls.append({"jsonrpc":"2.0","id":len(pcalls),"method":"eth_call","params":[{"to":a,"data":sel(fn+"()")},"latest"]})
            pkeys.append((a, fn))
    hits = {}
    for cid, r, err in rpc_chunked(pcalls, timeout=12):
        if r and isinstance(r, str) and len(r) >= 66 and not err:
            a, fn = pkeys[cid]; hits.setdefault(a, []).append(fn)
    for a in feed_new[:8]:
        h = hits.get(a, [])
        probe_status[a] = {"hits": h, "status": "probe-possible-sale" if h else "probe-not-sale-shape"}
out["probe"] = probe_status
out["probe_capped"] = max(0, len(feed_new) - 8)
new_seen = {}
for a in feed_new:
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "sourcify-feed-salvage",
                   "status": st.get("status", "probe-not-run"),
                   "note": json.dumps(st.get("hits", []))[:300]}
if new_seen:
    seen.update(new_seen); json.dump(seen, open(f"{HF}/hot-leg-seen.json","w"), indent=1)
out["seen_added"] = list(new_seen.keys())
out["elapsed_s"] = round(time.time()-t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0214-salvage.json","w"), indent=1)
print(json.dumps(out, indent=1))
