import json, urllib.request, urllib.error
feed=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0101-sourcify.json'))['results']
known={'0x1458b0c132fb51bdc65b1ca7a3be484bcd9a2f77','0xc205f8c74733d914776d66cbc4cf10bf701d96aa','0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC','0x11fa2c4b71ece40f242992a08c4acc6c23c99ca0','0x787b522d48084a83b8b1b0c206aa4a12b1fd1cc2','0x0ac5591d1b980c7be16861d722e59e21e2624868','0x2c215262635e66c798c5a1ba4411fa9f06852bdd','0x3815a26a6981baad0b850f7522b7a8bdddb6b70c','0xbbbbf437ce6275e21728bc6a9aa99d1bda9ce989','0xb257b3a30a795cad46ee4d25d0c730b10cad6b1e','0x68a971c9d2b54ae86daf59cd665e40f3e087fb7f','0xd987945d1df5fcdf11155bf9c494faa de3f91e3e'.replace(' ',''),'0x7fbedd1e2ef6e4765e8f72b2668e9f4a964600f7','0x81fc58bd054b95de96ea4bdf37a4bd45e9b6e1f4e','0xdec97178bfa4692a6cb60901c628c8e7437b5a83','0x27cd34c8a5cc9376030f44d5fec1a3dcc eeca2a3'.replace(' ','')}
# note: known set is for dedup only in narrative; shape-check all 30 anyway
FREE=['freesharesremaining','freeclaimed','freefor','freeleft','freeused','freeavailable','freesharepoolexhausted','freesharesclaimed','freebyid','soldfree','freetotal']
out=[]
for it in feed:
    a=it['address']; va=it.get('verifiedAt')
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        d=json.loads(urllib.request.urlopen(req,timeout=20).read())
        abi=d.get('abi') or []
        fns=[f.get('name','') for f in abi if f.get('type')=='function']
        low=[f.lower() for f in fns]
        has_mint=any('mint' in f for f in low)
        has_quote=any('quote' in f or f=='costfor' or f.startswith('cost') for f in low)
        has_free=any(f in FREE for f in low)
        has_reg=any('agent' in f or 'registry' in f for f in low)
        has_token=all(x in low for x in ['name','symbol','decimals','totalsupply'])
        has_nofree=any(f in ('mintfree',) for f in low)
        s1=has_mint and has_quote and has_free and has_reg
        s2=has_token and has_nofree and has_free and has_reg
        agent_nft=has_mint and (has_free or 'free_supply' in str(low) or 'freesupply' in low) and has_reg
        out.append({"address":a,"verifiedAt":va,"functions":fns,"S1":s1,"S2":s2,"agent_nft_shape":agent_nft})
        print(a, va, "S1" if s1 else "-", "S2" if s2 else "-", "NFTshape" if agent_nft else "-", fns[:25])
    except urllib.error.HTTPError as e:
        out.append({"address":a,"verifiedAt":va,"error":f"http_{e.code}"}); print(a, va, "UNVERIFIED http", e.code)
    except Exception as e:
        out.append({"address":a,"verifiedAt":va,"error":str(e)[:100]}); print(a, va, "ERR", str(e)[:100])
json.dump(out, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0101-sourcify-shape.json','w'), indent=1)
