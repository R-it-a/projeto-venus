import sys, pandas as pd
from dbfread import DBF
from multiprocessing import Pool
R='dados/'
A=R+'auditoria/'
SIMC=['DTOBITO','HORAOBITO','SEXO','CAUSABAS','LOCOCOR','CODMUNOCOR','IDADE','CIRCOBITO','DTNASC']
SINC=['DT_NOTIFIC','DT_OCOR','NU_ANO','CS_SEXO','LES_AUTOP','HORA_OCOR','LOCAL_OCOR','REL_CONJ','REL_EXCON','REL_NAMO','REL_EXNAM','REL_DESCO','REL_PAI','REL_MAE','REL_CONHEC','AUTOR_SEXO','AUTOR_ALCO','AG_CORTE','VIOL_FISIC','VIOL_SEXU','VIOL_PSICO','NDUPLIC','ID_MUNICIP','ID_MN_RESI','ID_MN_OCOR','ANO_NASC','NU_IDADE_N','TPUNINOT','OUT_VEZES','CS_RACA','SG_UF_NOT','EVOLUCAO','DT_DIGITA','ID_UNIDADE','CICL_VID','NUM_ENVOLV']
def sim(yy):
    t=DBF(R+'datasus_raw/DOEXT%s.dbf'%yy,encoding='latin-1',load=False,char_decode_errors='replace')
    fs=set(t.field_names); cols=[c for c in SIMC if c in fs]
    rows=[]
    for r in t:
        cb=(r.get('CAUSABAS') or '').strip()
        rows.append({c:(str(r[c]).strip() if r[c] is not None else '') for c in cols})
    df=pd.DataFrame(rows); df['FILE']=yy
    df.to_parquet(A+'sim_%s.parquet'%yy); return yy,len(df)
def sin(yy):
    t=DBF(R+'sinan_raw/VIOLBR%s.dbf'%yy,encoding='latin-1',load=False,char_decode_errors='replace')
    fs=set(t.field_names); cols=[c for c in SINC if c in fs]
    rows=[{c:(str(r[c]).strip() if r[c] is not None else '') for c in cols} for r in t]
    df=pd.DataFrame(rows); df['FILE']=yy
    df.to_parquet(A+'sin_%s.parquet'%yy); return yy,len(df)
if __name__=='__main__':
    simy=['%02d'%(y%100) for y in range(1996,2026)]
    siny=['%02d'%y for y in range(9,25)]
    with Pool(20) as p:
        a=p.map_async(sim,simy); b=p.map_async(sin,siny)
        print(a.get()); print(b.get())
