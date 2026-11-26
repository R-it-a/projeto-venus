import pandas as pd, numpy as np
A='dados/auditoria/'
df=pd.read_parquet(A+'sin_all.parquet')
s=df[(df.FILE.astype(int)>=16)&(df.oc>='2016-01-01')&(df.oc<='2024-12-31')&(df.LES_AUTOP!='1')].copy()
ND=3288
def exc(sub,k,ny=9,nd=ND):
    n=(sub.md==k).sum(); base=len(sub)/nd; r=(n/ny)/base-1; se=1.96/np.sqrt(max(n,1))
    return n, n/ny, r, (np.exp(np.log(1+r)-se)-1, np.exp(np.log(1+r)+se)-1)
F=s[s.CS_SEXO=='F']; M=s[s.CS_SEXO=='M']
conf=lambda x:x[x.lag.isin([0,1])]
FP=conf(F[F.parc]); 
print('F parc conf total',len(FP),'por dia %.1f'%(len(FP)/ND))
for k in ['01-01','12-25','12-24','12-31','01-02','01-03']:
    n,m,r,ci=exc(FP,k); print(k,n,'media %.1f'%m,'exc %+.1f%% IC %+.0f%% a %+.0f%%'%(100*r,100*ci[0],100*ci[1]))
# other day-1s
d1=FP[(FP.oc.dt.day==1)&(FP.oc.dt.month!=1)]; print('outros dias 1: exc %+.1f%%'%(100*((len(d1)/(9*11))/(len(FP)/ND)-1)))
d15=FP[(FP.oc.dt.day==15)]; print('dias 15: exc %+.1f%%'%(100*((len(d15)/(9*12))/(len(FP)/ND)-1)))
# weekday composition: compare 1/1 to sundays
FP_wd=FP.oc.dt.dayofweek; dr=pd.date_range('2016-01-01','2024-12-31')
for w,nm in [(6,'domingo'),(5,'sabado')]:
    print(nm,'exc %+.1f%%'%(100*((FP_wd==w).sum()/(dr.dayofweek==w).sum()/(len(FP)/ND)-1)))
# per-year 1/1 ratio
for y in range(2016,2025):
    sub=FP[FP.oc.dt.year==y]; nd=366 if y%4==0 else 365; n=(sub.md=='01-01').sum()
    print(' ',y,'1/1',n,'ratio %.2f'%(n/(len(sub)/nd)), 'natal ratio %.2f'%((sub.md=='12-25').sum()/(len(sub)/nd)))
# sensitivity to lag filter
for nm,flt in [('todas',lambda x:x),('lag0',lambda x:x[x.lag==0]),('lag1',lambda x:x[x.lag==1]),('lag0-7',lambda x:x[x.lag.between(0,7)]),('lag2-7',lambda x:x[x.lag.between(2,7)]),('lag>30',lambda x:x[x.lag>30])]:
    sub=flt(F[F.parc]); n,m,r,ci=exc(sub,'01-01'); n2,m2,r2,ci2=exc(sub,'12-25'); n3,_,r3,_=exc(sub,'01-02')
    d1=sub[(sub.oc.dt.day==1)&(sub.oc.dt.month!=1)]; r4=(len(d1)/(99))/(len(sub)/ND)-1
    print('sens',nm,'N',len(sub),'1/1 %+.0f%%'%(100*r),'natal %+.0f%%'%(100*r2),'2/1 %+.0f%%'%(100*r3),'dias1 outros %+.0f%%'%(100*r4))
# lag distribution 1/1 vs others for F parc
x=F[F.parc]; 
print('frac lag0-1 geral %.3f, 1/1 %.3f, natal %.3f, 2/1 %.3f'%(x.lag.isin([0,1]).mean(), x[x.md=='01-01'].lag.isin([0,1]).mean(), x[x.md=='12-25'].lag.isin([0,1]).mean(),x[x.md=='01-02'].lag.isin([0,1]).mean()))
# 1/1 occurrences: share notified in a later year (unknown date -> 01/01?)
j=x[x.md=='01-01']; print('1/1 ocorr: lag>30 share %.3f, lag>180 %.3f'%((j.lag>30).mean(),(j.lag>180).mean()), 'geral lag>30 %.3f'%((x.lag>30).mean()))
# notification weekday/holiday effect: notifications on the day 1/1 and 2/1 vs average
nf=F[F.parc]; nmd=nf.no.dt.strftime('%m-%d')
print('notificacoes (todas lags) datadas 1/1: %.2fx media; 2/1 %.2fx; 25/12 %.2fx'%(((nmd=='01-01').sum()/9)/(len(nf)/ND),((nmd=='01-02').sum()/9)/(len(nf)/ND),((nmd=='12-25').sum()/9)/(len(nf)/ND)))
# ALL women, men
for nm,sub in [('F todas',conf(F)),('M todas',conf(M)),('F desconhecido',conf(F[F.REL_DESCO=='1'])),('F pai/mae',conf(F[(F.REL_PAI=='1')|(F.REL_MAE=='1')])),('M parc',conf(M[M.parc])),('F parc sem filtro',F[F.parc])]:
    n,m,r,ci=exc(sub,'01-01'); n2,_,r2,_=exc(sub,'12-25')
    print(nm,'N',len(sub),'1/1 n',n,'%+.1f%%'%(100*r),'natal %+.1f%%'%(100*r2))
MP=conf(M[M.parc]); a=MP.AUTOR_SEXO.value_counts(normalize=True).round(3).to_dict(); print('M parc autor sexo',a, '1/1', MP[MP.md=='01-01'].AUTOR_SEXO.value_counts(normalize=True).round(3).to_dict())
print('F parc autor sexo',FP.AUTOR_SEXO.value_counts(normalize=True).round(3).to_dict())
# alcohol
def alc(sub):
    k=sub[sub.AUTOR_ALCO.isin(['1','2'])]; return (k.AUTOR_ALCO=='1').mean(), len(k), 1-len(k)/len(sub) if len(sub) else 0
wd=FP.oc.dt.dayofweek
hol=FP.md.isin(['01-01','12-25'])
print('alc geral %.3f n %d sem info %.3f'%alc(FP))
print('alc dia comum (seg-sex nao feriado) %.3f n %d semi %.3f'%alc(FP[(wd<5)&~hol]))
print('alc nao-1/1 nem natal %.3f'%alc(FP[~hol])[0])
print('alc domingo %.3f n %d semi %.3f'%alc(FP[(wd==6)&~hol]))
print('alc 1/1 %.3f n %d semi %.3f'%alc(FP[FP.md=='01-01']))
print('alc natal %.3f n %d semi %.3f'%alc(FP[FP.md=='12-25']))
print('alc sem info geral incl vazio', (~FP.AUTOR_ALCO.isin(['1','2'])).mean().round(3))
# alcohol among all women (not partner) by day
print('alc desconhecido 1/1 vs geral', alc(conf(F[F.REL_DESCO=='1'])[conf(F[F.REL_DESCO=='1']).md=='01-01'])[0], alc(conf(F[F.REL_DESCO=='1']))[0])
# local
print('local 1/1',FP[FP.md=='01-01'].LOCAL_OCOR.value_counts(normalize=True).round(3).head(5).to_dict())
print('local geral',FP[~hol].LOCAL_OCOR.value_counts(normalize=True).round(3).head(5).to_dict())
print('local natal',FP[FP.md=='12-25'].LOCAL_OCOR.value_counts(normalize=True).round(3).head(5).to_dict())
# hours
h=FP.HORA_OCOR; ok=h.str.fullmatch(r'\d\d:\d\d'); hh=h.str[:2].where(ok).astype(float); mm=h.str[3:].where(ok).astype(float)
print('com hora %.3f, 1/1 %.3f'%(ok.mean(), ok[FP.md=='01-01'].mean()))
mad=(hh<6)
print('madrugada 1/1',(mad&(FP.md=='01-01')).sum(),'comum %.1f'%(mad.sum()/ND), 'minuto 00 share %.3f'%((mm==0).sum()/ok.sum()), '1/1 madrugada minuto 00 share %.3f'%((mm[mad&(FP.md=='01-01')]==0).mean()))
print(' sem :00 1/1', (mad&(FP.md=='01-01')&(mm!=0)).sum(),'comum %.1f'%((mad&(mm!=0)).sum()/ND))
print(' madrugada domingo comum %.1f'%((mad&(wd==6)&~hol).sum()/(dr.dayofweek==6).sum()))
print(' hora 00:00 exata share %.3f'%((h=='00:00').sum()/ok.sum()))
# 2023-2024
r=FP[FP.oc.dt.year>=2023]; print('2023-24 por dia %.1f'%(len(r)/731),'1/1 media',(r.md=='01-01').sum()/2,'natal',(r.md=='12-25').sum()/2)
# year trend of daily count
print('por ano FP', FP.groupby(FP.oc.dt.year).size().to_dict())
# AG_CORTE, VIOL_FISIC
print('fisica share geral %.3f 1/1 %.3f'%((FP.VIOL_FISIC=='1').mean(),(FP[FP.md=='01-01'].VIOL_FISIC=='1').mean()), 'corte geral %.3f 1/1 %.3f'%((FP.AG_CORTE=='1').mean(),(FP[FP.md=='01-01'].AG_CORTE=='1').mean()))
FP.to_parquet(A+'FP.parquet')
