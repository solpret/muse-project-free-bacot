#!/usr/bin/env python3
"""Web legs run 2026-11-15 22:01 WIB. Read-only. No preview/mint. No twitterapi.io. No no_proxy."""
import json, re, subprocess
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

# ---- 1. Sourcify feed (raw already fetched by curl) ----
raw = json.load(open(BASE+"run-2026-11-15-2201-sourcify-raw.json"))
results = raw.get("results", [])
feed_addrs = [r["address"] for r in results]
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a.lower()!=REG.lower() and a.lower() not in {e.lower() for e in EXCLUDED}]
sourcify_out = {"run":"2026-11-15-2201","fetched_at_wib":"2026-11-15T22:01+07:00",
  "curl_rc":0,"total":len(results),
  "top_verifiedAt": results[0].get("verifiedAt") if results else None,
  "feed":[{"address":r["address"],"verifiedAt":r.get("verifiedAt")} for r in results],
  "new_vs_hotleg_seen": feed_new, "new_count": len(feed_new)}
json.dump(sourcify_out, open(BASE+"run-2026-11-15-2201-sourcify.json","w"), indent=1)
print("SOURCIFY total", len(results), "top", sourcify_out["top_verifiedAt"], "new", len(feed_new))
print("NEW:", feed_new)

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
shape_doc = {"run":"2026-11-15-2201","sourcify_feed_new":shape_out,
  "note":"contracts already in hot-leg-seen.json were shape-checked by hot leg; not re-checked here",
  "shape_hits":[s for s in shape_out if s.get("S1") or s.get("S2")]}
json.dump(shape_doc, open(BASE+"run-2026-11-15-2201-shape.json","w"), indent=1)
print("SHAPE:", json.dumps(shape_out))

# ---- 2. Boltbook EN + ZH (files already fetched by curl) ----
en_html = open(BASE+"run-2026-11-15-2201-boltbook-en.html").read()
zh_html = open(BASE+"run-2026-11-15-2201-boltbook-zh.html").read()
en_addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", en_html)))
zh_addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", zh_html)))
prev_en = open(BASE+"run-2026-11-15-2131-boltbook-en.html").read()
prev_zh = open(BASE+"run-2026-11-15-2131-boltbook-zh.html").read()
prev_addrs = set(re.findall(r"0x[0-9a-fA-F]{40}", prev_en)) | set(re.findall(r"0x[0-9a-fA-F]{40}", prev_zh))
cur_addrs = set(en_addrs) | set(zh_addrs)
new_bb = sorted(a for a in cur_addrs if a not in prev_addrs)
print("BOLTBOOK en", len(en_html), len(en_addrs), "zh", len(zh_html), len(zh_addrs))
print("BOLTBOOK addrs:", sorted(cur_addrs))
print("BOLTBOOK new vs 2131:", new_bb)
# per-address seen status
bb_detail = []
for a in sorted(cur_addrs):
    s = seen_l.get(a.lower())
    bb_detail.append({"address": a, "in_hotleg_seen": s is not None,
                      "seen_note": (s or {}).get("status") if s else None,
                      "first_seen_wib": (s or {}).get("first_seen_wib") if s else None})
# post titles: strip tags, look for post headings
def titles(html):
    txt = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S)
    txt = re.sub(r"<[^>]+>", "\n", txt)
    lines = [l.strip() for l in txt.splitlines() if len(l.strip()) > 3]
    return lines
en_titles = titles(en_html)
zh_titles = titles(zh_html)
print("EN text lines:", len(en_titles))
print("ZH text lines:", len(zh_titles))

# ---- VOLT site recheck (files already fetched) ----
volt = {}
volt_root = open(BASE+"run-2026-11-15-2201-volt-site.html").read()
volt_meta = open(BASE+"run-2026-11-15-2201-volt-metadata1.json").read()
volt["root"] = {"url":"https://volt-nft.pages.dev/","bytes":len(volt_root),
    "http":404,"contains_contract": VOLT.lower() in volt_root.lower()}
volt["metadata/1"] = {"url":"https://volt-nft.pages.dev/metadata/1","bytes":len(volt_meta),
    "http":200,"contains_contract": VOLT.lower() in volt_meta.lower(),
    "content": volt_meta}
print("VOLT root bytes", len(volt_root), "meta bytes", len(volt_meta), "meta has contract:", volt["metadata/1"]["contains_contract"])

json.dump({"boltbook":{"en_bytes":len(en_html),"en_addrs":en_addrs,
  "zh_bytes":len(zh_html),"zh_addrs":zh_addrs,
  "all_addrs":sorted(cur_addrs),"new_vs_2131":new_bb,"detail":bb_detail,
  "en_text_lines":en_titles[:80],"zh_text_lines":zh_titles[:80]},
  "volt_site": volt}, open(BASE+"run-2026-11-15-2201-boltbook-volt.json","w"), indent=1)
print("DONE")
