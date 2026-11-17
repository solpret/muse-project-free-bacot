#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 07:19 WIB, continuation: persist the 12 Leg-1
shape results already obtained (script 0719.py was killed by the 120s
timeout before its dump), probe the 5 ABI-unavailable contracts on-chain
(concurrent, hard 40s deadline), then run the Boltbook leg. Reloads
hot-leg-seen.json fresh before dumping so the 4 entries another writer
landed at 00:22:32 UTC are preserved."""
import json, urllib.request, subprocess, re, time, sys
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0719"
NOW = "2026-11-06T07:19:00+07:00"

# Results already printed by hot-leg-2026-11-06-0719.py before the timeout.
RESULTS = [
 ("0x87541675aAe2B521794D0763fa7c726dDDAd00a9", "2026-11-06T00:21:51Z", "error:retry-exhausted", None),
 ("0x33835c33d1C5162C1360dCad283c449407c7d292", "2026-11-06T00:18:47Z", "error:retry-exhausted", None),
 ("0x2c5b581F48cEb78B83CB4894c0AE3697E40A3233", "2026-11-06T00:17:02Z", "error:retry-exhausted", None),
 ("0xCa8820D36BEC22E462a45B6F658d3f7BB2542a82", "2026-11-06T00:16:38Z", "verified",
  {"S1": False, "S2": False, "mint_fns": [], "quote_fns": ["quote"], "free_views": ["freeClaimed"], "gate_fns": ["agentIds", "isAgent"], "token_fns": ["name", "symbol"]}),
 ("0xBe82F0081D4b5B67F847Faac637Cbf6510Ef5aa9", "2026-11-06T00:16:38Z", "error:retry-exhausted", None),
 ("0x25b466A9fFf9292B863b2449fACd9dc570b07777", "2026-11-06T00:16:12Z", "verified",
  {"S1": False, "S2": False, "mint_fns": [], "quote_fns": [], "free_views": [], "gate_fns": [], "token_fns": ["decimals", "name", "symbol", "totalSupply"]}),
 ("0x91B718f705318Dd7D63e1375DA7219D029314353", "2026-11-06T00:15:01Z", "error:retry-exhausted", None),
 ("0x7F5e1352B8E9048056fe595014B41E35F879003c", "2026-11-06T00:14:17Z", "verified",
  {"S1": False, "S2": False, "mint_fns": ["mint", "mintedBy", "totalSpotsMinted"], "quote_fns": ["PRICE", "quote"], "free_views": [], "gate_fns": ["isAgent"], "token_fns": ["decimals", "name", "symbol", "totalSupply"]}),
 ("0x2A159cA2A3706dE0a8B223eE7b592700eDda16eA", "2026-11-06T00:13:43Z", "verified",
  {"S1": False, "S2": False, "mint_fns": [], "quote_fns": ["quoteOFT", "quoteSend"], "free_views": [], "gate_fns": [], "token_fns": ["decimals", "name", "symbol", "totalSupply"]}),
 ("0xC346967bCcE5f27889527a34ACf3546Ec56657d1", "2026-11-06T00:13:41Z", "verified",
  {"S1": False, "S2": False, "mint_fns": [], "quote_fns": [], "free_views": [], "gate_fns": [], "token_fns": []}),
 ("0xe22dda811DA88d02495C1dd755e7d4A1C4351e21", "2026-11-06T00:13:41Z", "error:retry-exhausted", None),
 ("0xbacBb9098590c9D812b28E7D894851af9785D04D", "2026-11-06T00:13:29Z", "verified",
  {"S1": False, "S2": False, "mint_fns": ["mint", "minted", "mintedBy", "totalMinted"], "quote_fns": ["PRICE", "quote"], "free_views": [], "gate_fns": [], "token_fns": ["name", "symbol", "totalSupply"]}),
]

# ---- Fast on-chain probe for the 5 ABI-unavailable contracts ----
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
DL = time.time() + 40
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
SIGS = ["mintFree()", "freeClaimed()", "freeMinted()", "FREE_SLOTS()", "FREE_SUPPLY()",
        "freeSharesRemaining()", "freeLeft()", "agentRegistry()", "freeClaimed(address)",
        "quote(address,uint256)", "freeAvailable()"]
def probe_one(addr):
    hits = []
    for s in SIGS:
        if time.time() > DL:
            return {"address": addr, "probe": "deadline", "hits": hits}
        data = sel(s)
        got = False
        for rpc in RPCS:
            if time.time() > DL:
                return {"address": addr, "probe": "deadline", "hits": hits}
            try:
                body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                   "params": [{"to": addr, "data": data}, "latest"]}).encode()
                req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=4) as r:
                    out = json.load(r)
                if "error" in out:
                    continue
                v = out.get("result")
                if v and v != "0x":
                    got = True
                break
            except Exception:
                continue
        if got:
            hits.append(s)
    return {"address": addr, "probe": "done", "hits": hits}

unavail = [r for r in RESULTS if r[2].startswith("error")]
probe = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for res in ex.map(probe_one, [r[0] for r in unavail]):
        probe[res["address"].lower()] = res
        print("PROBE", res["address"], res["probe"], "hits=", res["hits"], flush=True)
json.dump(probe, open(f"{BASE}/run-{TS}-probe.json", "w"), indent=1)

# ---- Persist all 12 into seen (fresh reload first) ----
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
shape_out = []
for addr, vat, status, cls in RESULTS:
    r = {"address": addr, "verifiedAt": vat, "sourcify": status}
    if cls:
        r.update(cls)
    else:
        r["S1"] = False; r["S2"] = False
        pr = probe.get(addr.lower(), {})
        r["probe"] = pr.get("probe"); r["probe_hits"] = pr.get("hits", [])
    shape_out.append(r)
    if addr.lower() in seen_l:
        print("SKIP already in seen:", addr, flush=True)
        continue
    if cls is None:
        pr = probe.get(addr.lower(), {})
        hits = pr.get("hits", [])
        if hits:
            seen[addr] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                          "status": "checked-not-sale-shape-probe",
                          "note": f"Sourcify verifiedAt {vat}. ABI fetch retry-exhausted; on-chain probe hits {hits} but S1/S2 not established (no full shape); NOT a lead, never previewed/minted."}
        elif pr.get("probe") == "deadline":
            seen[addr] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                          "status": "checked-abi-unavailable",
                          "note": f"Sourcify verifiedAt {vat}. ABI fetch retry-exhausted; on-chain probe hit RPC deadline (degraded) — no sale-shape evidence obtained; recorded, not a lead, never previewed/minted."}
        else:
            seen[addr] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                          "status": "checked-not-sale-shape-probe",
                          "note": f"Sourcify verifiedAt {vat}. ABI fetch retry-exhausted; on-chain probe: no sale-shape selector returns data. NOT a lead, never previewed/minted."}
    else:
        seen[addr] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                      "status": "checked-not-sale-shape",
                      "note": (f"Sourcify verifiedAt {vat}. S1={cls['S1']} S2={cls['S2']} "
                               f"mint={cls['mint_fns']} quote={cls['quote_fns']} free={cls['free_views']} "
                               f"agent={cls['gate_fns']} token={cls['token_fns']}")}
json.dump(shape_out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("SEEN total", len(seen), flush=True)

# ---- Leg 2: Boltbook via Lemmy API ----
try:
    req = urllib.request.Request(
        "https://boltbook.ai/api/v3/post/list?type_=All&sort=New&limit=50",
        headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=20) as r:
        bb = json.load(r)
    json.dump(bb, open(f"{BASE}/hot-leg-{TS}-boltbook-api.json", "w"), indent=1)
    posts = bb.get("posts", [])
    print("BOLTBOOK OK", len(posts), "newest",
          posts[0]["post"].get("published") if posts else None, flush=True)
    kws_en = ["free share", "first share free", "1 free share", "free mint share", "free mint"]
    kws_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
    hits = []
    addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
    addrs_found = set()
    for p in posts:
        post = p.get("post", {})
        text = ((post.get("name") or "") + " " + (post.get("body") or "")).lower()
        if any(k in text for k in kws_en + kws_zh):
            hits.append((post.get("id"), post.get("name"), post.get("ap_id")))
        for m in addr_re.findall(post.get("name", "") + " " + (post.get("body") or "")):
            addrs_found.add(m)
    print("BOLTBOOK keyword hits:", len(hits), hits, flush=True)
    print("BOLTBOOK addresses in 50 posts:", sorted(addrs_found), flush=True)
    for m in sorted(addrs_found):
        print("  addr in seen:", m.lower() in {k.lower() for k in seen}, m, flush=True)
except Exception as e:
    print("BOLTBOOK FAIL", repr(e), flush=True)
print("DONE", time.strftime("%H:%M:%S"), flush=True)
