import sys, pandas as pd, numpy as np
s=pd.read_parquet(sys.argv[1]+"/datasus_sim/proxy_sim_feminicidio.parquet").drop_duplicates()
s["dt"]=pd.to_datetime(s.DT_OBITO,format="%d%m%Y",errors="coerce"); s=s[s.dt.dt.year.between(1996,2025)]
s["md"]=s.dt.dt.strftime("%m-%d")
dia=len(s)/((pd.Timestamp("2025-12-31")-pd.Timestamp("1996-01-01")).days+1)
s["h"]=pd.to_numeric(s.HORA_OBITO.str[:2],errors="coerce"); s.loc[~s.h.between(0,23),"h"]=np.nan
w=s[s.h.notna()&(s.dt.dt.year>=2006)]; mad_typ=(w.h<6).sum()/365.25
for md,nome in [("12-24","Véspera de Natal (24/12)"),("12-25","Natal (25/12)"),("12-31","Réveillon (31/12)"),("01-01","Ano Novo (1/1)")]:
    tot=(s.md==md).sum(); por=tot/30
    mad=((w.md==md)&(w.h<6)).sum()
    print(f"{nome}: total {tot} | por ano {por:.1f} | vs dia médio {dia:.1f}: {100*(por/dia-1):+.0f}% | madrugada 0-6h (2006-25, c/ hora): {mad} vs comum {mad_typ:.0f}")
print("Natal por ano:",s[s.md=="12-25"].groupby(s.dt.dt.year).size().reindex(range(1996,2026),fill_value=0).to_dict())
print("anos com Natal acima da media do proprio ano:", sum((s[s.md=='12-25'].groupby(s.dt.dt.year).size().reindex(range(1996,2026),fill_value=0) > s.groupby(s.dt.dt.year).size()/365).values),"de 30")
