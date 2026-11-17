#!/usr/bin/env python3
"""Web legs run 2026-11-15 21:31 WIB. Read-only. No preview/mint. No twitterapi.io. No no_proxy."""
import json, re, time, subprocess, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
              "freeMinted","freeCardsRemaining"]
VOLT = "0xa688e82567886a52bcc7344e8030c852da4866ed"

def curl(url, timeout=25, compressed=True):
    cmd = ["curl","-sL","--max-time",str(timeout),"-A","free-mint-search/1.0"]
    if compressed: cmd.append("--compressed")
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+10)
    return r.returncode, r.stdout, r.stderr

seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_l = {k.lower(): v for k,v in seen.items()}

# ---- 1. Sourcify feed ----
rc, body, err = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
feed = json.loads(body)
results = feed.get("results", [])
feed_addrs = [r["address"] for r in results]
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a.lower()!=REG.lower() and a not in EXCLUDED]
sourcify_out = {"run":"2026-11-15-2131","fetched_at_wib":"2026-11-15T21:31+07:00",
  "curl_rc":rc,"total":len(results),
  "top_verifiedAt": results[0].get("verifiedAt") if results else None,
  "feed":[{"address":r["address"],"verifiedAt":r.get("verifiedAt")} for r in results],
  "new_vs_hotleg_seen": feed_new, "new_count": len(feed_new)}
json.dump(sourcify_out, open(BASE+"run-2026-11-15-2131-sourcify.json","w"), indent=1)
print("SOURCIFY total", len(results), "top", sourcify_out["top_verifiedAt"], "new", len(feed_new), feed_new)

# ---- shape-check new contracts ----
def shape(addr):
    rc2, b2, e2 = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
    try:
        meta = json.loads(b2); abi = meta.get("abi", [])
    except Exception as ex:
        return {"address":addr,"error":f"parse: {ex}","status":"shape-check-failed"}
    fns = {}
    for e in abi:
        if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = (is_token and mintfree and bool(names & {"freeClaimed","freeMinted"})
          and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref)
    return {"address":addr,"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,
            "free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,
            "n_fns":len(names),"status":"checked",
            "verifiedAt": next((r.get("verifiedAt") for r in results if r["address"].lower()==addr.lower()), None)}
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    shape_out = list(ex.map(shape, feed_new))
shape_doc = {"run":"2026-11-15-2131","sourcify_feed_new":shape_out,
  "note":"contracts already in hot-leg-seen.json were shape-checked by hot leg; not re-checked here",
  "shape_hits":[s for s in shape_out if s.get("S1") or s.get("S2")]}
json.dump(shape_doc, open(BASE+"run-2026-11-15-2131-shape.json","w"), indent=1)
print("SHAPE", json.dumps(shape_out)[:1500])

# ---- 2. Boltbook EN + ZH ----
def boltbook(url, fname):
    rc3, html, e3 = curl(url, timeout=25)
    open(BASE+fname,"w").write(html)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    return len(html), addrs, rc3
en_bytes, en_addrs, en_rc = boltbook("https://boltbook.fun/","run-2026-11-15-2131-boltbook-en.html")
zh_bytes, zh_addrs, zh_rc = boltbook("https://boltbook.fun/?lang=zh","run-2026-11-15-2131-boltbook-zh.html")
prev_en = open(BASE+"run-2026-11-15-2101-boltbook-en.html").read()
prev_zh = open(BASE+"run-2026-11-15-2101-boltbook-zh.html").read()
prev_addrs = set(re.findall(r"0x[0-9a-fA-F]{40}", prev_en)) | set(re.findall(r"0x[0-9a-fA-F]{40}", prev_zh))
cur_addrs = set(en_addrs) | set(zh_addrs)
new_bb = sorted(a for a in cur_addrs if a not in prev_addrs)
print("BOLTBOOK en", en_bytes, en_rc, len(en_addrs), "zh", zh_bytes, zh_rc, len(zh_addrs))
print("BOLTBOOK addrs:", sorted(cur_addrs))
print("BOLTBOOK new vs 2101:", new_bb)

# ---- 5. VOLT site recheck ----
volt = {}
for path in ["", "metadata/1"]:
    url = "https://volt-nft.pages.dev/" + path
    rc4, b4, e4 = curl(url, timeout=20)
    volt[path or "root"] = {"url":url,"curl_rc":rc4,"bytes":len(b4),
        "contains_contract": VOLT.lower() in b4.lower() or VOLT in b4,
        "snippet": b4[:300]}
    print("VOLT", url, "rc", rc4, "bytes", len(b4), "has_contract", volt[path or "root"]["contains_contract"])
json.dump({"boltbook":{"en_bytes":en_bytes,"en_rc":en_rc,"en_addrs":en_addrs,
  "zh_bytes":zh_bytes,"zh_rc":zh_rc,"zh_addrs":zh_addrs,
  "all_addrs":sorted(cur_addrs),"new_vs_2101":new_bb},
  "volt_site": volt}, open(BASE+"run-2026-11-15-2131-boltbook-volt.json","w"), indent=1)
