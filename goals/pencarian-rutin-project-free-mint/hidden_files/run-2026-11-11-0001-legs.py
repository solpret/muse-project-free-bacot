#!/usr/bin/env python3
"""Run 2026-11-10 0001 WIB — legs: Sourcify shape-check (new feed + Boltbook),
NIGHTFORGE gate recheck (method H contractURI + site docs), SOLDERCATS/NIGHTFORGE
priority probe, Ankr pre-flight for scan leg. Read-only; no preview/mint."""
import json, subprocess, time, sys
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "run-2026-11-11-0001"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
out = {}

def curl(url, max_time=25):
    p = subprocess.run(["curl", "-sL", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

# ---- 1. Shape-check new contracts ----
feed = json.load(open("/tmp/sourcify-0001.json"))
feed_addrs = [r["address"] for r in feed.get("results", [])]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
bb = open("/tmp/bb-0001-zh.html", errors="ignore").read()
import re
bb_addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", bb)))
new = [a for a in feed_addrs if a.lower() not in seen_l]
new += [a for a in bb_addrs if a.lower() not in seen_l and a.lower() not in {x.lower() for x in new}]
print("SHAPE-CHECK new:", len(new), new, flush=True)

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
                "verified": bool(abi)}
    except Exception as e:
        return {"error": str(e)[:200]}

shape = {}
for a in new:
    shape[a] = shape_check(a)
    print("SHAPE", a, json.dumps(shape[a]), flush=True)
out["shape"] = shape

# ---- 2. NIGHTFORGE gate recheck (method H) ----
NF = "0x22f43ba09fd4beb9417d4484c60370354b220186"
nf_site = "https://nightforge.pages.dev"
gate = {"contract": NF, "site": nf_site, "checks": {}}
for path in ["", "/meta/collection.json", "/llms.txt", "/skill.md", "/launch.json", "/agent.json"]:
    url = nf_site + path
    body = curl(url, 20)
    hit = NF.lower() in body.lower()
    gate["checks"][path or "/"] = {"bytes": len(body), "prints_contract": hit,
                                   "snippet": body[:200].replace("\n", " ") if hit else ""}
    print("NF-GATE", path or "/", len(body), "prints_contract=" + str(hit), flush=True)
# EMBERANVIL same template — check its site too (minted already, informational)
em_site = "https://emberanvil.pages.dev"
em_body = curl(em_site, 20)
gate["emberanvil_site"] = {"bytes": len(em_body),
    "prints_contract": "0x7673c596a6702d32f844266dc2ca7b1fd6d7df21".lower() in em_body.lower()}
print("EM-GATE", em_site, len(em_body), gate["emberanvil_site"], flush=True)
out["nightforge_gate"] = gate

# ---- 3. Priority probe: SOLDERCATS + NIGHTFORGE + ORBITJANITOR fresh state ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def words(h):
    if not isinstance(h, str) or not h.startswith("0x"): return None
    hh = h[2:]
    if not hh or len(hh) % 64: return None
    return [int(hh[i:i+64], 16) for i in range(0, len(hh), 64)]

RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/"]
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

def probe(name, addr, spec):
    jobs = [(name, f, addr, d) for f, d in spec]
    for rpc in RPCS:
        r = batch(rpc, [(a, d) for (_, _, a, d) in jobs])
        if isinstance(r, list) and len(r) == len(jobs):
            res = {}
            ok = 0
            for (nm, field, ad, _), resp in zip(jobs, r):
                val = resp.get("result") if isinstance(resp, dict) else None
                if val:
                    w = words(val)
                    if w is not None:
                        res[field] = w if len(w) > 1 else w[0]
                        ok += 1
            print(f"PROBE {name} via {rpc}: {ok}/{len(jobs)}", json.dumps(res), flush=True)
            if ok:
                return res
    return {}

SC = "0x3D972EBbF7488f21b95250B867e2406c723C9DDC"
out["probe"] = {}
out["probe"]["SOLDERCATS"] = probe("SOLDERCATS", SC, [
    ("totalSupply", sel("totalSupply()")),
    ("agentFreeUsed", sel("agentFreeUsed()")),
    ("agentFreeCap", sel("agentFreeCap()")),
    ("mintOpen", sel("mintOpen()")),
    ("mintStart", sel("mintStart()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
    ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER)),
])
out["probe"]["ORBITJANITOR"] = probe("ORBITJANITOR", "0x8d5a0555446d37afaba75e36da318646a4b32420", [
    ("totalSupply", sel("totalSupply()")),
    ("agentFreeUsed", sel("agentFreeUsed()")),
    ("agentFreeCap", sel("agentFreeCap()")),
    ("mintOpen", sel("mintOpen()")),
    ("mintStart", sel("mintStart()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
    ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER)),
])
out["probe"]["NIGHTFORGE"] = probe("NIGHTFORGE", NF, [
    ("totalSupply", sel("totalSupply()")),
    ("status", sel("status()")),
    ("mintOpen", sel("mintOpen()")),
    ("mintStart", sel("mintStart()")),
    ("freeMinted", sel("freeMinted()")),
    ("freeLeft", sel("freeLeft()")),
    ("agentFreeUsed", sel("agentFreeUsed()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
    ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER)),
])

# ---- 4. Ankr pre-flight (small 50-block getLogs, <60s) ----
t_pre = time.time()
try:
    sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
    from ankr import ankr_post
    head = None
    try:
        hb = ankr_post("eth_blockNumber", [], timeout=15)
        head = int(hb["result"], 16) if isinstance(hb, dict) and hb.get("result") else None
    except Exception as e:
        head = f"err:{e}"[:120]
    print("PREFLIGHT head:", head, flush=True)
    if isinstance(head, int):
        body = ankr_post("ankr_getLogs", {"fromBlock": hex(head - 49), "toBlock": hex(head),
                                          "topics": [["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]]},
                         timeout=50)
        n = len(body.get("logs", [])) if isinstance(body, dict) else -1
        err = body.get("error") if isinstance(body, dict) else str(body)[:200]
        out["preflight"] = {"ok": n >= 0, "head": head, "logs_50blk": n,
                            "error": err, "secs": round(time.time() - t_pre, 1)}
        print("PREFLIGHT result:", json.dumps(out["preflight"]), flush=True)
    else:
        out["preflight"] = {"ok": False, "head": head, "secs": round(time.time() - t_pre, 1)}
        print("PREFLIGHT failed: head unreadable", flush=True)
except Exception as e:
    out["preflight"] = {"ok": False, "error": str(e)[:300], "secs": round(time.time() - t_pre, 1)}
    print("PREFLIGHT exception:", str(e)[:300], flush=True)

out["duration_sec"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + TAG + "-legs.json", "w"), indent=1)
print("LEGS DONE", out["duration_sec"], "s", flush=True)
