"""Extrai dos arquivos oficiais do SIM (DOEXTyy.dbc, DATASUS) os obitos por agressao (CID-10 X85-Y09), ambos os sexos."""
import sys, os, glob, datasus_dbc, dbfread, pandas as pd
from multiprocessing import Pool
F=["DTOBITO","HORAOBITO","SEXO","CAUSABAS","LOCOCOR","IDADE","DTNASC","RACACOR","CODMUNOCOR","CODMUNRES","CIRCOBITO","ESTCIV"]
def one(f):
    dbf=f[:-4]+".dbf"
    if not os.path.exists(dbf): datasus_dbc.decompress(f,dbf)
    t=dbfread.DBF(dbf,encoding="latin-1",char_decode_errors="replace")
    miss=[c for c in F if c not in t.field_names]; tot=0; rows=[]
    for r in t:
        tot+=1; c=(r.get("CAUSABAS") or "").strip()
        if "X85"<=c[:3]<="Y09": rows.append([("" if r.get(k) is None else str(r.get(k)).strip()) for k in F])
    df=pd.DataFrame(rows,columns=F); df["ARQ"]=os.path.basename(f)
    return df,(os.path.basename(f),miss,tot,len(df))
if __name__=="__main__":
    with Pool(8) as p: res=p.map(one,sorted(glob.glob(sys.argv[1]+"/DOEXT*.[dD][bB][cC]")))
    for _,m in res: print(m)
    pd.concat([r[0] for r in res]).to_parquet(sys.argv[2])
