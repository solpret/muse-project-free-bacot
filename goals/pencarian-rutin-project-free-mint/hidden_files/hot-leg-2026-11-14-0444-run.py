#!/usr/bin/env python3
"""Hot-leg 0444 (2026-11-14): same pattern as 0309 run, adapted.
Egress: shell curl 8s probes FAIL (20th consecutive run) but RPC works with
long timeouts (eth_blockNumber 19.2s dataseed / 15.5s dataseed1 at ~04:50).
Main job 04:31 re-read OK (16 items, block 133425817): Crown freeMinted
500/500 FREE_QUOTA (SELLOUT, freeClaimed_user 0 - slot unused); AngelEye
77D9/07bD freeRemaining 2221/2222 saleActive 1; AbsurdAgentNFT totalMinted 0
mintOpen 0 mintStartTime 1794650400 (pre-launch); binanceai launched 0
failed 1 isRefundPhase 1 (refund phase, still pending); WoozCode, MORFO,
NOISE, DragonAgents, NovaRemnants, RaceAgents, B77D, Zero, PX24, SKRR, HIVE.
Sourcify feed via browser.open: crawl 2026-11-13 21:31 UTC, SAME as 0429
(newest 0x4394 BscPoker, 0x96f7 IntentChainer) - 0 new, all 20 in seen.
Boltbook EN via browser.open: crawl 2026-11-13 21:54 UTC (FRESH, ~22h newer
than 0429's 23:23 UTC 12 Nov) - 7 full addresses, ALL in seen: DRAGON
0xad0d (624/1888), ACARD 0xf1d5 (346/3456, 3110 free left per post),
BUBB 0x0d72 (1428, freeMinted 1287), OLIVER 0xad86 (993/1000, 7 left),
ONLYAI 0x1564 (2865/5555), NAPPER 0x3964 (663/5555), AZEN 0x699b (260/2222).
Boltbook ZH via browser.open: crawl 2026-11-13 21:33 UTC - SAME as 0429
(stale-identical). Posts already processed by 0429 (SPLAT new then).
AZEN ABI (main job 04:31 fetch): ERC-721, AGENT_ID + MAX_FREE_PER_WALLET +
TOKENS_PER_FREE_MINT + freeMintedPerWallet, mint(uint256) payable, NO quote
fn, NO listed free view -> NOT literal S1/S2; agent-shaped free-mint NFT,
left to main 30-min job (NFT early-lead is main job's, not hot-leg's).
SPARKS ABI (main job 04:31 fetch): ERC-721, AGENT_ID_REGISTRY, mint payable,
MINT_FEE + mintFeeFor, NO free views -> NOT S1/S2; left to main job.
ACARD ABI: fetched via browser this run (see out['acard_abi']).
NEB 0xf08a: seen 10 Nov S1 track-C; age >24h now, no action.
Agentx: thread CLOSED (user declined override 13 Nov ~20:31) - NO re-check,
NO report, NEVER preview/mint. Age deadline 23:11 WIB 13 Nov EXPIRED.
OLIVER: age-excluded 21:00 13 Nov, already reported - LOG ONLY (sellout watch).
CRACE: early lead reported run 2331; 03:09 466/500; main 04:31 500/500 =
SELLOUT. Confirm fresh this run; if confirmed, REPORT ONCE as change
(free quota sold out, user slot unused) + record in hot-leg-reported.json.
LESSON: NEVER send a >24-call batch; ALL batches chunked to <=24 calls.
RPC timeout 60s per chunk (egress slow but alive); skip stalled legs.
Read-only except hot-leg-seen.json (note updates only) + run output files
+ hot-leg-reported.json (only if CRACE sellout reported)."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
CRACE = "0x7B1ca439312368dE8652b9B5d7A54cA74A884680"

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
out = {"run": "free-mint-hot-leg 2026-11-14 04:44 WIB", "started_wib": now_wib()}

# Egress probe (8s, same as prior runs) + RPC liveness (60s)
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

# Leg 1+2 already done via browser.open by parent; recorded here from results.
out["sourcify_feed"] = {"crawl": "2026-11-13 21:31 UTC (same as run 0429)",
                        "total": 20, "new": 0,
                        "note": "newest 0x4394 BscPoker + 0x96f7 IntentChainer (both checked-not-sale-shape run 0429); all 20 already in hot-leg-seen.json"}
out["boltbook_en"] = {"crawl": "2026-11-13 21:54 UTC (FRESH)",
                      "full_address_contracts": 7, "new": 0,
                      "note": "DRAGON 0xad0d 624/1888; ACARD 0xf1d5 346/3456 (3110 free left per post); BUBB 0x0d72 1428 freeMinted 1287; OLIVER 0xad86 993/1000 (7 left); ONLYAI 0x1564 2865/5555; NAPPER 0x3964 663/5555; AZEN 0x699b 260/2222 - all already in hot-leg-seen.json"}
out["boltbook_zh"] = {"crawl": "2026-11-13 21:33 UTC (same as run 0429, stale-identical)",
                      "new": 0,
                      "note": "NEB 0xf08a (seen 10 Nov, S1 track-C, age >24h now); SPARKS 0xd52f (seen 13 Nov, probe-not-sale-shape); ONI 0x852f (seen, not-sale-shape); Agentx 802/1111 (thread closed, no action); Crown Racer 502/2222 (see CRACE flag); all already seen"}

# Leg 3/4: focused re-read (chunked <=24). ACARD probe set included.
PLAN = [
 ("CRACE", CRACE,
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
  [("MAX_FREE_PER_WALLET", False), ("TOKENS_PER_FREE_MINT", False), ("MAX_SUPPLY", False),
   ("totalSupply", False), ("freeMintedPerWallet", True), ("TOKEN_PRICE", False)]),
 ("ACARD", "0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69",
  [("freeMinted", False), ("FREE_CAP", False), ("mintOpen", False),
   ("mintOpensAt", False), ("price", False), ("totalMinted", False),
   ("nextTokenId", False), ("freeClaimed", True), ("holdsAgentId", True),
   ("agentIdRegistry", False)]),
 ("SPARKS", "0xd52fd117c4b47d03e4e16e778871f09faa5a024b",
  [("MINT_FEE", False), ("mintFeeFor", False), ("totalMinted", False),
   ("totalSupply", False), ("MAX_SUPPLY", False), ("mintedByWallet", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        if fn == "mintFeeFor":
            # mintFeeFor(address,uint256): user + 1
            data = sel("mintFeeFor(address,uint256)") + USER_PAD + format(1, "064x")
        else:
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

# Bridge leg (read-only)
try:
    b = json.load(open(f"{HF}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge"] = {"n": len(c),
                     "not_in_snapshot": sum(1 for v in c.values() if not v.get("in_freebacot_snapshot")),
                     "same_owner_discarded": sum(1 for v in c.values() if v.get("same_owner_discarded")),
                     "note": "unchanged vs runs 0204-0429 (116 contracts, 33 not in hot-leg seen, 7 same_owner_discarded) unless counts differ"}
except Exception as e:
    out["bridge"] = {"error": str(e)}

# Flags
flags = {}
cr = reads.get("CRACE", {})
if cr.get("freeMinted") is not None and cr.get("FREE_QUOTA"):
    flags["CRACE_pct"] = round(cr["freeMinted"] / cr["FREE_QUOTA"] * 100, 1)
    flags["CRACE_freeMinted"] = cr["freeMinted"]
    flags["CRACE_FREE_QUOTA"] = cr["FREE_QUOTA"]
    flags["CRACE_soldout"] = bool(cr["freeMinted"] >= cr["FREE_QUOTA"])
    flags["CRACE_slot_open"] = bool(cr.get("freeClaimed_user") == 0)
    flags["CRACE_mintOpen"] = cr.get("mintOpen")
    flags["CRACE_totalSupply"] = cr.get("totalSupply")
    flags["CRACE_age"] = "UNVERIFIED (first-mint bound ~23:19 WIB 13 Nov; launch resmi UNVERIFIED)"
    flags["CRACE_website"] = "UNVERIFIED"
    flags["CRACE_strong_lead_legs"] = False
    flags["CRACE_report_sellout"] = bool(flags["CRACE_soldout"])
ol = reads.get("OLIVER", {})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    flags["OLIVER_pct"] = round(ol["freeMinted"] / ol["FREE_MAX"] * 100, 1)
    flags["OLIVER_freeRemaining"] = ol.get("freeRemaining")
    flags["OLIVER_soldout"] = bool((ol.get("freeRemaining") or 1) == 0)
    flags["OLIVER_note"] = "age-excluded 21:00 13 Nov, already reported - LOG ONLY"
ba = reads.get("binanceai-mint", {})
flags["binanceai_opened"] = bool(ba.get("launched") == 1)
flags["binanceai_failed"] = ba.get("failed")
flags["binanceai_refundPhase"] = ba.get("isRefundPhase")
flags["binanceai_tokenClaimed_user"] = ba.get("tokenClaimed_user")
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
    flags["AZEN_MAX_FREE_PER_WALLET"] = az.get("MAX_FREE_PER_WALLET")
    flags["AZEN_TOKENS_PER_FREE_MINT"] = az.get("TOKENS_PER_FREE_MINT")
    flags["AZEN_freeMintedPerWallet_user"] = az.get("freeMintedPerWallet_user")
    flags["AZEN_TOKEN_PRICE"] = az.get("TOKEN_PRICE")
    flags["AZEN_note"] = "ERC-721 agent-shaped free-mint NFT (AGENT_ID + free lane); NOT literal S1/S2; NFT early-lead stays with main 30-min job"
ac = reads.get("ACARD", {})
if ac:
    hits = [k for k, v in ac.items() if v is not None]
    flags["ACARD_probe_hits"] = hits
    flags["ACARD_freeMinted"] = ac.get("freeMinted")
    flags["ACARD_FREE_CAP"] = ac.get("FREE_CAP")
    flags["ACARD_totalMinted"] = ac.get("totalMinted")
    flags["ACARD_mintOpen"] = ac.get("mintOpen")
    flags["ACARD_mintOpensAt"] = ac.get("mintOpensAt")
    flags["ACARD_price"] = ac.get("price")
    flags["ACARD_freeClaimed_user"] = ac.get("freeClaimed_user")
    flags["ACARD_holdsAgentId_user"] = ac.get("holdsAgentId_user")
    flags["ACARD_agentIdRegistry"] = ac.get("agentIdRegistry")
    flags["ACARD_shape"] = "S1-literal-pass BUT ERC-721 NFT (ownerOf/tokenURI), NOT a track-C lead; NFT early-lead stays with main job; Boltbook claims 346/3456 live"
sp = reads.get("SPARKS", {})
if sp.get("totalSupply") is not None:
    flags["SPARKS_totalSupply"] = sp["totalSupply"]
    flags["SPARKS_totalMinted"] = sp.get("totalMinted")
    flags["SPARKS_MAX_SUPPLY"] = sp.get("MAX_SUPPLY")
    flags["SPARKS_MINT_FEE"] = sp.get("MINT_FEE")
    flags["SPARKS_mintFeeFor_user_1"] = sp.get("mintFeeFor_user")
    flags["SPARKS_mintedByWallet_user"] = sp.get("mintedByWallet_user")
    flags["SPARKS_note"] = "ERC-721, no free views; first-mint-free claim UNVERIFIED on-chain (MINT_FEE/mintFeeFor decide); left to main job"
out["flags"] = flags
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0444.json", "w"), indent=1)
print(json.dumps(out, indent=1))
