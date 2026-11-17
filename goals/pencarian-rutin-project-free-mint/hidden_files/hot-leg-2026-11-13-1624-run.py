#!/usr/bin/env python3
"""Hot-leg 1624 (2026-11-13): same pattern as 1614 run. Sourcify feed poll +
Boltbook EN/ZH + chunked on-chain selector PROBE shape-check for new contracts
+ chunked direct JSON-RPC re-read (bsc-dataseed) of priority watchlist/track-C
+ pending binanceai claim + AgentMuse + Zero + OLIVER + 2e34 (monitor-only).
Baselines: 1614 run (Agentx 740/1111 66.6%; OBFG 685/1230 55.7%,
Zero 288/500 57.6%, OLIVER 943/1000 94.3% freeRemaining 57, RESUME/BC1B
freeCount 469/3000 15.6%, Pickgrid freeMinted 216, MECHA freeClaimed 1929,
JNTM SOLD OUT 1000/1000, NOTV totalMinted 0 (freeStart 18:00 WIB), AgentMuse
freeClaimed 345, binanceai launched 0 (refund phase), 2e34 801/1000 80.1% at 1614, monitor-only,
Mossbound Key SOLD OUT 325/325 - REPORTED 1444, no further
action. Slate Insignia NEW5893 Slate Insignia OPENED 15:50:57 WIB - freeMinted 29/480 (6.0%)
at 1614; HANAMI 130/3333 3.9% (flat). HANAMI BLOOM (early lead run 1601,
97/3333 2.91%, mint-start ~12:59 WIB, age ~3h, website/X UNVERIFIED,
slot UNVERIFIED) added to re-read: freeMinted/totalSupply/mintOpen only;
no promotion possible at ~3-4% (needs >70% + slot + website). Ochre Medallion
0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D: strong-lead legs MET at 1509
(165/210 78.6%) but GATE FAILED - reported once
#strong-lead-legs-met-gate-blocked-20261113-1509; SELLOUT 210/210 at 1519
REPORTED ONCE #sellout-20261113-1519 (15:23 WIB) - terminal, no re-report.
Agentx gate website_failed (reported once 08:29 as 50pct-crossed+gate-blocked);
age VERIFIED (mintOpensAt 23:11:05 WIB 12 Nov) - if it crosses 70% (~778)
this run, legs are age+70%+slot but gate STILL blocks: report once as
strong-lead-legs-met-but-gate-blocked, NEVER preview/mint; do a light (D)
re-fetch of the 3 known candidate sites in that case only. OLIVER age
UNVERIFIED + slot user unreadable -> reported 2026-11-12 14:14 as
change-70pct-crossed, NOT a strong lead, never preview/mint; watch for
sellout (freeRemaining 61 at 1514). Zero 56.6% flat, velocity failed +
website unverified -> NOT a candidate, monitor only. Pickgrid cap disputed
(FREE_CAP 300 vs 555 claim) -> 72% not trusted as strong lead. LESSON:
NEVER send a >24-call batch; ALL batches chunked to <=24 calls. Read-only
except hot-leg-seen.json (new contracts only) and run output files. Strict
timeouts; skip stalled legs, never wait."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
AGENTX = "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"
OCHRE = "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=20):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def rpc_chunked(calls, timeout=30):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            for c in chunk:
                it = by_id.get(c["id"], {})
                out.append((c["id"], it.get("result"), it.get("error")))
        except Exception as e:
            out += [(c["id"], None, f"parse-failed: {e}") for c in chunk]
    return out

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-13 16:24 WIB", "started_wib": now_wib()}

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

# --- Leg 1: Sourcify feed ---
feed_new = []
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    parsed = json.loads(body) if body else {}
    feed = parsed.get("results", []) if isinstance(parsed, dict) else parsed
    out["feed"] = {"n": len(feed),
                   "newest_verifiedAt": feed[0].get("verifiedAt") if feed else None,
                   "oldest_verifiedAt": feed[-1].get("verifiedAt") if feed else None}
    for item in feed:
        addr = item.get("address", "")
        if addr and addr.lower() not in seen_lower and addr.lower() != REGISTRY.lower() \
                and addr.lower() not in EXCLUDED and addr not in feed_new:
            feed_new.append(addr)
except Exception as e:
    out["feed"] = {"error": str(e)}
out["feed_new"] = feed_new

# --- Leg 2: Boltbook EN+ZH ---
bb = {}
for lang, url in (("en", "https://boltbook.fun/?lang=en"), ("zh", "https://boltbook.fun/?lang=zh")):
    body = curl(url, timeout=20)
    if body:
        bb[lang] = {"bytes": len(body), "addrs": sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))}
    else:
        bb[lang] = {"error": "fetch-failed"}
out["boltbook"] = bb
bb_new = []
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addrs", []):
        if a.lower() not in seen_lower and a.lower() not in EXCLUDED and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new

# --- Probe shape-check (chunked, 2 contracts x 12 selectors = 24 calls) ---
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}
probe_targets = (feed_new + bb_new)[:12]
probe_calls, probe_keys = [], []
for a in probe_targets:
    for fn in PROBE:
        probe_calls.append({"jsonrpc": "2.0", "id": len(probe_calls),
                            "method": "eth_call",
                            "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        probe_keys.append((a, fn))
probe_hits = {}
if probe_calls:
    for cid, r, err in rpc_chunked(probe_calls, timeout=30):
        if r and isinstance(r, str) and len(r) >= 66 and not err:
            a, fn = probe_keys[cid]
            probe_hits.setdefault(a, []).append(fn)
probe_status = {}
for a in probe_targets:
    hits = probe_hits.get(a, [])
    free_hit = any(h in FREE_SET for h in hits)
    agent_hit = any(h in ("agentRegistry", "AGENT_ID_REGISTRY") for h in hits)
    sale_hit = any(h in ("saleOpen", "mintOpen") for h in hits)
    possible = bool(free_hit and (agent_hit or sale_hit))
    probe_status[a] = {"hits": hits, "free_hit": free_hit, "agent_hit": agent_hit,
                       "sale_hit": sale_hit,
                       "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
out["probe"] = probe_status
out["probe_capped"] = len(feed_new + bb_new) - len(probe_targets)

# --- Leg 3/4: chunked re-read (known-good views) + eth_getCode for bb_new ---
PLAN = [
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("freeAvailable", True)]),
 ("Mossbound", "0xe589A94316C68d4A4f008f841Deb7e9612445244",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("saleStart", False), ("isFreeOpen", False), ("freeRemaining", False), ("freeAvailable", True)]),
 ("Ochre", OCHRE,
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("isFreeOpen", False), ("saleStart", False), ("totalSupply", False),
   ("freeClaimed", True), ("freeAvailable", True)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("freeClaimed", False), ("FREE_LOTS_CAP", False), ("opened", False), ("mintStart", False), ("freeLeft", False), ("paidMinted", False)]),
 ("Agentx", AGENTX,
  [("freeMinted", False), ("FREE_CAP", False), ("freeClaimed", True), ("mintOpen", False)]),
 ("BC1B", "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
  [("freeCount", False), ("FREE_CAP", False)]),
 ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0",
  [("freeMinted", False), ("FREE_CAP", False), ("FREE_SUPPLY", False)]),
 ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
  [("freeClaimed", False)]),
 ("NOTV", "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
  [("totalMinted", False), ("freeStart", False)]),
 ("AgentMuse", "0x779fa133848d23052B7345F63B3b2E5309cd13ed",
  [("freeClaimed", False), ("FREE_SHARES", False), ("openedAt", False), ("bookedOf", True)]),
 ("Zero", "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
  [("freeMinted", False), ("FREE_CAP", False), ("mintOpen", False), ("freeClaimed", True)]),
 ("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810",
  [("freeMinted", False), ("FREE_MAX", False), ("freeRemaining", False), ("mintOpen", False),
   ("freeClaimed", True), ("freeClaimedByAgent", True)]),
 ("2e34", "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",
  [("freeMinted", False), ("freeRemaining", False), ("FREE_MAX", False), ("mintOpen", False)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False), ("claimable", True)]),
 ("NEW5893", "0x5893199322A5300775912ebD236d8f1fEFC700Db",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("totalSupply", False), ("saleStart", False), ("FREE_PER_WALLET", False), ("freeClaimed", True)]),
 ("HANAMI", "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
  [("freeMinted", False), ("totalSupply", False), ("mintOpen", False)]),
 ("UNRES1", "0x6430594F2C40A4374f2EfEdF034C77065DC4CC7D",
  [("freeMinted", False), ("totalSupply", False), ("mintOpen", False)]),
 ("UNRES2", "0xEa98b2065d43c0DE0Ad8629F5D0A08fDABcc708A",
  [("freeMinted", False), ("totalSupply", False), ("mintOpen", False)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
code_keys = []
for a in bb_new:
    reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_getCode",
                 "params": [a, "latest"]})
    code_keys.append(a)
reads, codes = {}, {}
for cid, r, err in rpc_chunked(reqs, timeout=30):
    if cid < len(keys):
        name, fn = keys[cid]
        v = None
        if r and r != "0x" and len(r) >= 66:
            try:
                v = int(r[-64:], 16)
            except Exception:
                v = None
        reads.setdefault(name, {})[fn] = v
    else:
        codes[code_keys[cid - len(keys)]] = ("0x" if r in (None, "0x") else "contract")
out["reads"] = reads
out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
out["eth_getCode"] = codes

# --- Bridge leg (read-only) ---
try:
    b = json.load(open(f"{HF}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge"] = {"n": len(c),
                     "not_in_snapshot": sum(1 for v in c.values() if not v.get("in_freebacot_snapshot")),
                     "same_owner_discarded": sum(1 for v in c.values() if v.get("same_owner_discarded"))}
except Exception as e:
    out["bridge"] = {"error": str(e)}

# --- Derived change flags vs 1614 hot-leg run ---
flags = {}
ax = reads.get("Agentx", {})
if ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    pct = ax["freeMinted"] / ax["FREE_CAP"] * 100
    flags["Agentx_pct"] = round(pct, 1)
    flags["Agentx_70pct_crossed"] = bool(pct > 70)
    flags["Agentx_strong_lead_legs"] = bool(pct > 70 and ax.get("freeClaimed_user") == 0
                                            and ax.get("mintOpen") == 1)
    flags["Agentx_gate"] = "website_failed (reported 08:29; re-check only if 70pct crossed)"
ob = reads.get("OBFG", {})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    flags["OBFG_pct"] = round(ob["freeMinted"] / ob["FREE_SUPPLY"] * 100, 1)
    flags["OBFG_soldout"] = bool(ob["freeMinted"] >= ob["FREE_SUPPLY"])
    flags["OBFG_slot_lost"] = bool(ob.get("freeAvailable_user") == 0)
mb = reads.get("Mossbound", {})
if mb.get("freeMinted") is not None and mb.get("FREE_SUPPLY"):
    flags["Mossbound_pct"] = round(mb["freeMinted"] / mb["FREE_SUPPLY"] * 100, 1)
    flags["Mossbound_sale_open"] = bool(mb.get("saleOpen") == 1 or mb.get("mintOpen") == 1
                                        or mb.get("isFreeOpen") == 1)
    flags["Mossbound_saleStart"] = mb.get("saleStart")
    flags["Mossbound_freeRemaining"] = mb.get("freeRemaining")
    flags["Mossbound_slot_user"] = mb.get("freeAvailable_user")
    flags["Mossbound_soldout"] = bool(mb["freeMinted"] >= mb["FREE_SUPPLY"])
ze = reads.get("Zero", {})
if ze.get("freeMinted") is not None and ze.get("FREE_CAP"):
    flags["Zero_pct"] = round(ze["freeMinted"] / ze["FREE_CAP"] * 100, 1)
    flags["Zero_50pct_crossed"] = bool(ze["freeMinted"] >= ze["FREE_CAP"] * 0.5)
    flags["Zero_slot_open"] = bool(ze.get("freeClaimed_user") == 0)
ol = reads.get("OLIVER", {})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    flags["OLIVER_pct"] = round(ol["freeMinted"] / ol["FREE_MAX"] * 100, 1)
    flags["OLIVER_soldout"] = bool((ol.get("freeRemaining") or 1) == 0)
    flags["OLIVER_slot_user"] = {"freeClaimed_user": ol.get("freeClaimed_user"),
                                 "freeClaimedByAgent_user": ol.get("freeClaimedByAgent_user")}
pk = reads.get("Pickgrid", {})
if pk.get("freeMinted") is not None:
    flags["Pickgrid_freeMinted"] = pk["freeMinted"]
    if pk.get("FREE_CAP"):
        flags["Pickgrid_pct_FREE_CAP"] = round(pk["freeMinted"] / pk["FREE_CAP"] * 100, 1)
    if pk.get("FREE_SUPPLY"):
        flags["Pickgrid_pct_FREE_SUPPLY"] = round(pk["freeMinted"] / pk["FREE_SUPPLY"] * 100, 1)
bc = reads.get("BC1B", {})
if bc.get("freeCount") is not None and bc.get("FREE_CAP"):
    flags["RESUME_pct"] = round(bc["freeCount"] / bc["FREE_CAP"] * 100, 1)
te = reads.get("2e34", {})
if te.get("freeMinted") is not None and te.get("FREE_MAX"):
    flags["2e34_pct"] = round(te["freeMinted"] / te["FREE_MAX"] * 100, 1)
    flags["2e34_monitor_only"] = True
    flags["2e34_50pct_crossed"] = bool(te["freeMinted"] >= te["FREE_MAX"] * 0.5)
n5 = reads.get("NEW5893", {})
if n5.get("freeMinted") is not None and n5.get("FREE_SUPPLY"):
    flags["NEW5893_pct"] = round(n5["freeMinted"] / n5["FREE_SUPPLY"] * 100, 1)
    flags["NEW5893_opened"] = bool(n5.get("saleOpen") == 1 or n5.get("mintOpen") == 1)
    flags["NEW5893_saleStart"] = n5.get("saleStart")
    flags["NEW5893_totalSupply"] = n5.get("totalSupply")
    flags["NEW5893_free_per_wallet"] = n5.get("FREE_PER_WALLET")
    flags["NEW5893_slot_user"] = n5.get("freeClaimed_user")
    flags["NEW5893_prelaunch"] = bool(n5.get("saleOpen") == 0 and n5.get("mintOpen") == 0 and n5.get("freeMinted") == 0)
hm = reads.get("HANAMI", {})
if hm.get("freeMinted") is not None:
    flags["HANAMI_freeMinted"] = hm["freeMinted"]
    flags["HANAMI_totalSupply"] = hm.get("totalSupply")
    if hm.get("totalSupply"):
        flags["HANAMI_pct_of_MAX3333"] = round(hm["freeMinted"] / 3333 * 100, 2)
    flags["HANAMI_mintOpen"] = hm.get("mintOpen")
    flags["HANAMI_delta_vs_1619_130"] = hm["freeMinted"] - 130
oc = reads.get("Ochre", {})
if oc.get("freeMinted") is not None and oc.get("FREE_SUPPLY"):
    flags["Ochre_pct"] = round(oc["freeMinted"] / oc["FREE_SUPPLY"] * 100, 1)
    flags["Ochre_opened"] = bool(oc.get("saleOpen") == 1 or oc.get("mintOpen") == 1 or oc.get("isFreeOpen") == 1)
    flags["Ochre_saleStart"] = oc.get("saleStart")
    flags["Ochre_totalSupply"] = oc.get("totalSupply")
    flags["Ochre_50pct_crossed"] = bool(oc["freeMinted"] >= oc["FREE_SUPPLY"] * 0.5)
    flags["Ochre_70pct_crossed"] = bool(oc["freeMinted"] > oc["FREE_SUPPLY"] * 0.7)
    flags["Ochre_soldout"] = bool(oc["freeMinted"] >= oc["FREE_SUPPLY"])
    flags["Ochre_slot_user"] = {"freeClaimed_user": oc.get("freeClaimed_user"),
                                "freeAvailable_user": oc.get("freeAvailable_user")}
    flags["Ochre_slot_open"] = bool(oc.get("freeClaimed_user") == 0 or oc.get("freeAvailable_user") == 1)
    flags["Ochre_strong_lead_legs"] = bool(flags["Ochre_70pct_crossed"] and flags["Ochre_slot_open"]
                                           and oc.get("saleStart") == 1794556267)
    flags["Ochre_sellout_already_reported_1519"] = True
for _k, _base in (("UNRES1", 3), ("UNRES2", 9)):
    _r = reads.get(_k, {})
    if _r.get("freeMinted") is not None:
        flags[_k + "_freeMinted"] = _r["freeMinted"]
        flags[_k + "_delta_vs_1614"] = _r["freeMinted"] - _base
        flags[_k + "_mintOpen"] = _r.get("mintOpen")
        flags[_k + "_totalSupply"] = _r.get("totalSupply")
flags["binanceai_opened"] = bool(reads.get("binanceai-mint", {}).get("launched") == 1)
flags["NOTV_opened"] = bool((reads.get("NOTV", {}).get("totalMinted") or 0) > 0)
flags["JNTM_opened"] = bool(reads.get("JNTM", {}).get("opened") == 1)
out["flags"] = flags

# --- Conditional Agentx gate re-check (method D only) if 70% crossed ---
if flags.get("Agentx_70pct_crossed"):
    recheck = {}
    for site in ("https://agentx.fun/", "https://agentx.pages.dev/", "https://agentx.vercel.app/"):
        body = curl(site, timeout=15)
        if body is None:
            recheck[site] = "fetch-failed"
        else:
            recheck[site] = {"bytes": len(body),
                             "prints_contract": AGENTX.lower() in body.lower()
                                                or AGENTX[2:].lower() in body.lower()}
    out["agentx_gate_recheck"] = recheck

# --- Update hot-leg-seen.json with newly seen contracts (only additions) ---
new_seen = {}
for a in feed_new:
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "sourcify-feed",
                   "status": st.get("status", "probe-not-run"),
                   "note": json.dumps(st.get("hits", []))[:400]}
for a in bb_new:
    code = codes.get(a, "unknown")
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "boltbook",
                   "status": "checked-not-contract" if code == "0x" else st.get("status", "probe-not-run"),
                   "note": f"eth_getCode={code}; probe_hits={json.dumps(st.get('hits', []))[:300]}"}
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = list(new_seen.keys())
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-13-1624.json", "w"), indent=1)
print(json.dumps(out, indent=1))
