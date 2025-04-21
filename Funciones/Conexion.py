import psycopg2
from urllib.parse import urlparse

# URL de conexión proporcionada
DATABASE_URL = "postgres://koyeb-adm:npg_eRNFcoYy4QH7@ep-silent-term-a2zpcjkl.eu-central-1.pg.koyeb.app/koyebdb"

# Función para obtener la conexión a PostgreSQL
def get_connection():
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],  # Nioy es el nombre de la base de datos
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    return conn

# Crear la base de datos y las tablas si no existen
def create_database_and_tables():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Crear las tablas si no existen
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    correo VARCHAR(255) UNIQUE NOT NULL,
                    contraseña VARCHAR(255) NOT NULL,
                    rango VARCHAR(20) DEFAULT 'User',
                    xp INT DEFAULT 0
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publicaciones (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(255) NOT NULL,
                    contenido TEXT NOT NULL,
                    user_id INT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios(id)
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY,
                    user_id INT,
                    mensaje TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios(id)
                );
            """)

            conn.commit()
            print("Base de datos y tablas creadas con éxito.")
    except Exception as e:
        print(f"Error al crear la base de datos y las tablas: {e}")
    finally:
        conn.close()

# Ejecutar el script
if __name__ == '__main__':
    create_database_and_tables()
