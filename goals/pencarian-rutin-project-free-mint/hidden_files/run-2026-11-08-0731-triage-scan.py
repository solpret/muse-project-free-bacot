#!/usr/bin/env python3
"""Run 2026-11-08 0731 triage: first-seen = scan contracts absent from
onchain-scan-seen.json (contracts) AND snapshot contracts/excluded
(by address) AND known_older_leads. Registry address excluded as
infrastructure. RWD 0xcfe5...ee40 is already-handled (hot-leg 0319
strong lead gate-blocked, reported once) — never re-report.
READ-ONLY on shared files; writes run-2026-11-08-0731-triage-scan.* only.
First-mint block timestamps via dataseed eth_getBlockByNumber (Ankr
returns fake timestamps — never use Ankr for block time)."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0731"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RWD = "0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40"

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-08-0731.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
seen_addrs = {k.lower() for k in seen.get("contracts", {})}
seen_addrs |= {k.lower() for k in seen.get("known_older_leads", {})}
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in snap.get("excluded", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
# excluded may also be a list in older shapes; guard
if isinstance(snap.get("excluded"), list):
    for v in snap["excluded"]:
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(v["address"].lower())

log = open(f"{BASE}/run-{TS}-triage-scan.log", "w")
def p(*a):
    print(*a, flush=True)
    print(*a, file=log, flush=True)

p(f"window {scan['from_block']}-{scan['to_block']} partial={scan['partial']} "
  f"ankr_calls={scan['ankr_calls']} errors={scan['errors']}")
p(f"scan: {len(scan['contracts'])} NFT contracts, "
  f"{scan['erc20_mint_contracts']} ERC20-mint contracts")
rwd_entry = [c for c in scan["contracts"] if c["address"].lower() == RWD]
p(f"RWD {RWD} in scan: {bool(rwd_entry)} "
  f"(in seen: {RWD in seen_addrs}; snapshot/excluded: {RWD in snap_addrs}) -> "
  f"SUDAH-DITANGANI hot-leg 0319, tidak dilaporkan ulang, tidak di-preview/mint")
if rwd_entry:
    c = rwd_entry[0]
    p(f"  RWD detail: {c.get('name')} {c.get('symbol')} kind={c.get('kind')} "
      f"mints={c.get('mint_count')} minters={c.get('distinct_minters')} "
      f"first_block={c.get('first_block')} last_block={c.get('last_block')} "
      f"registry={c.get('registry_bytes_hit')} sourcify={c.get('sourcify')} "
      f"free_shaped={c.get('free_shaped')} mint_funcs={c.get('mint_funcs')}")
reg_entry = [c for c in scan["contracts"] if c["address"].lower() == REGISTRY]
p(f"registry {REGISTRY} in scan: {len(reg_entry)} (infrastruktur, excluded)")

first_seen = []
for c in scan["contracts"]:
    a = c["address"].lower()
    if a == REGISTRY:
        continue
    if a in seen_addrs or a in snap_addrs:
        continue
    first_seen.append(c)
p(f"first-seen sejati: {len(first_seen)}")

def block_time_wib(blk):
    for ep in ["https://bsc-dataseed1.bnbchain.org/",
               "https://bsc-dataseed.binance.org/",
               "https://bsc-dataseed2.bnbchain.org/"]:
        try:
            res = batch([("eth_getBlockByNumber", [hex(blk), False])],
                        endpoint=ep, timeout=10)
            ts = int(res[0]["timestamp"], 16)
            dt = datetime.datetime.fromtimestamp(
                ts, datetime.timezone(datetime.timedelta(hours=7)))
            return dt.strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception as e:
            print(f"  block_time {blk} via {ep} failed: {e}", flush=True)
    return None

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
out_fs = []
for c in first_seen:
    r = {"address": c["address"], "kind": c.get("kind"),
         "name": c.get("name"), "symbol": c.get("symbol"),
         "mint_count": c.get("mint_count"),
         "distinct_minters": c.get("distinct_minters"),
         "first_block": c.get("first_block"), "last_block": c.get("last_block"),
         "registry_bytes_hit": c.get("registry_bytes_hit"),
         "sourcify": c.get("sourcify"),
         "free_shaped": c.get("free_shaped"), "mint_funcs": c.get("mint_funcs")}
    agent_shaped = bool(c.get("registry_bytes_hit")) or bool(c.get("free_shaped")) \
        or bool(c.get("mint_funcs"))
    r["agent_shaped"] = agent_shaped
    if agent_shaped:
        r["first_mint_time_wib"] = block_time_wib(c["first_block"])
        if r["first_mint_time_wib"]:
            dt = datetime.datetime.strptime(r["first_mint_time_wib"],
                                            "%Y-%m-%d %H:%M:%S WIB").replace(
                tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
            age_h = (now - dt).total_seconds() / 3600
            r["age_hours_at_run"] = round(age_h, 1)
            r["verdict"] = ("EARLY-LEAD (umur %.1f jam <=48h, perlu cek kuota/slot/gate "
                            "oleh parent)" % age_h) if age_h <= 48 else \
                "AGE-EXCLUDED (>48 jam, bukan lead)"
        else:
            r["verdict"] = "PERLU VERIFIKASI UMUR (timestamp blok gagal dibaca)"
    else:
        r["verdict"] = "BUKAN agent-shaped"
    out_fs.append(r)
    p(f"FIRST-SEEN {r['address']} {r['name']}({r['symbol']}) {r['kind']} "
      f"mints={r['mint_count']} minters={r['distinct_minters']} "
      f"first_block={r['first_block']} registry={r['registry_bytes_hit']} "
      f"sourcify={r['sourcify']} free={r['free_shaped']} mint_fns={r['mint_funcs']} "
      f"-> {r['verdict']}"
      + (f" first_mint={r.get('first_mint_time_wib')}" if r.get("first_mint_time_wib") else ""))
    if not agent_shaped:
        p(f"  (bukan agent-shaped: tanpa registry/free-mint/free-supply; "
          f"tidak masuk snapshot, tidak dilaporkan)")

result = {"run": TS, "checked_wib": now.strftime("%Y-%m-%d %H:%M WIB"),
          "source_scan": "onchain-scan-2026-11-08-0731.json",
          "window": [scan["from_block"], scan["to_block"]],
          "partial": scan["partial"], "ankr_calls": scan["ankr_calls"],
          "errors": scan["errors"], "enriched": len(scan["contracts"]),
          "nft_contracts": len(scan["contracts"]),
          "erc20_total": scan["erc20_mint_contracts"],
          "first_seen": out_fs, "first_seen_count": len(out_fs),
          "new_seen_would_append": len(out_fs),
          "rwd_seen_in_scan": bool(rwd_entry),
          "rwd_note": "SUDAH-DITANGANI hot-leg 0319 strong lead gate-blocked, "
                      "sudah dilaporkan sekali; tidak dilaporkan ulang.",
          "erc20_candidates": scan["erc20_mint_contracts_list"]}
json.dump(result, open(f"{BASE}/run-{TS}-triage-scan.json", "w"), indent=1)
p(f"TRIAGE DONE first_seen={len(out_fs)}")
log.close()
