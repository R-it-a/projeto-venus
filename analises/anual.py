import sys, pandas as pd, numpy as np
s=pd.read_parquet(sys.argv[1]+"/datasus_sim/proxy_sim_feminicidio.parquet")
print("registros brutos:",len(s),"| duplicatas exatas:",s.duplicated().sum())
s=s.drop_duplicates()
s["dt"]=pd.to_datetime(s.DT_OBITO,format="%d%m%Y",errors="coerce")
print("datas invalidas:",s.dt.isna().sum())
s=s[s.dt.notna()]
s["ano"]=s.dt.dt.year; s["md"]=s.dt.dt.strftime("%m-%d")
s["h"]=pd.to_numeric(s.HORA_OBITO.str[:2],errors="coerce"); s.loc[~s.h.between(0,23),"h"]=np.nan
s["raca_ok"]=s.RACA_COR.notna()&(s.RACA_COR!="IGNORADO")
g=s.groupby("ano")
t=pd.DataFrame({"mortes":g.size(),
 "1jan":g.apply(lambda x:(x.md=="01-01").sum()),
 "com_hora_%":g.h.apply(lambda x:round(100*x.notna().mean())),
 "1jan_0a6h":g.apply(lambda x:((x.md=="01-01")&(x.h<6)).sum()),
 "raca_inf_%":g.raca_ok.apply(lambda x:round(100*x.mean()))})
dias=t.index.map(lambda y: 366 if pd.Timestamp(f"{y}-12-31").dayofyear==366 else 365)
t["por_dia"]=(t.mortes/dias).round(1)
t["1jan_vs_dia"]=(t["1jan"]/t.por_dia).round(1)
pd.set_option("display.width",200)
print(t[["mortes","por_dia","1jan","1jan_vs_dia","1jan_0a6h","com_hora_%","raca_inf_%"]].to_string())
tt=t.loc[1996:2025]
print("TOTAL 1996-2025:",tt.mortes.sum(),"| media/ano",round(tt.mortes.mean()),"| 1jan total",tt["1jan"].sum())
print("anos com 1jan acima da media diaria:",(tt["1jan_vs_dia"]>1).sum(),"de",len(tt))
print("causa (3 dig) top:",s.CAUSA_BASICA.str[:3].value_counts().head(5).to_dict(), "| faixa:",s.CAUSA_BASICA.str[:3].min(),s.CAUSA_BASICA.str[:3].max())
print("tipo obito:",s.TIPO_OBITO.value_counts(dropna=False).to_dict())
