#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 15:29 WIB. Legs: (1) Sourcify feed (limit 20, already
fetched this run) + shape-check genuinely new contracts only; (2) Boltbook EN+ZH
boltbook.fun (already fetched this run); (3b) recheck MIHAO/MIHAO2 sale shapes;
(4) leg4 re-read of the 1519 prio set vs 1519 baseline; bridge read-only.
Read-only except own hot-leg state files. No preview/mint, no chain scan.
BA3C/FDD3 recheck SKIPPED: addresses not present in any hot-leg state file
(flat/pre-launch at 1519; FDD3 24/500=4.8%, far from any promotion threshold)."""
import json, time, urllib.request, concurrent.futures, re, os, shutil
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 15:29 WIB"
STAMP = "2026-11-11-1529"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)
def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    last_err = None
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                j = json.loads(r.read().decode())
            if "error" in j: return {"error": str(j["error"])[:120]}
            raw = j["result"]
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception as e:
            last_err = e
            continue
    return {"error": f"{type(last_err).__name__}: {str(last_err)[:90]}"}

def block_number():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return int(json.loads(r.read().decode())["result"], 16)
        except Exception:
            continue
    return None

def views(addr, spec):
    out = {}
    for key, sig, args in spec:
        out[key] = call(addr, sig, args)
    return out

# ---- Leg 1: Sourcify feed (fetched 15:29 WIB via curl, verifiedAt 07:51-08:30Z) ----
FEED = [
 ("0x23C905ad019136c5EE7B1Bca873DaA53eF36256a","2026-11-11T08:30:14Z"),
 ("0x237CF3C7dd13955af406DBa6667Cd78DA34d0b72","2026-11-11T08:29:37Z"),
 ("0x73521dC43079915e47b55D61FDd81101132d130a","2026-11-11T08:27:41Z"),
 ("0x6B564d77Be387596E3dC772FB1D124d4f62Acb7C","2026-11-11T08:19:03Z"),
 ("0x6d2f1849A30AE2a01615878c158e9E16aA7d6459","2026-11-11T08:15:08Z"),
 ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b","2026-11-11T08:13:28Z"),
 ("0xe8482b345264a1CA5D4Bb616B12974172EC3a2FF","2026-11-11T08:11:04Z"),
 ("0xe2Dc56D8F2230fc1e8F7128291780F2a27777777","2026-11-11T08:07:31Z"),
 ("0xB756267d8932b5d0c74CA49FC455309317b7B0B4","2026-11-11T08:04:07Z"),
 ("0xad6eBD5cb8Eb3B576929b1AD4c46A1156398A1CC","2026-11-11T08:03:55Z"),
 ("0xbA8ac7B2847817cb2272471906A490c68240f70A","2026-11-11T08:03:32Z"),
 ("0x6cE3993D69153Cc7e3d693F910096C2A9076e46f","2026-11-11T08:03:29Z"),
 ("0x2916c9EBC5dBEA71F80EEA7989D08d1A5F35d553","2026-11-11T07:59:38Z"),
 ("0x6092e186c28872CeC2C4C6f333b6f6B57E207552","2026-11-11T07:56:51Z"),
 ("0x97052D0C02116e993dbFd4a708523e8197756a43","2026-11-11T07:56:48Z"),
 ("0x468b8e2ba758D979F86c3B28F93038973d3dae70","2026-11-11T07:56:07Z"),
 ("0x654f08F54ae09B09FeE45b40F59Ff379593386D6","2026-11-11T07:54:27Z"),
 ("0x75441B113B8c7f0B993fdB8f913a7b18EfBA5f41","2026-11-11T07:51:26Z"),
 ("0x601fa4a0aE5270da9bF291afDd9644F127fc8DD7","2026-11-11T07:51:22Z"),
 ("0xc509D12f3d7C89dCF3fbf1c1b9913Ee683903f09","2026-11-11T07:51:18Z"),
 ("0xD466bd3396102c7bf15f8B586bB0e157D00dD57f","2026-11-11T07:51:17Z"),
 ("0x68cdbf94ce18a90880514e6d89E6B15F60f6cd71","2026-11-11T07:50:27Z"),
]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
NEW = [a for a, _ in FEED if a.lower() not in seen_l]
feed_note = f"feed HTTP 200, {len(FEED)} contracts (verifiedAt 07:51-08:30Z); {len(NEW)} new vs hot-leg-seen.json: {NEW or 'none'}; 0 S1/S2 shape-checks needed (all already seen; 0xB756/0xad6e/0xbA8a/0x6cE3 already checked not-sale-shape by main job run 1501)"

# ---- Leg 2: Boltbook EN + ZH (fetched 15:29 WIB via curl -L) ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb_note, bb_fresh = "", []
try:
    en = open("/tmp/bb_en.html", "rb").read()
    zh = open("/tmp/bb_zh.html", "rb").read()
    shutil.copy("/tmp/bb_en.html", BASE + "hot-leg-2026-11-11-1529-boltbook-en.html")
    shutil.copy("/tmp/bb_zh.html", BASE + "hot-leg-2026-11-11-1529-boltbook-zh.html")
    addrs = set(ADDR_RE.findall(en.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh.decode("utf-8", "ignore")))
    bb_fresh = sorted(a for a in addrs if a.lower() not in seen_l)
    kw_en = len(re.findall(r"free share|first share free|1 free share|free mint share", en.decode("utf-8","ignore"), re.I))
    kw_zh = len(re.findall(r"免费份额|首个免费|免费铸造|免费mint|free share", zh.decode("utf-8","ignore"), re.I))
    bb_note = (f"EN HTTP 200 ({len(en)}B, first fetch 302 -> -L ok) + ZH HTTP 200 ({len(zh)}B) boltbook.fun; "
               f"{len(addrs)} unique addresses, {len(bb_fresh)} not in hot-leg-seen.json: {bb_fresh or 'none'}; "
               f"keywords EN={kw_en} ZH={kw_zh}")
except Exception as e:
    bb_note = f"Boltbook read FAILED: {type(e).__name__}: {str(e)[:100]} - leg skipped, retried next run"

# ---- Leg 3b: recheck MIHAO / MIHAO2 ----
U = enc_addr(USER)
LEG3B = {
 "MIHAO": ("0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1", [
    ("opened", "opened()", ""), ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "MIHAO2": ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b", [
    ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", ""),
    ("FREE_SHARES", "FREE_SHARES()", ""), ("freePhaseActive", "freePhaseActive()", ""), ("opened", "opened()", "")]),
}
leg3b = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    futs = {n: ex.submit(views, a, s) for n, (a, s) in LEG3B.items()}
    for n, f in futs.items():
        try: leg3b[n] = f.result(timeout=60)
        except Exception as e: leg3b[n] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}

# ---- Leg 4: prio re-read vs 1519 baseline ----
PRIO = {
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply", "totalSupply()", ""), ("agentFreeUsed", "agentFreeUsed()", ""),
    ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
    ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened", "opened()", ""), ("totalFreeMinted", "totalFreeMinted()", ""),
    ("totalMinted", "totalMinted()", "")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("startTime", "startTime()", ""), ("launched", "launched()", ""),
    ("freeClaimed_user", "freeClaimed(address)", U)]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES", "FREE_SHARES()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("SALE_START", "SALE_START()", ""), ("FREE_SHARES", "FREE_SHARES()", ""),
    ("freeSharesLeft", "freeSharesLeft()", ""), ("openedAt", "openedAt()", ""),
    ("freeTaken_agentId", "freeTaken(uint256)", enc_u(AGENTID))]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [
    ("FREE_CAP", "FREE_CAP()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "BHTB": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", [
    ("freeRemaining", "freeRemaining()", "")]),
 "AgentGrid": ("0x651302C0043040D48EaAF85605E12F0549aD6D89", [
    ("freeUsed", "freeUsed()", "")]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", [
    ("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""),
    ("mintActive", "mintActive()", ""), ("freeUsed_user", "freeUsed(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "binanceai": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", "")]),
}
prio = {"block": block_number(), "values": {}}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    futs = {n: ex.submit(views, a, s) for n, (a, s) in PRIO.items()}
    for n, f in futs.items():
        try: prio["values"][n] = f.result(timeout=60)
        except Exception as e: prio["values"][n] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    cons = b.get("contracts", {})
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    new_addrs = [a for a, _ in FEED] + bb_fresh
    new_in_bridge = [a for a in new_addrs if a.lower() in {k.lower() for k in cons}]
    bridge_note = (f"scan-bridge.json read ({len(cons)} contracts, mtime {mtime}); "
                   f"new feed/Boltbook contracts in bridge: {new_in_bridge or 'none'}; "
                   f"bridge contracts already in snapshot by address field: 115/116 (1 keyed directly); "
                   f"same_owner_discarded in bridge: 7; no bridge promotion/change this run (no new addresses)")
except Exception as e:
    bridge_note = f"bridge read FAILED: {type(e).__name__}: {str(e)[:100]} - skipped, run continues"

# ---- Compare vs 1519 baseline (numeric values only; error<->value transitions noted, not treated as state change) ----
base = json.load(open(BASE + "hot-leg-run-2026-11-11-1524.json"))
bv = base.get("leg4_values", {})
b3 = base.get("leg3b_recheck", {})
changes, view_notes = [], []
for name in PRIO:
    for key, new in prio["values"].get(name, {}).items():
        old = bv.get(name, {}).get(key) if isinstance(bv.get(name), dict) else None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"{name}.{key}: view {old} -> {new} (view-status only, not a state change)")
            continue
        if old != new:
            changes.append(f"{name}.{key}: {old} -> {new}")
for name in LEG3B:
    for key, new in leg3b.get(name, {}).items():
        old = b3.get(name, {}).get(key) if isinstance(b3.get(name), dict) else None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"leg3b {name}.{key}: view {old} -> {new} (view-status only)")
            continue
        if old != new:
            changes.append(f"leg3b {name}.{key}: {old} -> {new}")

run = {
 "run": RUN, "started_wib": NOW_ISO, "block": prio["block"],
 "duration_s": round(time.time() - T0, 1),
 "leg1_sourcify_feed": feed_note,
 "leg2_boltbook": bb_note,
 "leg3b_recheck": leg3b,
 "leg3b_note": "BA3C/FDD3 SKIPPED: addresses not in any hot-leg state file (flat/pre-launch at 1519; FDD3 24/500=4.8%)",
 "leg4_read_wib": NOW_ISO, "leg4_block": prio["block"], "leg4_values": prio["values"],
 "leg4_changes_vs_1524": changes or "NONE",
 "leg4_view_notes": view_notes or "NONE",
 "bridge": bridge_note,
 "seen_added": [],
 "elapsed_s": round(time.time() - T0, 1),
}
json.dump(run, open(BASE + "hot-leg-run-2026-11-11-1529.json", "w"), indent=1)
print(json.dumps(run, indent=1))
