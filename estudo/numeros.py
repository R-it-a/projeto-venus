"""Projeto Venus - todos os numeros do estudo, a partir dos arquivos oficiais do DATASUS.
Uso: python -I numeros.py <sim_oficial.parquet> <sinan_oficial.parquet> <saida.json>"""
import sys, json, pandas as pd, numpy as np
from math import sqrt
R={}
def ci(k):
    lo=0 if k==0 else k*(1-1/(9*k)-1.96/(3*sqrt(k)))**3; hi=(k+1)*(1-1/(9*(k+1))+1.96/(3*sqrt(k+1)))**3; return lo,hi
def exc(k,ny,dia):
    lo,hi=ci(k); return dict(n=int(k),media=round(k/ny,1),pct=round(100*(k/ny/dia-1)),ic=[round(100*(lo/ny/dia-1)),round(100*(hi/ny/dia-1))])
# ---------------- SIM
o=pd.read_parquet(sys.argv[1]); o["d"]=pd.to_datetime(o.DTOBITO.str.zfill(8),format="%d%m%Y",errors="coerce")
o=o[o.d.dt.year.between(1996,2025)&o.SEXO.isin(["1","2"])].copy(); o["md"]=o.d.dt.strftime("%m-%d"); o["ano"]=o.d.dt.year
hh=o.HORAOBITO.str.zfill(4); o["h"]=pd.to_numeric(hh.str[:2],errors="coerce"); o["mi"]=pd.to_numeric(hh.str[2:],errors="coerce")
o.loc[~(o.h.between(0,23)&o.mi.between(0,59)&(o.HORAOBITO.str.len()>0)),["h","mi"]]=np.nan
days=pd.date_range("1996-01-01","2025-12-31"); ND=len(days)
for s,lab in [("2","mulheres"),("1","homens")]:
    x=o[o.SEXO==s]; dia=len(x)/ND; r=dict(total=len(x),por_ano=round(len(x)/30),por_dia=round(dia,1))
    r["ano_a_ano"]={int(y):dict(total=len(g),jan1=int((g.md=="01-01").sum()),natal=int((g.md=="12-25").sum())) for y,g in x.groupby("ano")}
    for md,k in [("01-01","jan1"),("12-25","natal"),("12-24","vespera_natal"),("12-31","reveillon")]: r[k]=exc((x.md==md).sum(),30,dia)
    r["casa"]=round(100*(x.LOCOCOR=="3").mean(),1)
    dom=x[x.LOCOCOR=="3"]; r["casa_jan1"]=exc((dom.md=="01-01").sum(),30,len(dom)/ND)
    cau=x.CAUSABAS.str[:3]; r["faca"]=round(100*(cau=="X99").mean(),1); r["arma_fogo"]=round(100*cau.isin(["X93","X94","X95"]).mean(),1)
    r["faca_jan1"]=round(100*(cau[x.md=="01-01"]=="X99").mean(),1)
    w=x[x.h.notna()&x.ano.between(2006,2025)]; cm=w.groupby("h").size()/(len(pd.date_range("2006-01-01","2025-12-31"))/20)
    r["hora_cobertura_pct"]=round(100*len(w)/len(x[x.ano>=2006]))
    r["virada_por_hora_2006_2025"]={"31dez":w[w.md=="12-31"].groupby("h").size().reindex(range(18,24),fill_value=0).tolist(),"1jan":w[w.md=="01-01"].groupby("h").size().reindex(range(0,6),fill_value=0).tolist(),"comum":cm.reindex(list(range(18,24))+list(range(6))).round(1).tolist()}
    r["madrugada_jan1"]=int(((w.md=="01-01")&(w.h<6)).sum()); r["madrugada_comum"]=round((w.h<6).sum()/365.25*20/20,1)
    r["madrugada_natal"]=int(((w.md=="12-25")&(w.h<6)).sum())
    for a,b in [(1996,2005),(2006,2015),(2016,2025)]:
        y=x[x.ano.between(a,b)]; dd=len(y)/sum((days.year>=a)&(days.year<=b)); r[f"jan1_{a}_{b}"]=round(100*((y.md=="01-01").sum()/10/dd-1))
    R["sim_"+lab]=r
# ---------------- SINAN (2016-2024, notificacao no mesmo dia ou no seguinte)
s=pd.read_parquet(sys.argv[2]); s["d"]=pd.to_datetime(s.DT_OCOR,errors="coerce"); s["n"]=pd.to_datetime(s.DT_NOTIFIC,errors="coerce")
s=s[(s.LES_AUTOP!="1")&s.CS_SEXO.isin(["F","M"])&s.d.dt.year.between(2016,2024)].copy(); s["lag"]=(s.n-s.d).dt.days
R["sinan_total_nao_autoprov"]=int(len(s)); R["sinan_pct_confiavel"]=round(100*s.lag.between(0,1).mean())
s=s[s.lag.between(0,1)].copy(); s["md"]=s.d.dt.strftime("%m-%d"); s["ano"]=s.d.dt.year
s["par"]=(s[["REL_CONJ","REL_EXCON","REL_NAMO","REL_EXNAM"]]=="1").any(axis=1)
hh=s.HORA_OCOR.str.replace(":","").str.zfill(4); s["h"]=pd.to_numeric(hh.str[:2],errors="coerce"); s["mi"]=pd.to_numeric(hh.str[2:4],errors="coerce")
s.loc[~(s.h.between(0,23)&(s.HORA_OCOR.str.len()>0)),"h"]=np.nan
dd=pd.date_range("2016-01-01","2024-12-31"); NDs=len(dd); NYs=9
def alc(x):
    a=x.AUTOR_ALCO; ok=a.isin(["1","2"]); return round(100*(a[ok]=="1").mean())
grupos={"mulheres_todas":(s.CS_SEXO=="F"),"mulheres_parceiro":(s.CS_SEXO=="F")&s.par,"mulheres_desconhecido":(s.CS_SEXO=="F")&(s.REL_DESCO=="1"),"mulheres_pai_mae":(s.CS_SEXO=="F")&((s.REL_PAI=="1")|(s.REL_MAE=="1")),"homens_todas":(s.CS_SEXO=="M"),"homens_parceiro":(s.CS_SEXO=="M")&s.par}
for k,m in grupos.items():
    x=s[m]; dia=len(x)/NDs; r=dict(n=int(len(x)),por_dia=round(dia,1))
    r["jan1"]=exc((x.md=="01-01").sum(),NYs,dia); r["natal"]=exc((x.md=="12-25").sum(),NYs,dia); r["jan2"]=exc((x.md=="01-02").sum(),NYs,dia)
    r["outros_dia1"]=round(100*(x[(x.d.dt.day==1)&(x.d.dt.month>1)].shape[0]/(dia*sum((dd.day==1)&(dd.month>1)))-1))
    dw=x.groupby(x.d.dt.dayofweek).size()/pd.Series(dd.dayofweek).value_counts().sort_index()
    r["domingo"]=round(100*(dw[6]/dia-1)); r["jan1_vs_dia_semana"]=round(100*((x.md=="01-01").sum()/NYs/np.mean([dw[pd.Timestamp(f'{y}-01-01').dayofweek] for y in range(2016,2025)])-1))
    r["alcool_comum"]=alc(x[~x.md.isin(["01-01","12-25"])]); r["alcool_domingo"]=alc(x[x.d.dt.dayofweek==6]); r["alcool_jan1"]=alc(x[x.md=="01-01"]); r["alcool_natal"]=alc(x[x.md=="12-25"])
    r["alcool_ign_pct"]=round(100*(~x.AUTOR_ALCO.isin(["1","2"])).mean())
    r["ano_a_ano_jan1"]={int(y):dict(jan1=int((g.md=="01-01").sum()),media_dia=round(len(g)/len(pd.date_range(f"{y}-01-01",f"{y}-12-31")),1)) for y,g in x.groupby("ano")}
    if k=="mulheres_parceiro":
        w=x[x.h.notna()]; cm=w.groupby("h").size()/365.25
        r["hora_cobertura_pct"]=round(100*len(w)/len(x)); r["minuto_00_pct"]=round(100*(w.mi==0).mean())
        r["virada_por_hora_2016_2024"]={"31dez":w[w.md=="12-31"].groupby("h").size().reindex(range(18,24),fill_value=0).tolist(),"1jan":w[w.md=="01-01"].groupby("h").size().reindex(range(6),fill_value=0).tolist(),"comum":cm.reindex(list(range(18,24))+list(range(6))).round(1).tolist()}
        r["madrugada_jan1"]=int(((w.md=="01-01")&(w.h<6)).sum()); r["madrugada_comum"]=round((w.h<6).sum()/365.25,1)
        r["casa_pct"]={"comum":round(100*(x[x.md!="01-01"].LOCAL_OCOR=="01").mean(),1),"jan1":round(100*(x[x.md=="01-01"].LOCAL_OCOR=="01").mean(),1)}
        r["via_publica_pct"]={"comum":round(100*(x[x.md!="01-01"].LOCAL_OCOR=="06").mean(),1),"jan1":round(100*(x[x.md=="01-01"].LOCAL_OCOR=="06").mean(),1)}
        r["bar_pct"]={"comum":round(100*(x[x.md!="01-01"].LOCAL_OCOR=="05").mean(),1),"jan1":round(100*(x[x.md=="01-01"].LOCAL_OCOR=="05").mean(),1)}
        r["autor_homem_pct"]=round(100*(x.AUTOR_SEXO=="1").mean(),1)
        r["faca_pct"]={"comum":round(100*(x[x.md!="01-01"].AG_CORTE=="1").mean(),1),"jan1":round(100*(x[x.md=="01-01"].AG_CORTE=="1").mean(),1)}
        r["fisica_pct"]={"comum":round(100*(x[x.md!="01-01"].VIOL_FISIC=="1").mean(),1),"jan1":round(100*(x[x.md=="01-01"].VIOL_FISIC=="1").mean(),1)}
        y=x[x.ano.isin([2023,2024])]; r["2023_2024"]=dict(por_dia=round(len(y)/731,1),jan1_media=(y.md=="01-01").sum()/2,natal_media=(y.md=="12-25").sum()/2)
    if k=="homens_parceiro": r["autor_mulher_pct"]=round(100*(x.AUTOR_SEXO=="2").mean(),1)
    R["sinan_"+k]=r
# ---------------- complementos da auditoria
rng = np.random.default_rng(42)
def boot(x, d0, d1, md="01-01", B=4000):  # IC bootstrap reamostrando anos
    anos = sorted(x.ano.unique()); tab = {a: ((x[x.ano == a].md == md).sum(), (x.ano == a).sum(), len(pd.date_range(f"{a}-01-01", f"{a}-12-31"))) for a in anos}
    v = []
    for _ in range(B):
        a = rng.choice(anos, len(anos)); k = sum(tab[y][0] for y in a); t = sum(tab[y][1] for y in a); nd = sum(tab[y][2] for y in a)
        v.append(100 * ((k / len(a)) / (t / nd) - 1))
    return [round(np.percentile(v, 2.5)), round(np.percentile(v, 97.5))]
def janela(x, dias_):  # noite 18h->6h: virada, noite comum, sabado->domingo (media por noite)
    w = x[x.h.notna()]; nv = len({d.year for d in dias_ if d.month == 1 and d.day == 1})
    vir = ((w.md == "12-31") & (w.h >= 18)).sum() + ((w.md == "01-01") & (w.h < 6)).sum()
    tot = ((w.h >= 18) | (w.h < 6)).sum(); nd = len(dias_)
    sab = ((w.d.dt.dayofweek == 5) & (w.h >= 18)).sum() + ((w.d.dt.dayofweek == 6) & (w.h < 6)).sum(); ns = int((dias_.dayofweek == 5).sum())
    return dict(virada=round(vir / nv, 1), comum=round(tot / nd, 2), sab_dom=round(sab / ns, 2), x_comum=round(vir / nv / (tot / nd), 1), x_sab=round(vir / nv / (sab / ns), 1))
def domingo(x, dias_, ny):
    dw = x.groupby(x.d.dt.dayofweek).size() / pd.Series(dias_.dayofweek).value_counts().sort_index()
    return round(100 * ((x.md == "01-01").sum() / ny / dw[6] - 1))
FER = {"01-01", "04-21", "05-01", "09-07", "10-12", "11-02", "11-15", "12-25"}
m = o[o.SEXO == "2"]
R["sim_mulheres"]["jan1_ic_boot"] = boot(m, 1996, 2025); R["sim_mulheres"]["natal_ic_boot"] = boot(m, 1996, 2025, "12-25")
R["sim_mulheres"]["jan1_vs_domingo"] = domingo(m, days, 30)
y = m[m.ano.between(2016, 2024)]; d9 = pd.date_range("2016-01-01", "2024-12-31")
R["sim_mulheres"]["jan1_2016_2024"] = exc((y.md == "01-01").sum(), 9, len(y) / len(d9)); R["sim_mulheres"]["jan1_2016_2024"]["ic_boot"] = boot(y, 2016, 2024)
R["sim_mulheres"]["natal_2016_2024"] = exc((y.md == "12-25").sum(), 9, len(y) / len(d9))
R["sim_mulheres"]["janela_2006_2025"] = janela(m[m.ano.between(2006, 2025)], pd.date_range("2006-01-01", "2025-12-31"))
R["sim_mulheres"]["janela_2016_2024"] = janela(y, d9)
R["sim_mulheres"]["pct_mulheres_jan1_vs_resto"] = [round(100 * (o[o.md == "01-01"].SEXO == "2").mean(), 1), round(100 * (o[o.md != "01-01"].SEXO == "2").mean(), 1)]
xp = s[(s.CS_SEXO == "F") & s.par]
R["sinan_mulheres_parceiro"]["jan1_ic_boot"] = boot(xp, 2016, 2024); R["sinan_mulheres_parceiro"]["jan1_vs_domingo"] = domingo(xp, dd, 9)
util = (xp.d.dt.dayofweek < 5) & ~xp.md.isin(FER)
R["sinan_mulheres_parceiro"]["alcool_dia_util"] = alc(xp[util])
R["sinan_mulheres_parceiro"]["janela"] = janela(xp, dd)
R["sinan_mulheres_parceiro"]["hora_cobertura_jan1_pct"] = round(100 * xp[xp.md == "01-01"].h.notna().mean())
f = s[s.CS_SEXO == "F"].copy(); f["id"] = pd.to_numeric(f.NU_IDADE_N, errors="coerce"); f["anos"] = np.where(f.id // 1000 == 4, f.id % 1000, np.where(f.id < 4000, 0, np.nan))
for lab, g in [("todas", f), ("adultas", f[f.anos >= 18])]:
    dia = len(g) / NDs; jan = g[g.md == "01-01"]; resto = g[g.md != "01-01"]
    R[f"sinan_composicao_{lab}"] = dict(total_jan1=round(100 * ((g.md == "01-01").sum() / NYs / dia - 1)),
        parceiro_pct=[round(100 * jan.par.mean(), 1), round(100 * resto.par.mean(), 1)])
R["sinan_pct_mulheres_jan1_vs_resto"] = [round(100 * (s[s.md == "01-01"].CS_SEXO == "F").mean(), 1), round(100 * (s[s.md != "01-01"].CS_SEXO == "F").mean(), 1)]
R["sinan_31dez_parceiro"] = exc(((xp.md == "12-31")).sum(), NYs, len(xp) / NDs)
# SIM no mesmo periodo do SINAN (para o relogio combinado)
x=o[(o.SEXO=="2")&o.ano.between(2016,2024)&o.h.notna()]; cm=x.groupby("h").size()/365.25
R["sim_mulheres_relogio_2016_2024"]={"31dez":x[x.md=="12-31"].groupby("h").size().reindex(range(18,24),fill_value=0).tolist(),"1jan":x[x.md=="01-01"].groupby("h").size().reindex(range(6),fill_value=0).tolist(),"comum":cm.reindex(list(range(18,24))+list(range(6))).round(1).tolist()}
json.dump(R,open(sys.argv[3],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
for k,v in R.items():
    if isinstance(v,dict): print(k,{a:b for a,b in v.items() if a not in("ano_a_ano","ano_a_ano_jan1")})
    else: print(k,v)
