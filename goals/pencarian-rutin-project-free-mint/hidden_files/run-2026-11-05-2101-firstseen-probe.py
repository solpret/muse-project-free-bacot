#!/usr/bin/env python3
"""READ-ONLY deep probe of first-seen NFT contracts, run 2101 (adapted from 2031 probe).
- Sourcify ABI fetch; list all functions.
- Call no-arg views matching free/mint/supply/price/cap/start/end/open.
- Registry getter calls (on-chain, never ABI text).
- For Sourcify-unverified contracts: probe COMMON free-view selectors directly
  (freeClaimed(address), freeLeft(), FREE_SUPPLY(), freeMinted(), freeFor(address),
   mintPrice(), totalSupply(), MAX_SUPPLY(), mintOpen(), agentRegistry(), etc.)
  so a STRICT verdict is possible without an ABI.
- First-mint corroboration: Ankr getLogs address-filtered 131826009..first_block,
  Transfer topic0 + from=zero; report earliest mint block + block timestamp.
No preview/mint/sign.
Usage: python3 run-2026-11-05-2101-firstseen-probe.py
"""
import json, sys, time, urllib.request, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
ZERO_TOPIC = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
GAP_START = 131826009

TARGETS = [
    ("0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e", "GHOST", 131828914),
    ("0x1eF7588Dff561b7390D3AF23d06E684D64217419", "Sonofluidic", 131829128),
    ("0xf7e72Bf8Cc48c47f53b99A6FdC3FF4B4B8cB8a54", "Tampesta", 131829396),
    ("0xD2001b3EF8Fb923aF515628E717f6AC1BC4a36e1", "Proof of Epoch", 131829236),
    ("0x77DAB9eDF367baE50Ce3d2D6458B2c56b5bB42b1", "Nine Lives", 131830623),
    ("0x9f8dC7160c20B65CB684EDA5D4799f329DAF5396", "OWLORD", 131829385),
    ("0xc8896FC6A923621105274AF0920190ec74c6cFD0", "Logic Node", 131830507),
    ("0x6F7d19f4D7e6956569bd7452E0fD44A512c17D27", "Cosmic Rat Agent", 131830576),
    ("0x58FbdEefd90C28c0B834817bBAf12A803d5c5760", "Hex Warden Agent", 131830549),
    ("0x35dCDBF60DccC0D80C57854337Ca142695Ae0d4f", "Obsidian Owl Agent", 131830621),
    ("0x681D1F88Dd93465f17CAb905be299B34eA2c414f", "Gale Sprite Agent", 131830642),
    ("0xFf221FAEA8DE547E325c4e08C558BE163811ACbb", "BSRC20 Invite Pass", 131829081),
    ("0x38Fb9535Cf0741C890164EE62507ebCaeB12b252", "Mirage Raven Agent", 131829546),
    ("0x8BD5296373dA51670B765519D23aaf357441937A", "Wraith Vellum", 131829975),
    ("0xeD555fbc6475035D39c169a33CCdD5c64461fA18", "Matrix Core", 131830239),
    ("0xFefEf878814BdF807b7789bd79dF772A1FFA6AfD", "Chiguachipmunk", 131830384),
    ("0x6A1081EAE3e1Cb9adE1fC5ceC10eF37d6574a9Fc", "Cerberuscorgi", 131830381),
    ("0xa739052D3C90bB73AA01AaFED09F0F7f166D2F8F", "Cablecobra", 131830378),
    ("0xDDE0cE49540Da95B8EbD273766c5249b5366a2B7", "Bluetoothbison", 131830374),
    ("0x47a5569f94c6055edF3E5900402c2c79Bcc39DD4", "erate", 131830463),
    ("0x7fa4d8D0c122F1dC38C756f79306f61DFEAD4Ab4", "GUARD Card", 131830778),
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

# Common selectors probed on Sourcify-unverified contracts (no ABI available).
COMMON_NOARG = ["freeLeft()", "freeMinted()", "FREE_SUPPLY()", "FREE_PER_WALLET()",
                "MAX_SUPPLY()", "totalSupply()", "totalMinted()", "mintPrice()",
                "PRICE()", "mintOpen()", "freeSupply()", "freeClaimed()",
                "agentRegistry()", "AGENT_REGISTRY()", "AGENT_ID()", "REGISTRY()"]
COMMON_ADDR = ["freeClaimed(address)", "freeFor(address)", "freeMintedBy(address)",
               "mintedBy(address)", "hasMinted(address)"]

def probe(addr, name, first_block):
    out = {"address": addr, "name_scan": name, "first_block_window": first_block}
    status, abi = get_abi(addr)
    out["sourcify"] = status
    if not abi:
        out["verdict_note"] = "ABI unavailable; probing common selectors"
        common = {}
        for sig in COMMON_NOARG:
            res = eth_call(addr, sel(sig))
            if res and res != "0x":
                common[sig] = {"uint": dec_uint(res),
                               "bool": dec_bool(res) if dec_uint(res) in (0, 1) else None,
                               "addr": dec_addr(res)}
        for sig in COMMON_ADDR:
            data = sel(sig) + USER[2:].lower().zfill(64)
            res = eth_call(addr, data)
            if res and res != "0x":
                common[sig] = {"uint": dec_uint(res),
                               "bool": dec_bool(res) if dec_uint(res) in (0, 1) else None}
        out["common_selector_probe"] = common
        out["registry_match"] = any(
            (v.get("addr") or "").lower() == REGISTRY.lower() for v in common.values())
    else:
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns[e.get("name")] = e
        out["functions"] = sorted(fns.keys())
        views = {}
        for n, e in fns.items():
            if len(e.get("inputs", [])) == 0 and any(s in n.lower() for s in INTEREST):
                res = eth_call(addr, sel(n + "()"))
                views[n] = {"raw": res, "uint": dec_uint(res),
                            "bool": dec_bool(res) if dec_uint(res) in (0, 1) else None,
                            "addr": dec_addr(res)}
        out["noarg_views"] = views
        reg = {}
        for g in ("AGENT_ID", "AGENT_REGISTRY", "REGISTRY", "agentRegistry"):
            if g in fns:
                res = eth_call(addr, sel(g + "()"))
                reg[g] = dec_addr(res)
        out["registry_getters"] = reg
        out["registry_match"] = any((v or "").lower() == REGISTRY.lower() for v in reg.values() if v)
        user_views = {}
        for n, e in fns.items():
            if len(e.get("inputs", [])) == 1 and e["inputs"][0].get("type") == "address" \
               and any(s in n.lower() for s in ("free", "claim", "minted", "gift")):
                data = sel(n + "(address)") + USER[2:].lower().zfill(64)
                res = eth_call(addr, data)
                user_views[n] = {"uint": dec_uint(res), "bool": dec_bool(res) if dec_uint(res) in (0, 1) else None}
        out["user_slot_views"] = user_views
    # first-mint corroboration: address-filtered getLogs GAP_START..first_block
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
            "fromBlock": hex(GAP_START), "toBlock": hex(first_block),
            "pageSize": 1000, "decodeLogs": False,
            "address": [addr], "topics": [TRANSFER, ZERO_TOPIC]}, timeout=30)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        blocks = sorted(int(l.get("blockNumber", "0x0"), 16) for l in logs)
        out["first_mint_probe"] = {"logs_in_range": len(logs),
                                   "earliest_block": blocks[0] if blocks else None,
                                   "latest_block": blocks[-1] if blocks else None}
    except Exception as e:
        out["first_mint_probe"] = {"error": str(e)}
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
          "| probe_logs:", r.get("first_mint_probe", {}).get("logs_in_range"),
          "| common:", list(r.get("common_selector_probe", {}).keys()))
    time.sleep(0.3)

with open("run-2026-11-05-2101-firstseen-probe.json", "w") as f:
    json.dump(results, f, indent=1)
print("wrote run-2026-11-05-2101-firstseen-probe.json")
