import pandas as pd, numpy as np, glob
A='dados/auditoria/'
df=pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(A+'sim_*.parquet'))],ignore_index=True)
df['cb3']=df.CAUSABAS.str[:3]
ag=df[(df.cb3>='X85')&(df.cb3<='Y09')].copy()
print('agressao total', len(ag), ag.SEXO.value_counts().to_dict())
d=ag.DTOBITO
print('DTOBITO len dist', d.str.len().value_counts().to_dict())
print('samples bad', d[d.str.len()!=8].head(20).tolist())
ag['dt']=pd.to_datetime(d.where(d.str.len()==8),format='%d%m%Y',errors='coerce')
ag['fileyear']=ag.FILE.astype(int).map(lambda x: 1900+x if x>=90 else 2000+x)
bad=ag[ag.dt.isna()]
print('invalid dates by sexo', bad.SEXO.value_counts().to_dict(), 'by file', bad.groupby('FILE').size().to_dict())
ag['y']=ag.dt.dt.year
print('year!=file', (ag.y!=ag.fileyear).sum(), ag[ag.y!=ag.fileyear].groupby(['fileyear','y']).size().head(30).to_dict())
ag.to_parquet(A+'sim_ag.parquet')
# deaths per year by file for women; 2025 by month vs 2024
v=ag[ag.dt.notna()]
print(v[v.SEXO=='2'].groupby('y').size().to_dict())
print('men', v[v.SEXO=='1'].groupby('y').size().to_dict())
m=v[(v.y>=2023)].groupby([v.y,v.dt.dt.month]).size().unstack(0); print(m)
