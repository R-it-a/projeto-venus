import sys, pandas as pd, numpy as np
s=pd.read_parquet(sys.argv[1]+"/datasus_sim/proxy_sim_feminicidio.parquet").drop_duplicates()
s["dt"]=pd.to_datetime(s.DT_OBITO,format="%d%m%Y",errors="coerce"); s=s[s.dt.dt.year.between(1996,2025)]
s["h"]=pd.to_numeric(s.HORA_OBITO.str[:2],errors="coerce"); s=s[s.h.between(0,23)].copy(); s["h"]=s.h.astype(int)
s["md"]=s.dt.dt.strftime("%m-%d")
typ=s.groupby("h").size()/365.25
def c(md): return s[s.md==md].groupby("h").size().reindex(range(24),fill_value=0)
for a,b,nome in [("12-24","12-25","NATAL"),("12-31","01-01","ANO NOVO")]:
    A,B=c(a),c(b); print(nome)
    for h in list(range(18,24))+list(range(0,6)):
        v=A[h] if h>=18 else B[h]; print(f"{h}h | {v} | {typ[h]:.1f}")
    print("18-24:",A[18:24].sum(),"comum",round(typ[18:24].sum(),1),"| 0-6:",B[0:6].sum(),"comum",round(typ[0:6].sum(),1))
