import pandas as pd, numpy as np
A='dados/auditoria/'
ag=pd.read_parquet(A+'sim_ag.parquet'); ag=ag[ag.dt.notna()&ag.SEXO.isin(['1','2'])]
ag['md']=ag.dt.dt.strftime('%m-%d'); ND=10958
for sx in ['2','1']:
    s=ag[ag.SEXO==sx]; base=len(s)/ND
    d1=s[(s.dt.dt.day==1)&(s.dt.dt.month!=1)]; print(sx,'outros dias 1: %+.1f%%'%(100*((len(d1)/(30*11))/base-1)))
    print(' janela 31/12+1/1 %+.1f%%'%(100*((s.md.isin(['12-31','01-01']).sum()/60)/base-1)), ' janela 24-26/12 %+.1f%%'%(100*((s.md.isin(['12-24','12-25','12-26']).sum()/90)/base-1)))
    wd=s.dt.dt.dayofweek; dr=pd.date_range('1996-01-01','2025-12-31')
    hol=s.md.isin(['01-01','12-25'])
    sun=((wd==6)&~hol).sum()/(dr.dayofweek==6).sum(); print(' domingo media %.2f exc %+.1f%%; 1/1 vs domingo %+.1f%%'%(sun,100*(sun/base-1),100*((s.md=='01-01').sum()/30/sun-1)))
    # madrugada domingo 2006-2025
    h=s[(s.dt.dt.year>=2006)&s.HORAOBITO.str.fullmatch(r'\d{4}')]; H=h.HORAOBITO.str[:2].astype(int); w=h.dt.dt.dayofweek
    dr2=pd.date_range('2006-01-01','2025-12-31'); hh=h.md.isin(['01-01','12-25'])
    print(' madrugada domingo media/noite %.2f x20 = %.1f ; 1/1 = %d'%(((H<6)&(w==6)&~hh).sum()/(dr2.dayofweek==6).sum(), 20*((H<6)&(w==6)&~hh).sum()/(dr2.dayofweek==6).sum(), ((H<6)&(h.md=='01-01')).sum()))
    # yearly 1/1 counts women
    if sx=='2': print(' 1/1 por ano', s[s.md=='01-01'].groupby(s.dt.dt.year).size().to_dict())
    # 1/1 records missing hour/age/local (unknown-date default sign)
    print(' IDADE vazio/9xx 1/1 %.3f geral %.3f'%(s[s.md=='01-01'].IDADE.str.startswith('9').mean() if True else 0, s.IDADE.str.startswith('9').mean()))
