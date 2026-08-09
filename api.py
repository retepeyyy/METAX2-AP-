from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "metax2.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ekibim (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                rol TEXT NOT NULL,
                discord TEXT,
                yetenek TEXT,
                katilim_tarihi TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("INSERT OR IGNORE INTO ekibim (id, ad, soyad, rol, discord, yetenek) VALUES (1, 'Ahmet', 'Yılmaz', 'Developer', 'ahmet#1234', 'Python, Lua')")
        conn.execute("INSERT OR IGNORE INTO ekibim (id, ad, soyad, rol, discord, yetenek) VALUES (2, 'Ayşe', 'Kaya', 'Designer', 'ayse#5678', 'UI/UX, Photoshop')")
        conn.execute("INSERT OR IGNORE INTO ekibim (id, ad, soyad, rol, discord, yetenek) VALUES (3, 'Mehmet', 'Demir', 'Admin', 'mehmet#9012', 'Yönetim')")

MENU_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>METAX2 - Ekip Yönetimi</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #00ff00; font-family: 'Courier New', monospace; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; padding: 20px; border-bottom: 2px solid #00ff00; margin-bottom: 20px; }
        .panel { background: #1a1a1a; border: 1px solid #00ff00; border-radius: 5px; padding: 20px; margin: 15px 0; }
        .panel h2 { border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px; }
        input, select { background: #0a0a0a; color: #00ff00; border: 1px solid #00ff00; padding: 10px; margin: 5px 0; width: 100%; font-family: 'Courier New'; }
        button { background: #006600; color: #00ff00; border: 1px solid #00ff00; padding: 10px 20px; cursor: pointer; font-family: 'Courier New'; font-weight: bold; }
        button:hover { background: #009900; color: #000; }
        .btn-edit { background: #006688; }
        .btn-edit:hover { background: #0088aa; }
        .btn-danger { background: #660000; }
        .btn-danger:hover { background: #990000; color: #fff; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; }
        th { background: #003300; }
        tr:hover { background: #1a1a1a; }
        .message { padding: 10px; margin: 10px 0; border-radius: 3px; }
        .success { background: #003300; border: 1px solid #00ff00; }
        .error { background: #330000; border: 1px solid #ff0000; color: #ff0000; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .stat { background: #0a0a0a; border: 1px solid #333; padding: 15px; text-align: center; }
        .stat span { font-size: 2em; font-weight: bold; display: block; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); }
        .modal-content { background: #1a1a1a; border: 2px solid #00ff00; border-radius: 10px; padding: 30px; width: 400px; margin: 100px auto; }
        .modal-content h2 { margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>METAX2 - Ekip Yonetimi</h1>
        
        <div class="stats">
            <div class="stat">Toplam Ekip<span>{{ stats['total'] }}</span></div>
            <div class="stat">Developer<span>{{ stats['developer'] }}</span></div>
            <div class="stat">Son Eklenen<span>{{ stats['last'] }}</span></div>
        </div>
        
        {% if message %}<div class="message {{ message_type }}">{{ message }}</div>{% endif %}
        
        <div class="panel">
            <h2>Ekip Uyesi Ekle</h2>
            <form method="POST" action="/api/menu/ekle">
                <input type="text" name="ad" placeholder="Ad" required>
                <input type="text" name="soyad" placeholder="Soyad" required>
                <select name="rol" required>
                    <option value="">Rol Seç</option>
                    <option value="Developer">Developer</option>
                    <option value="Designer">Designer</option>
                    <option value="Admin">Admin</option>
                    <option value="Moderator">Moderator</option>
                    <option value="Tester">Tester</option>
                    <option value="Scripter">Scripter</option>
                </select>
                <input type="text" name="discord" placeholder="Discord">
                <input type="text" name="yetenek" placeholder="Yetenekler">
                <button type="submit">EKLE</button>
            </form>
        </div>
        
        <div class="panel">
            <h2>Ekip Listesi</h2>
            <table>
                <tr><th>ID</th><th>Ad Soyad</th><th>Rol</th><th>Discord</th><th>Yetenekler</th><th>Tarih</th><th>İşlemler</th></tr>
                {% for uye in ekip %}
                <tr>
                    <td>{{ uye['id'] }}</td>
                    <td>{{ uye['ad'] }} {{ uye['soyad'] }}</td>
                    <td>{{ uye['rol'] }}</td>
                    <td>{{ uye['discord'] or '-' }}</td>
                    <td>{{ uye['yetenek'] or '-' }}</td>
                    <td>{{ uye['katilim_tarihi'][:10] }}</td>
                    <td>
                        <a href="/api/menu/duzenle/{{ uye['id'] }}"><button class="btn-edit" style="padding:5px 10px;">DÜZENLE</button></a>
                        <a href="/api/menu/sil/{{ uye['id'] }}" onclick="return confirm('Emin misin?')"><button class="btn-danger" style="padding:5px 10px;">SİL</button></a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

DUZENLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>METAX2 - Profil Düzenle</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #00ff00; font-family: 'Courier New', monospace; padding: 20px; }
        .container { max-width: 500px; margin: 100px auto; }
        .panel { background: #1a1a1a; border: 1px solid #00ff00; border-radius: 10px; padding: 30px; }
        h1 { text-align: center; margin-bottom: 20px; }
        input, select { background: #0a0a0a; color: #00ff00; border: 1px solid #00ff00; padding: 10px; margin: 5px 0; width: 100%; font-family: 'Courier New'; }
        button { background: #006600; color: #00ff00; border: 1px solid #00ff00; padding: 10px 20px; cursor: pointer; font-family: 'Courier New'; font-weight: bold; width: 100%; margin-top: 10px; }
        button:hover { background: #009900; color: #000; }
        .btn-back { background: #333; margin-top: 5px; }
        .btn-back:hover { background: #555; }
    </style>
</head>
<body>
    <div class="container">
        <div class="panel">
            <h1>Profil Duzenle</h1>
            <form method="POST" action="/api/menu/guncelle/{{ uye['id'] }}">
                <input type="text" name="ad" value="{{ uye['ad'] }}" required>
                <input type="text" name="soyad" value="{{ uye['soyad'] }}" required>
                <select name="rol" required>
                    <option value="Developer" {% if uye['rol'] == 'Developer' %}selected{% endif %}>Developer</option>
                    <option value="Designer" {% if uye['rol'] == 'Designer' %}selected{% endif %}>Designer</option>
                    <option value="Admin" {% if uye['rol'] == 'Admin' %}selected{% endif %}>Admin</option>
                    <option value="Moderator" {% if uye['rol'] == 'Moderator' %}selected{% endif %}>Moderator</option>
                    <option value="Tester" {% if uye['rol'] == 'Tester' %}selected{% endif %}>Tester</option>
                    <option value="Scripter" {% if uye['rol'] == 'Scripter' %}selected{% endif %}>Scripter</option>
                </select>
                <input type="text" name="discord" value="{{ uye['discord'] or '' }}" placeholder="Discord">
                <input type="text" name="yetenek" value="{{ uye['yetenek'] or '' }}" placeholder="Yetenekler">
                <button type="submit">KAYDET</button>
            </form>
            <a href="/api/menu"><button class="btn-back">GERİ DÖN</button></a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return jsonify({"api": "METAX2 API", "menu": "/api/menu"})

@app.route('/api/menu')
def menu():
    with get_db() as conn:
        ekip = conn.execute("SELECT * FROM ekibim ORDER BY id DESC").fetchall()
        total = len(ekip)
        developer_count = conn.execute("SELECT COUNT(*) as c FROM ekibim WHERE rol='Developer'").fetchone()['c']
        last = ekip[0]['ad'] if ekip else '-'
    stats = {'total': total, 'developer': developer_count, 'last': last}
    return render_template_string(MENU_HTML, ekip=ekip, stats=stats, message=None, message_type=None)

@app.route('/api/menu/ekle', methods=['POST'])
def menu_ekle():
    ad = request.form.get('ad')
    soyad = request.form.get('soyad')
    rol = request.form.get('rol')
    discord = request.form.get('discord', '')
    yetenek = request.form.get('yetenek', '')
    
    with get_db() as conn:
        conn.execute("INSERT INTO ekibim (ad, soyad, rol, discord, yetenek) VALUES (?, ?, ?, ?, ?)",
                    [ad, soyad, rol, discord, yetenek])
        ekip = conn.execute("SELECT * FROM ekibim ORDER BY id DESC").fetchall()
        total = len(ekip)
        developer_count = conn.execute("SELECT COUNT(*) as c FROM ekibim WHERE rol='Developer'").fetchone()['c']
        last = ekip[0]['ad'] if ekip else '-'
    stats = {'total': total, 'developer': developer_count, 'last': last}
    return render_template_string(MENU_HTML, ekip=ekip, stats=stats,
                                 message=f"'{ad} {soyad}' eklendi!", message_type="success")

@app.route('/api/menu/sil/<int:id>')
def menu_sil(id):
    with get_db() as conn:
        uye = conn.execute("SELECT * FROM ekibim WHERE id = ?", [id]).fetchone()
        if uye:
            conn.execute("DELETE FROM ekibim WHERE id = ?", [id])
            msg = f"'{uye['ad']} {uye['soyad']}' silindi!"
            msg_type = "success"
        else:
            msg = "Üye bulunamadı!"
            msg_type = "error"
        ekip = conn.execute("SELECT * FROM ekibim ORDER BY id DESC").fetchall()
        total = len(ekip)
        developer_count = conn.execute("SELECT COUNT(*) as c FROM ekibim WHERE rol='Developer'").fetchone()['c']
        last = ekip[0]['ad'] if ekip else '-'
    stats = {'total': total, 'developer': developer_count, 'last': last}
    return render_template_string(MENU_HTML, ekip=ekip, stats=stats, message=msg, message_type=msg_type)

@app.route('/api/menu/duzenle/<int:id>')
def menu_duzenle(id):
    with get_db() as conn:
        uye = conn.execute("SELECT * FROM ekibim WHERE id = ?", [id]).fetchone()
        if not uye:
            return "Kullanıcı bulunamadı", 404
    return render_template_string(DUZENLE_HTML, uye=uye)

@app.route('/api/menu/guncelle/<int:id>', methods=['POST'])
def menu_guncelle(id):
    ad = request.form.get('ad')
    soyad = request.form.get('soyad')
    rol = request.form.get('rol')
    discord = request.form.get('discord', '')
    yetenek = request.form.get('yetenek', '')
    
    with get_db() as conn:
        conn.execute("UPDATE ekibim SET ad=?, soyad=?, rol=?, discord=?, yetenek=? WHERE id=?",
                    [ad, soyad, rol, discord, yetenek, id])
        ekip = conn.execute("SELECT * FROM ekibim ORDER BY id DESC").fetchall()
        total = len(ekip)
        developer_count = conn.execute("SELECT COUNT(*) as c FROM ekibim WHERE rol='Developer'").fetchone()['c']
        last = ekip[0]['ad'] if ekip else '-'
    stats = {'total': total, 'developer': developer_count, 'last': last}
    return render_template_string(MENU_HTML, ekip=ekip, stats=stats,
                                 message=f"'{ad} {soyad}' güncellendi!", message_type="success")

# API
@app.route('/api/users')
def api_users():
    with get_db() as conn:
        return jsonify([dict(u) for u in conn.execute("SELECT * FROM ekibim ORDER BY id DESC").fetchall()])

@app.route('/api/user/<int:id>')
def api_user(id):
    with get_db() as conn:
        u = conn.execute("SELECT * FROM ekibim WHERE id = ?", [id]).fetchone()
        return jsonify(dict(u)) if u else (jsonify({"error": "Bulunamadı"}), 404)

@app.route('/api/user', methods=['POST'])
def api_user_ekle():
    d = request.json
    with get_db() as conn:
        c = conn.execute("INSERT INTO ekibim (ad, soyad, rol, discord, yetenek) VALUES (?,?,?,?,?)",
                        [d['ad'], d['soyad'], d['rol'], d.get('discord',''), d.get('yetenek','')])
        return jsonify(dict(conn.execute("SELECT * FROM ekibim WHERE id = ?", [c.lastrowid]).fetchone())), 201

@app.route('/api/user/<int:id>', methods=['PUT'])
def api_user_guncelle(id):
    d = request.json
    with get_db() as conn:
        u = conn.execute("SELECT * FROM ekibim WHERE id = ?", [id]).fetchone()
        if not u: return jsonify({"error": "Bulunamadı"}), 404
        conn.execute("UPDATE ekibim SET ad=?, soyad=?, rol=?, discord=?, yetenek=? WHERE id=?",
                    [d.get('ad',u['ad']), d.get('soyad',u['soyad']), d.get('rol',u['rol']),
                     d.get('discord',u['discord']), d.get('yetenek',u['yetenek']), id])
        return jsonify(dict(conn.execute("SELECT * FROM ekibim WHERE id = ?", [id]).fetchone()))

@app.route('/api/user/<int:id>', methods=['DELETE'])
def api_user_sil(id):
    with get_db() as conn:
        u = conn.execute("SELECT * FROM ekibim WHERE id = ?", [id]).fetchone()
        if not u: return jsonify({"error": "Bulunamadı"}), 404
        conn.execute("DELETE FROM ekibim WHERE id = ?", [id])
        return jsonify({"message": f"'{u['ad']} {u['soyad']}' silindi"})

if __name__ == '__main__':
    init_db()
    print("METAX2 API + Menu Başlatıldı!")
    print("Menu: http://localhost:5000/api/menu")
    app.run(debug=True, port=5000, host='0.0.0.0')