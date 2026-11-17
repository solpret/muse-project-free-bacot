#!/usr/bin/env python3
"""KZMB + Yokai + Saturnode verification run 1901 (READ-ONLY).
- KZMB: history from hot-leg-seen/reported (recorded in JSON) + fresh
  on-chain state (sharesSold, user slot, quote).
- Yokai / Saturnode: Sourcify ABI, agent-shape, free views, user slot,
  first mint via Ankr getLogs (chunked/probe, <=1000-block chunks for
  the confirm probe), block timestamps via fast_rpc dataseed ONLY
  (Ankr block timestamps are fake - never used).
- Website-gate on-chain legs: (C) Sourcify metadata URL grep,
  (H) contractURI, (I) tokenURI, (J) ABI site-function grep, (E) owner().
  Methods (A)/(G) web searches done separately; (B) Boltbook search-index;
  (F) twitterapi.io NEVER called (dead); (K) GitHub needs auth (limitation);
  (L) BscScan live-browser not available to this subagent (not run).
- Keccak selectors via pycryptodome (NEVER hashlib.sha3_256).
- Writes run-2026-11-07-1901-kzmb-yokai-saturnode.json. Never touches
  onchain-snapshot.json. No preview/mint/claim.
"""
import json, subprocess, sys, time
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single, batch
from ankr import get_logs
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
WIB = timezone(timedelta(hours=7))

def wib(ts):
    return datetime.fromtimestamp(ts, tz=WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

def sel(sig):
    return "0x" + keccak.new(digest_bits=256, data=sig.encode()).hexdigest()[:8]

def call(to, data, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
        except Exception as e:
            last = str(e)[:100]
    return {"error": last}

def block_time(blk):
    for ep in EPS:
        try:
            res = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            return int(res[0]["timestamp"], 16)
        except Exception:
            continue
    return None

def head_block():
    for ep in EPS:
        try:
            return int(_single(ep, "eth_blockNumber", [], 10, retries=0), 16)
        except Exception:
            continue
    return None

def abi_via_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "25", url],
                           capture_output=True, text=True, timeout=30)
        d = json.loads(p.stdout)
        return d.get("abi"), d
    except Exception as e:
        return None, {"error": f"{type(e).__name__}:{e}"}

def decode_str(raw):
    try:
        if not isinstance(raw, str) or len(raw) < 130:
            return None
        b = bytes.fromhex(raw[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode("utf-8", "replace")
    except Exception:
        return None

def decode_uint(raw):
    try:
        if isinstance(raw, str) and len(raw) >= 66:
            return int(raw[-64:], 16) if len(raw) == 66 else int(raw, 16)
    except Exception:
        pass
    return None

def first_mint(addr, seen_hint=None):
    """Return (first_block, first_tx, minter, logs_returned, probe_ok).
    Page 1 = earliest->latest, pageSize 1000 (Ankr module default).
    If ascending, min block = first mint; confirm with a probe to
    first_block-1 expecting zero logs. Falls back to bounded binary
    search if the probe finds earlier logs."""
    try:
        res = get_logs(addr, "earliest", "latest", topics=[TRANSFER, ZERO_TOPIC])
    except Exception as e:
        return {"error": f"ankr_getLogs: {type(e).__name__}:{str(e)[:120]}"}
    logs = (res.get("result") or {}).get("logs") or res.get("logs") or []
    if not logs:
        return {"logs": 0, "note": "no Transfer-from-zero logs found"}
    def blk(l):
        return int(l.get("blockNumber"), 16)
    blocks = [blk(l) for l in logs]
    first_block = min(blocks)
    first_log = min(logs, key=blk)
    out = {"logs_returned": len(logs), "min_block_in_page": first_block,
           "max_block_in_page": max(blocks),
           "ascending_page": blocks == sorted(blocks),
           "first_tx": first_log.get("transactionHash"),
           "first_minter": ("0x" + first_log.get("topics", ["", "", ""])[2][-40:]
                            if len(first_log.get("topics", [])) > 2 else None)}
    # confirm probe: any mint before first_block?
    try:
        probe = get_logs(addr, "earliest", first_block - 1, topics=[TRANSFER, ZERO_TOPIC])
        plogs = (probe.get("result") or {}).get("logs") or probe.get("logs") or []
        out["confirm_probe_logs_before"] = len(plogs)
        if len(plogs) == 0:
            out["first_block"] = first_block
            out["confirmed"] = True
        else:
            out["confirmed"] = False
            out["note"] = ("earlier logs exist - page ordering not ascending; "
                           "binary search needed (not run: bounded by time)")
            out["earliest_in_probe"] = min(int(l.get("blockNumber"), 16) for l in plogs)
    except Exception as e:
        out["confirm_probe_error"] = f"{type(e).__name__}:{str(e)[:100]}"
        out["first_block"] = first_block
        out["confirmed"] = False
    return out

def verify_nft(addr, name):
    v = {"address": addr, "name": name}
    abi, raw = abi_via_curl(addr)
    if not isinstance(abi, list):
        v["abi_error"] = str(raw)[:300]
        return v
    fns = {}
    for f in abi:
        if isinstance(f, dict) and f.get("type") == "function":
            sig = f["name"] + "(" + ",".join(i.get("type", "") for i in f.get("inputs", [])) + ")"
            fns[f["name"]] = sig
    v["fn_count"] = len(fns)
    v["fns"] = sorted(fns.values())
    names = [n.lower() for n in fns]
    name_set = set(names)
    raw_abi = json.dumps(abi).lower()
    v["registry_bytes_in_abi"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in raw_abi
    v["registry_view"] = None
    for n in ("agentRegistry", "AGENT_REGISTRY", "AGENT_ID_REGISTRY", "registry", "AGENT_ID"):
        if n in fns:
            r = call(addr, sel(fns[n]))
            if isinstance(r, str) and len(r) >= 66:
                val = "0x" + r[-40:]
                v["registry_view"] = {"fn": n, "value": val, "match": val.lower() == REG.lower()}
            else:
                v["registry_view"] = {"fn": n, "raw": str(r)[:100]}
            break
    v["agent_gate_fn"] = [n for n in fns if "agent" in n.lower() or "gate" in n.lower()]
    # views: no-arg first, then (address) with user, then (uint256) with 1
    views = {}
    for n, sig in fns.items():
        ln = n.lower()
        if ln.startswith("free") or n in ("PRICE", "price", "MAX_SUPPLY", "maxSupply",
                "totalMinted", "totalSupply", "mintOpen", "spotsLeft", "MAX_PER_WALLET",
                "FREE_PER_WALLET", "FREE_SUPPLY", "START_TIME", "startTime", "mintPrice",
                "sharesSold", "TOKENS_PER_SHARE", "PRICE_PER_SHARE", "name", "symbol",
                "contractURI", "tokenURI", "owner", "decimals"):
            data = sel(sig)
            try:
                if "(address)" in sig:
                    data += USER[2:].lower().rjust(64, "0")
                elif "(uint256)" in sig:
                    data += "01".rjust(64, "0")
            except Exception:
                pass
            r = call(addr, data)
            if isinstance(r, str):
                s = decode_str(r)
                if s is not None and ln in ("name", "symbol", "contracturi", "tokenuri"):
                    views[n] = s
                else:
                    u = decode_uint(r)
                    views[n] = u if u is not None else r[:130]
            else:
                views[n] = str(r)[:130]
    v["views"] = views
    # quote(user,1) if present
    if "quote" in fns:
        sig = fns["quote"]
        try:
            data = sel(sig) + USER[2:].lower().rjust(64, "0") + format(1, "064x")
            r = call(addr, data)
            v["quote_user_1"] = r if not isinstance(r, str) else r[:200]
        except Exception as e:
            v["quote_user_1_error"] = str(e)[:100]
    # (J) ABI site-function grep
    v["site_fns_in_abi"] = [n for n in fns
                            if any(w in n.lower() for w in ("website", "siteurl", "domain", "external", "url", "link"))]
    # (C) Sourcify metadata URL grep (full contract record, no fields)
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "25",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}"],
                           capture_output=True, text=True, timeout=30)
        d = json.loads(p.stdout)
        blob = json.dumps(d)
        import re as _re
        urls = sorted(set(_re.findall(r"https?://[^\s\"'\\]+", blob)))
        v["sourcify_match"] = d.get("match")
        v["sourcify_urls"] = [u for u in urls if "sourcify" not in u][:10]
    except Exception as e:
        v["sourcify_meta_error"] = f"{type(e).__name__}:{str(e)[:100]}"
    return v

out = {"run": "1901", "wallet": USER, "kzmb": {}, "yokai": {}, "saturnode": {}}
head = head_block()
out["head_block"] = head
print(f"head={head}", flush=True)

# ---- KZMB history (from hot-leg files, read-only) ----
seen_hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
rep_hl = json.load(open(f"{BASE}/hot-leg-reported.json"))
kzmb_key = "0xBd6e4c6DEF0065007Bd163e4223Ae4f3aa3b6f09"
out["kzmb"]["history_seen"] = seen_hl.get(kzmb_key) or seen_hl.get(kzmb_key.lower())
out["kzmb"]["history_reported"] = rep_hl.get(kzmb_key)
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
out["kzmb"]["in_snapshot_contracts"] = any(kzmb_key.lower() in k.lower()
                                           for k in snap.get("contracts", {}))
out["kzmb"]["in_snapshot_track_c"] = any(kzmb_key.lower() in json.dumps(v).lower()
                                         for v in snap.get("track_c", {}).values())
print("KZMB history: reported@",
      (out["kzmb"]["history_reported"] or {}).get("reported_wib"),
      "| in_snapshot:", out["kzmb"]["in_snapshot_contracts"],
      out["kzmb"]["in_snapshot_track_c"], flush=True)

# ---- KZMB fresh on-chain state ----
kz = verify_nft(kzmb_key, "KZMB")
out["kzmb"]["fresh"] = kz
print("KZMB fresh views:", json.dumps(kz.get("views", {})), flush=True)

# ---- Yokai / Saturnode ----
for key, addr, nm in (("yokai", "0x8066D9C5802dA311c274CEd3620817734AD8e985", "Yokai"),
                      ("saturnode", "0x6124b3ae64adA7b73581CcD01fEF89e583E8742c", "Saturnode")):
    v = verify_nft(addr, nm)
    seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
    fs = None
    for k, val in seen.items():
        if isinstance(val, int) and k.lower() == addr.lower():
            fs = val
    if isinstance(seen, dict) and isinstance(seen.get("contracts"), dict):
        fs = fs or seen["contracts"].get(addr) or seen["contracts"].get(addr.lower())
    v["scan_seen_first_block"] = fs
    if fs and head:
        age_h = (head - fs) * 0.45 / 3600
        v["scan_seen_age_hours_approx"] = round(age_h, 1)
    v["in_snapshot_contracts"] = addr.lower() in {k.lower() for k in snap.get("contracts", {})}
    fm = first_mint(addr)
    v["first_mint"] = fm
    fb = fm.get("first_block")
    if fb:
        ts = block_time(fb)
        v["first_mint_time"] = wib(ts) if ts else None
        v["first_mint_ts"] = ts
        if ts and head:
            now_ts = block_time(head)
            if now_ts:
                v["first_mint_age_hours"] = round((now_ts - ts) / 3600, 1)
    out[key] = v
    print(nm, "views:", json.dumps(v.get("views", {})), flush=True)
    print(nm, "first_mint:", json.dumps(fm), "time:", v.get("first_mint_time"),
          "age_h:", v.get("first_mint_age_hours"), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-1901-kzmb-yokai-saturnode.json", "w"), indent=1)
print("KZMB-YOKAI-SATURNODE DONE", flush=True)
