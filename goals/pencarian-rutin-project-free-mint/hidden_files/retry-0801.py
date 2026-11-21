#!/usr/bin/env python3
"""Retry leg run 2026-11-20 08:01 WIB: re-read contracts whose 0801 main re-read
returned null/transport-error views (dataseed chunk flakiness), plus TURTLE/LION
(not in the 49-contract view list) and YAMA quote raw decode. Read-only.
Writes run-2026-11-20-0801-reread-retry.json."""
import json, subprocess, time
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"

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

SIG = {
    "totalSupply": ("totalSupply()", None), "totalMinted": ("totalMinted()", None),
    "freeClaimed": ("freeClaimed()", None), "freeClaimed_user": ("freeClaimed(address)", "user"),
    "FREE_SUPPLY": ("FREE_SUPPLY()", None), "freeSupply": ("freeSupply()", None),
    "freeLeft": ("freeLeft()", None), "balanceOf_user": ("balanceOf(address)", "user"),
    "mintedBy_user": ("mintedBy(address)", "user"),
    "freeMintedByWallet_user": ("freeMintedByWallet(address)", "user"),
    "quote_user_1": ("quote(address,uint256)", "user1"),
    "mintOpen": ("mintOpen()", None), "name": ("name()", None), "symbol": ("symbol()", None),
    "contractURI": ("contractURI()", None), "owner": ("owner()", None),
    "launched": ("launched()", None), "failed": ("failed()", None),
    "isRefundPhase": ("isRefundPhase()", None), "totalShares": ("totalShares()", None),
    "tokenClaimed_user": ("tokenClaimed(address)", "user"),
    "refundClaimed_user": ("refundClaimed(address)", "user"),
    "freeMinted": ("freeMinted()", None),
}
STRING_VIEWS = {"name", "symbol", "contractURI"}
ADDR_VIEWS = {"owner"}

def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64:
            return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "replace")
    except Exception:
        return None

main = json.load(open(BASE + "run-2026-11-20-0801-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0801-interim.json"))
null_names = [k for k, v in interim["velocity"].items() if v["new_supply"] is None]
# also contracts whose views carry transport JSONDecodeError dicts
extra = set()
for name, entry in main["reads"].items():
    for vk, v in entry["views"].items():
        if isinstance(v, dict) and "JSONDecodeError" in str(v.get("error", "")):
            extra.add(name)
retry_names = sorted(set(null_names) | extra)
print("retry contracts:", len(retry_names), retry_names)

calls, labels = [], []
for name in retry_names:
    entry = main["reads"][name]
    addr = entry["address"]
    for vk in entry["views"]:
        if vk not in SIG:
            continue
        sig, arg = SIG[vk]
        calls.append((addr, encode(sig, arg)))
        labels.append((name, vk))
# TURTLE / LION (snapshot keys) - standard view set
snap = json.load(open(BASE + "onchain-snapshot.json"))
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    addr = snap["contracts"][name]["address"]
    for vk in ("totalSupply", "freeClaimed", "FREE_SUPPLY", "freeSupply", "freeLeft",
               "balanceOf_user", "mintOpen"):
        sig, arg = SIG[vk]
        calls.append((addr, encode(sig, arg)))
        labels.append((name, vk))
# YAMA quote raw (two-word return) - keep raw hex
YAMA_SALE = "0x86D779fc4d83044cCECCb53639f9a98E367D6E46"
calls.append((YAMA_SALE, encode("quote(address,uint256)", "user1")))
labels.append(("YAMA PROJECT", "quote_user_1_raw"))

def curl_batch(payload):
    o = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST", RPC,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return o.stdout

results = [None] * len(calls)
t0 = time.time()
for i in range(0, len(calls), 5):
    chunk = calls[i:i + 5]
    payload = [{"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                "params": [{"to": c[0], "data": c[1]}, "latest"]} for j, c in enumerate(chunk)]
    try:
        resp = json.loads(curl_batch(payload))
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by_id.get(j + 1, {})
            if "result" in it and it["result"] not in (None, "0x"):
                results[i + j] = it["result"]
            elif "error" in it:
                results[i + j] = {"error": str(it["error"])[:160]}
            else:
                results[i + j] = None
    except Exception as e:
        for j in range(len(chunk)):
            results[i + j] = {"error": f"transport {type(e).__name__}: {str(e)[:100]}"}
    time.sleep(1)
elapsed = round(time.time() - t0, 1)

reads = {}
raws = {}
for (name, vk), v in zip(labels, results):
    if vk == "quote_user_1_raw":
        raws[(name, vk)] = v
        continue
    entry = reads.setdefault(name, {"address": None, "views": {}})
    if isinstance(v, dict):
        entry["views"][vk] = v
    elif isinstance(v, str):
        if vk in STRING_VIEWS:
            entry["views"][vk] = dec_str(v)
        elif vk in ADDR_VIEWS:
            entry["views"][vk] = "0x" + v[-40:] if len(v) >= 42 else v
        else:
            try:
                entry["views"][vk] = int(v, 16)
            except Exception:
                entry["views"][vk] = v
    else:
        entry["views"][vk] = v
for name in retry_names:
    reads.setdefault(name, {"address": main["reads"][name]["address"], "views": {}})
    reads[name]["address"] = main["reads"][name]["address"]
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    reads.setdefault(name, {"address": snap["contracts"][name]["address"], "views": {}})
    reads[name]["address"] = snap["contracts"][name]["address"]

# YAMA quote raw decode into words
yq = raws.get(("YAMA PROJECT", "quote_user_1_raw"))
yama_quote = None
if isinstance(yq, str) and yq.startswith("0x"):
    h = yq[2:]
    words = [int(h[i:i + 64], 16) for i in range(0, len(h), 64)] if len(h) % 64 == 0 else None
    yama_quote = {"raw": yq, "words": words}
elif isinstance(yq, dict):
    yama_quote = yama_quote = {"error": yq}

try:
    blk = json.loads(curl_batch([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]))
    block = int(blk[0]["result"], 16)
except Exception as e:
    block = main.get("block", "ERR")
    print("blockNumber fetch failed, fallback to main block:", block, type(e).__name__)
out = {"started_wib": "2026-11-20 08:1x WIB", "block": block, "elapsed_s": elapsed,
       "n_calls": len(calls), "reads": reads, "yama_quote": yama_quote}
json.dump(out, open(BASE + "run-2026-11-20-0801-reread-retry.json", "w"), indent=1)
ok = sum(1 for v in results if isinstance(v, str))
print("calls:", len(calls), "ok:", ok, "elapsed:", elapsed, "block:", block)
print("yama_quote:", yama_quote)
for name in ("HIVE Agents", "Bubblebruin", "binanceai-mint", "bsccat-sale",
             "Prosperity Turtle Agents", "Guardian Lion Agents"):
    print(name, json.dumps(reads.get(name, {}).get("views", {}))[:400])
