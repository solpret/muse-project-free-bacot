#!/usr/bin/env python3
"""Run 2026-11-06 0609 WIB (part 2): track_c-only re-read (8 key views) + bridge check.
Same RPC helpers as the 0601 reread script. Read-only; never writes snapshot."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0609"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

TC = {
 "OSK": "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
 "NIULAI": "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
 "KillZero-K0-sale": "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",
 "DROID": "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
 "IMARS": "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
 "ASOC-43cE": "0x43cEef9313CB8c4ca3757bA841C44DF40A223205",
 "SENBAZURU-b215": "0xb21583A08581278BcF925351a99C61A4562C62f0",
 "FABE": "0xB44AC34F6089B7c5c99CBc1643E22838e67C9D4d",
 "QAGENT-2": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
 "ShibAgent-R2": "0x016a148e728b8d61b2440ed311946ac06d4b5648",
 "DeY": "0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
 "BoxBigem-3Ee9": "0x3Ee92296D663378D42521273aAA4779BDa8e25dD",
 "FANBEIMAO-824d": "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
 "Ikigai-Ihigi": "0x3611455bE1FC2c6987FE9d016971b7E40B341684",
 "Hongbao-HONGBAO": "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97",
 "Nvagent-NVGT-28Fe": "0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2",
 "Soarm-SOARM": "0x4a02e3824b301a1bf6a8230e56b44b526174ca97",
 "SAFUAI": "0xbd6087fc30f2395344020cb190255c56cbc517bd",
}
TC_VIEWS = ["opened()", "launched()", "freeMinted()", "freeSharesRemaining()",
            "freeClaimed(address)", "saleEnded()", "totalMinted()", "sharesMinted()"]

def read_item(args):
    name, addr = args
    d = {"address": addr}
    for sig in TC_VIEWS:
        key = sig.split("(")[0]
        if "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d

blk = block()
print("BLOCK", blk, flush=True)
t0 = time.time()
out = {"block": blk, "track_c": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_item, list(TC.items())):
        out["track_c"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-tc.json", "w"), indent=1)
print("DONE in %.1fs block %s" % (time.time() - t0, blk), flush=True)

try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap, "method": "full-text case-insensitive match on onchain-snapshot.json"},
              open(f"{BASE}/run-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
