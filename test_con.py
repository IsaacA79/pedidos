from conexion import get_connection

def probar_conexion():
    try:
        conn = get_connection()
        if conn.is_connected():
            print("Conexión exitosa a la base de datos MySQL.")
            db_info = conn.get_server_info()
            print(f"Versión del servidor: {db_info}")
        else:
            print("No se pudo conectar a la base de datos.")
        conn.close()
    except Exception as e:
        print(f"Error al conecta con la base de datos: {e}")

if __name__ == "__main__":
    probar_conexion()
