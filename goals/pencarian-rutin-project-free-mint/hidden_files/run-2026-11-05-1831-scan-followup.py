"""Run 2026-11-05-1831 (subagent A): STRICT first-seen verification.
Reads run-2026-11-05-1831-scan-firstseen-raw.json, probes each first-seen NFT
contract: Sourcify ABI + registry-bytes + FULL probe set incl. the 1731
costOf lesson: price()/costOf(user,1)/mintsLeft()/agentIds()/mintedBy()/mintOpen()
plus standard free views. Verifies first mints on-chain (Ankr getLogs,
address-filtered, chunked <=2000 blocks, back to window start - 2000).
READ-ONLY. Writes run-2026-11-05-1831-scan-followup.json.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def sourcify_abi(address, tries=4):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(4)
        except Exception:
            time.sleep(4)
    return ("error:retry-exhausted", None)

def block_time(blk):
    try:
        b = rpc_call("eth_getBlockByNumber", [hex(blk), False])
        ts = int(b["timestamp"], 16)
        return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
    except Exception as e:
        return "error:" + type(e).__name__

def probe_views(addr):
    out = {}
    UP = USER[2:].lower().rjust(64, "0")
    ONE = "0000000000000000000000000000000000000000000000000000000000000001"
    for sig in ["freeRemaining()", "freeLeft()", "freeClaimed()", "freeMinted()",
                "FREE_SUPPLY()", "freeSupply()", "totalMinted()", "maxSupply()",
                "mintOpen()", "totalSupply()", "freePerWallet()", "FREE_PER_WALLET()",
                "FREE_CAP()", "freeAllocation()", "price()", "PRICE()",
                "mintsLeft()", "spotsLeft()", "MAX_SUPPLY()", "MAX_SPOTS()"]:
        try:
            out[sig] = dec_uint(rpc_call("eth_call", [{"to": addr, "data": sel(sig)}, "latest"]))
        except Exception as e:
            out[sig] = "error:" + type(e).__name__
    for sig, data in [("balanceOf(address)", UP),
                      ("mintedBy(address)", UP), ("freeMintedBy(address)", UP),
                      ("freeClaimed(address)", UP), ("freeFor(address)", UP),
                      ("canFreeMint(address)", UP), ("agentIds(address)", UP),
                      ("costOf(address,uint256)", UP + ONE),
                      ("quote(address,uint256)", UP + ONE)]:
        try:
            out[sig] = dec_uint(rpc_call("eth_call", [{"to": addr, "data": sel(sig) + data}, "latest"]))
        except Exception as e:
            out[sig] = "error:" + type(e).__name__
    for sig, data in [("quote(uint256)", ONE), ("costOf(uint256)", ONE)]:
        try:
            out[sig] = dec_uint(rpc_call("eth_call", [{"to": addr, "data": sel(sig) + data}, "latest"]))
        except Exception as e:
            out[sig] = "error:" + type(e).__name__
    try:
        out["AGENT_REGISTRY()"] = rpc_call("eth_call", [{"to": addr, "data": sel("AGENT_REGISTRY()")}, "latest"])
    except Exception as e:
        out["AGENT_REGISTRY()"] = "error:" + type(e).__name__
    try:
        out["agentRegistry()"] = rpc_call("eth_call", [{"to": addr, "data": sel("agentRegistry()")}, "latest"])
    except Exception as e:
        out["agentRegistry()"] = "error:" + type(e).__name__
    return out

def earlier_mints(addr, frm, to):
    f = frm
    while f <= to:
        cto = min(f + 1999, to)
        params = {"blockchain": "bsc", "fromBlock": hex(f), "toBlock": hex(cto),
                  "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC], "address": addr}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
            logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        except Exception as e:
            return {"error": f"{f}-{cto}: {type(e).__name__}:{str(e)[:120]}"}
        if logs:
            b = int(logs[0]["blockNumber"], 16)
            return {"earliest_mint_block": b, "earliest_mint_tx": logs[0].get("transactionHash"),
                    "mints_in_chunk": len(logs), "chunk": f"{f}-{cto}"}
        f = cto + 1
        time.sleep(1.5)
    return {"earliest_mint_block": None, "mints_before_window": 0}

def verdict(rec, abi):
    """Agent-shaped if registry ref / AgentGate / free-mint fn / free-supply const,
    OR costOf(user,1)==0 with agentIds()==registry and mintOpen==1."""
    views = rec.get("free_views", {})
    reg_bytes = rec.get("registry_bytes_direct") is True
    fn_names = []
    if isinstance(abi, list):
        fn_names = [i.get("name", "") for i in abi if i.get("type") == "function"]
    has_free_fn = any("free" in n.lower() and not n.lower().startswith("freeze") for n in fn_names)
    has_mint_fn = any("mint" in n.lower() for n in fn_names)
    has_free_const = any(n in fn_names for n in ("FREE_SUPPLY", "FREE_CAP", "freeSupply"))
    has_gate = ("agentRegistry" in fn_names or "AGENT_REGISTRY" in fn_names
                or "agentId" in fn_names or any("agentgate" in n.lower() for n in fn_names)
                or reg_bytes)
    costof_free = views.get("costOf(address,uint256)") == 0
    agentids_reg = isinstance(views.get("agentIds(address)"), str) and REG.lower() in views["agentIds(address)"].lower()
    mint_open = views.get("mintOpen()") == 1
    if views.get("freeRemaining()") == 0 or views.get("freeLeft()") == 0:
        pool = "exhausted?"
    else:
        pool = "open-or-unknown"
    if (has_gate and (has_free_fn or has_free_const or has_mint_fn)) or (costof_free and agentids_reg and mint_open):
        return "agent-shaped"
    if has_gate and not (has_free_fn or has_free_const):
        return "registry-only-no-free-view"
    return "not-agent-shaped"

first = json.load(open(HF + "run-2026-11-05-1831-scan-firstseen-raw.json"))
scan = json.load(open(HF + "onchain-scan-2026-11-05-1831.json"))
win_from = scan.get("from_block")
win_to = scan.get("to_block")
out = {"scan_window": [win_from, win_to], "first_seen": {}}
for c in first:
    addr = c["address"]
    print(f"== {addr} {c.get('name')} ==", flush=True)
    rec = {"name": c.get("name"), "symbol": c.get("symbol"), "kind": c.get("kind"),
           "window_mints": c.get("mint_count"), "window_minters": c.get("distinct_minters"),
           "window_first_block": c.get("first_block"), "window_last_block": c.get("last_block"),
           "scan_registry_hit": c.get("registry_bytes_hit"), "scan_sourcify": c.get("sourcify")}
    status, abi = sourcify_abi(addr)
    rec["sourcify_retry"] = status
    if isinstance(abi, list):
        fns = [i.get("name", "") for i in abi if i.get("type") == "function"]
        rec["abi_free_funcs"] = sorted({n for n in fns if "free" in n.lower() and not n.lower().startswith("freeze")})
        rec["abi_mint_funcs"] = sorted({n for n in fns if "mint" in n.lower()})
        rec["abi_fn_count"] = len(fns)
        rec["abi_has_agentRegistry"] = "agentRegistry" in fns or "AGENT_REGISTRY" in fns
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        rec["registry_bytes_direct"] = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    except Exception as e:
        rec["registry_bytes_direct"] = "error:" + type(e).__name__
    rec["free_views"] = probe_views(addr)
    rec["earlier_mints"] = earlier_mints(addr, max(0, win_from - 2000), win_from - 1)
    rec["window_first_block_time"] = block_time(c["first_block"])
    em = rec["earlier_mints"].get("earliest_mint_block")
    if em:
        rec["earliest_mint_block_time"] = block_time(em)
    rec["verdict"] = verdict(rec, abi)
    out["first_seen"][addr] = rec
    print(f"   verdict={rec['verdict']} first_block_time={rec['window_first_block_time']}", flush=True)
    time.sleep(1)

json.dump(out, open(HF + "run-2026-11-05-1831-scan-followup.json", "w"), indent=1)
print("WROTE run-2026-11-05-1831-scan-followup.json")
