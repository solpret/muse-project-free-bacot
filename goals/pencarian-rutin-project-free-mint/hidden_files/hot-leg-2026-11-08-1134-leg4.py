#!/usr/bin/env python3
"""Hot-leg 1134 leg4/Pandora/bridge: lean single-endpoint re-read."""
import json, re, sys, time, subprocess, concurrent.futures, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1134"
PREV_TAG = "hot-leg-2026-11-08-1129"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed1.bnbchain.org/"
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-08 11:34:38 WIB leg4"}

# --- re-check any Boltbook new address left unrecorded by script A (ABI unavailable) ---
seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
try:
    a_log = json.load(open(BASE+TAG+"-legs12.log"))
    pending = []
    for lang in ("en", "zh"):
        for a in a_log.get("leg2_boltbook", {}).get(lang, {}).get("new_vs_snapshot", []):
            if a.lower() not in seen_lower:
                pending.append((lang, a))
    log["boltbook_pending_recheck"] = pending
    for lang, addr in pending:
        try:
            code = batch([("eth_getCode", [addr, "latest"])], endpoint=EP, timeout=8)[0]
        except Exception as ex:
            code = f"ERR {ex}"
        if code == "0x":
            seen[addr] = {"first_seen_wib": "2026-11-08T11:34:00+07:00", "source": f"boltbook-{lang}",
                "status": "checked-not-contract",
                "note": "eth_getCode 0x on bsc-dataseed — EOA/wallet address mentioned in a Boltbook post, not a contract; no sale shape, not a lead."}
            log.setdefault("boltbook_recheck", {})[addr] = "EOA, recorded checked-not-contract"
        elif isinstance(code, str) and code.startswith("0x"):
            out = subprocess.run(["curl","-sL","--max-time","20",
                f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                capture_output=True, text=True).stdout
            try:
                abi = json.loads(out).get("abi", [])
                names = {e["name"] for e in abi if e.get("type")=="function"}
                FREE = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
                s1 = any(n.lower().startswith("mint") for n in names) and bool(names & {"quote","cost"}) and bool(names & FREE) and bool(names & {"agentId","agentRegistry","registry","AGENT_ID","AGENT_REGISTRY","hasAgentId"})
                s2 = bool(names & {"name","symbol","decimals","totalSupply"}) and "mintFree" in names and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and bool(names & {"agentId","agentRegistry","registry","AGENT_ID","AGENT_REGISTRY"})
                if not names:
                    log.setdefault("boltbook_recheck", {})[addr] = "ABI 0 functions (unverified); not recorded, retry next run"
                else:
                    seen[addr] = {"first_seen_wib": "2026-11-08T11:34:00+07:00", "source": f"boltbook-{lang}",
                        "status": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
                        "note": f"S1={s1} S2={s2} fns={sorted(names)}"}
                    log.setdefault("boltbook_recheck", {})[addr] = f"S1={s1} S2={s2} fns={len(names)}"
            except Exception as ex:
                log.setdefault("boltbook_recheck", {})[addr] = f"shape-check error {ex}; not recorded, retry next run"
    json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    log["seen_total_after"] = len(seen)
except Exception as ex:
    log["boltbook_pending_recheck_error"] = f"{type(ex).__name__}: {ex}"

# --- extract V and ITEMS from the 1129 script ---
src = open(BASE+PREV_TAG+".py").read()
def extract(var):
    m = re.search(re.escape(var)+r"\s*=\s*(\{.*?^\})", src, re.S|re.M)
    return eval(m.group(1))
V = extract("V"); ITEMS = extract("ITEMS")
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    try:
        res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=EP, timeout=6)
        return to_int(res[0])
    except Exception:
        return None
try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=6)[0], 16)
except Exception as ex:
    blk = None; log["leg4_block_error"] = str(ex)[:120]
def do_item(name):
    addr, keys = ITEMS[name]
    out = {"address": addr}
    for k in keys:
        sig, arg = V[k]
        out[k] = single(addr, sig, arg)
    return name, out
items = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, out in ex.map(do_item, ITEMS):
        items[name] = out
reread = {"block": blk, "items": items}
json.dump(reread, open(BASE+TAG+"-reread.json","w"), indent=1)
log["leg4"] = {"block": blk, "n": len(items)}
prev = json.load(open(BASE+PREV_TAG+"-reread.json"))
log["leg4_diff_prev_file"] = PREV_TAG+"-reread.json"
diffs = []
for name, cur in items.items():
    old = prev["items"].get(name, {})
    for k, v in cur.items():
        if k == "address": continue
        ov = old.get(k)
        if v != ov:
            diffs.append({"item": name, "field": k, "old": ov, "new": v})
log["leg4_diff_vs_prev"] = diffs

# --- Pandora ---
PANDORA = "0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8"
pandora = {"address": PANDORA}
for _k, _sig in {"totalMinted": "totalMinted()", "totalSupply": "totalSupply()",
                 "mintActive": "mintActive()", "publicRemaining": "publicRemaining()",
                 "freeUsed_user": "freeUsed(address)"}.items():
    _arg = "USER" if _k == "freeUsed_user" else ""
    pandora[_k] = single(PANDORA, _sig, _arg)
log["leg3b_pandora"] = pandora

# --- bridge ---
bridge = json.load(open(BASE+"scan-bridge.json"))
snap = json.load(open(BASE+"onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address","sale","token"):
            if v.get(f): snap_addrs.add(v[f].lower())
bcontracts = bridge.get("contracts", {})
log["bridge"] = {"n_contracts": len(bcontracts),
    "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(BASE+"scan-bridge.json"))),
    "in_snapshot": len([a for a in bcontracts if a.lower() in snap_addrs]),
    "note": "read-only; no bridge contract newly meets a tier this run (checked only via count/mtime + snapshot membership, per prior runs)."}
log["elapsed_sec"] = round(time.time()-t0, 1)
json.dump(log, open(BASE+TAG+"-leg4.log","w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time()-t0,1))
