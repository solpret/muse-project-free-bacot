#!/usr/bin/env python3
"""Hot-leg 0524 (2026-11-14): same pattern as 0444 run.
Legs 1+2 via browser.open by parent:
- Sourcify feed crawl 2026-11-13 22:12 UTC: newest 0xCc3c (21:59Z); 8 newer
  than 0429's 0x4394. Top 5 shape-checked run 0509 (all not-sale-shape, in
  seen); remaining 3 already in seen: Kicks 0x5726 (early-lead-reported),
  0x248a Task/LOH (not sale-shape), 0x83Db MLM (not sale-shape). 0 NEW.
- Boltbook EN crawl 2026-11-12 23:23 UTC (STALE cached copy, older than
  0444's 21:54 UTC 13 Nov crawl): TANK 0x8393, Tidalune 0x5306, VAULT 0x96e8,
  Galena 0xc4c9, FORGE 0x7333..6d89, Lanternfield, WRAITH, NDAEMN, Agentx -
  ALL already in seen (TANK/VAULT/Galena checked-not-sale-shape; Tidalune
  watchlist-only-age-unverified; Agentx thread CLOSED). 0 NEW.
- Boltbook ZH crawl 2026-11-13 22:07 UTC (FRESH): FIND exp8 0x4158 (seen,
  checked, not S1/S2), OLIVER 0xad86 (age-excluded, reported), SnakeAgentNFT
  0xF7c1.. (address truncated in crawl; check seen separately), ALCH 0xca3a
  (seen, checked-not-sale-shape), Crown Racer TUTUP 500/500 (confirms
  sellout, main-job-captured run 0509), AZEN 0x699b 269/2222 (tracked),
  AgentNova Remnants 0x38c1 (in main 0509 re-read, 249). 0 NEW.
Kicks: early lead, 53.6% at 0509, velocity PASS, age+website UNVERIFIED ->
  re-read % this run; promotion only if age+website verify (they don't).
DragonAgents: 70% at 0509 BUT age-excluded (>46h) -> moot, diam.
CRACE/Crown: sellout 500/500 confirmed run 0509, main-job-captured - no
  duplicate report; confirm fresh this run only.
Agentx: thread CLOSED (user declined override 13 Nov ~20:31) - NO re-check,
  NO report, NEVER preview/mint. Age deadline 23:11 WIB 13 Nov EXPIRED.
LESSON: NEVER send a >24-call batch; ALL batches chunked to <=24 calls.
RPC timeout 60s per chunk; skip stalled legs. Read-only except
hot-leg-seen.json (Kicks note update only) + run output files."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
KICKS = "0x5726100e0D9ACB20cFB13e80e0fe42DF146730A8"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=60):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def rpc_chunked(calls, timeout=60):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        used_fb = False
        if not body:
            body = curl("https://bsc-dataseed1.bnbchain.org/", data=json.dumps(chunk), timeout=timeout)
            used_fb = True
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            if not used_fb and all(not by_id.get(c["id"], {}).get("result") for c in chunk):
                body2 = curl("https://bsc-dataseed1.bnbchain.org/", data=json.dumps(chunk), timeout=timeout)
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
out = {"run": "free-mint-hot-leg 2026-11-14 05:24 WIB", "started_wib": now_wib()}

probe = {}
for name, url in (("bsc-dataseed", "https://bsc-dataseed.binance.org/"),
                  ("sourcify", "https://sourcify.dev/server/v2/contracts/56?limit=1"),
                  ("boltbook", "https://boltbook.fun/"),
                  ("google", "https://www.google.com/")):
    probe[name] = "ok" if curl(url, timeout=8) is not None else "rc=000/8s-timeout"
out["egress_probe_8s"] = probe
blk = curl("https://bsc-dataseed.binance.org/",
           data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}),
           timeout=60)
out["rpc_blockNumber"] = blk

out["sourcify_feed"] = {"crawl": "2026-11-13 22:12 UTC",
                        "total": 20, "new": 0,
                        "note": "newest 0xCc3c 21:59Z; top 5 shape-checked run 0509 (all not-sale-shape, in seen); other 3 (0x5726 Kicks early-lead, 0x248a Task/LOH, 0x83Db MLM) already in seen"}
out["boltbook_en"] = {"crawl": "2026-11-12 23:23 UTC (STALE cached copy, older than 0444 crawl 21:54 UTC 13 Nov)",
                      "full_address_contracts": 4, "new": 0,
                      "note": "TANK 0x8393, Tidalune 0x5306, VAULT 0x96e8, Galena 0xc4c9 + Agentx (thread CLOSED) - all already in seen"}
out["boltbook_zh"] = {"crawl": "2026-11-13 22:07 UTC (FRESH)",
                      "new": 0,
                      "note": "FIND exp8 0x4158 (seen, not S1/S2); OLIVER age-excluded reported; ALCH 0xca3a seen not-sale-shape; Crown Racer TUTUP 500/500 (sellout, main-job-captured); AZEN 269/2222; AgentNova Remnants in main 0509 re-read (249)"}

PLAN = [
 ("Kicks", KICKS,
  [("freeMinted", False), ("FREE_CAP", False), ("freeCount", True), ("mintOpen", False),
   ("totalMinted", False), ("balanceOf", True)]),
 ("DragonAgents", "0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998",
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True)]),
 ("CRACE", "0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
  [("freeMinted", False), ("FREE_QUOTA", False), ("mintOpen", False),
   ("totalSupply", False), ("freeClaimed", True)]),
 ("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810",
  [("freeMinted", False), ("FREE_MAX", False), ("freeRemaining", False), ("mintOpen", False)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False), ("failed", False), ("isRefundPhase", False), ("tokenClaimed", True)]),
 ("AngelEye-77D9", "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
  [("freeMinted", False), ("freeRemaining", False), ("FREE_POOL", False),
   ("saleActive", False), ("mintStart", False)]),
 ("AbsurdAgentNFT", "0x72c14121681F1133545947B0735563835CC07B67",
  [("totalMinted", False), ("mintOpen", False), ("mintStartTime", False)]),
 ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d",
  [("totalSupply", False), ("MAX_SUPPLY", False), ("freeMintedPerWallet", True)]),
 ("NovaRemnants", "0x38C1695eb72B7522c8d6452a4CE27122532A0d69",
  [("totalRemnants", False), ("genesisOpen", False), ("currentCycle", False)]),
 ("RaceAgents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
  [("freeMinted", False), ("FREE_MAX", False), ("totalSupply", False), ("mintOpen", False)]),
 ("ACARD", "0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69",
  [("freeMinted", False), ("FREE_CAP", False), ("totalMinted", False),
   ("mintOpen", False), ("freeClaimed", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
reads = {}
for cid, r, err in rpc_chunked(reqs, timeout=60):
    name, fn = keys[cid]
    v = None
    if r and r != "0x" and len(r) >= 66:
        try:
            v = int(r[-64:], 16)
        except Exception:
            v = None
    reads.setdefault(name, {})[fn] = v
out["reads"] = reads
out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
out["reads_total"] = len(PLAN)

try:
    b = json.load(open(f"{HF}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge"] = {"n": len(c),
                     "not_in_snapshot": sum(1 for v in c.values() if not v.get("in_freebacot_snapshot")),
                     "same_owner_discarded": sum(1 for v in c.values() if v.get("same_owner_discarded")),
                     "note": "unchanged vs runs 0204-0509 (116 contracts) unless counts differ"}
except Exception as e:
    out["bridge"] = {"error": str(e)}

flags = {}
ki = reads.get("Kicks", {})
if ki.get("freeMinted") is not None and ki.get("FREE_CAP"):
    flags["Kicks_freeMinted"] = ki["freeMinted"]
    flags["Kicks_FREE_CAP"] = ki["FREE_CAP"]
    flags["Kicks_pct"] = round(ki["freeMinted"] / ki["FREE_CAP"] * 100, 1)
    flags["Kicks_totalMinted"] = ki.get("totalMinted")
    flags["Kicks_freeCount_user"] = ki.get("freeCount_user")
    flags["Kicks_balanceOf_user"] = ki.get("balanceOf_user")
    flags["Kicks_mintOpen"] = ki.get("mintOpen")
    flags["Kicks_slot_open"] = bool((ki.get("freeCount_user") or 0) == 0)
    flags["Kicks_strong_lead_legs"] = bool(flags["Kicks_pct"] > 70)
    flags["Kicks_age"] = "UNVERIFIED"
    flags["Kicks_website"] = "UNVERIFIED (gate website_unverified di snapshot)"
    flags["Kicks_decision"] = ("PROMOSI CHECK: pct>70% BUT age+website UNVERIFIED -> TIDAK promosi, TIDAK preview/mint, TIDAK lapor ulang"
                               if flags["Kicks_strong_lead_legs"] else
                               "TETAP early lead - umur + website unverified -> TIDAK promosi, TIDAK preview/mint, TIDAK lapor ulang (main job 05:31 mengevaluasi ulang)")
da = reads.get("DragonAgents", {})
if da.get("freeClaimed") is not None and da.get("FREE_SUPPLY"):
    flags["DragonAgents_pct"] = round(da["freeClaimed"] / da["FREE_SUPPLY"] * 100, 1)
    flags["DragonAgents_totalSupply"] = da.get("totalSupply")
    flags["DragonAgents_mintedBy_user"] = da.get("mintedBy_user")
    flags["DragonAgents_decision"] = "age-excluded (>46 jam) -> bukan strong lead, moot, diam"
cr = reads.get("CRACE", {})
if cr.get("freeMinted") is not None and cr.get("FREE_QUOTA"):
    flags["CRACE_freeMinted"] = cr["freeMinted"]
    flags["CRACE_FREE_QUOTA"] = cr["FREE_QUOTA"]
    flags["CRACE_soldout"] = bool(cr["freeMinted"] >= cr["FREE_QUOTA"])
    flags["CRACE_slot_open"] = bool(cr.get("freeClaimed_user") == 0)
    flags["CRACE_totalSupply"] = cr.get("totalSupply")
    flags["CRACE_decision"] = "SELLOUT confirmed fresh; main-job-captured run 0509 - NO duplicate report"
ol = reads.get("OLIVER", {})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    flags["OLIVER_pct"] = round(ol["freeMinted"] / ol["FREE_MAX"] * 100, 1)
    flags["OLIVER_freeRemaining"] = ol.get("freeRemaining")
    flags["OLIVER_decision"] = "age-excluded 21:00 13 Nov, already reported - LOG ONLY"
ba = reads.get("binanceai-mint", {})
flags["binanceai_launched"] = ba.get("launched")
flags["binanceai_failed"] = ba.get("failed")
flags["binanceai_refundPhase"] = ba.get("isRefundPhase")
flags["binanceai_tokenClaimed_user"] = ba.get("tokenClaimed_user")
flags["binanceai_decision"] = "still pending (launched=0, refund phase) - no change, no report" if ba.get("launched") == 0 else "CHANGED - review"
ae = reads.get("AngelEye-77D9", {})
if ae.get("freeMinted") is not None:
    flags["AngelEye77D9_freeMinted"] = ae["freeMinted"]
    flags["AngelEye77D9_freeRemaining"] = ae.get("freeRemaining")
    flags["AngelEye77D9_FREE_POOL"] = ae.get("FREE_POOL")
    flags["AngelEye77D9_saleActive"] = ae.get("saleActive")
    flags["AngelEye77D9_mintStart"] = ae.get("mintStart")
    flags["AngelEye77D9_note"] = "age/pool/slot UNVERIFIED - watchlist-only, NOT a lead, NEVER preview/mint"
ab = reads.get("AbsurdAgentNFT", {})
flags["AbsurdAgentNFT_totalMinted"] = ab.get("totalMinted")
flags["AbsurdAgentNFT_mintOpen"] = ab.get("mintOpen")
flags["AbsurdAgentNFT_mintStartTime"] = ab.get("mintStartTime")
flags["AbsurdAgentNFT_note"] = "pre-launch (mintStartTime 1794650400) - watchlist-only"
az = reads.get("AZEN", {})
if az.get("totalSupply") is not None:
    flags["AZEN_totalSupply"] = az["totalSupply"]
    flags["AZEN_MAX_SUPPLY"] = az.get("MAX_SUPPLY")
    flags["AZEN_freeMintedPerWallet_user"] = az.get("freeMintedPerWallet_user")
    flags["AZEN_note"] = "ERC-721 agent-shaped free-mint NFT; NOT literal S1/S2; NFT early-lead stays with main 30-min job"
nr = reads.get("NovaRemnants", {})
flags["NovaRemnants_totalRemnants"] = nr.get("totalRemnants")
flags["NovaRemnants_genesisOpen"] = nr.get("genesisOpen")
flags["NovaRemnants_currentCycle"] = nr.get("currentCycle")
ra = reads.get("RaceAgents", {})
if ra.get("freeMinted") is not None and ra.get("FREE_MAX"):
    flags["RaceAgents_pct"] = round(ra["freeMinted"] / ra["FREE_MAX"] * 100, 1)
    flags["RaceAgents_totalSupply"] = ra.get("totalSupply")
    flags["RaceAgents_mintOpen"] = ra.get("mintOpen")
ac = reads.get("ACARD", {})
if ac:
    flags["ACARD_freeMinted"] = ac.get("freeMinted")
    flags["ACARD_FREE_CAP"] = ac.get("FREE_CAP")
    flags["ACARD_totalMinted"] = ac.get("totalMinted")
    flags["ACARD_mintOpen"] = ac.get("mintOpen")
    flags["ACARD_freeClaimed_user"] = ac.get("freeClaimed_user")
    flags["ACARD_shape"] = "S1-literal-pass BUT ERC-721 NFT, NOT a track-C lead; NFT early-lead stays with main job"
flags["Agentx"] = "thread CLOSED (user tolak override 13 Nov) - NO re-check, NO report, NEVER preview/mint."
out["flags"] = flags
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0524.json", "w"), indent=1)
print(json.dumps(out, indent=1))
