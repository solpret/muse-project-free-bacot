#!/usr/bin/env python3
"""Parent closeout verification run 0501: HokiCat, Voltoad, HAMMER, APASS, Nidavellir
(new to snapshot) + WAR3 (strong-lead check) + Thetavox (age check).
Read-only; never previews/mints. Writes run-2026-11-08-0501-parent-verify.json/.log
and per-contract ABI files run-2026-11-08-0501-abi-<name>.json
"""
import json, sys, time, subprocess, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch as _batch
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
LOG = open(f"{HF}/run-2026-11-08-0501-parent-verify.log", "w")
def log(*a):
    print(*a, flush=True); print(*a, file=LOG, flush=True)

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:])
        if len(b) < 96: return None
        ln = int.from_bytes(b[64:96], "big")
        s = b[96:96+ln].decode("utf-8", "replace")
        return s
    except Exception:
        return None

def rpc_call(method, params, timeout=12):
    last = None
    for ep in EPS:
        try:
            return _batch([(method, params)], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last

def ankr_addr_logs(addr, frm, to):
    params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
              "address": addr, "pageSize": 1000, "decodeLogs": False,
              "topics": [TRANSFER, ZERO_TOPIC]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    res = body.get("result", {}) if isinstance(body, dict) else {}
    return res.get("logs", [])

def first_mint(addr, head, lo, tag):
    fm = {"firstMintBlock": None, "firstMintWib": None, "calls": 0, "note": ""}
    t0 = time.time()
    try:
        probe = ankr_addr_logs(addr, head - 999, head)
        fm["calls"] += 1
        log(f"  [{tag}] probe last chunk [{head-999},{head}]: {len(probe)} logs")
    except Exception as e:
        log(f"  [{tag}] probe fail", str(e)[:120]); fm["note"] = "probe-fail"
        fm["seconds"] = round(time.time() - t0, 1); return fm
    hi = head
    while hi - lo > 1000:
        mid = (lo + hi) // 2
        try:
            logs = ankr_addr_logs(addr, mid - 999, mid)
            fm["calls"] += 1
        except Exception as e:
            log(f"  [{tag}] chunk fail", mid, str(e)[:100]); fm["note"] = "chunk-fail"; break
        if logs: hi = mid
        else: lo = mid
        log(f"  [{tag}] bs lo={lo} hi={hi} logs={len(logs)}")
    try:
        logs = ankr_addr_logs(addr, lo, hi)
        fm["calls"] += 1
        if logs:
            first = min(logs, key=lambda l: int(l["blockNumber"], 16))
            fb = int(first["blockNumber"], 16)
            fm["firstMintBlock"] = fb
            blk = rpc_call("eth_getBlockByNumber", [hex(fb), False], timeout=15)
            ts = int(blk["timestamp"], 16)
            fm["firstMintWib"] = datetime.datetime.fromtimestamp(
                ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
            fm["firstMintTx"] = first.get("transactionHash")
            log(f"  [{tag}] FIRST MINT block {fb} {fm['firstMintWib']} tx {first.get('transactionHash')}")
        else:
            fm["note"] = "no-mint-in-window"
            log(f"  [{tag}] no mint logs in final window [{lo},{hi}]")
    except Exception as e:
        log(f"  [{tag}] final window fail", str(e)[:120]); fm["note"] = "final-fail"
    fm["seconds"] = round(time.time() - t0, 1)
    return fm

VIEWS_INT = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
    "freeCount()", "FREE_CAP()", "FREE_SUPPLY()", "FREE_PER_WALLET()", "mintOpen()",
    "MAX_SUPPLY()", "PRICE()", "paidMintedCount()", "balanceOf(address)",
    "freeClaimed(address)", "freeMintedBy(address)", "mintedBy(address)",
    "freeLeft(address)", "freeFor(address)", "quote(uint256)", "quote(address,uint256)",
    "freeRemaining()", "freeWindowOpen()", "remainingFree()", "freeQuota()"]
VIEWS_STR = ["name()", "symbol()", "contractURI()", "tokenURI(uint256)"]

CONTRACTS = {
 "HokiCat": "0xdb51Dcc2D8cAf9942D9A975a2e68e023aB5E1fcA",
 "Voltoad": "0xbc95e0a5bb1305958ba3263c6e9943b7a2554757",
 "HAMMER": "0xce67038f8703dff3aadaf77d41823b4b039c9446",
 "APASS": "0x01c106835091c09d5c69737631af133530093c89",
 "Nidavellir": "0xd527109571b039298b65bCB26313dcbED0978c97",
 "WAR3": "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe",
 "Thetavox": "0x37D39Fcc21ADDbB753e9366216E494d7956Bd859",
}

try:
    head = int(rpc_call("eth_blockNumber", [], timeout=12), 16)
except Exception as e:
    head = None; log("head fail", e)
log("head:", head)
out = {"head": head, "contracts": {}}

for name, addr in CONTRACTS.items():
    log(f"=== {name} {addr} ===")
    c = {"address": addr}
    # 1. Sourcify ABI
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "30",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
            capture_output=True, text=True)
        d = json.loads(r.stdout)
        json.dump(d, open(f"{HF}/run-2026-11-08-0501-abi-{name}.json", "w"), indent=1)
        abi = d.get("abi") or []
        c["sourcify_match"] = d.get("match")
        fns = [e["name"] + "(" + ",".join(i["type"] for i in e.get("inputs", [])) + ")"
               for e in abi if e.get("type") == "function"]
        c["functions"] = fns
        c["free_fns"] = [f for f in fns if "free" in f.lower()]
        c["registry_literal"] = REG.lower() in r.stdout.lower()
        c["agent_shape"] = c["registry_literal"] or any(
            ("gate" in f.lower() or "registry" in f.lower()) and "agent" in f.lower() for f in fns)
        log(f"  ABI fns={len(fns)} match={d.get('match')} free={c['free_fns']} registry_literal={c['registry_literal']} agent_shape={c['agent_shape']}")
    except Exception as e:
        c["sourcify_error"] = str(e)[:120]
        log("  sourcify fail", str(e)[:120])
    # 2. views (single-call each)
    vals = {}
    for sig in VIEWS_INT:
        base = sig.split("(")[0]
        data = sel(sig) + (enc(USER) if "(address)" in sig else ("0"*63 + "1" if "(uint256)" in sig else ""))
        try:
            r = rpc_call("eth_call", [{"to": addr, "data": data}, "latest"], timeout=10)
            vals[base] = to_int(r)
        except Exception:
            vals[base] = None
    for sig in VIEWS_STR:
        base = sig.split("(")[0]
        arg = "0"*63 + "1" if "(uint256)" in sig else ""
        data = sel(sig) + arg
        try:
            r = rpc_call("eth_call", [{"to": addr, "data": data}, "latest"], timeout=10)
            vals[base] = dec_str(r)
        except Exception:
            vals[base] = None
    c["views"] = vals
    for k, v in vals.items():
        log(f"  {k} = {v}")
    out["contracts"][name] = c

# 3. first-mint searches (time-boxed; WAR3 age already verified in snapshot)
if head:
    out["contracts"]["HokiCat"]["firstMint"] = first_mint(CONTRACTS["HokiCat"], head, head - 390000, "HokiCat")
    out["contracts"]["Voltoad"]["firstMint"] = first_mint(CONTRACTS["Voltoad"], head, head - 390000, "Voltoad")
    out["contracts"]["HAMMER"]["firstMint"] = first_mint(CONTRACTS["HAMMER"], head, head - 390000, "HAMMER")
    out["contracts"]["APASS"]["firstMint"] = first_mint(CONTRACTS["APASS"], head, head - 390000, "APASS")
    out["contracts"]["Thetavox"]["firstMint"] = first_mint(CONTRACTS["Thetavox"], head, 131200000, "Thetavox")
    out["contracts"]["Nidavellir"]["firstMint"] = first_mint(CONTRACTS["Nidavellir"], head, head - 390000, "Nidavellir")

json.dump(out, open(f"{HF}/run-2026-11-08-0501-parent-verify.json", "w"), indent=1)
log("DONE")
