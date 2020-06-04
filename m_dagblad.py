# coding: utf-8
from bottle import route, run, template, request, static_file, redirect, error, os
import psycopg2
from time import gmtime, strftime
from datetime import datetime, timedelta

# connect
conn = psycopg2.connect(dbname="ai7773_dagbladm", user="ai7773", password="bo16ns3r", host="pgserver.mah.se")
conn.set_client_encoding('UTF8')

# create a cursor
cursor = conn.cursor()

@route("/")
def list_articles():
    '''
    Hämtar alla artiklar som är skapade inom en 14-dagars period från dagens datum.
    Titel, ingress, datum och artikel-id hämtas tillsammans med dess huvudkategori.
    '''
    datum_nu = datetime.now().strftime('%Y-%m-%d')
    datum_innan = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')

    cursor.execute("select distinct h.huvudkategori from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where a.undid=u.undid order by h.huvudkategori asc;")
    hcat = cursor.fetchall()

    cursor.execute("select titel, datum, ingress, artikelid from artikel where datum between %s and %s order by datum desc;", (datum_innan, datum_nu,))
    articles = cursor.fetchall()

    cursor.execute("select ")

    return template("public/index", articles=articles, hcat=hcat)

@route("/category/<pagename>")
def main_category(pagename):
    '''
    Visar upp alla artiklar med den specificerade huvudkategorin. Listar även underkategorierna som den huvudkategorien innehåller.
    '''
    pagename=pagename
    
    cursor.execute("select distinct h.huvudkategori from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where a.undid=u.undid order by h.huvudkategori asc;")
    hcat = cursor.fetchall()
    
    cursor.execute("select titel, datum, ingress, artikelid from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where h.huvudkategori=%s;", (pagename,))
    articles = cursor.fetchall()

    cursor.execute("select distinct u.underkategori, h.huvudkategori from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where h.huvudkategori=%s;", (pagename,))
    subcat = cursor.fetchall()

    return template("public/main_category", articles=articles, hcat=hcat, subcat=subcat, pagename=pagename)

@route("/subcategory/<pagename1>/<pagename2>")
def sub_category(pagename1, pagename2):
    '''
    Visar upp alla artiklar med den specificerade underkategorin.
    '''

    pagename1=pagename1
    pagename2=pagename2

    cursor.execute("select distinct h.huvudkategori from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where a.undid=u.undid order by h.huvudkategori asc;")
    hcat = cursor.fetchall()
    
    cursor.execute("select titel, datum, ingress, artikelid from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where h.huvudkategori=%s and u.underkategori=%s;", (pagename1, pagename2,))
    articles = cursor.fetchall()

    return template("public/sub_category", articles=articles, hcat=hcat, pagename1=pagename1, pagename2=pagename2)

@route("/login", method="POST")
def login():
    '''
    En admin kan "logga in" för att komma till administrationsidan. 
    Skrivs fel användarnamn och lösenord in så studsar användaren tillbaka till förstasidan igen bara
    '''
    user = getattr(request.forms, "user")
    pwd = getattr(request.forms, "pwd")

    if user == "admin" and pwd == "12345":
        redirect("/admin")

    else:
        redirect("/")

@route("/admin")
def admin_view():
    '''
    Sidan som användaren möts av när hen loggar in på administrationssidan.
    '''
    cursor.execute("select Titel, Ingress from Artikel;")
    articles = cursor.fetchall()

    cursor.execute("select namn from journalist")
    journalist = cursor.fetchall()

    return template("public/admin", articles=articles, journalist=journalist)
    
@route('/admin_comments/<pagename>')
def admin_comments(pagename):
    '''
    Genom administrationen går det att se kommentarer som skrivits kopplade till dess artikel.
    Det går även att ta bort enskilda kommentarer.
    '''
    cursor.execute("select ArtikelID, Titel from Artikel where Titel=%s;", (pagename,))
    artikel = cursor.fetchone()

    cursor.execute("select kommentar.Signatur, kommentar.Kommentar, kommentar.Datum, kommentar.Tid, kommentar.id from (artikel join kommentar on artikel.artikelid=kommentar.artikelid) where artikel.artikelid=%s;", (artikel[0],))
    kommentarer = cursor.fetchall()

    return template('public/admin_comments', kommentarer=kommentarer, artikel=artikel)

@route('/admin/staff')
def admin_staff():
    '''
    Visar upp sidan över antal anställda. 
    '''
    cursor.execute("select personnr, namn, anteckningar from journalist order by namn asc")
    journalister = cursor.fetchall()

    return template("public/admin_staff", journalister=journalister)

@route('/create-staff', method="POST")
def create_staff():
    '''
    Från sidan med antal anställda kan man lägga till ny personal. 
    Formuläret skickas hit där nedan parametrar tas emot.
    '''
    personnummer = getattr(request.forms, "personnummer")
    namn = getattr(request.forms, "namn")
    inriktning = getattr(request.forms, "inriktning")

    cursor.execute("insert into journalist values (%s, %s, %s);", (personnummer, namn, inriktning,))
    conn.commit()

    redirect("/admin/staff")

@route("/artikel/<pagename>")
def show_article(pagename):
    '''
    Visar upp enskild artikel tillsammans med tillhörande bild och bildtext.
    '''
    cursor.execute("select distinct h.huvudkategori from (underkategori as u join artikel as a on u.undid=a.undid join huvudkategori as h on u.hid=h.hid) where a.undid=u.undid order by h.huvudkategori asc;")
    hcat = cursor.fetchall()

    cursor.execute("select Titel, Artikel, Datum, ArtikelID, ingress from Artikel where Titel=%s;", (pagename,))
    artikel = cursor.fetchone()
    id = artikel[3]

    cursor.execute("select journalist.namn from (journalist join publicering on journalist.personnr=publicering.personnr) where publicering.artikelid = %s", (id,))
    journalist = cursor.fetchall()

    cursor.execute("select kommentar.Signatur, kommentar.Kommentar, kommentar.Datum, kommentar.Tid, kommentar.id from (artikel join kommentar on artikel.artikelid=kommentar.artikelid) where artikel.Titel=%s order by kommentar.datum desc;", (artikel[0],))
    kommentarer = cursor.fetchall()

    cursor.execute("select bild.filnamn, bild.alttext, bild_artikel.bild_text from (bild_artikel join bild on bild_artikel.bildid=bild.bildid) where bild_artikel.artikelID=%s", (id,))
    bild = cursor.fetchall()

    return template("public/artikel", artikel=artikel, kommentarer=kommentarer, journalist=journalist, bild=bild, hcat=hcat)

@route("/kommentar", method="POST")
def comment():
    '''
    Från en enskild artikel kan kommentarer göras, formuläret skickas hit där nedan parametrar tas emot.
    '''
    tid = datetime.now().strftime('%H:%M:%S')
    datum = datetime.now().strftime('%Y-%m-%d')
    signatur = getattr(request.forms, "signatur")
    kommentar = getattr(request.forms, "kommentar")
    id = getattr(request.forms, "id")

    cursor.execute("insert into kommentar (signatur, kommentar, datum, tid, ArtikelID) values (%s, %s, %s, %s, %s)", (signatur, kommentar, datum, tid, id,))
    conn.commit()

    cursor.execute("select titel from artikel where artikelid=%s", (id,))
    artikelid = cursor.fetchone()
    artid = artikelid[0]

    redirect ("/artikel/" + artid)

@route('/delete', method="POST")
def delete_comment():
    '''
    Från administrationsvyn kan enskilda kommentarer tas bort. Formuläret från den sidan skickas hit och nedan parametrar tas emot och därefter raderas kommentaren i databasen.
    '''
    delete = getattr(request.forms, "id")
    id = getattr(request.forms, "artikelid")

    cursor.execute("delete from kommentar where ID=%s", (delete,))
    conn.commit()

    cursor.execute("select titel from artikel where artikelid=%s", (id,))
    artikelid = cursor.fetchone()
    artid = artikelid[0]

    redirect ('/admin_comments/' + artid)

@route('/create', method="POST")
def add_article():
    '''
    Via administrationsvyn går det att skapa en ny artikel, formulöäret skickas hit där nedan parametrar tas emot.
    '''
    titel = getattr(request.forms, "titel")
    ingress = getattr(request.forms, "ingress")
    artikel = getattr(request.forms, "artikel")
    datum = datetime.now().strftime('%Y-%m-%d')
    journalist = getattr(request.forms, "journalist")
    huvudkategori = getattr(request.forms, "huvudkategori")
    underkategori = getattr(request.forms, "underkategori")

    bild = request.files.get('bild')
    bilden = os.path.splitext(bild.filename)
    bilder = ''.join(map(str, bilden))
    bildtext = getattr(request.forms, "bildtext")
    alttext = getattr(request.forms, "alttext")

    save_path = "/Users/Zandra/Skrivbord/Mörtforsdagblad/static"
    file_path = "{path}/{file}".format(path=save_path, file=bild.filename)
    bild.save(file_path)
   
    if journalist == "--":
        redirect("fel")
    
    else:
        cursor.execute("insert into huvudkategori (huvudkategori) values (%s);", (huvudkategori,))
        cursor.execute("select hid from huvudkategori where huvudkategori=%s;", (huvudkategori,))
        hkat = cursor.fetchone()
        hid = hkat[0]

        cursor.execute("insert into underkategori (underkategori, hid) values (%s, %s);", (underkategori, hid,))
        cursor.execute("select undid from underkategori where underkategori=%s;", (underkategori,))
        ukat = cursor.fetchone()
        uid = ukat[0]

        cursor.execute("insert into artikel (titel, ingress, artikel, datum, undid) values (%s, %s, %s, %s, %s)", (titel, ingress, artikel, datum, uid,))

        cursor.execute("select personnr from journalist where namn=%s", (journalist,))
        person = cursor.fetchall()
        pers = person[0]
        cursor.execute("select ArtikelID from artikel where titel=%s", (titel,))
        id = cursor.fetchall()
        aid = id[0]

        cursor.execute("insert into publicering values (%s, %s)", (aid, pers,))

        cursor.execute("insert into bild (filnamn, alttext) values (%s, %s);", (bilder, alttext,))

        cursor.execute("select BildID from bild where filnamn=%s", (bilder,))
        bid = cursor.fetchall()
        bildid = bid[0]

        cursor.execute("insert into bild_artikel values (%s, %s, %s);", (aid, bildid, bildtext,))
       
        conn.commit()

        redirect ("/admin")

@route('fel')
def fel():
    '''
    Om ingen journalist väljs vid skapandet av ny artikel så omdirigeras användaren till denna sida.
    '''
    return template('public/fel')

@route("/static/<filename>")
def static_files(filename):
    '''
    Handles the routes to our static files
    '''

    return static_file(filename, root="static")

run(host='localhost', port=8081, debug=True, reloader=True)

