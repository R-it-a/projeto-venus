import pandas as pd, numpy as np
A='dados/auditoria/'
df=pd.read_parquet(A+'sin_all.parquet')
s=df[(df.FILE.astype(int)>=16)&(df.oc>='2016-01-01')&(df.oc<='2024-12-31')&(df.LES_AUTOP!='1')]
F=s[(s.CS_SEXO=='F')&s.parc].copy()
ND=3288
# duplicates
k1=['oc','CS_SEXO','ANO_NASC','NU_IDADE_N','ID_MN_RESI','ID_MUNICIP','CS_RACA','HORA_OCOR','LOCAL_OCOR']
F['dup']=F.duplicated(k1,keep='first')
FP=F[F.lag.isin([0,1])].copy(); FP['dup2']=FP.duplicated(k1,keep='first')
print('dup (sem data notif) geral %.4f; 1/1 %.4f; natal %.4f'%(FP.dup2.mean(),FP[FP.md=='01-01'].dup2.mean(),FP[FP.md=='12-25'].dup2.mean()))
D=FP[~FP.dup2]; n=(D.md=='01-01').sum(); print('1/1 exc dedup %+.1f%%'%(100*((n/9)/(len(D)/ND)-1)), 'natal %+.1f%%'%(100*(((D.md=='12-25').sum()/9)/(len(D)/ND)-1)))
# capture: lag0-1 share among lag<=30
c=F[F.lag<=30]
for k in ['01-01','12-25','01-02','12-31']:
    print('share lag0-1 entre lag<=30',k,'%.3f'%c[c.md==k].lag.isin([0,1]).mean())
print(' geral %.3f'%c.lag.isin([0,1]).mean(), 'domingos %.3f'%c[c.oc.dt.dayofweek==6].lag.isin([0,1]).mean())
# excess using lag<=30 (removes most heaping)
n=(c.md=='01-01').sum(); print('1/1 exc lag<=30 %+.1f%%'%(100*((n/9)/(len(c)/ND)-1)))
# bootstrap by year
FP['y']=FP.oc.dt.year
yr=FP.groupby('y').size(); j=FP[FP.md=='01-01'].groupby('y').size(); nd=pd.Series({y:366 if y%4==0 else 365 for y in yr.index})
rng=np.random.default_rng(0); bs=[]
for _ in range(5000):
    b=rng.choice(yr.index.values,9); bs.append(j[b].sum()/(yr[b]/nd[b]).sum())
print('1/1 ratio agregado-ano %.3f bootstrap IC'%(j.sum()/(yr/nd).sum()), np.percentile(bs,[2.5,97.5]).round(3))
# 1/1 vs Sunday
wd=FP.oc.dt.dayofweek; dr=pd.date_range('2016-01-01','2024-12-31'); hol=FP.md.isin(['01-01','12-25'])
sun=((wd==6)&~hol).sum()/((dr.dayofweek==6).sum()); print('domingo media %.1f; 1/1 vs domingo %+.1f%%'%(sun, 100*(300.1/sun-1)))
# weekday-control: expected = mean same weekday same year
exp=0;obs=0
for y in range(2016,2025):
    w=pd.Timestamp(y,1,1).dayofweek; dd=pd.date_range(f'{y}-01-01',f'{y}-12-31')
    sub=FP[FP.y==y]; exp+=(sub.oc.dt.dayofweek==w).sum()/(dd.dayofweek==w).sum(); obs+=(sub.md=='01-01').sum()
print('SINAN controle dia semana: exc %+.1f%%'%(100*(obs/exp-1)))
# 31/12+1/1 window
print('31/12+1/1 janela exc %+.1f%%'%(100*((((FP.md=='12-31')|(FP.md=='01-01')).sum()/18)/(len(FP)/ND)-1)))
# heaping of 01/01 among lag>30 vs other day1
L=F[F.lag>30]; print('lag>30: 1/1 n',(L.md=='01-01').sum(),'media dia %.1f'%(len(L)/ND/9*9))
# Carnival/other holidays check: top dates
cnt=FP.groupby('md').size()/9/(len(FP)/ND)-1
print('top datas', cnt.sort_values(ascending=False).head(8).round(3).to_dict())
# UF composition on 1/1 vs geral (notification state)
u=FP.SG_UF_NOT.value_counts(normalize=True); u1=FP[FP.md=='01-01'].SG_UF_NOT.value_counts(normalize=True)
print('UF share 1/1 / geral (top desvios)', (u1/u).sort_values().round(2).iloc[[0,1,2,-3,-2,-1]].to_dict())
# excess restricted to physical violence + age 18-59
