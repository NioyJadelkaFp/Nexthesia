import psycopg2
from urllib.parse import urlparse

# URL de conexión proporcionada
DATABASE_URL = "postgres://koyeb-adm:npg_eRNFcoYy4QH7@ep-silent-term-a2zpcjkl.eu-central-1.pg.koyeb.app/Nioy"

def get_connection():
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    return conn

def clear_all_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Desactivar restricciones de clave foránea temporalmente
            cursor.execute("SET session_replication_role = replica;")
            
            # Eliminar datos en orden (primero dependencias)
            cursor.execute("DELETE FROM mensajes;")
            cursor.execute("DELETE FROM publicaciones;")
            cursor.execute("DELETE FROM usuarios;")
            
            # Reactivar restricciones
            cursor.execute("SET session_replication_role = DEFAULT;")
            
            conn.commit()
            print("¡Todos los datos fueron eliminados con éxito!")
    except Exception as e:
        print(f"Error al eliminar datos: {e}")
    finally:
        conn.close()

# Ejecutar
if __name__ == '__main__':
    clear_all_data()
