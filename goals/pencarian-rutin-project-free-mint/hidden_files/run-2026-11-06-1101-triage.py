#!/usr/bin/env python3
"""Run 2026-11-06 1101 WIB triage: full on-chain reads + first-mint bound for
agent-shaped first-seen contracts from scan window 131941909-131942908.
Excludes Laser Agents + Worldygg Tree (excluded list). Log-only items are
listed in the run log, not triaged here.
Method: (1) threaded full-state reads; (2) 48h-boundary single-chunk Ankr
getLogs test (block ~head-384000); hits there => age >48h => AGE-EXCLUDED.
(3) backward chunked search (cap 40 chunks of 1000) to find first mint +
block timestamp; log count vs totalSupply corroborates completeness."""
import json, sys, time, urllib.request, datetime
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1101"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
ZERO = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

CANDS = {
 "Thundra": "0xdd97B0A6680c6cF4880ce1759185418888e5F48f",
 "Prompt Seeds": "0x8696d7f90b4c3D5564215a20B7d7ffb9742F5281",
 "Dunora": "0x443CF08bbD6cF3FC900f107949b8e8ad69392e1a",
 "Agent Miner": "0xCe67038f8703Dff3Aadaf77d41823b4b039C9446",
 "sidecoo Agent Pass": "0xf3f0F05EbEB73543F569369DF5Dc29c0f0418f99",
 "Agent Apes": "0xbF18B0CfDd9e4FD138a362A92F29674197Fdb886",
 "sidecoo Daily": "0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8",
 "Shard Id": "0x5C46de8D0c5DfDF535558d363F492967cd5e146b",
 "Pixel Sentinels": "0x4e4e43f84E2E80716d03153F3c675e8E715Fa698",
 "Bianren": "0xd24A02198e12B35faDE9DD8334Fb7f6333CD05eF",
 "Agent Fronk": "0xF4F2A87100Bb8fECF562cF4cCaC6D615C424316c",
 "BN Agent File": "0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1",
 "SoulWallet Agent": "0x30Ffd5d0b2d3908A38fA31016F148E6b651587A2",
 "Bridgely": "0x603fc142BFeF4e8e86972b04e9629Bc971d7970A",
 "Dropnix": "0xB95531Eb859c556B7c9521a99B7b67BA12519564",
 "Candlix": "0x263D87E3B4a284B6E4B0b80F7945B6095113ffE6",
 "Arcadion": "0x8d0f3FCdaec965120C53a753a456Ed85A6624aD3",
 "Coffeeling": "0x4b896313B21A1190f257f1560dF03A22CCc77FDC",
 "Mindstream": "0x2C631D53dA9C921D4C0e82290864f87D920E2938",
 "Labyrinthos": "0xF3F5Cc63D94e97ea3A425094609A1bAa830A271A",
 "VampireVibes": "0xa5FB4e0E83837E9c7035b47C2f02D7dB075563dE",
 "Core Reactor": "0x199734eda03e4a34EC06D754d45D817e51741985",
 "AGENT GLYPHS": "0x622c41902107e43bba06C865086A449777240D7A",
}
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "quote(address,uint256)",
         "mintedBy(address)", "freeUsed(address)", "balanceOf(address)",
         "freeLeft(address)", "freeFor(address)", "price()", "spotsLeft()"]

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

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def read_item(args):
    name, addr = args
    d = {"address": addr}
    for sig in VIEWS:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    return name, d

def block_ts(blk):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(blk), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                out = json.load(r)
            ts = int(out["result"]["timestamp"], 16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception:
            continue
    return None

def ankr_logs(addr, frm, to):
    body = ankr_post("ankr_getLogs", {
        "blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
        "pageSize": 1000, "decodeLogs": False,
        "topics": [TRANSFER, ZERO],
        "address": addr}, timeout=30)
    logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
    return [int(l["blockNumber"], 16) for l in logs]

head = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r: head = int(json.load(r)["result"], 16); break
    except Exception: continue
print("HEAD", head, flush=True)
BOUNDARY48 = head - 384000
print("48H-BOUNDARY block", BOUNDARY48, block_ts(BOUNDARY48), flush=True)

t0 = time.time()
out = {"head": head, "boundary48": BOUNDARY48, "reads": {}, "firstmint": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_item, list(CANDS.items())):
        out["reads"][name] = d
        print(name, d, flush=True)
print("READS done %.1fs" % (time.time() - t0), flush=True)

for name, addr in CANDS.items():
    r = out["reads"][name]
    sup = r.get("totalSupply") or r.get("totalMinted")
    try:
        hits48 = ankr_logs(addr, BOUNDARY48, BOUNDARY48 + 999)
    except Exception as e:
        print(name, "48h-test ERROR", repr(e), flush=True)
        out["firstmint"][name] = {"error": repr(e)}
        continue
    if hits48:
        fm = {"verdict": "AGE-EXCLUDED", "evidence": f"mints exist at 48h-boundary block {BOUNDARY48} ({block_ts(BOUNDARY48)})",
              "boundary_hits": len(hits48)}
        print(name, "AGE-EXCLUDED (mints at 48h boundary)", flush=True)
        out["firstmint"][name] = fm
        continue
    earliest = None; total_logs = 0; chunks = 0; nohit_before = None
    to_b = head
    while chunks < 40:
        frm_b = max(0, to_b - 999)
        try:
            logs = ankr_logs(addr, frm_b, to_b)
        except Exception as e:
            print(name, "backward chunk error", frm_b, repr(e), flush=True)
            break
        chunks += 1
        if not logs:
            nohit_before = (frm_b, to_b)
            break
        earliest = min(logs); total_logs += len(logs)
        to_b = frm_b - 1
    fm = {"earliest_found_block": earliest,
          "earliest_found_wib": block_ts(earliest) if earliest else None,
          "logs_found": total_logs, "supply": sup,
          "chunks_searched": chunks, "nohit_chunk_before": nohit_before,
          "complete": (sup is not None and total_logs >= sup)}
    print(name, "first-mint bound block", earliest, fm["earliest_found_wib"],
          "logs", total_logs, "supply", sup, "complete", fm["complete"], flush=True)
    out["firstmint"][name] = fm
    json.dump(out, open(f"{BASE}/run-{TS}-triage.json", "w"), indent=1)
print("TRIAGE done %.1fs" % (time.time() - t0), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-triage.json", "w"), indent=1)
