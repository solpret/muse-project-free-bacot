#!/usr/bin/env python3
"""Parent triage run 2301: Hexrotta / HOURGLASS / DRAGON (new S1 finds from Subagent B).
Lean read-only verification: fresh views + user slot + owner + first-mint probe.
No preview/mint/claim/sign. Writes only run-2026-11-08-2301-triage-new.{py,log,json}."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as fr_post
from eth_hash.auto import keccak
import ankr as ankr_mod

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/", "https://bsc-dataseed4.bnbchain.org/"]
ZERO = "0x0000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def sel(sig):
    return "0x" + keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0x" + a.lower().replace("0x", "").rjust(64, "0")

def enc_u(n):
    return "0x" + format(n, "064x")

def call(to, data, timeout=25):
    for ep in EPS:
        try:
            r = fr_post(ep, [{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": to, "data": data}, "latest"]}], timeout=timeout)
            res = r[0].get("result")
            if res is not None:
                return res
            err = r[0].get("error")
            if err:
                return {"_error": str(err)}
        except Exception as e:
            continue
    return None

def dec_u(res):
    if res is None or isinstance(res, dict):
        return None
    try:
        return int(res, 16)
    except Exception:
        return None

def dec_bool(res):
    v = dec_u(res)
    return None if v is None else bool(v)

def dec_str(res):
    if res is None or isinstance(res, dict):
        return None
    try:
        b = bytes.fromhex(res[2:])
        if len(b) < 64:
            return None
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode("utf-8", "replace")
    except Exception:
        return None

def block_ts(num):
    for ep in EPS:
        try:
            r = fr_post(ep, [{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(num), False]}], timeout=25)
            ts = r[0]["result"]["timestamp"]
            return int(ts, 16)
        except Exception:
            continue
    return None

def wib(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime(ts + 7 * 3600)) if ts else None

def head_block():
    for ep in EPS:
        try:
            r = fr_post(ep, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=25)
            return int(r[0]["result"], 16)
        except Exception:
            continue
    return None

# views: (key, signature, arg-builder or None, decoder)
VIEWS = [
    ("name", "name()", None, dec_str),
    ("symbol", "symbol()", None, dec_str),
    ("totalSupply", "totalSupply()", None, dec_u),
    ("mintOpen", "mintOpen()", None, dec_bool),
    ("freeClaimed_total", "freeClaimed()", None, dec_u),
    ("freeMintedTotal", "freeMintedTotal()", None, dec_u),
    ("freeCount", "freeCount()", None, dec_u),
    ("freeMinted", "freeMinted()", None, dec_u),
    ("freeLeft", "freeLeft()", None, dec_u),
    ("FREE_CAP", "FREE_CAP()", None, dec_u),
    ("FREE_SUPPLY", "FREE_SUPPLY()", None, dec_u),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", None, dec_u),
    ("PRICE", "PRICE()", None, dec_u),
    ("price", "price()", None, dec_u),
    ("mintCost", "mintCost()", None, dec_u),
    ("freeWindowOpen", "freeWindowOpen()", None, dec_u),
    ("freeWindowEnd", "freeWindowEnd()", None, dec_u),
    ("FREE_WINDOW", "FREE_WINDOW()", None, dec_u),
    ("deployTime", "deployTime()", None, dec_u),
    ("contractURI", "contractURI()", None, dec_str),
    ("owner", "owner()", None, None),  # address decode
    ("AGENT_ID", "AGENT_ID()", None, None),
    ("agentRegistry", "agentRegistry()", None, None),
    ("REGISTRY", "REGISTRY()", None, None),
    ("agentIdRegistry", "agentIdRegistry()", None, None),
    ("balanceOf_user", "balanceOf(address)", "addr", dec_u),
    ("freeClaimed_user", "freeClaimed(address)", "addr", dec_u),
    ("freeUsed_user", "freeUsed(address)", "addr", dec_u),
    ("freeFor_user", "freeFor(address)", "addr", dec_u),
    ("freeLeft_user", "freeLeft(address)", "addr", dec_u),
    ("quote_user_1_addr", "quote(address,uint256)", "addr_u1", None),  # tuple decode
    ("quote_1", "quote(uint256)", "u1", None),
]
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def dec_addr(res):
    if res is None or isinstance(res, dict) or len(res) < 42:
        return None
    return "0x" + res[-40:]

def dec_tuple_u(res):
    if res is None or isinstance(res, dict):
        return None
    try:
        b = bytes.fromhex(res[2:])
        return [int.from_bytes(b[i:i + 32], "big") for i in range(0, len(b), 32)]
    except Exception:
        return None

CONTRACTS = {
    "Hexrotta": "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9",
    "HOURGLASS": "0xD743c793b23D1adE2099892B010d4F4530d44E0a",
    "DRAGON": "0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4",
}

def read_contract(name, addr):
    out = {"address": addr}
    for key, sig, arg, dec in VIEWS:
        data = sel(sig)
        if arg == "addr":
            data += enc_addr(USER)[2:]
        elif arg == "u1":
            data += enc_u(1)[2:]
        elif arg == "addr_u1":
            data += enc_addr(USER)[2:] + enc_u(1)[2:]
        res = call(addr, data)
        if res is None:
            out[key] = None
        elif isinstance(res, dict):
            out[key] = {"error": res.get("_error")}
        else:
            if key in ("owner", "AGENT_ID", "agentRegistry", "REGISTRY", "agentIdRegistry"):
                out[key] = dec_addr(res)
            elif key in ("quote_user_1_addr", "quote_1"):
                out[key] = dec_tuple_u(res)
            else:
                out[key] = dec(res) if dec else res
    return out

def first_mint_probe(addr):
    """Probe chunks for earliest Transfer-from-zero. Returns dict with probes."""
    head = head_block()
    probes = []
    # probe points going back: recent first
    points = [head - 1000, 132420000, 132415000, 132410000, 132400000, 132380000,
              132350000, 132300000, 132200000, 132100000, 132000000, 131900000,
              131197748]
    seen_first = None
    for p in points:
        if p is None or p < 0:
            continue
        frm, to = p, min(p + 999, head)
        try:
            resp = ankr_mod.get_logs(addr, frm, to, topics=[TRANSFER])
            if isinstance(resp, dict):
                res = resp.get("result", resp)
                logs = res.get("logs", []) if isinstance(res, dict) else []
            elif isinstance(resp, list):
                logs = resp
            else:
                logs = []
            n_from_zero = 0
            first_blk = None
            for lg in logs:
                topics = lg.get("topics", [])
                if len(topics) >= 2 and topics[1].lower() == ("0x" + "0" * 64):
                    n_from_zero += 1
                    b = int(lg.get("blockNumber", "0x0"), 16)
                    if first_blk is None or b < first_blk:
                        first_blk = b
            probes.append({"chunk": [frm, to], "logs": len(logs), "from_zero": n_from_zero,
                           "first_block_in_chunk": first_blk})
            if n_from_zero and seen_first is None:
                seen_first = first_blk
        except Exception as e:
            probes.append({"chunk": [frm, to], "error": str(e)[:200]})
    return {"head": head, "probes": probes, "earliest_from_zero_in_probes": seen_first}

def main():
    log = open(BASE + "/run-2026-11-08-2301-triage-new.log", "w")
    def p(*a):
        print(*a, flush=True)
        print(*a, file=log, flush=True)
    head = head_block()
    p("head:", head, "wib:", wib(block_ts(head)) if head else None)
    result = {"head": head, "contracts": {}}
    for name, addr in CONTRACTS.items():
        p(f"\n=== {name} {addr} ===")
        r = read_contract(name, addr)
        for k, v in r.items():
            p(f"  {k}: {v}")
        result["contracts"][name] = r
        # registry match?
        for rk in ("AGENT_ID", "agentRegistry", "REGISTRY", "agentIdRegistry"):
            if isinstance(r.get(rk), str) and r[rk].lower() == REGISTRY.lower():
                p(f"  REGISTRY MATCH via {rk}")
        # first-mint probe
        fm = first_mint_probe(addr)
        p("  first-mint probes:")
        for pr in fm["probes"]:
            p("   ", pr)
        if fm["earliest_from_zero_in_probes"]:
            b = fm["earliest_from_zero_in_probes"]
            ts = block_ts(b)
            p(f"  earliest from-zero in probes: block {b} = {wib(ts)}")
            fm["earliest_wib"] = wib(ts)
        result["contracts"][name]["first_mint_probe"] = fm
    json.dump(result, open(BASE + "/run-2026-11-08-2301-triage-new.json", "w"), indent=1)
    p("\nwritten run-2026-11-08-2301-triage-new.json")
    log.close()

if __name__ == "__main__":
    main()
