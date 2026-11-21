#!/usr/bin/env python3
"""Verify 3 sweep finds (run free-mint-search 2026-11-20 07:01 WIB) + 2 Boltbook addrs.
Read-only. Writes run-2026-11-20-0701-verify-new.json. No preview/mint/claim."""
import json, subprocess, time
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0701"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0x" + keccak(b"Transfer(address,address,uint256)").hex()

def sel(sig):
    return keccak(sig.encode())[:4].hex()
def enc_addr(a):
    return "0" * 24 + a[2:].lower()
def encode(sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user":
        d += enc_addr(USER)
    elif arg == "one":
        d += "%064x" % 1
    elif arg == "user1":
        d += enc_addr(USER) + "%064x" % 1
    return d

def rpc(payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", RPC,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return json.loads(o.stdout)

def batch_calls(calls):
    out = [None] * len(calls)
    for i in range(0, len(calls), 20):
        chunk = calls[i:i + 20]
        payload = [{"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                    "params": [{"to": c[0], "data": c[1]}, "latest"]} for j, c in enumerate(chunk)]
        try:
            resp = rpc(payload)
            by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
            for j in range(len(chunk)):
                it = by_id.get(j + 1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    out[i + j] = it["result"]
                elif "error" in it:
                    out[i + j] = {"error": str(it["error"])[:120]}
                else:
                    out[i + j] = None
        except Exception as e:
            for j in range(len(chunk)):
                out[i + j] = {"error": f"transport {type(e).__name__}"}
        time.sleep(1)
    return out

def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64:
            return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "replace")
    except Exception:
        return None

def read_views(addr, viewdefs):
    calls, labels = [], []
    for vk, (sig, arg) in viewdefs.items():
        calls.append((addr, encode(sig, arg)))
        labels.append(vk)
    res = batch_calls(calls)
    views = {}
    for vk, v in zip(labels, res):
        if isinstance(v, dict):
            views[vk] = v
        elif isinstance(v, str):
            if vk in ("name", "symbol", "contractURI"):
                views[vk] = dec_str(v)
            elif vk in ("owner", "core", "agentRegistry"):
                views[vk] = "0x" + v[-40:] if len(v) >= 42 else v
            else:
                try:
                    views[vk] = int(v, 16)
                except Exception:
                    views[vk] = v
        else:
            views[vk] = v
    return views

def sourcify(addr):
    try:
        o = subprocess.run(["curl", "-sL", "--max-time", "25",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
                           capture_output=True, text=True).stdout
        m = json.loads(o)
        abi = m.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
                      "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
                      "freeMinted", "freeCardsRemaining"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate", "AGENT_ID", "AGENT_ID_REGISTRY",
                                  "agentIdOf", "hasAgentId"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and \
            bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"verified": True, "S1": s1, "S2": s2, "is_nft": bool(names & {"ownerOf", "tokenURI"}),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
                "fns": sorted(names)}
    except Exception as e:
        return {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}

def get_code(addr):
    try:
        r = rpc([{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                  "params": [addr, "latest"]}])
        code = r[0].get("result", "")
        return code
    except Exception as e:
        return {"error": str(e)[:100]}

def first_mint_logs(addr, from_block, to_block):
    """One eth_getLogs: Transfer from zero address. Returns count/first or error."""
    try:
        r = rpc([{"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                  "params": [{"fromBlock": hex(from_block), "toBlock": hex(to_block),
                              "address": addr, "topics": [TRANSFER, ZERO_TOPIC]}]}], timeout=60)
        if isinstance(r, list) and r and isinstance(r[0], dict) and "error" in r[0]:
            return {"error": str(r[0]["error"])[:200]}
        if isinstance(r, list):
            return {"count": len(r),
                    "first": (r[0].get("blockNumber"), r[0].get("transactionHash")) if r else None,
                    "last": (r[-1].get("blockNumber"),) if r else None}
        return {"error": f"unexpected {str(r)[:200]}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:150]}"}

blk = rpc([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])
head = int(blk[0]["result"], 16)
out = {"run": RUN, "head": head, "projects": {}, "boltbook_addrs": {}}

# ---- Boltbook new addresses: bytecode registry grep ----
for a in ("0x3b1bab350fc3eb708d0aa66cc0b453d50d50deb5",
          "0xc5dc1f2aa1d962789f1a06fdb199a25c038d7777"):
    code = get_code(a)
    if isinstance(code, dict):
        out["boltbook_addrs"][a] = code
    else:
        low = code.lower()
        out["boltbook_addrs"][a] = {
            "code_len": len(code), "is_contract": len(code) > 2,
            "registry_bytes": REG in low,
            "is_minimal_proxy": low.startswith("0x363d3d373d3d3d363d73"),
            "sourcify": sourcify(a),
        }

# ---- Pocket Ai (NFT) ----
POCKET = "0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102"
POCKET_TOK = "0x7D72D6D06d1240F927039fB364e1B55bd4473d80"
pocket_views = {
    "totalSupply": ("totalSupply()", None), "totalMinted": ("totalMinted()", None),
    "freeClaimed": ("freeClaimed()", None), "freeMinted": ("freeMinted()", None),
    "FREE_SUPPLY": ("FREE_SUPPLY()", None), "freeSupply": ("freeSupply()", None),
    "freeLeft": ("freeLeft()", None), "mintOpen": ("mintOpen()", None),
    "mintActive": ("mintActive()", None), "MAX_SUPPLY": ("MAX_SUPPLY()", None),
    "balanceOf_user": ("balanceOf(address)", "user"),
    "mintedBy_user": ("mintedBy(address)", "user"),
    "freeMintedByWallet_user": ("freeMintedByWallet(address)", "user"),
    "name": ("name()", None), "symbol": ("symbol()", None),
    "contractURI": ("contractURI()", None), "owner": ("owner()", None),
}
out["projects"]["Pocket Ai"] = {
    "nft": POCKET, "token": POCKET_TOK,
    "sourcify_nft": sourcify(POCKET), "sourcify_token": sourcify(POCKET_TOK),
    "views_nft": read_views(POCKET, pocket_views),
    "code_nft": (lambda c: {"len": len(c), "registry_bytes": REG in c.lower()} if isinstance(c, str) else c)(get_code(POCKET)),
    "first_mint_window_100k": first_mint_logs(POCKET, head - 100000, head),
}

# ---- YAMA (Track C sale) ----
YAMA_SALE = "0x86D779fc4d83044cCECCb53639f9a98E367D6E46"
YAMA_TOK = "0xa84EA20a667B3b1859aB9a9984FF5F03D8688aE2"
yama_views = {
    "freeSharesRemaining": ("freeSharesRemaining()", None),
    "freeClaimed": ("freeClaimed()", None),
    "freeClaimed_user": ("freeClaimed(address)", "user"),
    "freeLeft": ("freeLeft()", None),
    "freeAvailable": ("freeAvailable()", None),
    "quote_user_1": ("quote(address,uint256)", "user1"),
    "totalSupply": ("totalSupply()", None),
    "name": ("name()", None), "symbol": ("symbol()", None),
    "owner": ("owner()", None),
}
out["projects"]["YAMA PROJECT"] = {
    "sale": YAMA_SALE, "token": YAMA_TOK,
    "sourcify_sale": sourcify(YAMA_SALE), "sourcify_token": sourcify(YAMA_TOK),
    "views_sale": read_views(YAMA_SALE, yama_views),
    "code_sale": (lambda c: {"len": len(c), "registry_bytes": REG in c.lower()} if isinstance(c, str) else c)(get_code(YAMA_SALE)),
    "first_mint_window_100k": first_mint_logs(YAMA_SALE, head - 100000, head),
}

# ---- Agent Vein (Track C token; sale via core()) ----
VEIN_TOK = "0x17ccdcd9763e824a59c78f60c10e6976d5663479"
vein_tok_views = {
    "core": ("core()", None), "name": ("name()", None), "symbol": ("symbol()", None),
    "totalSupply": ("totalSupply()", None), "decimals": ("decimals()", None),
    "freeClaimed": ("freeClaimed()", None), "freeMinted": ("freeMinted()", None),
    "FREE_SUPPLY": ("FREE_SUPPLY()", None), "agentRegistry": ("agentRegistry()", None),
    "owner": ("owner()", None),
}
vt = read_views(VEIN_TOK, vein_tok_views)
sale = vt.get("core") if isinstance(vt.get("core"), str) and vt["core"].startswith("0x") else None
vein = {"token": VEIN_TOK, "sourcify_token": sourcify(VEIN_TOK),
        "views_token": vt, "sale_via_core": sale,
        "first_mint_window_100k": first_mint_logs(VEIN_TOK, head - 100000, head)}
if sale:
    vein["sourcify_sale"] = sourcify(sale)
    vein["views_sale"] = read_views(sale, yama_views)
    vein["code_sale"] = (lambda c: {"len": len(c), "registry_bytes": REG in c.lower()} if isinstance(c, str) else c)(get_code(sale))
    vein["first_mint_sale_window_100k"] = first_mint_logs(sale, head - 100000, head)
out["projects"]["Agent Vein"] = vein

json.dump(out, open(BASE + f"run-{RUN}-verify-new.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:9000])
print("HEAD", head)
