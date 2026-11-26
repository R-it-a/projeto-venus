import pandas as pd
A='dados/auditoria/'
d=pd.read_parquet(A+'sin_19.parquet')
for c in ['DT_NOTIFIC','DT_OCOR','HORA_OCOR','LOCAL_OCOR','REL_CONJ','AUTOR_ALCO','AUTOR_SEXO','LES_AUTOP','NDUPLIC','TPUNINOT','CS_SEXO','NU_ANO','DT_DIGITA']:
    print(c, d[c].value_counts().head(8).to_dict())
