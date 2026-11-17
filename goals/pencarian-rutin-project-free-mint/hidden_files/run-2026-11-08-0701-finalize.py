#!/usr/bin/env python3
"""Run 2026-11-08 0701 finalize (scan SUCCEEDED, partial=False, 0 errors):
- append newly seen contracts (NFT + ERC20) from the scan window to
  onchain-scan-seen.json, ONLY if absent from seen (address-based) AND
  absent from snapshot (address-based, contracts + excluded).
- advance onchain-scan-state.json watermark to the scanned head
  (last_scanned_block = to_block) + record window/gap/notes.
- patch run-2026-11-08-0701-sourcify.json in_scan flags now the scan exists.
Follows append-seen-1031.py pattern. NO snapshot/bridge writes."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0701"

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-08-0701.json"))
assert scan["partial"] is False and not scan["errors"], "scan not clean, refuse finalize"
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_contracts = seen["contracts"]
seen_l = {k.lower() for k in seen_contracts}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in (snap.get("excluded", {}) or {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
if isinstance(snap.get("excluded"), list):
    for v in snap["excluded"]:
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(v["address"].lower())

window = f"{scan['from_block']}-{scan['to_block']}"
added = []
for e in scan.get("erc20_mint_contracts_list", []):
    a = e["address"]
    if a.lower() in seen_l or a.lower() in snap_addrs:
        continue
    seen_contracts[a] = {"first_seen_block": e["first_block"], "last_block": e["last_block"],
                         "window": window, "run": TS, "kind": "ERC20",
                         "name": None, "symbol": None,
                         "mint_count": e["mint_count"], "distinct_minters": e["distinct_minters"]}
    seen_l.add(a.lower())
    added.append((a, "ERC20"))
for c in scan.get("contracts", []):
    a = c["address"]
    if a.lower() in seen_l or a.lower() in snap_addrs:
        continue
    seen_contracts[a] = {"first_seen_block": c["first_block"], "last_block": c["last_block"],
                         "window": window, "run": TS, "kind": c["kind"],
                         "name": c.get("name"), "symbol": c.get("symbol"),
                         "mint_count": c["mint_count"], "distinct_minters": c["distinct_minters"],
                         "registry_bytes_hit": c.get("registry_bytes_hit"),
                         "sourcify": c.get("sourcify")}
    seen_l.add(a.lower())
    added.append((a, c["kind"]))
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
print(f"SEEN appended {len(added)} (NFT {sum(1 for _,k in added if k!='ERC20')}, ERC20 {sum(1 for _,k in added if k=='ERC20')})")
for a, k in added:
    print(f"  + {k} {a}")

# Watermark advance (scan succeeded). Skipped gap: watermark 132290410 -> window start 132292853.
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
old_wm = state.get("last_scanned_block")
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
state["last_scan_wib"] = f"run 0701 2026-11-08 ~{now_wib[11:16]} WIB (main scan; watermark advanced per task)"
state["ankr_calls"] = scan["ankr_calls"]
state["errors"] = scan["errors"]
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = scan["erc20_mint_contracts"]
state["skipped_gap"] = ("132290411-132292852 (2442 blok; window main scan 132292853-132293852 "
                        "dimulai dari head-999 karena gap ke watermark 3409 blok > cap 1000; "
                        "backfill DINONAKTIFKAN user ~06:28 WIB, jadi gap ini TIDAK ditutup otomatis)")
state["runNote0701_scan"] = ("Scan 0701: pre-flight LULUS 26,0 dtk (head 132293819, 309 log/50 blok; "
    "dataseed1 timeout, fallback publicnode). Window 132292853-132293852 (1000 blok cap), "
    "20/20 chunk + 148/148 enrich, 40 panggilan Ankr, 0 error, partial=false. "
    "148 NFT + 353 ERC-20 mint. 2 first-seen: JINLI 0x0f45b52f (43 mint/43 minter, registry-bytes "
    "saja, Sourcify unverified) + Binance ART 0xfc97f4Ab (1 mint; hot-leg 0659: bukan agent-shaped). "
    "Watermark 132290410 -> 132293852; skipped gap 132290411-132292852 (2442 blok, backfill off).")
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print(f"WATERMARK {old_wm} -> {scan['to_block']}")

# Patch sourcify in_scan flags now that the scan file exists.
sj = json.load(open(f"{BASE}/run-{TS}-sourcify.json"))
scan_addrs = {c["address"].lower() for c in scan["contracts"]}
scan_addrs |= {e["address"].lower() for e in scan.get("erc20_mint_contracts_list", [])}
for r in sj["results"]:
    r["in_scan_window"] = r["address"].lower() in scan_addrs
sj["cross_check"] = ("Feed vs scan window 132292853-132293852: 2 overlap — Binance ART 0xfc97f4Ab "
    "(bukan agent-shaped, bukan sale-shape; hot leg 0659) dan HokiCat 0xdb51Dcc2 (S1, SUDAH excluded "
    "sold-out 2026-11-08); keduanya dilaporkan SEKALI (bukan temuan baru). 10 alamat feed mint-shape "
    "lainnya (template paid-mint: mint+PRICE/quote+AGENT_REGISTRY/isAgent, TANPA free view) tidak "
    "masuk window scan ini.")
json.dump(sj, open(f"{BASE}/run-{TS}-sourcify.json", "w"), indent=1)
print("SOURCIFY cross-check patched:", [r["address"] for r in sj["results"] if r["in_scan_window"]])
print("FINALIZE DONE")
