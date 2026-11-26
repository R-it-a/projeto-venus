import pandas as pd, numpy as np, glob
A='dados/auditoria/'
df=pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(A+'sin_*.parquet'))],ignore_index=True)
print('total linhas',len(df))
df['oc']=pd.to_datetime(df.DT_OCOR,errors='coerce'); df['no']=pd.to_datetime(df.DT_NOTIFIC,errors='coerce')
df['lag']=(df.no-df.oc).dt.days
df['md']=df.oc.dt.strftime('%m-%d')
df['parc']=df[['REL_CONJ','REL_EXCON','REL_NAMO','REL_EXNAM']].eq('1').any(axis=1)
df.to_parquet(A+'sin_all.parquet')
# Artefact checks by file year
g=df.groupby('FILE')
out=pd.DataFrame({'n':g.size(),'oc_na':g.oc.apply(lambda s:s.isna().mean()),'lag0':g.lag.apply(lambda s:(s==0).mean()),'lag01':g.lag.apply(lambda s:s.isin([0,1]).mean()),
 'oc_0101':g.md.apply(lambda s:(s=='01-01').mean()*365),'oc_day1':g.oc.apply(lambda s:(s.dt.day==1).mean()*30.4),'oc_day15':g.oc.apply(lambda s:(s.dt.day==15).mean()*30.4),
 'lagneg':g.lag.apply(lambda s:(s<0).mean())})
print(out.round(3))
