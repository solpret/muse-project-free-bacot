import json, re, subprocess, urllib.request
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-07-1844"
seen=json.load(open(f"{BASE}/hot-leg-seen.json"))
EXCLUDED={"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493","0x60b9262456de011f7d15a54cdd8c48baaa8b022f"}
# Leg 1: Sourcify feed
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", headers={"User-Agent":"curl/8"})
    feed=json.load(urllib.request.urlopen(req, timeout=30))
except Exception as e:
    feed={"error":str(e)}
json.dump(feed, open(f"{BASE}/hot-leg-{TS}-feed.json","w"), indent=1)
addrs=[]
for r in feed.get("results",[]):
    a=r.get("address"); 
    if a: addrs.append(a)
new=[a for a in addrs if a not in seen and a.lower() not in EXCLUDED]
json.dump(new, open(f"{BASE}/hot-leg-{TS}-new.json","w"), indent=1)
print("FEED n=",len(addrs)," new=",new)
for r in feed.get("results",[])[:3]:
    print(" ",r.get("address"), r.get("verifiedAt"))
# Leg 2: Boltbook front page en + zh
for lang, suf in [("en",""),("zh","?lang=zh")]:
    try:
        r=subprocess.run(["curl","-s","-m","30","-A","Mozilla/5.0",f"https://boltbook.fun/{suf}"],capture_output=True,text=True,timeout=40)
        open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html","w").write(r.stdout)
        print(f"BOLTBOOK {lang} bytes={len(r.stdout)}")
    except Exception as e:
        print(f"BOLTBOOK {lang} ERR {e}")
