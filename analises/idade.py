import sys, pandas as pd, numpy as np
s=pd.read_parquet(sys.argv[1]+"/datasus_sim/proxy_sim_feminicidio.parquet").drop_duplicates()
s["dt"]=pd.to_datetime(s.DT_OBITO,format="%d%m%Y",errors="coerce"); s=s[s.dt.dt.year.between(1996,2025)]
n=pd.to_datetime(s.DT_NASCIMENTO,format="%d%m%Y",errors="coerce"); s["id"]=((s.dt-n).dt.days/365.25)
tot=len(s); inf=s.id.notna().sum()
for lab,m in [("menos de 1 ano",s.id<1),("1 a 11 anos",(s.id>=1)&(s.id<12)),("12 a 17 anos",(s.id>=12)&(s.id<18)),("18 anos ou mais",s.id>=18),("idade não informada",s.id.isna())]:
    print(f"{lab}: {m.sum()} ({100*m.sum()/tot:.1f}%)")
print("Y06/Y07 (abandono/maus-tratos):",s.CAUSA_BASICA.str[:3].isin(["Y06","Y07"]).sum())
a=s[s.id>=18]; dia=len(a)/10958; j=(a.dt.dt.strftime("%m-%d")=="01-01").sum()/30
print(f"so adultas: {len(a)/30:.0f}/ano | {dia:.1f}/dia | 1jan {j:.1f} | +{100*(j/dia-1):.0f}%")
