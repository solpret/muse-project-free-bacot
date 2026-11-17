#!/usr/bin/env python3
"""Verification run 2026-11-14 14:31 WIB (free-mint-search run 1431).
- Hashcat Depot 0x5aff... (new Boltbook): Sourcify ABI + on-chain reads + tokenURI + registry bytes.
- Saturnagent 0xef87... ('9 left' per Boltbook): quick supply/free reads.
- ECHO 0xb3ca... (ERC20 recheck): Sourcify ABI sale-shape check.
- YUANBAO first-mint attempt: eth_getLogs Transfer-from-zero, chunked windows
  around WANGCAI first-mint block (133437037, 06:08 WIB), dataseed endpoints.
Read-only; writes run-2026-11-14-1431-verify.json. No preview/mint."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
REG = "60b9262456de011f7d15a54cdd8c48baa8b022f"
t0 = time.time()
out = {"started_wib": "2026-11-14T14:31+07:00"}

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
def post_rpc(ep, payload, timeout=60):
    outp = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                           "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                          capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(outp)
def batch_read(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls): continue
            r = {}
            for it, key in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    r[key] = None
                else:
                    v = it["result"]
                    r[key] = to_int(v[:66]) if len(v) >= 66 else v
            return r, ep
        except Exception:
            continue
    return None, None
def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), str):
                return r["result"], ep
        except Exception:
            continue
    return None, None
def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl"})
        d = json.load(urllib.request.urlopen(req, timeout=60))
        abi = d.get("abi") or []
        fns = sorted(set(f.get("name") for f in abi if f.get("type") == "function"))
        return {"match": d.get("match"), "verifiedAt": d.get("verifiedAt"),
                "fns": fns, "n_fns": len(fns)}, None
    except Exception as e:
        return None, str(e)[:200]

U = [USER]
# --- Hashcat Depot ---
HADE = "0x5aff123300685b6e08aa4396227baf44aabbd4ed"
hade_views = [("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("owner","owner()",[]),("tokenURI_1","tokenURI(uint256)",[1]),
    ("contractURI","contractURI()",[]),("priceFor_user","priceFor(address)",U),
    ("quote_user_1","quote(address,uint256)",[USER,1]),
    ("freeLeft","freeLeft()",[]),("freeFor_user","freeFor(address)",U)]
hade_reads, hade_ep = batch_read(HADE, hade_views)
hade_abi, hade_abi_err = sourcify_abi(HADE)
code, code_ep = get_code(HADE)
out["hashcat"] = {"address": HADE, "reads": hade_reads, "reads_ep": hade_ep,
                  "sourcify": hade_abi, "sourcify_err": hade_abi_err,
                  "code_len": len(code) if code else None,
                  "registry_bytes_in_code": (REG in code.lower()) if code else None,
                  "code_ep": code_ep}
print("hashcat reads:", json.dumps(hade_reads), flush=True)
print("hashcat sourcify:", json.dumps(hade_abi)[:400] if hade_abi else hade_abi_err, flush=True)
print("hashcat registry bytes:", out["hashcat"]["registry_bytes_in_code"], "code_len:", out["hashcat"]["code_len"], flush=True)

# --- Saturnagent ---
SAT = "0xef870a9b4a529373fb2e174b59ca7a66eb018074"
sat_views = [("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("priceFor_user","priceFor(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("owner","owner()",[])]
sat_reads, sat_ep = batch_read(SAT, sat_views)
sat_abi, sat_abi_err = sourcify_abi(SAT)
out["saturnagent"] = {"address": SAT, "reads": sat_reads, "reads_ep": sat_ep,
                      "sourcify": sat_abi, "sourcify_err": sat_abi_err}
print("saturnagent reads:", json.dumps(sat_reads), flush=True)
print("saturnagent sourcify:", json.dumps(sat_abi)[:300] if sat_abi else sat_abi_err, flush=True)

# --- ECHO ERC20 shape ---
ECHO = "0xb3ca4b947872f92307bcb5b69fb3a675abfd8f41"
echo_abi, echo_err = sourcify_abi(ECHO)
out["echo"] = {"address": ECHO, "sourcify": echo_abi, "sourcify_err": echo_err}
print("echo sourcify:", json.dumps(echo_abi)[:300] if echo_abi else echo_err, flush=True)

# --- YUANBAO first-mint attempt (chunked eth_getLogs) ---
YUAN = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def get_logs(ep, frm, to, topics):
    r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                      "params": [{"fromBlock": hex(frm), "toBlock": hex(to),
                                  "address": YUAN, "topics": topics}]}, timeout=60)
    if isinstance(r, dict) and isinstance(r.get("result"), list):
        return r["result"], None
    return None, str(r)[:200]
yuan_logs = {"attempts": []}
# window 1: around WANGCAI first-mint block, 2000 blocks
for (frm, to) in [(133437000, 133438999), (133435000, 133436999), (133439000, 133440999)]:
    ok = None
    for ep in EPS:
        try:
            logs, err = get_logs(ep, frm, to, [TRANSFER, ZERO_TOPIC])
            if logs is not None:
                ok = {"from": frm, "to": to, "ep": ep, "n": len(logs),
                      "first": logs[0] if logs else None}
                break
            yuan_logs["attempts"].append({"from": frm, "to": to, "ep": ep, "err": err})
        except Exception as e:
            yuan_logs["attempts"].append({"from": frm, "to": to, "ep": ep, "err": str(e)[:120]})
    if ok:
        yuan_logs.setdefault("windows_ok", []).append(ok)
        print("yuanbao logs window", frm, "-", to, "n=", ok["n"], flush=True)
        if ok["n"]:
            break
out["yuanbao_first_mint"] = yuan_logs
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1431-verify.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
