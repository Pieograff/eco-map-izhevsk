from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Разрешенные форматы фото
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Создаем папки если нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS markers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  lat REAL NOT NULL,
                  lon REAL NOT NULL,
                  title TEXT,
                  description TEXT,
                  category TEXT,
                  photo_filename TEXT,
                  user_id TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'active')''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/add')
def add_marker_page():
    lat = request.args.get('lat', 56.8528)
    lon = request.args.get('lon', 53.2045)
    user_id = request.args.get('user_id', 'anonymous')
    return render_template('add_marker.html', lat=lat, lon=lon, user_id=user_id)

@app.route('/api/markers', methods=['GET'])
def get_markers():
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM markers WHERE status='active'")
    markers = c.fetchall()
    conn.close()
    
    result = []
    for marker in markers:
        result.append({
            'id': marker[0],
            'lat': marker[1],
            'lon': marker[2],
            'title': marker[3],
            'description': marker[4],
            'category': marker[5],
            'photo_url': f"/static/uploads/{marker[6]}" if marker[6] else None,
            'user_id': marker[7],
            'created_at': marker[8]
        })
    return jsonify(result)

@app.route('/api/markers', methods=['POST'])
def add_marker():
    try:
        data = request.form
        lat = data.get('lat')
        lon = data.get('lon')
        title = data.get('title', 'Нарушение')
        description = data.get('description', '')
        category = data.get('category', 'мусор')
        user_id = data.get('user_id', 'anonymous')
        
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                photo_filename = unique_filename
        
        conn = sqlite3.connect('markers.db')
        c = conn.cursor()
        c.execute('''INSERT INTO markers 
                     (lat, lon, title, description, category, photo_filename, user_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (lat, lon, title, description, category, photo_filename, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Метка добавлена!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/markers/<int:marker_id>', methods=['DELETE'])
def delete_marker(marker_id):
    try:
        password = request.args.get('password', '')
        
        # Простой пароль для демо
        if password != 'eco2024':
            return jsonify({'success': False, 'error': 'Неверный пароль'}), 403
        
        conn = sqlite3.connect('markers.db')
        c = conn.cursor()
        c.execute("UPDATE markers SET status='deleted' WHERE id=?", (marker_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Метка удалена'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)