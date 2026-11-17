import json, sys, time
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr
from Crypto.Hash import keccak
TRANSFER = '0x' + keccak.new(digest_bits=256, data=b'Transfer(address,address,uint256)').hexdigest()
ZERO = '0x' + '00'*32
SAMPLE = [
    ("Auditrix",  "0x13eEa6a99720e2C9dDEda9B28d7eF5306B7322F4", 131393366, True),
    ("Synaptik",  "0xE5523bf6AA0F92aCC7d2898F65596a0A088a8f0F", 131359859, False),
    ("Robogent",  "0x5eA7E757dfc4654f7478841BD30175bd7F186e24", 131375872, False),
    ("Yydsgent",  "0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61", 131382200, False),
    ("Deepvane",  "0xDd682169A6699eA7feF7E6E15C727Cf970C98d97", 131361211, False),
    ("Animora",   "0x150699b44B36b542B9F954272bDD0aC3fDD9519b", 131351277, False),
    ("Sentrix",   "0xb7dce0412BB89dE075413855875D1DB31AC89E8f", 131342312, False),
    ("Emberforge","0x6C90D2302bF0a9DaaF453f3Af2CD79f3C9B79CF8", 131258343, True),
]
def fetch(ca, fb, tb):
    r = ankr.get_logs(ca, fb, tb, topics=[TRANSFER, ZERO])
    logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
    return logs
def fetch_window_earliest(ca, fb, tb):
    """Return logs in [fb,tb] ascending, splitting on 1000-cap."""
    logs = fetch(ca, fb, tb)
    if len(logs) < 1000:
        logs.sort(key=lambda l: (int(l["blockNumber"],16), int(l.get("logIndex", "0x0"),16)))
        return logs, False
    mid = (fb + tb)//2
    if mid <= fb:
        return [], True
    left, _ = fetch_window_earliest(ca, fb, mid)
    return left, True
out = {}
for name, ca, anchor, exact in SAMPLE:
    mints, capped, err = [], False, None
    fb = anchor
    try:
        while fb < anchor + 4000 and len(mints) < 100:
            tb = min(fb + 200, anchor + 4000)
            logs, cap = fetch_window_earliest(ca, fb, tb)
            capped = capped or cap
            for l in logs:
                mints.append({"block": int(l["blockNumber"],16), "minter": "0x"+l["topics"][2][-40:]})
            fb = tb + 1
            time.sleep(0.2)
    except Exception as e:
        err = str(e)
    mints = mints[:100]
    out[name] = {"contract": ca, "anchor": anchor, "anchor_exact_first_mint": exact,
                 "covered_to": fb-1, "mints": len(mints), "capped_window": capped, "error": err,
                 "distinct": len(set(m["minter"] for m in mints)), "list": mints}
    print(name, "mints:", len(mints), "distinct:", out[name]["distinct"],
          "first:", mints[0]["block"] if mints else None, "last:", mints[-1]["block"] if mints else None,
          "capped:", capped, "err:", err)
json.dump(out, open('/tmp/m6_early.json','w'), indent=1)
