import sys, pandas as pd, numpy as np
s=pd.read_parquet(sys.argv[1]+"/datasus_sim/proxy_sim_feminicidio.parquet").drop_duplicates()
s["dt"]=pd.to_datetime(s.DT_OBITO,format="%d%m%Y",errors="coerce")
print("ultima data na base:",s.dt.max().date())
s["h"]=pd.to_numeric(s.HORA_OBITO.str[:2],errors="coerce"); s.loc[~s.h.between(0,23),"h"]=np.nan
for d in ["2025-12-31","2026-01-01"]:
    x=s[s.dt==d]
    print(f"--- {d}: {len(x)} mortes | com hora {x.h.notna().sum()} | 0-6h {(x.h<6).sum()} | 18-24h {(x.h>=18).sum()}")
    nasc=pd.to_datetime(x.DT_NASCIMENTO,format="%d%m%Y",errors="coerce"); idade=((x.dt-nasc).dt.days//365.25)
    print("   idades: min",idade.min(),"mediana",idade.median(),"max",idade.max(),"| menores de 18:",(idade<18).sum())
    print("   local:",x.LOCAL_OCORRENCIA_OBITO.value_counts().to_dict())
    print("   raca:",x.RACA_COR.value_counts().to_dict())
    print("   horas:",x.h.value_counts().sort_index().to_dict())
# media diaria 2025 e 2026 parcial
for y in [2025,2026]:
    x=s[s.dt.dt.year==y]; dias=(x.dt.max()-pd.Timestamp(f"{y}-01-01")).days+1
    print(y,"media/dia ate",x.dt.max().date(),":",round(len(x)/dias,1))
