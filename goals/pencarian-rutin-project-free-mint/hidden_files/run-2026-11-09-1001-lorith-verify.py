#!/usr/bin/env python3
"""Lorith 0x65B3... fresh on-chain verification for run 1001 (READ-ONLY).
Fetches Sourcify ABI, computes selectors, eth_call views via fast_rpc single
calls (avoid batch-revert quirk), confirms first mint via ankr_getLogs +
dataseed block timestamp (Ankr timestamps are fake - never use)."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from ankr import ankr_post
from Crypto.Hash import keccak

ADDR = "0x65B3b58C6fe1B98087b022AB41c54a2987494ddF"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call(fn_sig, args_hex=""):
    data = sel(fn_sig) + args_hex
    r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])])[0]
    return r

def u256(v):
    if v is None: return None
    try: return int(v, 16)
    except Exception: return None

def addr_arg(a):
    return "00"*12 + a[2:].lower()

out = {"contract": ADDR, "run": "1001", "wib": "2026-11-09 ~10:40 WIB"}
# head block (via batch, race() stalls per 2201 patch note)
head = batch([("eth_blockNumber", [])])[0]
out["head_block"] = int(head, 16) if head else None

# ABI from Sourcify
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{ADDR}", headers={"User-Agent": "free-bacot/1.0"})
    abi_doc = json.load(urllib.request.urlopen(req, timeout=20))
    abi = abi_doc.get("stdJson", {}).get("abi") or abi_doc.get("abi") or []
    out["sourcify_http"] = 200
    out["abi_fns"] = sorted({e.get("name") for e in abi if e.get("type") == "function"})
except Exception as e:
    out["sourcify_http"] = f"ERR {e}"
    abi = []

views = {
    "name": ("name()", ""),
    "symbol": ("symbol()", ""),
    "totalSupply": ("totalSupply()", ""),
    "totalMinted": ("totalMinted()", ""),
    "freeMinted": ("freeMinted()", ""),
    "freeLeft": ("freeLeft()", ""),
    "FREE_SUPPLY": ("FREE_SUPPLY()", ""),
    "FREE_PER_WALLET": ("FREE_PER_WALLET()", ""),
    "MAX_SUPPLY": ("MAX_SUPPLY()", ""),
    "MAX_PER_WALLET": ("MAX_PER_WALLET()", ""),
    "PRICE": ("PRICE()", ""),
    "SALE_END": ("SALE_END()", ""),
    "mintOpen": ("mintOpen()", ""),
    "saleOpen": ("saleOpen()", ""),
    "owner": ("owner()", ""),
    "AGENT_ID_REGISTRY": ("AGENT_ID_REGISTRY()", ""),
    "PAYEE": ("PAYEE()", ""),
    "freeClaimed_user": ("freeClaimed(address)", addr_arg(USER)),
    "freeAvailable_user": ("freeAvailable(address)", addr_arg(USER)),
    "mintedBy_user": ("mintedBy(address)", addr_arg(USER)),
    "balanceOf_user": ("balanceOf(address)", addr_arg(USER)),
    "quoteFor_user_1": ("quoteFor(address,uint256)", addr_arg(USER) + "%064x" % 1),
    "hasAgentId_user": ("hasAgentId(address)", addr_arg(USER)),
    "contractURI": ("contractURI()", ""),
}
raw = {}
for k, (sig, args) in views.items():
    try:
        r = call(sig, args)
        raw[k] = r
    except Exception as e:
        raw[k] = f"ERR {e}"
out["raw"] = raw
for k in ("totalSupply","totalMinted","freeMinted","freeLeft","FREE_SUPPLY","FREE_PER_WALLET","MAX_SUPPLY","MAX_PER_WALLET","PRICE","SALE_END","mintOpen","saleOpen","freeClaimed_user","freeAvailable_user","mintedBy_user","balanceOf_user","quoteFor_user_1","hasAgentId_user"):
    out[k] = u256(raw.get(k)) if isinstance(raw.get(k), str) and raw.get(k,"").startswith("0x") else raw.get(k)
for k in ("owner","AGENT_ID_REGISTRY","PAYEE"):
    v = raw.get(k)
    out[k] = ("0x" + v[-40:]) if isinstance(v, str) and v.startswith("0x") and len(v) >= 42 else v
for k in ("name","symbol"):
    v = raw.get(k)
    if isinstance(v, str) and v.startswith("0x"):
        try:
            ln = int(v[130:194], 16); out[k] = bytes.fromhex(v[194:194+ln*2]).decode()
        except Exception: out[k] = v
    else: out[k] = v
cu = raw.get("contractURI")
if isinstance(cu, str) and cu.startswith("0x"):
    try:
        ln = int(cu[130:194], 16); out["contractURI_decoded"] = bytes.fromhex(cu[194:194+ln*2]).decode()
    except Exception: out["contractURI_decoded"] = cu
else: out["contractURI_decoded"] = cu
out["registry_matches"] = (out.get("AGENT_ID_REGISTRY") or "").lower() == REGISTRY.lower()
out["owner_is_zero"] = (out.get("owner") or "").lower() == "0x0000000000000000000000000000000000000000"

# first-mint confirmation: Transfer from zero on Lorith, window around deployment
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00"*32
first_block, first_tx = 132509105, "0xc101e78506c4d7337e3d2175229e89b2ebf1838889fa5290ae4dc6dd41a68672"
try:
    res = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132508900), "toBlock": hex(132509105),
        "address": ADDR.lower(), "topics": [TRANSFER, ZERO]})
    logs = res.get("logs", []) if isinstance(res, dict) else []
    out["firstmint_window_logs"] = len(logs)
    if logs:
        b = min(int(l["blockNumber"], 16) for l in logs)
        out["firstmint_window_earliest_block"] = b
        # confirm no mint before 132509105 in this window
        out["firstmint_confirmed_block"] = b
        txs = [l["transactionHash"] for l in logs if int(l["blockNumber"],16)==b]
        out["firstmint_txs_at_block"] = txs
except Exception as e:
    out["firstmint_window_err"] = str(e)
# block timestamp via dataseed (NOT ankr)
try:
    blk = batch([("eth_getBlockByNumber", [hex(132509105), False])])[0]
    out["firstmint_block_ts"] = int(blk["timestamp"], 16) if blk else None
    import datetime
    if out["firstmint_block_ts"]:
        out["firstmint_block_wib"] = datetime.datetime.fromtimestamp(out["firstmint_block_ts"], datetime.timezone(datetime.timedelta(hours=7))).isoformat()
except Exception as e:
    out["firstmint_block_ts_err"] = str(e)

out["free_pct"] = (out["freeMinted"]/out["FREE_SUPPLY"]*100) if isinstance(out.get("freeMinted"), int) and isinstance(out.get("FREE_SUPPLY"), int) and out["FREE_SUPPLY"] else None
json.dump(out, open("run-2026-11-09-1001-lorith-verify.json","w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "raw"}, indent=1))
