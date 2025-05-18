from conexion import get_connection

class Menu:
    def __init__(self):
        self.conn = get_connection()
        if self.conn:
            self.cursor = self.conn.cursor(buffered=True)
        else:
            raise Exception("No se pudo establecer la conexión con la base de datos.")
        
    def verificar_conexion(self):
    
        try:
            if not self.conn.is_connected():
                self.conn.reconnect(attempts=3, delay=2)
                self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as e:
            print(f"Error al reconectar: {e}")
            raise

    def agregar_producto(self, clave, nombre, precio):
        try:
            query = "INSERT INTO menu VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (clave, nombre, precio, 0))  # 0 = no eliminado
            self.conn.commit()
        except Exception as e:
            print(f"Error al agregar producto: {e}")

    def eliminar_producto(self, clave):
        try:
            self.cursor.execute("UPDATE menu SET eliminado = 1 WHERE clave = %s", (clave,))
            self.conn.commit()
        except Exception as e:
            print(f"Error al eliminar producto: {e}")

    def actualizar_producto(self, clave, nombre=None, precio=None):
        try:
            if nombre:
                self.cursor.execute("UPDATE menu SET nombre = %s WHERE clave = %s", (nombre, clave))
            if precio is not None:
                self.cursor.execute("UPDATE menu SET precio = %s WHERE clave = %s", (precio, clave))
            self.conn.commit()
        except Exception as e:
            print(f"Error al actualizar producto: {e}")

    def obtener_productos(self):
            self.verificar_conexion()
            self.cursor.execute("SELECT * FROM menu WHERE eliminado = 0")
            return self.cursor.fetchall()

    def cerrar_conexion(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            pass
