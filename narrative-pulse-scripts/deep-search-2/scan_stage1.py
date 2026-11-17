#!/usr/bin/env python3
import sys, json, time, urllib.request
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
from eth_utils import keccak
from fast_rpc import race, batch, call_many

FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
def sel(sig): return keccak(text=sig)[:4].hex()
def pad(a): return "0"*24 + a[2:].lower()
def enc_call(sig, args):
    # args: list of addresses (only getPair/decimals/balanceOf used here)
    data = sel(sig)
    for a in args:
        data += pad(a)
    return "0x" + data

COINS = {
 "COLLECT": "0x4b3d30992f003c8167699735f5ab2831b2a087d3",
 "AEON": "0x277add739c6e0477616948357af9e79fe1ec9b80",
 "ESPORTS": "0xf39e4b21c84e737df08e2c3b32541d856f508e48",
}
# getPair + decimals in one batch via call_many (to,data)
calls=[]
for name, ca in COINS.items():
    calls.append((FACTORY, enc_call("getPair(address,address)", [ca, WBNB])))
    calls.append((ca, "0x"+sel("decimals()")))
res = call_many(calls)
for i,(name,ca) in enumerate(COINS.items()):
    pair_raw = res[2*i]; dec_raw = res[2*i+1]
    pair = "0x"+pair_raw[-40:] if pair_raw and len(pair_raw)>=42 else pair_raw
    dec = int(dec_raw,16) if dec_raw else None
    print(name, ca, "pair=", pair, "decimals=", dec, flush=True)

tip = int(race("eth_blockNumber", []),16)
print("TIP", tip, flush=True)

def header_ts(blk):
    r = race("eth_getBlockByNumber", [hex(blk), False])
    return int(r["timestamp"],16)

# Gecko pools
for name, ca in COINS.items():
    url = f"https://api.geckoterminal.com/api/v2/networks/bsc/tokens/{ca}/pools"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        pools=[]
        for p in data.get("data",[]):
            attrs=p.get("attributes",{})
            pid=p.get("id","")
            addr = pid.split("_")[-1] if "_" in pid else pid
            pools.append({"id":pid,"addr":addr,"created":attrs.get("pool_created_at"),"name":attrs.get("name")})
        pools.sort(key=lambda x: x["created"] or "")
        print(f"GECKO {name} n={len(pools)}", flush=True)
        for p in pools[:10]:
            print("  ", p, flush=True)
        with open(f"/tmp/gecko_{name}.json","w") as f: json.dump(pools,f,indent=1)
    except Exception as e:
        print(f"GECKO {name} FAILED {type(e).__name__}: {e}", flush=True)

# binary search creation block for each gecko earliest created_at
import datetime
for name in COINS:
    try:
        pools=json.load(open(f"/tmp/gecko_{name}.json"))
        if not pools: continue
        created=pools[0]["created"]
        ts=int(datetime.datetime.fromisoformat(created.replace("Z","+00:00")).timestamp())
        print(f"BINSEARCH {name} created={created} ts={ts}", flush=True)
        lo, hi = 0, tip
        # find smallest block with ts >= target
        while lo<hi:
            mid=(lo+hi)//2
            try: t=header_ts(mid)
            except Exception as e:
                print(" header fail", mid, e); time.sleep(1); continue
            if t<ts: lo=mid+1
            else: hi=mid
        print(f"CREATION {name} block={lo} ts={header_ts(lo)} target={ts}", flush=True)
    except Exception as e:
        print(f"BINSEARCH {name} FAILED {e}", flush=True)
