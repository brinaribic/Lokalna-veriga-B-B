from bottle import *
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki

import os
import hashlib
import datetime

napakaSporocilo = None
# funkcija za brisanje in nastavljanje sporočila ob morebitnem pojavu napake
def nastaviSporocilo(sporocilo = None):
    global napakaSporocilo
    staro = napakaSporocilo
    napakaSporocilo = sporocilo
    return staro

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 


# mapa za statične vire
static_dir = "./static"

# streženje statičnih datotek
@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

# Odkomentiraj, če želiš sporočila o napakah
debug(True)

skrivnost = "k1094107c907cw982982c42"

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


@get('/')
def index():
    redirect('/izbira_uporabnika')

# Ali se želimo prijaviti kot zaposleni ali skozi rezervacijo:
@get('/izbira_uporabnika')
def izbira_uporabnika():
    napaka = nastaviSporocilo(None)
    return template('izbira_uporabnika.html', izbira_uporabnika=izbira_uporabnika, napaka=napaka)


@get('/zaposleni/prijava') 
def prijava_get():
    napaka = nastaviSporocilo()
    return template("prijava_zaposleni.html", napaka=napaka)

@post('/zaposleni/prijava') 
def prijava_post():
    emso = request.forms.get('emso')
    geslo = request.forms.get('geslo')
    if emso is None or geslo is None:
        nastaviSporocilo('Izpolniti morate vsa okenca.') 
        redirect('/zaposleni/prijava')
    redirect('/zaposleni/izbira')


# Kaj si želimo ogledati/potencialno spremeniti kot zaposleni:
@get('/zaposleni/izbira')
def izbira_pregleda():
    return template('izbira_pregleda.html', izbira_pregleda=izbira_pregleda)

@get('/zaposleni/rezervacije')
def pregled_vseh_rezervacij():
    cur.execute("""
        SELECT id, rezervirana_soba, pricetek_bivanja, stevilo_nocitev, vkljucuje FROM rezervacija
        ORDER BY pricetek_bivanja
    """)
    rezervacija = cur.fetchall()
    return template('pregled_rezervacija.html', rezervacija=rezervacija)

@get('/zaposleni/osebje')
def pregled_osebja():
    napaka = nastaviSporocilo()
    cur.execute("""
        SELECT emso, ime, priimek FROM zaposleni
        ORDER BY priimek
    """)
    osebje = cur.fetchall()
    return template('pregled_zaposleni.html', osebje=osebje, napaka=napaka)

# dodajanje zaposlenih - dostop do ustreznega okna in potrditev izpolnjenega obrazca
@get('/zaposleni/osebje/dodaj')
def dodaj_zaposlenega_get():
    return template('zaposleni_uredi.html')

@post('/zaposleni/osebje/dodaj')
def dodaj_zaposlenega():
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    cur.execute("INSERT INTO zaposleni (emso, ime, priimek) VALUES (%s, %s, %s)", (emso, ime, priimek))
    conn.commit()
    redirect('/zaposleni/osebje')

# urejanje osebja
@get('/zaposleni/osebje/uredi/<emso>')
def uredi_zaposlenega_get(emso):
    cur.execute("SELECT emso, ime, priimek FROM zaposleni WHERE emso = %s", (emso, ))
    zaposleni = cur.fetchone()
    return template('zaposleni_uredi.html', zaposleni=zaposleni)

@post('/zaposleni/osebje/uredi/<emso>')
def uredi_zaposlenega_post(emso):
    ime = request.forms.ime
    priimek = request.forms.priimek
    cur.execute("UPDATE zaposleni SET ime = %s, priimek = %s WHERE emso = %s", (ime, priimek, emso))
    conn.commit()
    redirect('/zaposleni/osebje')

@get('/zaposleni/lokacije')
def pregled_lokacij():
    cur.execute("""
        SELECT lokacija.id, lokacija.ime AS lokacija, zaposleni.ime, zaposleni.priimek 
        FROM lokacija
        INNER JOIN zaposleni ON lokacija.vodja = zaposleni.emso
    """)
    lokacije = cur.fetchall()
    return template('pregled_lokacij.html', lokacije=lokacije)

# pregled sob na določeni lokaciji
@get('/zaposleni/sobe/<id>')
def pregled_sob_lokacije(id):
    cur.execute("""
        SELECT soba.id, velikost, cena, zaposleni.ime, zaposleni.priimek FROM soba
        INNER JOIN lokacija ON soba.lokacija = lokacija.id
        INNER JOIN zaposleni ON soba.ureja = zaposleni.emso
        WHERE lokacija = %s
        ORDER BY soba.id
        """, 
        (id, ))
    sobe = cur.fetchall()
    return template('pregled_sob.html', sobe=sobe)

@get('/zaposleni/zajtrki')
def pregled_zajtrkov():
    napaka = nastaviSporocilo() # s tem izbrišemo  napako in dobimo morebitno novo sporočilo
    cur.execute("""
        SELECT id, ime, cena
        FROM zajtrk
        ORDER BY id
    """)
    zajtrki = cur.fetchall()
    return template('pregled_zajtrkov.html', zajtrki=zajtrki, napaka=napaka)

# dodajanje zajtrkov
@get('/zaposleni/zajtrki/dodaj')
def dodaj_zajtrk_get():
    return template('zajtrk_uredi.html')

@post('/zaposleni/zajtrki/dodaj')
def dodaj_zajtrk():
    id = request.forms.id
    ime = request.forms.ime
    cena = request.forms.cena
    cur.execute("INSERT INTO zajtrk (id, ime, cena) VALUES (%s, %s, %s)", (id, ime, cena))
    conn.commit()
    redirect('/zaposleni/zajtrki')

# urejanje zajtrkov
@get('/zaposleni/zajtrki/uredi/<id>')
def uredi_zajtrk_get(id):
    cur.execute("SELECT id, ime, cena FROM zajtrk WHERE id = %s", (id, ))
    zajtrk = cur.fetchone()
    return template('zajtrk_uredi.html', zajtrk=zajtrk)

@post('/zaposleni/zajtrki/uredi/<id>')
def uredi_zajtrk_post(id):
    ime = request.forms.ime
    cena = request.forms.cena
    cur.execute("UPDATE zajtrk SET ime = %s, cena = %s WHERE id = %s", (ime, cena, id))
    conn.commit()
    redirect('/zaposleni/zajtrki')

@get('/rezervacija/prijava')
def rezervacija_prijava_get():
    napaka = nastaviSporocilo()
    return template("prijava_rezervacija.html", napaka=napaka)

@post('/rezervacija/prijava') 
def rezervacija_prijava_post():
    id = request.forms.get('id')
    geslo = request.forms.get('geslo')
    hashBaza = None
    try: 
        cur.execute("SELECT geslo FROM rezervacija WHERE id = %s", [id])
        hashBaza = cur.fetchall()[0][0]
    except:
        hashBaza = None
    if hashBaza is None:
        nastaviSporocilo('Prijava ni mogoča.') 
        redirect('/rezervacija/prijava')
        return
    if hashGesla(geslo) != hashBaza:
        nastaviSporocilo('Nekaj je šlo narobe.') 
        redirect('/rezervacija/prijava')
        return
    redirect(f'/rezervacija/pregled/{id}')



@get('/rezervacija/nova/lokacija')
def izbira_lokacije():
    cur.execute("""
        SELECT id, ime
        FROM lokacija
        ORDER BY id
    """)
    lokacija = cur.fetchall()
    return template('izbira_lokacije.html',lokacija=lokacija)

@get('/rezervacija/nova/<id_lokacije>')
def nova_rezervacija(id_lokacije):
    cur.execute("""
    SELECT lokacija.id, lokacija.ime FROM lokacija
    INNER JOIN soba ON soba.lokacija = lokacija.id
    INNER JOIN rezervacija ON rezervirana_soba = soba.id
    WHERE lokacija = %s
    """,
    (id_lokacije, ))
    rezervacija = cur.fetchall()
    cur.execute("""
    SELECT id, velikost, lokacija, cena
    FROM soba
    WHERE lokacija = %s
    """,
    (id_lokacije, ))
    soba = cur.fetchall()
    cur.execute("""
        SELECT id, ime, cena
        FROM zajtrk
        ORDER BY id
    """)
    zajtrki = cur.fetchall()
    return template('nova_rezervacija.html', nova_rezervacija=nova_rezervacija, zajtrki=zajtrki, rezervacija=rezervacija, soba=soba)


@post('/rezervacija/nova/<id_lokacije>')
def dodaj_rezervacijo(id_lokacije):
    cur.execute("SELECT MAX(id) FROM rezervacija")
    id = cur.fetchall()[0][0] + 1 
    rezervirana_soba = request.forms.rezervirana_soba
    pricetek_bivanja = request.forms.pricetek_bivanja
    stevilo_nocitev = request.forms.stevilo_nocitev
    vkljucuje = request.forms.vkljucuje
    geslo = request.forms.geslo
    zgostitev = hashGesla(geslo)
    cur.execute("INSERT INTO rezervacija (id, rezervirana_soba, pricetek_bivanja, stevilo_nocitev, vkljucuje, geslo) VALUES (%s, %s, %s, %s, %s, %s)",
                    (id, rezervirana_soba, pricetek_bivanja, stevilo_nocitev, vkljucuje, zgostitev))
    conn.commit()
    redirect(f'/rezervacija/zakljucek/{id}')

@get('/rezervacija/zakljucek/<id>')
def konec_rezervacije(id):
    id=id
    cur.execute("SELECT id,rezervirana_soba,pricetek_bivanja,stevilo_nocitev,vkljucuje FROM rezervacija WHERE id = %s", 
    (id, ))
    rezervacija = cur.fetchall()
    stevilo_nocitev = datetime.timedelta(rezervacija[0][3])
    pricetek_bivanja = datetime.datetime.strptime(str(rezervacija[0][2]), "%Y-%m-%d")
    konec_bivanja = stevilo_nocitev + pricetek_bivanja
    konec_bivanja = konec_bivanja.date()
    # dodaj se celotno placilo 
    return template('rezervacija_konec.html',id=id,rezervacija=rezervacija,konec_bivanja=konec_bivanja, pricetek_bivanja=pricetek_bivanja)


# poizvedba, ki uporabniku vrne le njegovo rezervacijo
@get('/rezervacija/pregled/<id>')
def pregled_rezervacije(id):
    cur.execute("SELECT id,rezervirana_soba,pricetek_bivanja,stevilo_nocitev,vkljucuje FROM rezervacija WHERE id = %s", 
    (id, ))
    rezervacija = cur.fetchall()
    stevilo_nocitev = datetime.timedelta(rezervacija[0][3])
    pricetek_bivanja = datetime.datetime.strptime(str(rezervacija[0][2]), "%Y-%m-%d")
    konec_bivanja = stevilo_nocitev + pricetek_bivanja
    konec_bivanja = konec_bivanja.date()
    return template('pregled_rezervacija.html', rezervacija=rezervacija,konec_bivanja=konec_bivanja)





# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)