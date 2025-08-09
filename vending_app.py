from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash, jsonify
import json, os
from werkzeug.security import generate_password_hash, check_password_hash
import webbrowser
import threading
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "enova2025"
ARTIKLI_FAJL = 'artikli.json'
LOG_FAJL = 'log.txt'
SLIKE_FOLDER = os.path.join('static', 'slike')
os.makedirs(SLIKE_FOLDER, exist_ok=True)

# Lista podržanih jezika
JEZICI = ['sr', 'de', 'en']

PASSWORD = "securePassword123"
# Mock database (in a real app, use a proper database)
users_db = {
    "admin": {
        "password_hash": generate_password_hash(PASSWORD),
        "role": "admin"
    }
}


# Funkcija za učitavanje artikala
# Učitava artikle iz JSON fajla
def ucitaj_artikle():
    # Ako fajl ne postoji, vrati praznu listu
    if not os.path.exists(ARTIKLI_FAJL):
        return []
    # Učitava iz fajla u listu
    with open(ARTIKLI_FAJL, 'r', encoding='utf-8') as f:
        artikli = json.load(f)
    # Za svaki artikal, ako ne postoji 'plus18' ključ, postavi ga na False
    for a in artikli:
        if 'plus18' not in a:
            a['plus18'] = False
    return artikli

# Funkcija za učitavanje poruka (prema jeziku iz sesije)
def ucitaj_poruke(jezik):
    # Ako fajl ne postoji, vrati praznu listu
    if not os.path.exists("poruke.json"):
        return {}
    # Učitava iz fajla u listu
    try:
        # Učitava iz fajla u listu
        with open("poruke.json", "r", encoding="utf-8") as f:
            sve_poruke = json.load(f)
        # Pronalazi poruku prema jeziku
        return {
            k: v.get(jezik, v.get('sr', '')) 
            for k, v in sve_poruke.items()
        }
    except Exception as e:
        print(f"Greška pri učitavanju poruka: {e}")
        return {}

# Funkcija za čuvanje artikala
def sacuvaj_artikle(artikli):
    with open(ARTIKLI_FAJL, 'w', encoding='utf-8') as f:
        json.dump(artikli, f, indent=4, ensure_ascii=False)

# Funkcija za logovanje
def loguj(tekst):
    with open(LOG_FAJL, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] {tekst}\n")

# Populiše index strnicu
@app.route('/')
def index():
    # Učitava artikle
    artikli = [a for a in ucitaj_artikle() if a.get('aktivan', True)]
    # Učitava jezik
    jezik = session.get('lang', 'sr')
    # Učitava poruke za trenutni jezik
    poruke = ucitaj_poruke(jezik)
    audio_kljuc = "izaberi"
    poruka_audio = f"static/audio/{audio_kljuc}_{jezik}.mp3"
    # Renderuje stranicu
    return render_template('index.html', artikli=artikli, poruke=poruke, poruka_audio=poruka_audio)
    
# Stranica za uređivanje
@app.route("/edit")
def edit():
    return render_template("edit.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real app, check if user is logged in via session
        if not request.headers.get('Authorization'):
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    # Serve the login page
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
    </head>
    <body>
        <h1>Please login at <a href="/login">/login</a></h1>
    </body>
    </html>
    """

# login stranica
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = users_db.get(username)

    if user and check_password_hash(user['password_hash'], password):
        return jsonify({
            "message": "Login successful",
            "user": {
                "username": username,
                "role": user['role']
            }
        })
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/dashboard')
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
    </head>
    <body>
        <script>
            window.location.href = 'admin';
        </script>
    </body>
    </html>
    """

# Funkcija za postavljanje jezika
@app.route("/lang/<jezik>", methods=["POST"])
def postavi_jezik(jezik):
    if jezik in JEZICI:
        session['lang'] = jezik
        flash("Jezik promenjen.")
    return redirect(request.referrer or url_for('index'))

# Stranica za admina
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Učitava artikle
    artikli = ucitaj_artikle()
    # Ako je zahtev POST
    if request.method == 'POST':
        # Resetuje vrednosti za svaki artikal, čuva i loguje promene
        if 'reset' in request.form:
            for a in artikli:
                a['zaduzeno'] = 0
                a['prodato'] = 0
            sacuvaj_artikle(artikli)
            loguj("Resetovane vrednosti za sve artikle.")
            return redirect(url_for('admin'))

        # Za svaki artikal, učitava vrednosti iz zahteva
        for j in range(len(artikli)):
            artikli[j]['aktivan'] = ('aktivan%d' % j) in request.form
            artikli[j]['plus18'] = ('plus18%d' % j) in request.form
            artikli[j]['naziv'] = request.form.get(f'naziv{j}', artikli[j]['naziv'])
            try:
                artikli[j]['cena'] = float(request.form.get(f'cena{j}', artikli[j]['cena']))
            except:
                pass

            fslika = request.files.get(f'slika{j}')
            if fslika and fslika.filename:
                fname = f'slot{j}.{fslika.filename.split(".")[-1].lower()}'
                slika_path = os.path.join(SLIKE_FOLDER, fname)
                fslika.save(slika_path)
                artikli[j]['slika'] = fname

            try:
                dop = int(request.form.get(f'dopuni{j}', 0))
                if dop != 0:
                    artikli[j]['zaduzeno'] += dop
            except:
                pass

        sacuvaj_artikle(artikli)
        loguj("Ažurirani artikli preko admin panela.")
        return redirect(url_for('admin'))
    return render_template('admin.html', artikli=artikli)

# Bavi se dodavanjem novih artikala
@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj():
    artikli = ucitaj_artikle()

    # Brisanje
    if request.method == 'POST' and 'brisanje' in request.form:
        index = int(request.form.get('brisanje'))
        if 0 <= index < len(artikli):
            naziv = artikli[index]['naziv']
            artikli.pop(index)
            sacuvaj_artikle(artikli)
            loguj(f"Obrisan artikal: {naziv}")
        return redirect(url_for('dodaj'))

    # Dodavanje
    if request.method == 'POST':
        naziv = request.form.get('naziv', '')
        cena = float(request.form.get('cena', '0'))
        zaduzeno = int(request.form.get('zaduzeno', '0'))
        plus18 = 'plus18' in request.form
        slika_file = request.files.get('slika')
        slika_naziv = ''
        if slika_file and slika_file.filename:
            slika_naziv = f"slot{len(artikli)}.{slika_file.filename.split('.')[-1].lower()}"
            slika_file.save(os.path.join(SLIKE_FOLDER, slika_naziv))

        novi = {
            "naziv": naziv,
            "cena": cena,
            "zaduzeno": zaduzeno,
            "prodato": 0,
            "slika": slika_naziv,
            "aktivan": True,
            "plus18": plus18
        }
        artikli.append(novi)
        sacuvaj_artikle(artikli)
        loguj(f"Dodat novi artikal: {naziv}")
        return redirect(url_for('admin'))

    return render_template("dodaj.html", artikli=artikli, vreme=datetime.now())

# Bavi se zahtevima za kupovinu
@app.route('/kupi/<int:slot>', methods=['POST'])
def kupi(slot):
    artikli = ucitaj_artikle()
    if 0 <= slot < len(artikli) and artikli[slot].get('aktivan', True):
        if artikli[slot].get('plus18', False) and not session.get('verifikovan'):
            flash("Potrebna je verifikacija punoletstva.")
            return redirect(url_for('index'))
        if artikli[slot]['zaduzeno'] - artikli[slot]['prodato'] > 0:
            artikli[slot]['prodato'] += 1
            sacuvaj_artikle(artikli)
            loguj(f"Kupljen artikal: {artikli[slot]['naziv']}")
    return redirect(url_for('index'))

@app.route("/verifikuj", methods=['POST'])
def verifikuj():
    session['verifikovan'] = True
    flash("Verifikacija uspešna. Možete nastaviti kupovinu.")
    return redirect(url_for('index'))

@app.route("/izvestaj")
def izvestaj():
    artikli = ucitaj_artikle()
    ukupno_prihod = sum(a['prodato'] * a['cena'] for a in artikli)
    return render_template("izvestaj.html", artikli=artikli, ukupno_prihod=ukupno_prihod)

@app.route("/log")
def prikaz_log():
    if os.path.exists(LOG_FAJL):
        with open(LOG_FAJL, 'r', encoding='utf-8') as f:
            sadrzaj = f.read()
    else:
        sadrzaj = "Log fajl je prazan."
    return render_template("log.html", sadrzaj=sadrzaj)

@app.route("/export_excel")
def export_excel():
    import pandas as pd
    artikli = ucitaj_artikle()
    df = pd.DataFrame(artikli)
    file_path = "export.xlsx"
    df.to_excel(file_path, index=False)
    loguj("Izvezen Excel fajl.")
    return send_file(file_path, as_attachment=True)

# Novi deo za servis panel i testiranja

@app.route("/servis5")
def servis():
    artikli = ucitaj_artikle()
    return render_template("servis5.html", artikli=artikli)

@app.route("/testiraj/<int:slot>", methods=["POST"])
def testiraj_motor(slot):
    artikli = ucitaj_artikle()
    if 0 <= slot < len(artikli):
        naziv = artikli[slot]['naziv']
        loguj(f"[SERVIS] Testiran motor za slot {slot} – {naziv}")
    return redirect(url_for('servis'))

@app.route("/dodaj_prodaju/<int:slot>", methods=["POST"])
def dodaj_prodaju(slot):
    artikli = ucitaj_artikle()
    if 0 <= slot < len(artikli):
        artikli[slot]['prodato'] += 1
        sacuvaj_artikle(artikli)
        loguj(f"[SERVIS] Ručno dodata prodaja za slot {slot} – {artikli[slot]['naziv']}")
    return redirect(url_for('servis'))

@app.route("/sacuvaj_edit", methods=["POST"])
def sacuvaj_edit():
    try:
        podaci = request.get_json()
        with open("config_editor.json", "w", encoding="utf-8") as f:
            json.dump(podaci, f, indent=4, ensure_ascii=False)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

import webbrowser
import threading

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False)