import json, re, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
src = open(BASE+"hot-leg-2026-11-08-1129.py").read()
def extract(var):
    m = re.search(re.escape(var)+r"\s*=\s*(\{.*?^\})", src, re.S|re.M)
    return eval(m.group(1))
V = extract("V"); ITEMS = extract("ITEMS")
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
targets = [("Tri333","freeMinted"),("WAR3","freeMinted"),("HUNT PASS","totalMinted"),
           ("DinoAgent","freeMinted"),("LOCKSMITH","totalMinted"),
           ("HOG ORBIT","freeLeft"),("AgentBook","FREE_QUOTA"),
           ("AURISLE","FREE_SUPPLY"),("Dafeiyu","freeClaimed")]
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
out = {}
for name, field in targets:
    addr, keys = ITEMS[name]
    sig, arg = V[field]
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    vals = {}
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=20)
            vals[ep] = int(res[0], 16) if res and res[0] else None
        except Exception as ex:
            vals[ep] = f"ERR {type(ex).__name__}: {str(ex)[:80]}"
    out[f"{name}.{field}"] = {"address": addr, "vals": vals}
print(json.dumps(out, indent=1))
json.dump(out, open(BASE+"hot-leg-2026-11-08-1924-nullrecheck.json","w"), indent=1)
