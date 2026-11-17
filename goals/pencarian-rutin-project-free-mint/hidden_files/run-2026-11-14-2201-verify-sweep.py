#!/usr/bin/env python3
"""Verify sweep finds (run 2201): WhaleFirst, Golden Agents, Cosmic Sentinel, Glitchpilotfox.
Read-only. Sourcify ABI (singular endpoint) + batched eth_calls + getLogs probe.
No preview/mint. Writes run-2026-11-14-2201-verify-sweep.json."""
import json, urllib.request, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
TARGETS = {
    "WhaleFirst": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
    "GoldenAgents": "0x4233c62919cc03168a361c547117c1553c375bfc",
    "CosmicSentinel": "0x88731d1eb41c36f3d705fdb58b658244c06afc36",
    "Glitchpilotfox": "0xda552a0b709d09a2532689c6e39d981f527817b6",
}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000"

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/2201"})
    return urllib.request.urlopen(req, timeout=timeout).read()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(int(n), "064x")

def batch_call(calls, timeout=60):
    """calls: list of (to, data). One JSON-RPC batch; race endpoints."""
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]} for i, (to, data) in enumerate(calls)]
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"})
            out = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            if isinstance(out, list) and out:
                return ep, out
        except Exception as e:
            last = e
    return None, []

def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

def dec_str(hexs):
    try:
        b = bytes.fromhex(hexs[2:])
        if len(b) < 64: return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode(errors="replace")
    except Exception:
        return None

def get_logs(ep, frm, to, addr, timeout=45):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
               "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": addr,
                           "topics": [TRANSFER, "0x" + "0" * 24 + ZERO[2:]]}]}
    req = urllib.request.Request(ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def head_block():
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
                headers={"Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=30).read())
            if r.get("result"): return ep, int(r["result"], 16)
        except Exception:
            continue
    return None, None

out = {"run": "verify-sweep-2201", "targets": {}}
ep_head, head = head_block()
out["head"] = head
print("head:", head, "via", ep_head)

VIEW_SIGS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
             "FREE_SUPPLY()", "FREE_POOL()", "FREE_MAX()", "FREE_CAP()",
             "saleStart()", "saleEnd()", "mintStart()", "mintEnd()",
             "owner()", "agentId()", "agentRegistry()", "price()", "mintCost()",
             "freeLeft()", "freeRemaining()", "mintOpen()", "saleActive()",
             "genesisStart()", "genesisOpen()"]
ADDR_VIEWS = ["freeClaimed(address)", "freeMinted(address)", "mintedBy(address)",
              "freeUsed(address)", "balanceOf(address)", "holdsAgentId(address)"]
STR_VIEWS = ["name()", "symbol()", "contractURI()"]

for name, addr in TARGETS.items():
    t = {"address": addr}
    # Sourcify ABI
    try:
        meta = json.loads(http_get(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20).decode())
        abi = meta.get("abi", [])
        fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
        t["sourcify"] = {"verified": True, "n_fns": len(fns), "fns": fns}
    except Exception as e:
        t["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
        fns = []
    fset = set(fns)
    # Build calls only for views present in ABI (plus totalSupply/totalMinted probes)
    calls, labels = [], []
    for sig in VIEW_SIGS:
        nm = sig.split("(")[0]
        if nm in fset or nm in ("totalSupply", "totalMinted"):
            calls.append((addr, sel(sig))); labels.append(sig)
    for sig in ADDR_VIEWS:
        nm = sig.split("(")[0]
        if nm in fset:
            calls.append((addr, sel(sig) + enc_addr(USER))); labels.append(sig + "(user)")
    str_calls, str_labels = [], []
    for sig in STR_VIEWS:
        if sig.split("(")[0] in fset:
            str_calls.append((addr, sel(sig))); str_labels.append(sig)
    ep, res = batch_call(calls + str_calls)
    views = {}
    for lab, r in zip(labels + str_labels, res or []):
        v = (r or {}).get("result")
        if v and not (r or {}).get("error"):
            if lab in STR_VIEWS:
                views[lab] = dec_str(v)
            else:
                views[lab] = to_int(v)
        else:
            views[lab] = None
    t["views"] = views
    t["rpc_ep"] = ep
    # contractURI external_link (method H)
    if views.get("contractURI()"):
        try:
            cu = views["contractURI()"]
            if cu.startswith("data:application/json;base64,"):
                import base64
                cj = json.loads(base64.b64decode(cu.split(",", 1)[1]).decode())
                t["contractURI_json"] = cj
            else:
                t["contractURI_raw"] = cu[:300]
        except Exception as e:
            t["contractURI_error"] = str(e)[:150]
    # first-mint probe: up to 10 x 1000-block windows backwards from head (address-filtered)
    probe = {"windows": [], "first_mint_block": None, "error": None}
    if head:
        for i in range(10):
            to_b = head - i * 1000
            frm_b = to_b - 999
            ok = False
            for ep2 in EPS:
                try:
                    r = get_logs(ep2, frm_b, to_b, addr)
                    logs = r.get("result") or []
                    probe["windows"].append({"from": frm_b, "to": to_b, "n": len(logs), "ep": ep2})
                    if logs:
                        probe["first_mint_block"] = int(logs[0]["blockNumber"], 16)
                        probe["first_mint_tx"] = logs[0]["transactionHash"]
                    ok = True
                    break
                except Exception as e:
                    probe.setdefault("errors", []).append(f"{ep2}: {type(e).__name__}: {str(e)[:100]}")
            if not ok:
                probe["error"] = "all endpoints failed window %d" % i
                break
            if probe["first_mint_block"] is not None:
                break
    t["first_mint_probe"] = probe
    out["targets"][name] = t
    print(name, "| sourcify:", t["sourcify"].get("verified"), "| views:",
          {k: v for k, v in views.items() if v is not None}, "| first_mint_block:",
          probe.get("first_mint_block"))

json.dump(out, open(BASE + "run-2026-11-14-2201-verify-sweep.json", "w"), indent=1)
print("wrote verify-sweep.json")
