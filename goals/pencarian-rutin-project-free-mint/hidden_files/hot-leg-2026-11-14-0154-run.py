#!/usr/bin/env python3
# NOTE 0154: 0149 full run KILLED by 280s timeout (EXIT=124, no output);
# 0149 SALVAGE (started 01:58, 41.7s, reads_ok 11/11 in 1 batch): feed n=0;
# Boltbook EN+ZH both fetch-failed; Agentx 794 FLAT, OBFG 723 FLAT, Zero 315 FLAT,
# 2e34 922 FLAT, NEW5893 90 FLAT, VIOLET 133 (+1 vs 0144), OLIVER 985/15 FLAT,
# Pickgrid 216 FLAT, binanceai launched=0, NOTV 0, JNTM opened=0.
# 0144 full run OK (135.9s, reads_ok 24/25; feed n=0; Boltbook EN fetch-failed,
# ZH 42062 bytes, 10 addrs, no new). Mossbound 325/325 SOLD OUT (reported 0144),
# Ochre 210/210 SOLD OUT (reported 1519), JNTM SOLD OUT 1000/1000,
# GoldVein SOLD OUT 500/500 (reported main job 2201), Cinder SOLD OUT 325/325
# (reported once #sellout-20261114-0029). Main job run 0101 note: 0 kandidat baru,
# 0 strong lead baru, 0 early lead baru; Crown Racer 451/500 = 90.2% tapi umur
# UNVERIFIED -> bukan strong lead; binanceai pending TIDAK BERUBAH (refund phase);
# scan leg fast-fail; feed 1 baru 0x912D bukan agent-shaped.
# Terminal items trimmed to key views this run to cut call count (timeout lesson).
"""Hot-leg 0154 (2026-11-14): same pattern as 0149 run. Baselines from 0149
salvage (feed n=0; Boltbook EN+ZH fetch-failed; reads_ok 11; elapsed 41.7s)
and 0144 full run for the rest.
Sourcify feed poll + Boltbook EN/ZH + chunked on-chain selector PROBE
shape-check for new contracts + chunked direct JSON-RPC re-read (bsc-dataseed
primary, defibit fallback) of priority watchlist/track-C + pending binanceai claim.
Baselines (0149 salvage where read OK, else 0144):
Agentx 794/1111 71.5% - CROSSED 70%, legs met but gate website_failed
+ user declined override 13 Nov ~20:31 (thread closed: NO re-check, NO report,
NEVER preview/mint); age deadline 23:11 WIB 13 Nov EXPIRED - AGE-EXCLUDED, log only.
OBFG 723/1230 58.8%; age ~29.8h, AGE-EXCLUDED reported 12 Nov 20:02 - 70pct=861, log only.
Zero 315/500 63.0% (flat), OLIVER freeRemaining 15 (985/1000 98.5%);
AGE-EXCLUDED reported 21:00 (age >24h). RESUME/BC1B freeCount 470/3000 15.7% (0144),
Pickgrid 216 FLAT (0149 salvage), MECHA freeClaimed 1984, JNTM freeLeft 0 paidMinted 212 (SOLD OUT 1000/1000),
NOTV totalMinted 0 (freeStart 1794567600 = 18:00 WIB 13 Nov), AgentMuse freeClaimed 457/888,
binanceai launched()=0 (refund phase, still pending), 2e34 922/1000 92.2% (FLAT),
NEW5893 90/480 18.8% (0149 salvage, totalSupply 91), Mossbound Key SOLD OUT 325/325 - REPORTED 0144, no further action.
Slate Insignia NEW5893 OPENED 15:50:57 WIB - freeMinted 90/480 (18.8%). HANAMI 130 FLAT, UNRES1 129, UNRES2 79 FLAT, GoldVein SOLD OUT 500/500 (already reported),
Cinder SOLD OUT 325/325 (reported once #sellout-20261114-0029), binanceai NOT opened, NOTV NOT opened, JNTM NOT opened.
Crown Racer Cards CRACE 0x7B1ca439312368dE8652b9B5d7A54cA74A884680: early lead reported run 2331; main job run 0101: freeMinted 451/500 = 90.2%, slot user OPEN (freeClaimed=0), mintOpen=1, BUT age UNVERIFIED (first-mint bound ~23:19 WIB 13 Nov; launch resmi UNVERIFIED) + website UNVERIFIED -> NOT a strong lead, NEVER preview/mint. Re-read this run for sellout/promotion detection only.
Ochre Medallion 0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D:
strong-lead legs MET at 1509 (165/210 78.6%) but GATE FAILED - reported once;
SELLOUT 210/210 at 1519 REPORTED ONCE - terminal, no re-report.
GoldVein track-C (S2, sale/token 0xB5Bb50828eB449e7b27AaAd8F7e0CFc621347CB8,
SELLOUT 500/500 at 2314; sellout ALREADY reported once by main job run 2201
(cross-job dedupe) - terminal, no re-report; sale opened 19:00 WIB 13 Nov).
Cinder Crucible track-C lead (0x73f1A09e49cA70F8ac6a2F8673Bf7f0f69219b23):
SOLD OUT 325/325 at 0029, REPORTED ONCE (#sellout-20261114-0029) - terminal, no
re-report. Re-read this run only to confirm terminal state; NEVER preview/mint.
Agentx gate website_failed (reported once 08:29 as 50pct-crossed+gate-blocked);
age deadline 23:11 WIB 13 Nov EXPIRED during 2314 run - AGE-EXCLUDED, thread
closed: NO gate re-check, NO report, NEVER preview/mint (user declined
override outright 13 Nov ~20:31). OLIVER age UNVERIFIED + slot user unreadable -> reported
2026-11-12 14:14 as change-70pct-crossed, NOT a strong lead, never preview/mint;
age-excluded 21:00; watch for sellout (freeRemaining 15 at 0149) - LOG ONLY
(age-excluded = out of active monitoring, already reported once). Zero 62.8%,
velocity failed + website unverified -> NOT a candidate, monitor only. Pickgrid
cap disputed (FREE_CAP 300 vs 555 claim) -> 72% not trusted as strong lead.
AAdd (0xa78F525F...) S1-plausible but
pool/slot/age/website UNVERIFIED (followup 2314) - NOT leads, NOT reported,
left for main 30-min job.
LESSON: NEVER send a >24-call batch; ALL batches chunked to <=24 calls.
Terminal sold-out items trimmed to key views this run (timeout lesson).
Read-only except hot-leg-seen.json (new contracts only) and run output files.
Strict timeouts; skip stalled legs, never wait."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
AGENTX = "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"
OCHRE = "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
GOLDVEIN = "0xB5Bb50828eB449e7b27AaAd8F7e0CFc621347CB8"
CINDER = "0x73f1A09e49cA70F8ac6a2F8673Bf7f0f69219b23"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=15):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def rpc_chunked(calls, timeout=20):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        used_fallback = False
        if not body:
            body = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(chunk), timeout=timeout)
            used_fallback = True
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            # 0134: if the whole chunk came back null/error, retry once on the
            # fallback endpoint before giving up (0124 lost 20/25 reads this way).
            if not used_fallback and all(not by_id.get(c["id"], {}).get("result") for c in chunk):
                body2 = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(chunk), timeout=timeout)
                if body2:
                    try:
                        resp2 = json.loads(body2)
                        items2 = resp2 if isinstance(resp2, list) else [resp2]
                        by_id2 = {it.get("id"): it for it in items2 if isinstance(it, dict)}
                        if any(by_id2.get(c["id"], {}).get("result") for c in chunk):
                            by_id = by_id2
                    except Exception:
                        pass
            for c in chunk:
                it = by_id.get(c["id"], {})
                out.append((c["id"], it.get("result"), it.get("error")))
        except Exception as e:
            out += [(c["id"], None, f"parse-failed: {e}") for c in chunk]
    return out

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-14 01:54 WIB", "started_wib": now_wib()}

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

# --- Leg 1: Sourcify feed ---
feed_new = []
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
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
    body = curl(url, timeout=15)
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
         "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}
FROST = "0x18fdbee7fdd021688057d452e1ddb58f71fb5ea0"
probe_targets = ([FROST] + feed_new + bb_new)[:12]
probe_calls, probe_keys = [], []
for a in probe_targets:
    for fn in PROBE:
        probe_calls.append({"jsonrpc": "2.0", "id": len(probe_calls),
                            "method": "eth_call",
                            "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        probe_keys.append((a, fn))
probe_hits = {}
if probe_calls:
    for cid, r, err in rpc_chunked(probe_calls, timeout=20):
        if r and isinstance(r, str) and len(r) >= 66 and not err:
            a, fn = probe_keys[cid]
            probe_hits.setdefault(a, []).append(fn)
probe_status = {}
for a in probe_targets:
    hits = probe_hits.get(a, [])
    free_hit = any(h in FREE_SET for h in hits)
    agent_hit = any(h in ("agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY") for h in hits)
    sale_hit = any(h in ("saleOpen", "mintOpen") for h in hits)
    possible = bool(free_hit and (agent_hit or sale_hit))
    probe_status[a] = {"hits": hits, "free_hit": free_hit, "agent_hit": agent_hit,
                       "sale_hit": sale_hit,
                       "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
# --- Sourcify ABI shape-check for probe-possible-sale new contracts ---
abi_shape = {}
for a in probe_targets:
    if probe_status.get(a, {}).get("status") == "probe-possible-sale":
        try:
            mj = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", timeout=15) or "{}")
            abi = mj.get("abi") or []
            fns = [f.get("name") for f in abi if f.get("type") == "function"]
            has_mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "claim"))
            has_quote = any(n in fns for n in ("quote", "price", "cost", "getQuote"))
            free_views = [n for n in fns if n in ("freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft", "freeAvailable", "freeFor", "freeUsed", "freeSharePoolExhausted", "freeSharesClaimed")]
            agent = any(n in fns for n in ("agentIdRegistry", "agentRegistry", "AGENT_ID_REGISTRY")) or "AgentGate" in json.dumps(abi)
            token = all(n in fns for n in ("name", "symbol", "decimals", "totalSupply"))
            abi_shape[a] = {"fns": len(fns), "mint": has_mint, "quote": has_quote,
                            "free_views": free_views, "agent": agent, "token_on_same": token,
                            "S1": bool(has_mint and has_quote and free_views and agent),
                            "S2": bool(token and "mintFree" in fns and free_views and agent)}
        except Exception as e:
            abi_shape[a] = {"error": str(e)[:120]}
out["abi_shape"] = abi_shape
out["probe"] = probe_status
out["probe_capped"] = len(feed_new + bb_new) - len(probe_targets)

# --- Leg 3/4: chunked re-read (known-good views) + eth_getCode for bb_new ---
PLAN = [
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("freeAvailable", True)]),
 ("Mossbound", "0xe589A94316C68d4A4f008f841Deb7e9612445244",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("freeAvailable", True)]),
 ("Ochre", OCHRE,
  [("freeMinted", False), ("FREE_SUPPLY", False), ("freeAvailable", True)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("freeClaimed", False), ("FREE_LOTS_CAP", False), ("opened", False), ("freeLeft", False)]),
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
 ("VIOLET", "0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("isFreeOpen", False), ("saleStart", False), ("totalSupply", False),
   ("FREE_PER_WALLET", False), ("freeClaimed", True), ("freeAvailable", True)]),
 ("Frost", FROST,
  [("freeMinted", False), ("FREE_SUPPLY", False), ("FREE_CAP", False), ("totalSupply", False),
   ("mintOpen", False), ("saleOpen", False), ("freeClaimed", True), ("freeAvailable", True)]),
 ("MossSignal", "0xb2e5d82900b854d3cb8c6bb917426abadb687f68",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("FREE_CAP", False), ("totalSupply", False),
   ("mintOpen", False), ("saleOpen", False), ("freeClaimed", True), ("freeAvailable", True)]),
 ("BUBB", "0x0d72970046c056db90888351b739246f468bff0b",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("FREE_CAP", False), ("totalSupply", False),
   ("mintOpen", False), ("saleOpen", False), ("freeClaimed", True), ("freeAvailable", True),
   ("paidMinted", False)]),
 ("AgentCosmos", "0x3aeda314ec05bc22e3c26a543e16df2b8cc8fe69",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("totalSupply", False), ("mintOpen", False),
   ("freeClaimed", True)]),
 ("HANAMI", "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
  [("freeMinted", False), ("totalSupply", False), ("mintOpen", False)]),
 ("UNRES1", "0x6430594F2C40A4374f2EfEdF034C77065DC4CC7D",
  [("freeMinted", False), ("totalSupply", False), ("mintOpen", False)]),
 ("UNRES2", "0xEa98b2065d43c0DE0Ad8629F5D0A08fDABcc708A",
  [("freeMinted", False), ("totalSupply", False), ("mintOpen", False)]),
 ("GoldVein", GOLDVEIN,
  [("freeSold", False), ("FREE_SHARES", False), ("freeClaimed", True)]),
 ("Cinder", CINDER,
  [("freeMinted", False), ("FREE_SUPPLY", False), ("freeRemaining", False),
   ("freeAvailable", True)]),
 ("CRACE", "0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
  [("freeMinted", False), ("FREE_QUOTA", False), ("mintOpen", False),
   ("totalSupply", False), ("freeClaimed", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
code_keys = []
for a in ["0x5d051572cf9814f613d25d162e914b3c7e2bad05"]:
    reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_getCode",
                 "params": [a, "latest"]})
    code_keys.append(a)
for a in bb_new:
    reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_getCode",
                 "params": [a, "latest"]})
    code_keys.append(a)
reads, codes = {}, {}
for cid, r, err in rpc_chunked(reqs, timeout=20):
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

# --- Derived change flags vs 0144 hot-leg run ---
flags = {}
ax = reads.get("Agentx", {})
if ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    pct = ax["freeMinted"] / ax["FREE_CAP"] * 100
    flags["Agentx_pct"] = round(pct, 1)
    flags["Agentx_delta_vs_0149_794"] = ax["freeMinted"] - 794
    flags["Agentx_70pct_crossed"] = bool(pct > 70)
    flags["Agentx_strong_lead_legs"] = bool(pct > 70 and ax.get("freeClaimed_user") == 0
                                            and ax.get("mintOpen") == 1)
    flags["Agentx_gate"] = "website_failed (reported 08:29; user declined override 13 Nov ~20:31 - NO re-check, NO report, NEVER preview/mint)"
    flags["Agentx_age_deadline_wib"] = "23:11 WIB 13 Nov (EXPIRED - age-excluded)"
ob = reads.get("OBFG", {})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    flags["OBFG_pct"] = round(ob["freeMinted"] / ob["FREE_SUPPLY"] * 100, 1)
    flags["OBFG_delta_vs_0149_723"] = ob["freeMinted"] - 723
    flags["OBFG_soldout"] = bool(ob["freeMinted"] >= ob["FREE_SUPPLY"])
    flags["OBFG_slot_lost"] = bool(ob.get("freeAvailable_user") == 0)
    flags["OBFG_70pct_crossed"] = bool(ob["freeMinted"] > ob["FREE_SUPPLY"] * 0.7)
    flags["OBFG_age_h"] = round((time.time() - 1794488476) / 3600, 1)
    flags["OBFG_strong_lead_legs"] = bool(flags["OBFG_70pct_crossed"] and not flags["OBFG_slot_lost"]
                                          and flags["OBFG_age_h"] < 24)
    flags["OBFG_gate"] = "website_failed (reported once 12 Nov ~20:10 as gate-blocked lead; re-check only if 70pct crossed)"
mb = reads.get("Mossbound", {})
if mb.get("freeMinted") is not None and mb.get("FREE_SUPPLY"):
    flags["Mossbound_pct"] = round(mb["freeMinted"] / mb["FREE_SUPPLY"] * 100, 1)
    flags["Mossbound_soldout"] = bool(mb["freeMinted"] >= mb["FREE_SUPPLY"])
ze = reads.get("Zero", {})
if ze.get("freeMinted") is not None and ze.get("FREE_CAP"):
    flags["Zero_pct"] = round(ze["freeMinted"] / ze["FREE_CAP"] * 100, 1)
    flags["Zero_delta_vs_0149_315"] = ze["freeMinted"] - 315
    flags["Zero_50pct_crossed"] = bool(ze["freeMinted"] >= ze["FREE_CAP"] * 0.5)
    flags["Zero_slot_open"] = bool(ze.get("freeClaimed_user") == 0)
ol = reads.get("OLIVER", {})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    flags["OLIVER_pct"] = round(ol["freeMinted"] / ol["FREE_MAX"] * 100, 1)
    flags["OLIVER_delta_vs_0149_freeRemaining15"] = (ol.get("freeRemaining") or 0) - 15
    flags["OLIVER_freeRemaining"] = ol.get("freeRemaining")
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
    flags["2e34_delta_vs_0149_922"] = te["freeMinted"] - 922
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
vl = reads.get("VIOLET", {})
if vl.get("freeMinted") is not None and vl.get("FREE_SUPPLY"):
    flags["VIOLET_pct"] = round(vl["freeMinted"] / vl["FREE_SUPPLY"] * 100, 1)
    flags["VIOLET_opened"] = bool(vl.get("saleOpen") == 1 or vl.get("mintOpen") == 1 or vl.get("isFreeOpen") == 1)
    flags["VIOLET_saleStart"] = vl.get("saleStart")
    flags["VIOLET_totalSupply"] = vl.get("totalSupply")
    flags["VIOLET_free_per_wallet"] = vl.get("FREE_PER_WALLET")
    flags["VIOLET_slot_user"] = {"freeClaimed_user": vl.get("freeClaimed_user"),
                                 "freeAvailable_user": vl.get("freeAvailable_user")}
    flags["VIOLET_prelaunch"] = bool(vl.get("saleOpen") == 0 and vl.get("mintOpen") == 0 and vl.get("freeMinted") == 0)
for _nm in ("Frost", "MossSignal", "BUBB", "AgentCosmos"):
    _r = reads.get(_nm, {})
    if _r.get("freeMinted") is not None:
        flags[_nm + "_freeMinted"] = _r["freeMinted"]
        flags[_nm + "_totalSupply"] = _r.get("totalSupply")
        flags[_nm + "_mintOpen"] = _r.get("mintOpen")
        flags[_nm + "_saleOpen"] = _r.get("saleOpen")
        flags[_nm + "_slot_user"] = {"freeClaimed_user": _r.get("freeClaimed_user"),
                                     "freeAvailable_user": _r.get("freeAvailable_user")}
        for _cap in ("FREE_SUPPLY", "FREE_CAP"):
            if _r.get(_cap):
                flags[_nm + "_pct_" + _cap] = round(_r["freeMinted"] / _r[_cap] * 100, 1)
hm = reads.get("HANAMI", {})
if hm.get("freeMinted") is not None:
    flags["HANAMI_freeMinted"] = hm["freeMinted"]
    flags["HANAMI_totalSupply"] = hm.get("totalSupply")
    if hm.get("totalSupply"):
        flags["HANAMI_pct_of_MAX3333"] = round(hm["freeMinted"] / 3333 * 100, 2)
    flags["HANAMI_mintOpen"] = hm.get("mintOpen")
    flags["HANAMI_delta_vs_0144_130"] = hm["freeMinted"] - 130
oc = reads.get("Ochre", {})
if oc.get("freeMinted") is not None and oc.get("FREE_SUPPLY"):
    flags["Ochre_pct"] = round(oc["freeMinted"] / oc["FREE_SUPPLY"] * 100, 1)
    flags["Ochre_soldout"] = bool(oc["freeMinted"] >= oc["FREE_SUPPLY"])
for _k, _base in (("UNRES1", 129), ("UNRES2", 79)):
    _r = reads.get(_k, {})
    if _r.get("freeMinted") is not None:
        flags[_k + "_freeMinted"] = _r["freeMinted"]
        flags[_k + "_delta_vs_0114"] = _r["freeMinted"] - _base
        flags[_k + "_mintOpen"] = _r.get("mintOpen")
        flags[_k + "_totalSupply"] = _r.get("totalSupply")
gv = reads.get("GoldVein", {})
if gv.get("freeSold") is not None and gv.get("FREE_SHARES"):
    flags["GoldVein_pct"] = round(gv["freeSold"] / gv["FREE_SHARES"] * 100, 1)
    flags["GoldVein_freeSold"] = gv["freeSold"]
    flags["GoldVein_delta_vs_0144_500"] = gv["freeSold"] - 500
    flags["GoldVein_soldout"] = bool(gv["freeSold"] >= gv["FREE_SHARES"])
    flags["GoldVein_pool_left"] = gv["FREE_SHARES"] - gv["freeSold"]
    flags["GoldVein_slot_user"] = gv.get("freeClaimed_user")
    flags["GoldVein_paidSold"] = gv.get("paidSold")
    flags["GoldVein_report_sellout"] = False  # sellout ALREADY reported once by main job run 2201 - cross-job dedupe, NEVER re-report
cd = reads.get("Cinder", {})
if cd.get("freeMinted") is not None and cd.get("FREE_SUPPLY"):
    flags["Cinder_pct"] = round(cd["freeMinted"] / cd["FREE_SUPPLY"] * 100, 1)
    flags["Cinder_delta_vs_0029_325"] = cd["freeMinted"] - 325
    flags["Cinder_70pct_crossed"] = bool(cd["freeMinted"] > cd["FREE_SUPPLY"] * 0.7)
    flags["Cinder_opened"] = bool(cd.get("saleOpen") == 1 or cd.get("mintOpen") == 1 or cd.get("isFreeOpen") == 1)
    flags["Cinder_saleStart"] = cd.get("saleStart")
    flags["Cinder_freeRemaining"] = cd.get("freeRemaining")
    flags["Cinder_totalMinted"] = cd.get("totalMinted")
    flags["Cinder_slot_user"] = cd.get("freeAvailable_user")
    flags["Cinder_age_h"] = round((time.time() - 1794567061) / 3600, 1) if cd.get("saleStart") == 1794567061 else None  # saleStart 1794567061 = ~17:51 WIB 13 Nov
    flags["Cinder_strong_lead_legs"] = bool(flags["Cinder_70pct_crossed"] and cd.get("freeAvailable_user") == 1
                                            and flags["Cinder_age_h"] is not None and flags["Cinder_age_h"] < 24)
    flags["Cinder_gate"] = "website_failed (reported run 1801 as track-C lead gate-blocked; report once if legs met)"
cr = reads.get("CRACE", {})
if cr.get("freeMinted") is not None and cr.get("FREE_QUOTA"):
    flags["CRACE_pct"] = round(cr["freeMinted"] / cr["FREE_QUOTA"] * 100, 1)
    flags["CRACE_delta_vs_0101_451"] = cr["freeMinted"] - 451
    flags["CRACE_soldout"] = bool(cr["freeMinted"] >= cr["FREE_QUOTA"])
    flags["CRACE_slot_open"] = bool(cr.get("freeClaimed_user") == 0)
    flags["CRACE_mintOpen"] = cr.get("mintOpen")
    flags["CRACE_totalSupply"] = cr.get("totalSupply")
    flags["CRACE_70pct_crossed"] = bool(cr["freeMinted"] > cr["FREE_QUOTA"] * 0.7)
    flags["CRACE_age"] = "UNVERIFIED (first-mint bound ~23:19 WIB 13 Nov; launch resmi UNVERIFIED)"
    flags["CRACE_website"] = "UNVERIFIED"
    flags["CRACE_strong_lead_legs"] = False  # age + website unverified -> never a strong lead
    flags["CRACE_report_sellout"] = bool(flags["CRACE_soldout"])  # report once if sold out
flags["binanceai_opened"] = bool(reads.get("binanceai-mint", {}).get("launched") == 1)
flags["NOTV_opened"] = bool((reads.get("NOTV", {}).get("totalMinted") or 0) > 0)
flags["JNTM_opened"] = bool(reads.get("JNTM", {}).get("opened") == 1)
out["flags"] = flags

# --- Conditional Agentx gate re-check: DISABLED this run ---
# User declined the Agentx override outright 13 Nov ~20:31 WIB ("biarkan saja") -
# thread closed, must not be re-offered. If 70% crossed, record in flags only,
# NO gate re-check, NO chat report, NEVER preview/mint.
if flags.get("Agentx_70pct_crossed"):
    out["agentx_gate_recheck"] = "skipped - user declined override 13 Nov ~20:31, thread closed"

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
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0154.json", "w"), indent=1)
print(json.dumps(out, indent=1))
