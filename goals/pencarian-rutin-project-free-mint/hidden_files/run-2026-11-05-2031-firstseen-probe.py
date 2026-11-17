#!/usr/bin/env python3
"""READ-ONLY deep probe of first-seen NFT contracts, run 2031.
- Sourcify ABI fetch; list all functions.
- Call no-arg views matching free/mint/supply/price/cap/start/end/open.
- Registry getter calls (on-chain, never ABI text).
- First-mint corroboration: Ankr getLogs address-filtered 131810000..first_block,
  Transfer topic0 + from=zero; report earliest mint block + block timestamp.
No preview/mint/sign.
Usage: python3 run-2026-11-05-2031-firstseen-probe.py
"""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
ZERO_TOPIC = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

TARGETS = [
    ("0xf6E6c51fe4bA9317a1CaA476A8FbDC3401a47D36", "HashDoge", 131824018),
    ("0xB8b23307BEe243E36e464665f4B7825a4afC7e73", "HASH ERAS", 131825018),
    ("0x53e43b924e016598942b857ea5B00D37Fc278dE5", "AgentDraw Pass", 131824167),
    ("0x3D1F1DAd36DFe781ee813B8d7fe8aF69f332f620", "Rune Bear Agent", 131824640),
    ("0x8d22b007b404EF49bDCdB9819e0981D9eD514E8D", "Sigma Ibis Agent", 131825338),
    ("0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9", "NAOMI GENESIS", 131825139),
]

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def eth_call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"], "id": 1}).encode()
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                d = json.load(r)
            if "result" in d:
                return d["result"]
        except Exception:
            continue
    return None

def dec_uint(h):
    if not h or h == "0x":
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

def dec_addr(h):
    if not h or h == "0x":
        return None
    try:
        return "0x" + format(int(h, 16), "040x")
    except Exception:
        return None

def dec_bool(h):
    v = dec_uint(h)
    return None if v is None else bool(v)

def get_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        return ("verified", d.get("abi"))
    except urllib.error.HTTPError as e:
        return ("not_verified" if e.code == 404 else f"http_{e.code}", None)
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

INTEREST = ("free", "mint", "supply", "price", "cap", "start", "end", "open",
            "claim", "gift", "airdrop", "quote", "cost", "registry", "agent",
            "total", "left", "remaining", "sold", "max", "phase", "window")

def probe(addr, name, first_block):
    out = {"address": addr, "name_scan": name, "first_block_window": first_block}
    status, abi = get_abi(addr)
    out["sourcify"] = status
    if not abi:
        out["verdict_note"] = "ABI unavailable; shape unknown"
    else:
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns[e.get("name")] = e
        out["functions"] = sorted(fns.keys())
        # no-arg views of interest
        views = {}
        for n, e in fns.items():
            if len(e.get("inputs", [])) == 0 and any(s in n.lower() for s in INTEREST):
                sig = n + "()"
                res = eth_call(addr, sel(sig))
                views[n] = {"raw": res, "uint": dec_uint(res),
                            "bool": dec_bool(res) if dec_uint(res) in (0, 1) else None,
                            "addr": dec_addr(res)}
        out["noarg_views"] = views
        # registry getters
        reg = {}
        for g in ("AGENT_ID", "AGENT_REGISTRY", "REGISTRY", "agentRegistry"):
            if g in fns:
                res = eth_call(addr, sel(g + "()"))
                reg[g] = dec_addr(res)
        out["registry_getters"] = reg
        out["registry_match"] = any((v or "").lower() == REGISTRY.lower() for v in reg.values() if v)
        # user-slot views (address input) if present
        user_views = {}
        for n, e in fns.items():
            if len(e.get("inputs", [])) == 1 and e["inputs"][0].get("type") == "address" \
               and any(s in n.lower() for s in ("free", "claim", "minted", "gift")):
                data = sel(n + "(address)") + USER[2:].lower().zfill(64)
                res = eth_call(addr, data)
                user_views[n] = {"uint": dec_uint(res), "bool": dec_bool(res) if dec_uint(res) in (0, 1) else None}
        out["user_slot_views"] = user_views
    # first-mint corroboration: address-filtered getLogs 131810000..first_block
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
            "fromBlock": hex(131810000), "toBlock": hex(first_block),
            "pageSize": 1000, "decodeLogs": False,
            "address": [addr], "topics": [TRANSFER, ZERO_TOPIC]}, timeout=30)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        blocks = sorted(int(l.get("blockNumber", "0x0"), 16) for l in logs)
        out["first_mint_probe"] = {"logs_in_range": len(logs),
                                   "earliest_block": blocks[0] if blocks else None,
                                   "latest_block": blocks[-1] if blocks else None}
    except Exception as e:
        out["first_mint_probe"] = {"error": str(e)}
    # block timestamp of earliest mint block (or first_block if none found)
    blk = (out["first_mint_probe"].get("earliest_block") or first_block)
    out["earliest_mint_block"] = blk
    ts = None
    for url in RPCS:
        try:
            payload = json.dumps({"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                                  "params": [hex(blk), False], "id": 1}).encode()
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                d = json.load(r)
            res = d.get("result") or {}
            ts = int(res.get("timestamp", "0x0"), 16)
            break
        except Exception:
            continue
    out["earliest_mint_timestamp"] = ts
    if ts:
        import datetime
        out["earliest_mint_wib"] = datetime.datetime.fromtimestamp(
            ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    return out

results = []
for addr, name, fb in TARGETS:
    r = probe(addr, name, fb)
    results.append(r)
    print(addr, name, "-> sourcify:", r["sourcify"],
          "| registry_match:", r.get("registry_match"),
          "| earliest_mint:", r.get("earliest_mint_block"), r.get("earliest_mint_wib"),
          "| probe_logs:", r.get("first_mint_probe", {}).get("logs_in_range"))
    time.sleep(0.3)

with open("run-2026-11-05-2031-firstseen-probe.json", "w") as f:
    json.dump(results, f, indent=1)
print("wrote run-2026-11-05-2031-firstseen-probe.json")
