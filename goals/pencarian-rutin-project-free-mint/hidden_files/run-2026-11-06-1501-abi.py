import json, subprocess
first=json.load(open('run-2026-11-06-1501-firstseen.json'))
out={}
for c in first:
    addr=c['address']
    r=subprocess.run(["curl","-sS","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=40)
    try:
        d=json.loads(r.stdout)
    except Exception as e:
        print(addr,"JSON ERR",r.stdout[:200],r.stderr[:200],flush=True); out[addr]={"error":"json"}; continue
    abi=d.get("abi")
    fns=[f.get("name") for f in abi if isinstance(abi,list) and f.get("type")=="function"] if isinstance(abi,list) else []
    print(addr,c['name'],"verifiedAt:",d.get("verifiedAt"),"match:",d.get("match"),"creationMatch:",d.get("creationMatch"),"fn_count:",len(fns),flush=True)
    print("  fns:",fns,flush=True)
    free=[f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")]
    mint=[f for f in fns if "mint" in f.lower()]
    print("  free:",free,"mint:",mint,flush=True)
    out[addr]={"verifiedAt":d.get("verifiedAt"),"match":d.get("match"),"creationMatch":d.get("creationMatch"),"fns":fns,"free":free,"mint":mint}
json.dump(out,open('run-2026-11-06-1501-abi.json','w'),indent=1)
# discards owner lookup for NIULAI owner
disc=json.load(open('same-owner-discards.json'))
for d in disc:
    if d.get('owner','').lower()=="0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3":
        print("NIULAI owner discard entry:",d,flush=True)
