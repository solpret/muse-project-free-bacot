#!/usr/bin/env python3
"""Hot-leg run 2026-11-10 22:59 WIB (scheduled).
Leg 1: Sourcify feed (limit 20, fetched fresh) - shape-check new contracts.
Leg 2: Boltbook front page EN + ZH (boltbook.fun, fetched fresh).
Leg 4: small-batch re-reads (lesson 22:09: big batch failed wholesale):
  BYTEBLOOM (minted #508 run 2201 - confirm slot used),
  NIGHTFORGE (strong-lead legs met, GATE-BLOCKED; site root re-checked
  pre-script: still 23.857-byte medical infographic, 0 contract matches),
  SOLDERCATS (early, 12.85% at 22:54, pace ~2.4/mnt - watch 25%),
  CosmicSentinel, YAMA, LOWB, ELEVEN, UFO (A), SAGENT (B).
Bridge read-only (stale since 8 Nov, noted only).
Read-only; no preview/mint in-script (parent decides on strong-lead guard).
"""
import json, subprocess, time, re, datetime, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-10-2259"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/"]

def curl(url, max_time=20):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return hex(n)[2:].rjust(64, "0")

def words(hexstr):
    if not isinstance(hexstr, str) or not hexstr.startswith("0x"): return None
    h = hexstr[2:]
    if not h or len(h) % 64: return None
    return [int(h[i:i+64], 16) for i in range(0, len(h), 64)]

def batch(rpc, calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try:
        r = json.loads(p.stdout)
        return r if isinstance(r, list) else {"_err": str(r)[:200]}
    except Exception:
        return {"_err": (p.stdout + p.stderr)[:200]}

def run_batch(jobs):
    out = {}
    for rpc in RPCS:
        r = batch(rpc, [(a, d) for (_, _, a, d) in jobs])
        if isinstance(r, list) and len(r) == len(jobs):
            ok = 0
            for (name, field, addr, _), resp in zip(jobs, r):
                val = resp.get("result") if isinstance(resp, dict) else None
                if val:
                    w = words(val)
                    if w is not None:
                        out.setdefault(name, {})[field] = w if len(w) > 1 else w[0]
                        ok += 1
            print(f"  batch via {rpc}: {ok}/{len(jobs)} ok")
            if ok:
                return out, rpc
        else:
            print(f"  batch via {rpc}: bad response {str(r)[:150]}")
    return out, None

def block_number(rpc):
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json",
                        "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                       capture_output=True, text=True)
    try: return int(json.loads(p.stdout)["result"], 16)
    except Exception: return None

# ---- Leg 1: feed ----
feed = json.load(open("/tmp/hotleg-feed-2259.json"))
json.dump(feed, open(BASE + TAG + "-feed.json", "w"), indent=1)
addrs = [r["address"] for r in feed.get("results", [])]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in addrs if a.lower() not in seen_l]
print("FEED count:", len(addrs), "new:", new_feed)

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeSupply", "freeSlots"]
def shape_check(a):
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 20)
        d = json.loads(raw)
        abi = d.get("abi") or []
        fns = [e.get("name", "") for e in abi if e.get("type") == "function"]
        mint = [f for f in fns if "mint" in f.lower()]
        quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower()]
        free = [f for f in fns if any(v.lower() in f.lower() for v in FREE_VIEWS)]
        agent = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
        token = [f for f in fns if f in ("name", "symbol", "decimals", "totalSupply")]
        s1 = bool(mint and quote and free and agent)
        s2 = bool(token == ["name", "symbol", "decimals", "totalSupply"] and
                  any(f in fns for f in ("mintFree",)) and free and agent)
        return {"S1": s1, "S2": s2, "mint": mint, "quote": quote,
                "free": free, "agent": agent, "token": token, "fns": len(fns),
                "verifiedAt": next((r.get("verifiedAt") for r in feed["results"]
                                    if r["address"].lower() == a.lower()), None)}
    except Exception as e:
        return {"error": str(e)[:200]}

shape = {}
for a in new_feed:
    shape[a] = shape_check(a)
    print("FEED-SHAPE", a, json.dumps(shape[a]))

# ---- Leg 2: Boltbook ----
bb_new = []
for lang, path in [("en", "/tmp/bb-en-2259.html"), ("zh", "/tmp/bb-zh-2259.html")]:
    try:
        html = open(path, errors="ignore").read()
    except Exception as e:
        html = ""
        print(f"BOLTBOOK {lang}: READ ERROR {e}")
    open(BASE + TAG + "-boltbook-" + lang + ".html", "w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new_bb = [a for a in found if a.lower() not in seen_l and a.lower() not in {x.lower() for x in new_feed}]
    bb_new += new_bb
    print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs, new: {new_bb}")
    for kw in ["free share", "first share free", "free mint", "免费份额", "首个免费", "免费铸造", "免费mint"]:
        if kw.lower() in html.lower():
            print(f"  keyword hit {lang}: {kw}")
for a in bb_new[:3]:
    shape[a] = shape_check(a)
    shape[a]["source"] = "boltbook-frontpage"
    print("BB-SHAPE", a, json.dumps(shape[a]))
json.dump(shape, open(BASE + TAG + "-shape.json", "w"), indent=1)

# ---- Leg 4: small-batch re-reads ----
BB = "0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"
NF = "0x22f43ba09fd4beb9417d4484c60370354b220186"
CS = "0x88731d1eb41c36f3d705fdb58b658244c06afc36"
YAMA = "0x86D779fc4d83044cCECCb53639f9a98E367D6E46"
LOWB = "0x00487ED061C77A1dd5085ef3a2D593366f9C6B35"
ELEVEN = "0x64767b1a39441e72046c2162065a2896e154b341"
UFO = "0xE4059eA596392AcA14100af6CDC9481c330E2728"
SAGENT = "0x67299f979508CeDBb1Fb04226c3846D2b82c93A4"
SCATS = "0x3D972EBbF7488f21b95250B867e2406c723C9DDC"

def J(jobs, name, field, addr, data): jobs.append((name, field, addr, data))

all_out = {}
rpcs_used = {}
def do(name, spec):
    jobs = []
    for f, d in spec:
        J(jobs, name, f, spec_addr[name], d)
    print("==", name, spec_addr[name])
    out, rpc = run_batch(jobs)
    print(json.dumps(out, indent=1))
    all_out.update(out)
    rpcs_used[name] = rpc

spec_addr = {"BYTEBLOOM": BB, "NIGHTFORGE": NF, "CosmicSentinel": CS,
             "YAMA": YAMA, "LOWB": LOWB, "ELEVEN": ELEVEN, "UFO": UFO, "SAGENT": SAGENT, "SOLDERCATS": SCATS}

do("BYTEBLOOM", [("totalSupply", sel("totalSupply()")),
                 ("agentFreeUsed", sel("agentFreeUsed()")),
                 ("agentFreeLeft", sel("agentFreeLeft()")),
                 ("mintOpen", sel("mintOpen()")),
                 ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
                 ("walletInfo_user", sel("walletInfo(address)") + enc_addr(USER)),
                 ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER))])
do("NIGHTFORGE", [("totalSupply", sel("totalSupply()")),
                  ("status", sel("status()")),
                  ("mintOpen", sel("mintOpen()")),
                  ("mintStart", sel("mintStart()")),
                  ("freeMinted", sel("freeMinted()")),
                  ("freeLeft", sel("freeLeft()")),
                  ("agentFreeUsed", sel("agentFreeUsed()")),
                  ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
                  ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER))])
do("CosmicSentinel", [("totalSupply", sel("totalSupply()")),
                      ("freeMinted", sel("freeMinted()")),
                      ("mintOpen", sel("mintOpen()")),
                      ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
                      ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER))])
do("YAMA", [("freeSharesRemaining", sel("freeSharesRemaining()")),
            ("totalShares", sel("totalShares()")),
            ("totalFreeShares", sel("totalFreeShares()")),
            ("freeUsed_user", sel("freeUsed(address)") + enc_addr(USER)),
            ("isAgent_user", sel("isAgent(address)") + enc_addr(USER))])
do("LOWB", [("opened", sel("opened()")),
            ("totalFreeMinted", sel("totalFreeMinted()")),
            ("totalMinted", sel("totalMinted()"))])
do("ELEVEN", [("freeMinted", sel("freeMinted()")),
              ("FREE_MINTS", sel("FREE_MINTS()")),
              ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER)),
              ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER))])
do("UFO", [("saleOpen", sel("saleOpen()")),
           ("saleStart", sel("saleStart()")),
           ("FREE_SHARES", sel("FREE_SHARES()")),
           ("totalFreeShares", sel("totalFreeShares()")),
           ("totalShares", sel("totalShares()")),
           ("totalPaidShares", sel("totalPaidShares()")),
           ("freeUsed_user", sel("freeUsed(address)") + enc_addr(USER)),
           ("quote_1", sel("quote(uint256)") + enc_uint(1))])
do("SOLDERCATS", [("totalSupply", sel("totalSupply()")),
                  ("agentFreeUsed", sel("agentFreeUsed()")),
                  ("agentFreeLeft", sel("agentFreeLeft()")),
                  ("mintOpen", sel("mintOpen()")),
                  ("mintStart", sel("mintStart()")),
                  ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
                  ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER))])
do("SAGENT", [("launched", sel("launched()")),
              ("totalShares", sel("totalShares()")),
              ("freeFor_0", sel("freeFor(uint256)") + enc_uint(0)),
              ("quotaOf_user", sel("quotaOf(address)") + enc_addr(USER)),
              ("quote_1", sel("quote(uint256)") + enc_uint(1))])

block = block_number(rpcs_used.get("BYTEBLOOM") or RPCS[0])
res = {"block": block, "rpcs": rpcs_used, "items": all_out}
json.dump(res, open(BASE + TAG + "-priority-reread.json", "w"), indent=1)

# ---- Bridge check (read-only) ----
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = b.get("contracts", {})
    print("BRIDGE contracts:", len(bcontracts),
          "mtime:", datetime.datetime.fromtimestamp(
              os.path.getmtime(BASE + "scan-bridge.json"),
              datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds"))
except Exception as e:
    print("BRIDGE read error:", e)

# ---- Update hot-leg-seen.json with newly shape-checked contracts ----
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
for a, s in shape.items():
    if a.lower() in seen_l: continue
    if "error" in s:
        note = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": now, "note": note,
               "source": s.get("source", "sourcify-feed"), "status": status}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
print("seen total now:", len(seen))
print("DURATION sec:", round(time.time() - T0, 1))
