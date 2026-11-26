"""Extrai das notificacoes oficiais do SINAN (VIOLBRyy.dbc, DATASUS) os campos usados no estudo."""
import sys, os, glob, datasus_dbc, dbfread, pandas as pd
from multiprocessing import Pool
F=["DT_NOTIFIC","DT_OCOR","HORA_OCOR","CS_SEXO","NU_IDADE_N","CS_RACA","LES_AUTOP","LOCAL_OCOR","OUT_VEZES",
   "REL_CONJ","REL_EXCON","REL_NAMO","REL_EXNAM","REL_DESCO","REL_CONHEC","REL_PAI","REL_MAE","REL_PAD","REL_FILHO","REL_IRMAO",
   "AUTOR_SEXO","AUTOR_ALCO","VIOL_FISIC","VIOL_PSICO","VIOL_SEXU","AG_FORCA","AG_CORTE","AG_FOGO","AG_ENFOR","EVOLUCAO","ID_AGRAVO","NDUPLIC"]
def one(f):
    dbf=f[:-4]+".dbf"
    if not os.path.exists(dbf): datasus_dbc.decompress(f,dbf)
    t=dbfread.DBF(dbf,encoding="latin-1",char_decode_errors="replace")
    miss=[c for c in F if c not in t.field_names]
    rows=[[("" if r.get(c) is None else str(r.get(c)).strip()) for c in F] for r in t]
    df=pd.DataFrame(rows,columns=F); df["ARQ"]=os.path.basename(f)
    return df, (os.path.basename(f), miss, len(df))
if __name__=="__main__":
    with Pool(8) as p: res=p.map(one,sorted(glob.glob(sys.argv[1]+"/VIOLBR*.dbc")))
    for _,m in res: print(m)
    pd.concat([r[0] for r in res]).to_parquet(sys.argv[2])
