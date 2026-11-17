#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 07:04 WIB.
Leg1: Sourcify ABI shape-check (S1/S2) for 2 new feed contracts.
Leg2: Boltbook EN+ZH quick fetch (20s cap each), extract 0x addrs, diff vs seen.
Leg4: re-read same 21-item focus set as 07:01 run, diff vs 07:01 values.
Bridge: count check only (file mtime unchanged since 11-08).
Read-only on-chain; writes only run-2026-11-14-0704-*.json/md + hot-leg-seen.json notes.
No preview/mint. Target <2 min; legs that stall are skipped, not waited on."""
import json, re, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()
out = {"started_wib": "2026-11-14T07:04+07:00", "run": "hot-leg 0704"}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=25):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

# ---------- Leg 1: shape-check ----------
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "-m", "25", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=30)
        if p.returncode != 0 or not p.stdout:
            return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
        return json.loads(p.stdout).get("abi", []), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"
def call1(addr, data, timeout=15):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": addr, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = post_rpc(ep, payload, timeout=timeout)
            if isinstance(r, dict) and isinstance(r.get("result"), str) and r["result"] not in (None, "0x"):
                return r["result"]
        except Exception:
            continue
    return None

NEW = [("0xc8e1Fd7eE35C49F8F44C25e902Ce1E401788CD5b", "2026-11-14T00:03:49Z"),
       ("0x4a4b031E501A82bb6E1Ef292F910A59e178ba9c5", "2026-11-14T00:03:34Z")]
shape = []
for addr, vat in NEW:
    abi, err = fetch_abi(addr)
    if abi is None:
        shape.append({"address": addr, "verifiedAt": vat, "S1": None, "S2": None, "error": err})
        print(addr, "ABI FETCH FAILED", err, flush=True); continue
    names = set(); fns = {}
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"]); fns.setdefault(e["name"], []).append(e)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = any(n.lower().startswith("quote") or n.lower() in ("cost", "price", "getcost") for n in names)
    free_views = [n for n in names if n in FREE_VIEWS]
    abi_text = json.dumps(abi).lower()
    has_registry_ref = ("agentgate" in abi_text or "agentregistry" in abi_text or
                        "agent_id" in abi_text or "agentid" in abi_text or
                        REGISTRY.lower() in abi_text)
    is_token = all(n in names for n in ("name", "symbol", "decimals", "totalSupply"))
    noarg_free = any(n in ("mintFree", "freeMint", "claimFree") and fns[n] and
                     len(fns[n][0].get("inputs", [])) == 0 for n in names)
    s1 = bool(has_mint and has_quote and free_views and has_registry_ref)
    s2 = bool(is_token and noarg_free and
              (("freeClaimed" in names or "freeMinted" in names) and
               ("FREE_SLOTS" in names or "FREE_SUPPLY" in names)) and has_registry_ref)
    agent_id = None
    if "AGENT_ID" in names:
        r = call1(addr, sel("AGENT_ID()"))
        agent_id = to_int(r)
    shape.append({"address": addr, "verifiedAt": vat, "S1": s1, "S2": s2,
                  "n_fns": len(names), "has_mint": has_mint, "has_quote": has_quote,
                  "free_views": free_views, "has_registry_ref": has_registry_ref,
                  "is_token": is_token, "noarg_free": noarg_free, "AGENT_ID": agent_id,
                  "fns_sample": sorted(names)[:25]})
    print(addr, "S1", s1, "S2", s2, "fns", len(names), flush=True)
out["leg1_shape"] = shape

# ---------- Leg 2: Boltbook EN + ZH (20s cap each) ----------
seen = json.load(open(BASE + "hot-leg-seen.json"))
bb = {}
for lang, url in [("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")]:
    try:
        p = subprocess.run(["curl", "-sS", "-L", "-m", "20", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=25)
        body = p.stdout or ""
        addrs = sorted(set(a for a in re.findall(r"0x[a-fA-F0-9]{40}", body)))
        new_addrs = [a for a in addrs if a not in seen and a.lower() not in [k.lower() for k in seen]]
        bb[lang] = {"ok": p.returncode == 0 and len(body) > 1000, "bytes": len(body),
                    "addrs": len(addrs), "new_addrs": new_addrs}
        print("boltbook", lang, bb[lang]["ok"], bb[lang]["bytes"], "addrs", len(addrs),
              "new", new_addrs, flush=True)
    except Exception as e:
        bb[lang] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
        print("boltbook", lang, "FAILED", bb[lang]["error"], flush=True)
out["leg2_boltbook"] = bb

# ---------- Leg 4: re-read focus set ----------
U = [USER]
ITEMS = {
 "WoozCode": ("0xfF172b79d040faefA1Bf34B47151edc87130246E", [
    ("totalSnippets","totalSnippets()",[]),("currentCommit","currentCommit()",[]),
    ("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),
    ("commitEnd_1","commitEnd(uint256)",[1]),
    ("priceFor_user","priceFor(address)",U),("holdsAgentId_user","holdsAgentId(address)",U),
    ("snippetsOf_1_user","snippetsOf(uint256,address)",[1, USER])]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "NOISE": ("0xBA5352A3A05Ec637394810D791a412E78A349247", [
    ("totalMinted","totalMinted()",[]),("remainingSupply","remainingSupply()",[]),
    ("mintOpen","mintOpen()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("priceFor_user","priceFor(address)",U),("freeUsed_user","freeUsed(address)",U)]),
 "DragonAgents": ("0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("price","price()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "AngelEye-07bD": ("0x07bD6DbbEf508ad83BA2C557ED979732488894A1", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "NovaRemnants": ("0x38C1695eb72B7522c8d6452a4CE27122532A0d69", [
    ("totalRemnants","totalRemnants()",[]),("genesisOpen","genesisOpen()",[]),
    ("genesisStart","genesisStart()",[]),("currentCycle","currentCycle()",[]),
    ("priceFor_user","priceFor(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "AbsurdAgentNFT": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("mintStartTime","mintStartTime()",[]),("isEligible_user","isEligible(address)",U)]),
 "B77D": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("standardRemaining","standardRemaining()",[]),("legendaryRemaining","legendaryRemaining()",[]),
    ("freeCount","freeCount()",[]),("hasAgentId_user","hasAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Zero": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AgentZENITH": ("0x699b6397986cc6c444069efe692023b1253dc26d", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("freeMintedPerWallet_user","freeMintedPerWallet(address)",U),
    ("mintedPerWallet_user","mintedPerWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("hasAgentId_user","hasAgentId(address)",U),
    ("paused","paused()",[]),("mintedByWallet_user","mintedByWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("AGENT_ID","AGENT_ID()",[]),
    ("balanceOf_user","balanceOf(address)",U),("owner","owner()",[])]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("AGENT_ID","AGENT_ID()",[]),
    ("balanceOf_user","balanceOf(address)",U),("owner","owner()",[])]),
 "NOTV": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("FREE_SHARES","FREE_SHARES()",[]),
    ("freeStart","freeStart()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
}

def chunked(items, n=15):
    for i in range(0, len(items), n):
        yield items[i:i + n]

reads = {}
prev = {}
try:
    prev = json.load(open(BASE + "run-2026-11-14-0701-reread.json"))["reads"]
except Exception as e:
    prev = {}
    out["leg4_prev_missing"] = str(e)[:120]
ok = 0
block = None
for name, (addr, views) in ITEMS.items():
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if isinstance(res, list) and len(res) == len(calls):
                got = res
                if block is None:
                    blk = post_rpc(ep, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=15)
                    if isinstance(blk, list) and blk and isinstance(blk[0], dict):
                        block = to_int(blk[0].get("result"))
                break
        except Exception:
            continue
    if got is None:
        reads[name] = {"address": addr, "views": None, "error": "rpc-failed-all-endpoints"}
        print(name, "RPC FAILED", flush=True); continue
    vs = {}
    for it, k in zip(got, keys):
        if isinstance(it, dict) and "error" in it:
            vs[k] = None
        else:
            vs[k] = to_int(it.get("result")) if isinstance(it, dict) else None
    reads[name] = {"address": addr, "views": vs}
    ok += 1
    print(name, json.dumps(vs), flush=True)
out["leg4_reads"] = reads
out["leg4_ok"] = ok
out["leg4_total"] = len(ITEMS)
out["block"] = block

# diff vs 07:01
diffs = {}
for name, r in reads.items():
    if r.get("views") is None: continue
    pv = (prev.get(name) or {}).get("views") or {}
    ch = {k: (pv.get(k), v) for k, v in r["views"].items() if pv.get(k) != v}
    if ch: diffs[name] = ch
out["leg4_diffs_vs_0701"] = diffs

# ---------- Bridge (count only) ----------
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    import os
    out["bridge"] = {"contracts": len(br.get("contracts", {})),
                     "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}

out["elapsed_s"] = round(time.time() - t0, 1)
print("ELAPSED", out["elapsed_s"], "leg4 ok", ok, "/", len(ITEMS), flush=True)
json.dump(out, open(BASE + "run-2026-11-14-0704.json", "w"), indent=1)

# update hot-leg-seen.json: record the 2 new feed contracts + re-read notes
from datetime import datetime, timezone, timedelta
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
for s in shape:
    a = s["address"]
    seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed-0704",
               "verifiedAt": s.get("verifiedAt"), "S1": s.get("S1"), "S2": s.get("S2"),
               "note": f"feedshape-0704: S1={s.get('S1')} S2={s.get('S2')} fns={s.get('n_fns')} "
                       f"mint={s.get('has_mint')} quote={s.get('has_quote')} free_views={s.get('free_views')} "
                       f"registry_ref={s.get('has_registry_ref')} AGENT_ID={s.get('AGENT_ID')}"}
def note_append(addr, text):
    if isinstance(seen.get(addr), dict):
        seen[addr]["note"] = (seen[addr].get("note", "") + text)[:900]
for name, r in reads.items():
    if r.get("views"):
        note_append(r["address"], f" | REREAD-0704: " + ", ".join(f"{k}={v}" for k, v in r["views"].items() if v is not None)[:300])
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
print("seen updated; total entries:", len(seen), flush=True)
