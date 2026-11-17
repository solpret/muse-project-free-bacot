import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
from fast_rpc import race
from ankr import get_logs
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FACTORY = "0xcA143Ce32Fe78f1f7019d7D551a6402fC5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
USDT = "0x55d398326f99059fF775485246999027B3197955"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, data, tries=3):
    for _ in range(tries):
        try: return race("eth_call", [{"to": addr, "data": data}, "latest"])
        except Exception: time.sleep(2)
    return None
out = {}
for name, tok in [("A","0x9791d92B63a566AC578e6070ee1F8546C8b2153B"),
                  ("B","0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7")]:
    d = {}
    for other, olabel in [(WBNB,"WBNB"),(USDT,"USDT")]:
        data = sel("getPair(address,address)") + enc(tok) + enc(other)
        raw = call(FACTORY, data)
        pair = ("0x"+raw[-40:]) if raw and len(raw) >= 42 else None
        d[f"pair_{olabel}"] = pair
        if pair and pair != "0x0000000000000000000000000000000000000000":
            # token0/token1 + reserves
            t0 = call(pair, sel("token0()")); t1 = call(pair, sel("token1()"))
            res = call(pair, sel("getReserves()"))
            d[f"pair_{olabel}_token0"] = ("0x"+t0[-40:]) if t0 else None
            d[f"pair_{olabel}_token1"] = ("0x"+t1[-40:]) if t1 else None
            d[f"pair_{olabel}_reserves_raw"] = res
    out[f"DYOR_token_{name}"] = d
    print(name, json.dumps(d, indent=1), flush=True)
# First claim bound: first Transfer OUT of each token contract (mint/claim distribution)
# Claim emits Transfer from contract itself? claim() likely transfers from contract balance.
# Use Ankr: any Transfer where address=token and topic1 = token contract (from=contract) is a claim payout.
# Existence probe binary search over [131000000, head] for Transfer from token contract.
HEAD = None
for _ in range(5):
    try:
        HEAD = int(race("eth_blockNumber", []), 16); break
    except Exception: time.sleep(3)
out["head"] = HEAD
print("HEAD", HEAD, flush=True)
def has_claim_payout(tok, fb, tb):
    try:
        r = get_logs(tok, fb, tb, topics=[TRANSFER, "0x"+tok[2:].lower().rjust(64,"0")])
        logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
        return len(logs) > 0
    except Exception as e:
        print(f"  payout probe FAIL {fb}-{tb}: {type(e).__name__}", flush=True)
        return None
if HEAD:
    for name, tok in [("A","0x9791d92B63a566AC578e6070ee1F8546C8b2153B"),
                      ("B","0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7")]:
        f = has_claim_payout(tok, 131000000, HEAD)
        print(f"payout-any-{name}:", f, flush=True)
        out[f"payout_any_{name}"] = f
        if f:
            a, b = 131000000, HEAD
            while a < b:
                mid = (a+b)//2
                ff = has_claim_payout(tok, a, mid)
                if ff is None: break
                if ff: b = mid
                else: a = mid+1
            out[f"first_payout_block_{name}"] = a
            try:
                blk = race("eth_getBlockByNumber", ["0x"+format(a,"x"), False])
                out[f"first_payout_ts_{name}"] = int(blk.get("timestamp","0x0"),16)
            except Exception: pass
            print(f"first-payout-{name}: block {a} ts {out.get('first_payout_ts_'+name)}", flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-0931-dyor3.json","w"), indent=1)
print("DONE", flush=True)
