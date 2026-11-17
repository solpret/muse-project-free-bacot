#!/usr/bin/env python3
"""Retry 1619: re-read the null leg-4 items from the 1619 run (bsc-dataseed
degraded: OBFG/Mossbound/Ochre/2e34/binanceai/NEW5893/HANAMI fully null,
OLIVER/JNTM/UNRES1 partially null). Chunked <=24 calls. Merges into the
1619 run JSON (retry_* keys) and updates flags for the retried items."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def curl(url, data=None, timeout=30):
    cmd = ["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0"]
    if data is not None: cmd += ["-H","Content-Type: application/json","-d",data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
def rpc_chunked(calls, timeout=30):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i+24]
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
PLAN = [
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("freeAvailable", True)]),
 ("Mossbound", "0xe589A94316C68d4A4f008f841Deb7e9612445244",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("saleStart", False), ("isFreeOpen", False), ("freeRemaining", False), ("freeAvailable", True)]),
 ("Ochre", "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("mintOpen", False),
   ("isFreeOpen", False), ("saleStart", False), ("totalSupply", False),
   ("freeClaimed", True), ("freeAvailable", True)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("freeClaimed", False), ("FREE_LOTS_CAP", False), ("opened", False)]),
 ("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810",
  [("FREE_MAX", False), ("freeRemaining", False), ("mintOpen", False),
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
  [("freeMinted", False), ("totalSupply", False)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
reads, errs = {}, {}
for cid, r, err in rpc_chunked(reqs, timeout=30):
    name, fn = keys[cid]
    v = None
    if r and r != "0x" and len(r) >= 66:
        try: v = int(r[-64:], 16)
        except Exception: v = None
    reads.setdefault(name, {})[fn] = v
    if err: errs[f"{name}:{fn}"] = err
ok = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
out = {"run": "retry-1619", "reads": reads, "errors": errs, "reads_ok": ok,
       "total_names": len(PLAN),
       "elapsed_s": round(time.time() - time.time(), 1)}
# merge into main run json
run = json.load(open(f"{HF}/hot-leg-run-2026-11-13-1619.json"))
run["retry_reads"] = reads
run["retry_reads_ok"] = ok
run["retry_errors"] = errs
for name, vals in reads.items():
    for fn, v in vals.items():
        if run["reads"].get(name, {}).get(fn) is None and v is not None:
            run["reads"][name][fn] = v
# recompute flags for retried items
f = run["flags"]
ob = run["reads"].get("OBFG", {})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    f["OBFG_pct"] = round(ob["freeMinted"]/ob["FREE_SUPPLY"]*100, 1)
    f["OBFG_soldout"] = bool(ob["freeMinted"] >= ob["FREE_SUPPLY"])
    f["OBFG_slot_lost"] = bool(ob.get("freeAvailable_user") == 0)
mb = run["reads"].get("Mossbound", {})
if mb.get("freeMinted") is not None and mb.get("FREE_SUPPLY"):
    f["Mossbound_pct"] = round(mb["freeMinted"]/mb["FREE_SUPPLY"]*100, 1)
    f["Mossbound_sale_open"] = bool(mb.get("saleOpen")==1 or mb.get("mintOpen")==1 or mb.get("isFreeOpen")==1)
    f["Mossbound_saleStart"] = mb.get("saleStart")
    f["Mossbound_freeRemaining"] = mb.get("freeRemaining")
    f["Mossbound_slot_user"] = mb.get("freeAvailable_user")
    f["Mossbound_soldout"] = bool(mb["freeMinted"] >= mb["FREE_SUPPLY"])
oc = run["reads"].get("Ochre", {})
if oc.get("freeMinted") is not None and oc.get("FREE_SUPPLY"):
    f["Ochre_pct"] = round(oc["freeMinted"]/oc["FREE_SUPPLY"]*100, 1)
    f["Ochre_opened"] = bool(oc.get("saleOpen")==1 or oc.get("mintOpen")==1 or oc.get("isFreeOpen")==1)
    f["Ochre_saleStart"] = oc.get("saleStart")
    f["Ochre_totalSupply"] = oc.get("totalSupply")
    f["Ochre_50pct_crossed"] = bool(oc["freeMinted"] >= oc["FREE_SUPPLY"]*0.5)
    f["Ochre_70pct_crossed"] = bool(oc["freeMinted"] > oc["FREE_SUPPLY"]*0.7)
    f["Ochre_soldout"] = bool(oc["freeMinted"] >= oc["FREE_SUPPLY"])
    f["Ochre_slot_user"] = {"freeClaimed_user": oc.get("freeClaimed_user"), "freeAvailable_user": oc.get("freeAvailable_user")}
    f["Ochre_slot_open"] = bool(oc.get("freeClaimed_user")==0 or oc.get("freeAvailable_user")==1)
    f["Ochre_strong_lead_legs"] = bool(f["Ochre_70pct_crossed"] and f["Ochre_slot_open"] and oc.get("saleStart")==1794556267)
    f["Ochre_sellout_already_reported_1519"] = True
ol = run["reads"].get("OLIVER", {})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    f["OLIVER_pct"] = round(ol["freeMinted"]/ol["FREE_MAX"]*100, 1)
    f["OLIVER_soldout"] = bool((ol.get("freeRemaining") or 1) == 0)
    f["OLIVER_slot_user"] = {"freeClaimed_user": ol.get("freeClaimed_user"), "freeClaimedByAgent_user": ol.get("freeClaimedByAgent_user")}
te = run["reads"].get("2e34", {})
if te.get("freeMinted") is not None and te.get("FREE_MAX"):
    f["2e34_pct"] = round(te["freeMinted"]/te["FREE_MAX"]*100, 1)
    f["2e34_monitor_only"] = True
    f["2e34_50pct_crossed"] = bool(te["freeMinted"] >= te["FREE_MAX"]*0.5)
n5 = run["reads"].get("NEW5893", {})
if n5.get("freeMinted") is not None and n5.get("FREE_SUPPLY"):
    f["NEW5893_pct"] = round(n5["freeMinted"]/n5["FREE_SUPPLY"]*100, 1)
    f["NEW5893_opened"] = bool(n5.get("saleOpen")==1 or n5.get("mintOpen")==1)
    f["NEW5893_saleStart"] = n5.get("saleStart")
    f["NEW5893_totalSupply"] = n5.get("totalSupply")
    f["NEW5893_free_per_wallet"] = n5.get("FREE_PER_WALLET")
    f["NEW5893_slot_user"] = n5.get("freeClaimed_user")
    f["NEW5893_prelaunch"] = bool(n5.get("saleOpen")==0 and n5.get("mintOpen")==0 and n5.get("freeMinted")==0)
hm = run["reads"].get("HANAMI", {})
if hm.get("freeMinted") is not None:
    f["HANAMI_freeMinted"] = hm["freeMinted"]
    f["HANAMI_totalSupply"] = hm.get("totalSupply")
    f["HANAMI_pct_of_MAX3333"] = round(hm["freeMinted"]/3333*100, 2)
    f["HANAMI_mintOpen"] = hm.get("mintOpen")
    f["HANAMI_delta_vs_1601_97"] = hm["freeMinted"] - 97
u1 = run["reads"].get("UNRES1", {})
if u1.get("freeMinted") is not None:
    f["UNRES1_freeMinted"] = u1["freeMinted"]
    f["UNRES1_delta_vs_1614"] = u1["freeMinted"] - 1
    f["UNRES1_mintOpen"] = u1.get("mintOpen")
    f["UNRES1_totalSupply"] = u1.get("totalSupply")
f["binanceai_opened"] = bool(run["reads"].get("binanceai-mint", {}).get("launched") == 1)
f["JNTM_opened"] = bool(run["reads"].get("JNTM", {}).get("opened") == 1)
run["flags"] = f
run["reads_ok_after_retry"] = sum(1 for n in run["reads"] if any(v is not None for v in run["reads"][n].values()))
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1619-retry.json", "w"), indent=1)
json.dump(run, open(f"{HF}/hot-leg-run-2026-11-13-1619.json", "w"), indent=1)
print(json.dumps(out, indent=1))
