from flask_socketio import SocketIO
from functools import wraps
from flask import Flask, redirect, render_template, send_file, request, jsonify, session
import hashlib
import pymysql
from datetime import timedelta
import psycopg2
import psycopg2.extras  # Asegúrate de importar extras
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'nexthesia'
app.permanent_session_lifetime = timedelta(days=20)
socketio = SocketIO(app)
Titulo_Webs = 'Nexthesia'

# URL de conexión proporcionada
DATABASE_URL = "postgres://koyeb-adm:npg_eRNFcoYy4QH7@ep-silent-term-a2zpcjkl.eu-central-1.pg.koyeb.app/koyebdb"

def get_connection():
    result = urlparse(DATABASE_URL)
    
    # Crear la conexión a la base de datos PostgreSQL
    conn = psycopg2.connect(
        database=result.path[1:],  # Extrae el nombre de la base de datos (Nioy)
        user=result.username,       # Nombre de usuario
        password=result.password,   # Contraseña
        host=result.hostname,       # Host
        port=result.port            # Puerto
    )
    conn.cursor_factory = psycopg2.extras.DictCursor  # Usa el DictCursor para obtener resultados como diccionarios
    return conn

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorada

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        contraseña_hash = hashlib.sha256(contraseña.encode()).hexdigest()

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE correo=%s AND contraseña=%s", (correo, contraseña_hash))
            user = cursor.fetchone()
        conn.close()

        if user:
            session.permanent = True
            session['user_id'] = user[0]  # Asumiendo que el id está en la primera columna
            session['nombre'] = user[1]   # Asumiendo que el nombre está en la segunda columna
            session['rango'] = user[3]    # Asumiendo que el rango está en la cuarta columna
            return redirect('/home')
        else:
            return redirect('/login')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        contraseña_hash = hashlib.sha256(contraseña.encode()).hexdigest()

        conn = get_connection()
        with conn.cursor() as cursor:
            # Verificar si el correo ya existe
            cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
            existente = cursor.fetchone()
            if existente:
                return redirect('/login')

            # Insertar nuevo usuario
            cursor.execute("INSERT INTO usuarios (nombre, correo, contraseña, rango, xp) VALUES (%s, %s, %s, %s, %s)",
                           (nombre, correo, contraseña_hash, 'User', 0))
            conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/subir', methods=['GET', 'POST'])
@login_requerido
def subir_publicacion():
    if request.method == 'POST':
        texto = request.form['texto']  # Texto de la publicación
        
        # Obtiene el ID del usuario desde la sesión
        user_id = session.get('user_id')

        if not user_id:
            return redirect('/login')

        # Conexión a la base de datos para obtener el nombre del usuario y XP
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT nombre, xp FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        conn.close()

        if not user:
            return redirect('/login')  # Si no se encuentra el usuario, redirige al login

        # Usar índices para acceder a la información de la tupla
        nombre_usuario = user[0]  # Primer valor es el nombre
        xp_actual = user[1]       # Segundo valor es el xp

        # Inserta la nueva publicación
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(""" 
                INSERT INTO publicaciones (titulo, contenido, user_id)
                VALUES (%s, %s, %s)
            """, (nombre_usuario, texto, user_id))  # Usamos el nombre del usuario como título
            conn.commit()

        # Agregar 10 puntos a la experiencia del usuario
        xp_nueva = xp_actual + 10
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(""" 
                UPDATE usuarios SET xp = %s WHERE id = %s
            """, (xp_nueva, user_id))
            conn.commit()

        conn.close()

        return redirect('/chat')

    return render_template('chat.html')


@app.route('/chat')
@login_requerido
def publicaciones():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT p.*, u.nombre
            FROM publicaciones p
            JOIN usuarios u ON p.user_id = u.id
            ORDER BY p.fecha DESC
        """)
        publicaciones = cursor.fetchall()
    conn.close()
    return render_template('chat.html', publicaciones=publicaciones)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/perfil')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    usuario = {
        'id': session['user_id'],
        'nombre': session['nombre'],
        'rango': session['rango']
    }
    
    return render_template('perfil.html', usuario=usuario)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('nombre', None)
    session.pop('rango', None)
    return redirect('/login')

@app.route('/home')
@login_requerido
def index():
    return render_template('index.html', Titulo_Web=Titulo_Webs)

# Producción
if __name__ == '__main__':
    socketio.run(app)

# Desarrollo
#if __name__ == '__main__':
    #socketio.run(app, host='0.0.0.0', port=5000, debug=True)
