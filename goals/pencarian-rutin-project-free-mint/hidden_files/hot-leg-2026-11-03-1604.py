import json, re, sys, urllib.request, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
seen = json.load(open(f"{H}/hot-leg-seen.json"))
reported = json.load(open(f"{H}/hot-leg-reported.json"))
snap = json.load(open(f"{H}/onchain-snapshot.json"))
out = {"block": None}
try: out["block"] = int(race("eth_blockNumber", []), 16)
except Exception as e: out["block_error"] = str(e)[:120]
print("block", out["block"], flush=True)

# (1) Sourcify feed
feed = None
try:
    req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", headers={"User-Agent": "Mozilla/5.0"})
    feed = json.loads(urllib.request.urlopen(req, timeout=25).read())
except Exception as e:
    print("sourcify urllib fail", str(e)[:100], flush=True)
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "25", "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"], capture_output=True, text=True)
        feed = json.loads(r.stdout)
    except Exception as e2:
        print("sourcify curl fail", str(e2)[:100], flush=True)
addrs = []
if isinstance(feed, list):
    for it in feed:
        a = it.get("address") or (it.get("contract") or {}).get("address")
        if a: addrs.append(a)
elif isinstance(feed, dict):
    for it in feed.get("results", []) or feed.get("contracts", []):
        a = it.get("address")
        if a: addrs.append(a)
print("feed contracts:", len(addrs), flush=True)
json.dump({"feed": addrs}, open(f"{H}/hot-leg-2026-11-03-1604-sourcify.json", "w"), indent=1)
new = [a for a in addrs if a not in seen and a.lower() not in [k.lower() for k in seen]]
print("new vs seen:", new, flush=True)
REG = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
shape = {}
for a in new:
    if a.lower() == REG: shape[a] = "skip-registry"; continue
    if a in ("0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124", "0x8b47354E7b76B1970a0D06365c8244a810d37493"): shape[a] = "excluded-example"; continue
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{a}", headers={"User-Agent": "Mozilla/5.0"})
        meta = json.loads(urllib.request.urlopen(req, timeout=20).read())
        abi = meta.get("abi") or (meta.get("stdJson") or {}).get("abi") or []
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        src = json.dumps(meta)[:200000].lower()
        has_mint = any(n and n.lower().startswith("mint") for n in fns)
        has_quote = any("quote" in (n or "").lower() or "cost" in (n or "").lower() for n in fns)
        has_free = any(n in FREE_VIEWS for n in fns)
        has_agent = REG in src or "agentgate" in src or "agentid" in src
        is_token = all(n in fns for n in ["name","symbol","decimals","totalSupply"])
        has_free_mint = "mintFree" in fns
        s1 = has_mint and has_quote and has_free and has_agent
        s2 = is_token and has_free_mint and (any(n in fns for n in ["freeClaimed","freeMinted"])) and any(n in fns for n in ["FREE_SLOTS","FREE_SUPPLY"]) and has_agent
        shape[a] = {"fns_sample": fns[:40], "s1": s1, "s2": s2, "is_erc721": ("ownerOf" in fns or "tokenURI" in fns), "has_mint": has_mint, "has_quote": has_quote, "has_free": has_free, "has_agent": has_agent}
    except Exception as e:
        shape[a] = {"error": str(e)[:120]}
    print("shape", a, shape[a], flush=True)
json.dump(shape, open(f"{H}/hot-leg-2026-11-03-1604-sourcify-shape.json", "w"), indent=1)

# (2) Boltbook
bolt_new = {}
for lang, suffix in [("en", ""), ("zh", "?lang=zh")]:
    html = None
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "25", f"https://boltbook.app/{suffix}"], capture_output=True, text=True)
        html = r.stdout
    except Exception as e:
        print("boltbook", lang, "fail", str(e)[:80], flush=True)
    if html:
        found = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))
        print("boltbook", lang, "chars", len(html), "addrs", len(found), flush=True)
        for a in found:
            if a not in seen and a not in new:
                bolt_new[a] = lang
print("boltbook new addrs:", bolt_new, flush=True)

# bridge read-only
try:
    bridge = json.load(open(f"{H}/scan-bridge.json"))
    bcon = bridge.get("contracts", {})
    print("bridge contracts:", len(bcon), flush=True)
    discarded = [k for k, v in bcon.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    print("bridge discarded:", discarded, flush=True)
    out["bridge_count"] = len(bcon); out["bridge_discarded"] = discarded
except Exception as e:
    print("bridge unreadable, skip:", str(e)[:100], flush=True); out["bridge_skip"] = str(e)[:100]

# (4) re-read curated snapshot items (generic views) + key specifics
def one(addr, sig, args=""):
    try:
        r = race("eth_call", [{"to": addr, "data": "0x" + sel(sig) + args}, "latest"])
        if isinstance(r, str) and r.startswith("0x") and len(r) == 66: return int(r, 16)
        return None
    except Exception: return None
views = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("totalMinted()", ""), ("freeMinted()", ""), ("mintedBy(address)", pad), ("freeUsed(address)", pad), ("balanceOf(address)", pad)]
names = ["Fangcount", "Mechfarm", "Threadmoth", "Syntaxia", "Compilur", "Robogent", "Glasscore", "Crtdroid", "Medusine", "Gearpixel", "Dronegent", "Jelly"]
targets = {}
for n in names:
    e = snap["contracts"].get(n)
    if e and e.get("address"): targets[n] = e["address"]
# track_c open-ish + pending pollen + verify items
for k, e in snap["track_c"].items():
    if e.get("sale"): targets[f"trackc-{k}"] = e["sale"]
targets["pending-pollen"] = snap["pending_claims"]["hive-pollen"]["mint"]
targets["AgentZero-5a67"] = "0x5A67Db8389A08762D6120903Eec43e719Cf67c43"
targets["trackc-ORBIT-sale"] = "0x429f23778562bc4be82c215ba12180e1ff297e8f" if "trackc-ORBIT-sale" not in targets else targets["trackc-ORBIT-sale"]
reread = {}
for name, addr in targets.items():
    d = {sig: one(addr, sig, args) for sig, args in views}
    reread[name] = {"address": addr, **d}
    print("reread", name, d, flush=True)
# pollen specifics
for sig in ["launched()", "phase()", "pollenAgents()", "paidSold()"]:
    reread["pending-pollen"][sig] = one(targets["pending-pollen"], sig)
print("pollen extra", {k: reread["pending-pollen"][k] for k in ["launched()", "phase()", "pollenAgents()", "paidSold()"]}, flush=True)
# Agent Zero specifics
az = targets["AgentZero-5a67"]
for sig, args in [("FREE_CAP()", ""), ("poolOpened()", ""), ("startTime()", ""), ("quote(address,uint256)", pad + "0"*63 + "1")]:
    reread["AgentZero-5a67"][sig] = one(az, sig, args)
print("agentzero", {k: reread["AgentZero-5a67"][k] for k in ["FREE_CAP()", "poolOpened()", "startTime()", "quote(address,uint256)"]}, flush=True)
json.dump({"block": out["block"], "reread": reread, "sourcify_shape": shape, "boltbook_new": bolt_new, "bridge": out.get("bridge_count")}, open(f"{H}/hot-leg-2026-11-03-1604-reread.json", "w"), indent=1)
# update seen only for confirmed non-leads: sourcify new + boltbook new that are not sale-shape (boltbook shape unknown here -> do NOT add boltbook unknowns)
for a in new:
    seen[a] = "2026-11-03T16:04:00+07:00"
json.dump(seen, open(f"{H}/hot-leg-seen.json", "w"), indent=1)
print("seen now", len(seen), flush=True)
print("DONE")
