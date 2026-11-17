#!/usr/bin/env python3
"""Run 2026-11-14 18:01 WIB: (a) shape-check 3 genuinely new Sourcify feed contracts
vs hot-leg 17:59; (b) on-chain probe of Boltbook-new addresses: Storm Agent
0x57cb78a8 (99% free), Sora Agent 0x5aaa9dca (99% free), BUGHOUND 0x8a7be94d,
CAVE 0xF8654BB7. Read-only; writes run-2026-11-14-1801-probe.json. No preview/mint."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
t0 = time.time()
out = {"started_wib": "2026-11-14T18:01+07:00", "shape": [], "probe": {}}

def curl(url, timeout=30):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except Exception as e:
        return None

FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeRemaining","freeSupply","freeCount","freeMintsLeft","freeSharesLeft"}
def shape_check(addr, vat):
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 30)
    try:
        abi = json.loads(raw).get("abi", []) if raw else []
    except Exception:
        return {"address": addr, "verifiedAt": vat, "S1": None, "S2": None, "status": "abi-fetch-failed"}
    names = set(); fns = {}
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"]); fns.setdefault(e["name"], []).append(e)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId",
                              "agentGate","AgentGate","AGENT_ID_REGISTRY",
                              "agentIdRegistry","AGENT_ID"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed","freeMinted"})
              and (names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref)
    return {"address": addr, "verifiedAt": vat, "S1": s1, "S2": s2,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names), "status": "checked"}

NEW_FEED = [
 ("0xe778a8401cb1b835c806eebe7025538263195335", "2026-11-14T11:01:23Z"),
 ("0x5a5eff4e9c5bad00e97cc33d6e6d26983509eeb8", "2026-11-14T11:01:20Z"),
 ("0xcbbaf9b2b3393d75d2fd1ebf344af1b43ef292e8", "2026-11-14T11:00:35Z"),
]
for a, v in NEW_FEED:
    r = shape_check(a, v)
    out["shape"].append(r)
    print("shape", a[:10], "S1", r.get("S1"), "S2", r.get("S2"), "mint", r.get("has_mint"),
          "quote", r.get("has_quote"), "free", r.get("free_views"), "agent", r.get("agent_ref"),
          "n", r.get("n_fns"), r.get("status"), flush=True)

# ---- on-chain probe ----
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
def post_rpc(ep, payload, timeout=120):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

PROBE = {
 "Storm Agent": ("0x57cb78a895b783e210659a8b3371971641b968a3", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",[USER]),("freeUsed_user","freeUsed(address)",[USER]),
    ("balanceOf_user","balanceOf(address)",[USER]),("owner","owner()",[]),
    ("AGENT_ID","AGENT_ID()",[]),("contractURI","contractURI()",[]),
    ("genesisStart","genesisStart()",[]),("mintStart","mintStart()",[]),
    ("price","price()",[]),("mintCost_1","mintCost(uint256)",[1])]),
 "Sora Agent": ("0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",[USER]),("freeUsed_user","freeUsed(address)",[USER]),
    ("balanceOf_user","balanceOf(address)",[USER]),("owner","owner()",[]),
    ("AGENT_ID","AGENT_ID()",[]),("contractURI","contractURI()",[]),
    ("genesisStart","genesisStart()",[]),("mintStart","mintStart()",[]),
    ("price","price()",[]),("mintCost_1","mintCost(uint256)",[1])]),
 "BUGHOUND": ("0x8a7be94d1c36a60bcdd155d37faf84403b8a26ae", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",[USER]),("balanceOf_user","balanceOf(address)",[USER]),
    ("owner","owner()",[]),("AGENT_ID","AGENT_ID()",[])]),
 "CAVE": ("0xF8654BB769B48fD4c619bfFD5a5fEED066d6a85F", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",[USER]),("balanceOf_user","balanceOf(address)",[USER]),
    ("owner","owner()",[]),("AGENT_ID","AGENT_ID()",[])]),
}
def code_of(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}, 60)
            if isinstance(r, dict) and r.get("result") is not None:
                return r["result"]
        except Exception:
            continue
    return None

for name, (addr, views) in PROBE.items():
    code = code_of(addr)
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call",
                      "params":[{"to":addr,"data":build_data(sig,args)},"latest"]})
        meta.append(key)
    res = {}
    for ep in EPS:
        try:
            r = post_rpc(ep, calls, 120)
            if not isinstance(r, list) or len(r) != len(calls):
                print(" probe", name, "ep", ep, "bad shape", flush=True); continue
            for it, key in zip(r, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    res[key] = None
                else:
                    v = it["result"]
                    res[key] = to_int(v[:66]) if len(v) >= 66 else v
            break
        except Exception as e:
            print(" probe", name, "ep", ep, "exc", str(e)[:80], flush=True); continue
    out["probe"][name] = {"address": addr, "code_len": (len(code)-2)//2 if code else None,
                          "registry_bytes": (REGISTRY[2:].lower() in (code or "").lower()),
                          "views": res}
    print("probe", name, json.dumps(res), "code_len", out["probe"][name]["code_len"],
          "registry_bytes", out["probe"][name]["registry_bytes"], flush=True)

try:
    r = post_rpc(EPS[0], {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, 60)
    out["block"] = int(r["result"], 16) if isinstance(r, dict) and r.get("result") else None
except Exception:
    out["block"] = None
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1801-probe.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"], "block", out["block"])
