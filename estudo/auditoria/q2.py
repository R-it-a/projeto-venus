import pandas as pd, numpy as np
A='dados/auditoria/'
df=pd.read_parquet(A+'sin_all.parquet')
df=df[(df.FILE.astype(int)>=16)&(df.LES_AUTOP!='1')&df.lag.isin([0,1])].copy()
df['age']=pd.to_numeric(df.NU_IDADE_N,errors='coerce'); df['adult']=df.age>=4018
S=df[(df.oc>='2016-01-01')&(df.oc<='2024-12-31')]
j=S.md=='01-01'; n=S.md=='12-25'
print('Q1 fatia mulheres: 1/1 %.3f natal %.3f resto %.3f'%((S[j].CS_SEXO=='F').mean(),(S[n].CS_SEXO=='F').mean(),(S[~j&~n].CS_SEXO=='F').mean()))
Sa=S[S.adult]; ja=Sa.md=='01-01'
print('   adultos: fatia mulheres 1/1 %.3f resto %.3f'%((Sa[ja].CS_SEXO=='F').mean(),(Sa[~ja&(Sa.md!='12-25')].CS_SEXO=='F').mean()))
for nm,X in [('todas idades',S[S.CS_SEXO=='F']),('18+',S[(S.CS_SEXO=='F')&S.adult])]:
    jj=X.md=='01-01'; rr=~jj&(X.md!='12-25'); nn=X.md=='12-25'
    cats={'parceiro/ex':X.parc,'pai/mae':(X.REL_PAI=='1')|(X.REL_MAE=='1'),'desconhecido':X.REL_DESCO=='1','conhecido':X.REL_CONHEC=='1'}
    print(' ',nm,'N',len(X),'1/1 n',jj.sum())
    for c,m in cats.items():
        print('    %-13s 1/1 %.3f natal %.3f resto %.3f | exc 1/1 %+.0f%%'%(c,m[jj].mean(),m[nn].mean(),m[rr].mean(),100*((m&jj).sum()/9/(m.sum()/3288)-1)))
    print('    exc total %+.0f%%'%(100*(jj.sum()/9/(len(X)/3288)-1)))
    # partner share among adults, excluding pai/mae etc: share of partner among aggressions with partner|desconhecido|conhecido
# Q2 windows
def win(oc,H,md,wd,start,end,ny_v,dates):
    pass
dr_sin=pd.date_range('2016-01-01','2024-12-31')
P=df[(df.CS_SEXO=='F')&df.parc&(df.oc>='2015-12-31')&(df.oc<='2024-12-31')].copy()
ok=P.HORA_OCOR.str.fullmatch(r'\d\d:\d\d'); P=P[ok]; P['H']=P.HORA_OCOR.str[:2].astype(int); P=P[P.H<24]
def windows(D,d0,d1,vy,label):
    D=D[(D.oc>=d0)&(D.oc<=d1)]; nd=(pd.Timestamp(d1)-pd.Timestamp(d0)).days+1
    ev=D[(D.H>=18)]; mo=D[D.H<6]
    # virada: 31/12/(Y-1) 18-23 + 1/1/Y 0-5 for Y in vy
    v=sum(((ev.oc==pd.Timestamp(y-1,12,31))).sum()+((mo.oc==pd.Timestamp(y,1,1))).sum() for y in vy)/len(vy)
    v1=sum(((ev.oc==pd.Timestamp(y-1,12,31))).sum() for y in vy)/len(vy); v2=sum(((mo.oc==pd.Timestamp(y,1,1))).sum() for y in vy)/len(vy)
    com=len(ev)/nd+len(mo)/nd
    dr=pd.date_range(d0,d1); nsat=(dr.dayofweek==5).sum(); nsun=(dr.dayofweek==6).sum()
    sat=(ev.oc.dt.dayofweek==5).sum()/nsat+(mo.oc.dt.dayofweek==6).sum()/nsun
    # natal: 24/12 18h -> 25/12 6h
    yrs=range(int(d0[:4]),int(d1[:4])+1)
    nat=sum((ev.oc==pd.Timestamp(y,12,24)).sum()+(mo.oc==pd.Timestamp(y,12,25)).sum() for y in yrs)/len(list(yrs))
    print('%s: virada media %.2f (31/12 18-24h %.2f + 1/1 0-6h %.2f) | noite comum %.2f (18-24 %.2f) | sab->dom %.2f | natal %.2f || virada/comum %.2f, virada/sabdom %.2f, n viradas %d, soma viradas %.0f, comum x n %.1f'%(label,v,v1,v2,com,len(ev)/nd,sat,nat,v/com,v/sat,len(vy),v*len(vy),com*len(vy)))
windows(P,'2015-12-31','2024-12-31',range(2016,2025),'SINAN parc 9 viradas 2016-24')
# SIM
ag=pd.read_parquet(A+'sim_ag.parquet'); ag=ag[ag.dt.notna()&(ag.SEXO=='2')].copy(); ag['oc']=ag.dt; ag['HORAOBITO']=ag.HORAOBITO.fillna('')
ok=ag.HORAOBITO.str.fullmatch(r'\d{4}'); W=ag[ok].copy(); W['H']=W.HORAOBITO.str[:2].astype(int); W=W[W.H<24]
windows(W,'2006-01-01','2025-12-31',range(2007,2026),'SIM mulheres 2006-25 (19 viradas)')
windows(W,'2015-12-31','2024-12-31',range(2016,2025),'SIM mulheres 9 viradas 2016-24')
# Q3 bootstrap SIM women 1/1 and Natal; Q4 excess 2016-2024
s=ag.copy(); s['y']=s.dt.dt.year.astype(int); s['md']=s.dt.dt.strftime('%m-%d')
yd=s.groupby('y').size(); nd=pd.Series({y:366 if y%4==0 else 365 for y in yd.index}); rng=np.random.default_rng(1)
for k in ['01-01','12-25']:
    c=s[s.md==k].groupby('y').size().reindex(yd.index,fill_value=0); bs=[]
    for _ in range(10000):
        b=rng.choice(yd.index.values,len(yd)); bs.append(c[b].sum()/(yd[b]/nd[b]).sum())
    print('Q3',k,'ratio %.3f'%(c.sum()/(yd/nd).sum()),'boot IC',np.percentile(bs,[2.5,97.5]).round(3))
x=s[(s.y>=2016)&(s.y<=2024)]; ndd=3288
for k in ['01-01','12-25']:
    m=(x.md==k).sum(); print('Q4 SIM mulheres 2016-24',k,m,'exc %+.1f%%'%(100*((m/9)/(len(x)/ndd)-1)))
print('SIM %% com hora 2016-24 mulheres %.3f'%(x.HORAOBITO.str.fullmatch(r'\d{4}').mean()))
# gancho: SINAN todas agressoes mulheres - ranking datas
F=S[S.CS_SEXO=='F']; r=(F.groupby('md').size()/9/(len(F)/3288)-1).sort_values(ascending=False).head(3).round(3).to_dict(); print('SINAN F todas top datas',r)
