import pandas as pd, numpy as np

A='dados/auditoria/'
ag=pd.read_parquet(A+'sim_ag.parquet'); ag=ag[ag.dt.notna()&ag.SEXO.isin(['1','2'])]
ag['md']=ag.dt.dt.strftime('%m-%d'); ag['y']=ag.y.astype(int)
ND=10958
def poisci(n):
    return n-1.96*np.sqrt(n), n+1.96*np.sqrt(n)
for sx,nm in [('2','MULHER'),('1','HOMEM')]:
    s=ag[ag.SEXO==sx]; T=len(s); base=T/ND
    print('\n=====',nm,'total',T,'por ano',T/30,'por dia',base)
    c=s.groupby('md').size()
    exc=(c/30)/base-1
    # 29/02 correct: only 8 leap years
    c2=c.copy().astype(float); per=c2/30; per['02-29']=c['02-29']/8 if '02-29' in c else 0
    exc2=per/base-1
    for k in ['01-01','12-25','12-24','12-31','01-02','01-03','11-02','06-12']:
        n=c.get(k,0); lo,hi=poisci(n)
        print(k,n,'media/dia %.2f'%(n/30),'exc %+.1f%%'%(100*exc2[k]),'IC poisson %+.0f%% a %+.0f%%'%(100*(lo/30/base-1),100*(hi/30/base-1)))
    print('top5', exc2.sort_values(ascending=False).head(6).round(3).to_dict())
    # per-year ratio 1/1 vs own year daily mean
    yd=s.groupby('y').size(); ndays=pd.Series({y:(366 if pd.Timestamp(y,12,31).dayofyear==366 else 365) for y in yd.index})
    j1=s[s.md=='01-01'].groupby('y').size().reindex(yd.index,fill_value=0)
    r=j1/(yd/ndays)
    print('anos 1/1 acima media do ano', (r>1).sum(),'de',len(r),'min ratio',r.min().round(2), 'mediana',r.median().round(2))
    # yearly-bootstrap CI (overdispersion)
    lr=np.log(r[r>0]); 
    bs=[]; rng=np.random.default_rng(1); yrs=yd.index.values
    for _ in range(5000):
        b=rng.choice(yrs,len(yrs)); bs.append(j1[b].sum()/(yd[b]/ndays[b]).sum())
    print('ratio agregado %.3f'%(j1.sum()/(yd/ndays).sum()),'bootstrap anos IC95', np.percentile(bs,[2.5,97.5]).round(3))
    # weekday control: expected = mean daily deaths on same weekday in same year
    s2=s.copy(); s2['wd']=s2.dt.dt.dayofweek
    cnt=s2.groupby(['y','wd']).size()
    nwd={}
    for y in yd.index:
        dr=pd.date_range(f'{y}-01-01',f'{y}-12-31'); nwd.update({(y,w):(dr.dayofweek==w).sum() for w in range(7)})
    exp=0;obs=0
    for y in yd.index:
        w=pd.Timestamp(y,1,1).dayofweek; exp+=cnt.get((y,w),0)/nwd[(y,w)]; obs+=j1[y]
    print('controle dia semana: obs',obs,'esp %.1f'%exp,'exc %+.1f%%'%(100*(obs/exp-1)))
    # and vs same-weekday excluding holidays, and vs Jan mean
    jan=s2[(s2.dt.dt.month==1)&(s2.dt.dt.day>=8)&(s2.dt.dt.day<=31)].groupby('y').size()/24
    print('vs media 8-31 jan:', '%+.1f%%'%(100*(j1.sum()/jan.sum()-1)))
    nat=s[s.md=='12-25'].groupby('y').size().reindex(yd.index,fill_value=0)
    print('natal acima media do ano',(nat/(yd/ndays)>1).sum())
    # decades
    for a,b in [(1996,2005),(2006,2015),(2016,2025)]:
        ss=s[(s.y>=a)&(s.y<=b)]; nd=(pd.Timestamp(b,12,31)-pd.Timestamp(a,1,1)).days+1
        n=(ss.md=='01-01').sum(); print(a,b,'1/1 n',n,'exc %+.1f%%'%(100*((n/10)/(len(ss)/nd)-1)), 'natal %+.1f%%'%(100*(((ss.md=='12-25').sum()/10)/(len(ss)/nd)-1)))
    # local
    lc=s.LOCOCOR.value_counts(normalize=True).round(4).to_dict(); print('LOCOCOR geral',lc)
    print('LOCOCOR 1/1',s[s.md=='01-01'].LOCOCOR.value_counts(normalize=True).round(4).to_dict())
    print('LOCOCOR natal',s[s.md=='12-25'].LOCOCOR.value_counts(normalize=True).round(4).to_dict())
    # excess by location
    for l in ['1','3','4']:
        sl=s[s.LOCOCOR==l]; n=(sl.md=='01-01').sum(); print(' local',l,'1/1 exc %+.1f%%'%(100*((n/30)/(len(sl)/ND)-1)),'n',n)
    # hours
    h=s[(s.y>=2006)].copy(); hh=h.HORAOBITO
    print('HORAOBITO len',hh.str.len().value_counts().to_dict())
    h['ok']=hh.str.fullmatch(r'\d{4}') & (hh.str[:2].astype(float,errors='ignore').where(hh.str.fullmatch(r'\d{4}')).fillna(99).astype(float)<24)
    print('%% com hora geral %.3f'%h.ok.mean(),'1/1 %.3f'%h[h.md=='01-01'].ok.mean(),'natal %.3f'%h[h.md=='12-25'].ok.mean())
    hv=h[h.ok].copy(); hv['H']=hv.HORAOBITO.str[:2].astype(int); hv['M']=hv.HORAOBITO.str[2:].astype(int)
    print('share minuto 00 geral %.3f'%(hv.M==0).mean(), ' share hora exata 0000 %.4f'%(hv.HORAOBITO=='0000').mean(),'vs 0001-0059 media por minuto %.4f'%(((hv.H==0)&(hv.M>0)).mean()/59))
    md=hv[hv.H<6]
    for k in ['01-01','12-25','12-24','12-31']:
        n=(md.md==k).sum(); n00=((md.md==k)&(md.M!=0)).sum(); n0000=((md.md==k)&(md.HORAOBITO=='0000')).sum()
        print(' madrugada',k,n,'sem :00',n00,'com 0000',n0000)
    com=len(md)/365.25; com00=(md.M!=0).sum()/365.25
    print(' noite comum %.1f'%com,'sem :00 %.1f'%com00, 'ratio 1/1 %.2f'%((md.md=='01-01').sum()/com),'ratio sem00 %.2f'%(((md.md=='01-01')&(md.M!=0)).sum()/com00))
    # madrugada 1/1 by hour
    print(' 1/1 por hora', md[md.md=='01-01'].groupby('H').size().to_dict(), 'comum por hora', (md.groupby('H').size()/365.25).round(1).to_dict())
    # hours 0-5 excluding 0000 exact
    x=md[md.HORAOBITO!='0000']; print(' sem 0000: 1/1',(x.md=='01-01').sum(),'comum %.1f'%(len(x)/365.25))
    # LOCOCOR in madrugada 1/1
    print(' local madrugada 1/1',md[md.md=='01-01'].LOCOCOR.value_counts().to_dict())
    # rest of 1/1 (6h-23h59)
    n=((hv.md=='01-01')&(hv.H>=6)).sum(); print(' 1/1 6h-24h',n,'comum %.1f'%((hv.H>=6).sum()/365.25))
