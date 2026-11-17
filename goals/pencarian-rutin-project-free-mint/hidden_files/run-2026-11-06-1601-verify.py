#!/usr/bin/env python3
"""Run 1601: verify 2 fresh Boltbook leads (Soul Agent, THE WALL) + re-read
Quantumfarm (snapshot early lead, Boltbook pace update). Read-only.
- Sourcify ABI classify (agent-shape: mint + quote/free views + registry ref)
- On-chain reads via public RPCs (name/symbol/supply/free views/slot/contractURI)
- First-mint bound via Ankr getLogs (module import, address-filtered Transfer
  from zero, 1000-block chunks, backwards until an empty chunk).
Never writes the main snapshot; writes run-2026-11-06-1601-verify.json only.
"""
import json, urllib.request, urllib.error, subprocess, time, sys, base64
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post  # noqa: E402

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1601"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
from Crypto.Hash import keccak

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def raw_str(to, data, timeout=6):
    """eth_call returning raw hex (for string/bytes returns)."""
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

def decode_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        # abi string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for i in range(3):
        try:
            out = subprocess.run(["curl","-sL","--max-time","12","-A","Mozilla/5.0",url],
                                 capture_output=True, text=True, timeout=18)
            if out.returncode == 0 and out.stdout.strip():
                data = json.loads(out.stdout)
                if "abi" in data: return ("verified", data["abi"])
                return ("not_verified", None)
        except Exception:
            pass
        time.sleep(1)
    return ("error", None)

FREE_VIEWS = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused",
              "freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted",
              "freeremaining","free_slots","free_supply","free_amount","freequota",
              "remainingfree","mintedby","hasminted","canfreemint","claimedfree",
              "freeleftfor","freemintsleft","mintsleft"]
QUOTE_FNS = ["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost",
             "price","mintprice","feefor","costo","mintcost"]
GATE_WORDS = ["agentid","agent_id","agentregistry","agent_registry","agentgate",
              "agent_gate","hasagentid","isagent"]

def classify(abi):
    funcs = [it.get("name","") for it in abi if isinstance(abi, list)
             and isinstance(it, dict) and it.get("type") == "function"]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name","symbol","decimals","totalsupply")]
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "agent_shaped": bool(mint_fns) and bool(free_views) and bool(gate)}

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"

def ankr_logs(from_block, to_block, address):
    params = {"blockchain": "bsc", "fromBlock": hex(from_block), "toBlock": hex(to_block),
              "address": [address],
              "topics": [[TRANSFER], [ZERO_TOPIC]]}
    try:
        body = ankr_post("ankr_getLogs", params, timeout=30)
    except Exception as e:
        return ("error", str(e))
    if isinstance(body, dict) and "error" in body:
        return ("error", str(body["error"]))
    logs = body.get("logs", []) if isinstance(body, dict) else []
    return ("ok", logs)

def block_ts(blk):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(blk), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r: out = json.load(r)
            if "result" in out and out["result"]:
                return int(out["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "freeLeft()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
         "mintedBy(address)", "freeUsed(address)", "balanceOf(address)",
         "quote(address,uint256)", "costOf(address,uint256)",
         "freeQuota()", "remainingFree()", "spotsLeft()"]

TARGETS = {
    "Soul Agent": "0x8fdb9411753c58476a41f7b88a44989f8d687d63",
    "THE WALL": "0xa804bBBe09fa2F5832d11D09329cc4230D1d7899",
    "Quantumfarm": "0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010",
}

head = block()
print("HEAD", head, flush=True)
out = {"head": head, "targets": {}}
for name, addr in TARGETS.items():
    d = {"address": addr}
    st, abi = fetch_abi(addr)
    d["sourcify"] = st
    if abi is not None:
        d.update(classify(abi))
    else:
        d["agent_shaped"] = False
    # string views
    for sig in ["name()", "symbol()", "contractURI()"]:
        hx = raw_str(addr, sel(sig))
        d[sig.split("(")[0]] = decode_str(hx) if hx else None
    for sig in VIEWS:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, json.dumps(d, default=str), flush=True)
    out["targets"][name] = d
    json.dump(out, open(f"{BASE}/run-{TS}-verify.json", "w"), indent=1)

# ---- first-mint bound for SOUL + WALL (backwards 1000-block chunks) ----
for name in ["Soul Agent", "THE WALL"]:
    addr = TARGETS[name]
    to_blk = head
    first_blk = None
    chunks = 0
    while chunks < 40 and to_blk > 0:
        frm = max(0, to_blk - 999)
        st, logs = ankr_logs(frm, to_blk, addr)
        chunks += 1
        if st == "error":
            print(name, "ankr error chunk", frm, to_blk, logs, flush=True)
            break
        if not logs:
            break  # empty chunk -> first mint is after frm
        first_blk = min(int(l["blockNumber"], 16) for l in logs)
        to_blk = frm - 1
    if first_blk is not None:
        ts = block_ts(first_blk)
        import datetime
        wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
        print(name, "FIRST_MINT block", first_blk, "ts", ts, "wib", wib, "chunks", chunks, flush=True)
        out["targets"][name]["firstMintBlock"] = first_blk
        out["targets"][name]["firstMintWib"] = wib
    else:
        print(name, "FIRST_MINT not found in", chunks, "chunks back from head", flush=True)
        out["targets"][name]["firstMintBlock"] = None
    json.dump(out, open(f"{BASE}/run-{TS}-verify.json", "w"), indent=1)

print("VERIFY DONE", flush=True)
