#!/usr/bin/env python3
"""Hot-leg 2026-11-20 09:09 leg-4 retry #3 (chunked curl batch): root cause found
- a single 43-call batch hits bsc-dataseed rate limit (-32005, one-element
error list, id null), which the batch parsers turned into all-None.
Fix: chunk into <=10 calls per batch, retry a rate-limited chunk once after 3s.
Updates hot-leg-run-2026-11-20-0909-reread.json + run JSON threshold/diff."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0909"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
UA = enc_addr(USER)[2:]
def iv(val):
    try: return int(val,16) if val else None
    except Exception: return None
def num(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else None

ITEMS = None  # built below from retry2 source
_src = open(BASE+"hot-leg-2026-11-20-0909-leg4-retry2.py").read()
_items_src = _src.split("ITEMS = [",1)[1].split("\n]\n",1)[0]
ITEMS = eval("[" + _items_src + "\n]")
calls, keys = [], []
for name, addr, views in ITEMS:
    for vk, sig, argt in views:
        data = sel(sig)
        if argt == "addr": data += UA
        elif argt == "addr_uint1": data += UA + enc_uint(1)[2:]
        elif argt == "uint4": data += enc_uint(4)[2:]
        elif argt == "addr_uint4": data += UA + enc_uint(4)[2:]
        calls.append({"to": addr, "data": data})
        keys.append((name, vk))

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/")
def curl_chunk(chunk, base_id):
    payload = [{"jsonrpc":"2.0","id":base_id+i,"method":"eth_call",
                "params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(chunk)]
    for ep in EPS:
        p = subprocess.run(["curl","-s","--max-time","25","-H","Content-Type: application/json",
            "-d", json.dumps(payload), ep], capture_output=True, text=True)
        try:
            resp = json.loads(p.stdout)
        except Exception:
            continue
        if isinstance(resp, list) and len(resp) == len(chunk):
            by_id = {r.get("id"): r for r in resp if isinstance(r, dict)}
            out = []
            for i in range(len(chunk)):
                r = by_id.get(base_id+i, {})
                if "result" in r: out.append(r["result"])
                elif "error" in r: out.append({"error": str(r["error"])[:120]})
                else: out.append(None)
            return out, ep
        # rate-limit single-element error list or wrong length -> try next endpoint
    return None, None

out = {"retry": "leg4-chunked-curl-batch", "started_wib": NOW, "chunk_size": 10}
t0 = time.time()
results = [None]*len(calls)
chunk_notes = []
CH = 10
for start in range(0, len(calls), CH):
    chunk = calls[start:start+CH]
    res, ep = curl_chunk(chunk, start)
    if res is None:
        time.sleep(3)
        res, ep = curl_chunk(chunk, start)
    if res is None:
        chunk_notes.append({"start": start, "status": "FAILED-both-attempts"})
    else:
        results[start:start+len(chunk)] = res
        chunk_notes.append({"start": start, "status": "ok", "endpoint": ep})
out["chunks"] = chunk_notes
out["batch_s"] = round(time.time()-t0, 1)
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
for (name, vk), r in zip(keys, results):
    if isinstance(r, str): reads[name]["views"][vk] = iv(r)
    elif isinstance(r, dict): reads[name]["views"][vk] = r
    else: reads[name]["views"][vk] = None
n_int = sum(1 for it in reads.values() for v in it["views"].values() if isinstance(v, int))
n_tot = sum(len(it["views"]) for it in reads.values())
out["ints"] = f"{n_int}/{n_tot}"
blk = None
try:
    p = subprocess.run(["curl","-s","--max-time","15","-H","Content-Type: application/json",
        "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}',
        "https://bsc-dataseed.binance.org/"], capture_output=True, text=True)
    blk = int(json.loads(p.stdout)["result"], 16)
except Exception:
    pass
out["block"] = blk
json.dump(out, open(BASE+f"hot-leg-run-{RUN}-reread-retry3.json","w"), indent=1)
main = json.load(open(BASE+f"hot-leg-run-{RUN}.json"))
main["leg4_retry3"] = out
if n_int > 0:
    json.dump({"started_wib": NOW, "block": blk, "reads": reads, "method": "chunked-curl-batch-retry3"},
              open(BASE+f"hot-leg-run-{RUN}-reread.json","w"), indent=1)
    try:
        prev = json.load(open(BASE+"hot-leg-run-2026-11-20-0904-reread.json"))
        prev_reads = prev.get("reads", {})
    except Exception:
        prev_reads = {}
    changes = {}
    for k, cur in reads.items():
        pv = prev_reads.get(k, {}).get("views", {})
        cv = cur["views"]
        diff = {}
        for kk, vv in cv.items():
            pvv = pv.get(kk)
            if isinstance(vv, int) and isinstance(pvv, int) and pvv != vv:
                diff[kk] = {"prev": pvv, "now": vv}
            elif isinstance(vv, int) and pvv is None:
                diff[kk] = {"prev": "unreadable-prev", "now": vv}
        changes[k] = diff
    def pct(c, t):
        c, t = num(c), num(t)
        return round(100*c/t, 1) if c is not None and t else None
    st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
    st_fs, st_fl = num(st.get("FREE_SUPPLY")), num(st.get("freeLeft"))
    stock_pct = pct((st_fs - st_fl) if st_fs is not None and st_fl is not None else None, st_fs)
    lumen_pct = pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY"))
    notes = (main.get("threshold_check") or {}).get("notes", "")
    main["leg4_block"] = blk
    main["leg4_method"] = "chunked-curl-batch-retry3"
    main["leg4_changes_vs_2026-11-20-0904_reread"] = changes
    main["threshold_check"] = {
      "STOCKAGENT_free_pct": stock_pct, "STOCKAGENT": st,
      "Lumenhold_free_pct": lumen_pct, "Lumenhold": lu,
      "AUGENT": reads["AUGENT"]["views"],
      "binanceai": reads["binanceai-mint"]["views"],
      "AONE_sale": reads["AONE-sale"]["views"],
      "bsccat_sale": reads["bsccat-sale"]["views"],
      "CTXGRAPH4": reads["CTXGRAPH4-nodesv2"]["views"],
      "AgentGrove": reads["Agent Grove"]["views"],
      "YAMA": reads["YAMA-sale"]["views"],
      "notes": notes,
    }
    out["changes_vs_0904"] = changes
    out["threshold_check"] = main["threshold_check"]
    json.dump(out, open(BASE+f"hot-leg-run-{RUN}-reread-retry3.json","w"), indent=1)
else:
    main["leg4_note"] = ("leg4 chunked retry also failed (0 ints). No change detection "
        "possible this run; retried next run per body rules.")
json.dump(main, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
