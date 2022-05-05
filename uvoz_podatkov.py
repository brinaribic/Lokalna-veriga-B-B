import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import csv

# povezava na bazo
conn = psycopg2.connect(database='sem2022_tiak', host='baza.fmf.uni-lj.si', user='javnost', password='javnogeslo')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def ustvari_tabele():
    with open('lokalna_veriga.sql') as f:
        koda = f.read()
    cur.execute(koda)
    conn.commit()


def pobrisi_tabelo(tabela):
    cur.execute("""
        DROP TABLE {0};
    """.format(tabela))
    conn.commit()

#def uvozi_podatke():
#    with open('podatki/zaposleni.csv', encoding='UTF-8') as f:
#        rd = csv.reader(f)
#        next(rd) # izpusti naslovno vrstico
#        for r in rd:
#            r = [None if x in ('','.') else x for x in r]
#            cur.execute("""
#            INSERT INTO zaposleni
#            (emso, ime, priimek, geslo)
#            VALUES (%s, %s, %s, %s)
#            """, r)
#            rid, = cur.fetchone()
#    conn.commit()

# uvoz podatkov v sql formatu na bazo 

def uvoziSQL(datoteka):
    with open(datoteka) as f:
        koda = f.read()
        cur.execute(koda)
    conn.commit()

#uvoziSQL('podatki/zaposleni.sql')
uvoziSQL('podatki/soba.sql')
uvoziSQL('podatki/lokacija.sql')
uvoziSQL('podatki/zajtrk.sql')
uvoziSQL('podatki/rezervacija.sql')