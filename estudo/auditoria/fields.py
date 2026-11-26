from dbfread import DBF
import sys
R='dados/'
for f in ['datasus_raw/DOEXT96.dbf','datasus_raw/DOEXT06.dbf','datasus_raw/DOEXT25.dbf','sinan_raw/VIOLBR11.dbf','sinan_raw/VIOLBR16.dbf','sinan_raw/VIOLBR24.dbf']:
    t=DBF(R+f,encoding='latin-1',load=False); print(f,len(t), t.field_names)
