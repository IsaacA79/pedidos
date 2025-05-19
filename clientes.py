from conexion import get_connection

class Cliente:
    def __init__(self):
        self.conn = get_connection()
        if self.conn:
            self.cursor = self.conn.cursor(buffered=True) 
        else:
            raise Exception("No se pudo establecer la conexión a la base de datos.")

    def agregar_cliente(self, clave, nombre, direccion, correo, telefono):
        self.cursor.execute("SELECT clave FROM clientes WHERE clave = %s", (clave,))
        if self.cursor.fetchone():
            print(f"Ya existe un cliente con la clave '{clave}'. No se insertó.")
            return
        query = "INSERT INTO clientes VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (clave, nombre, direccion, correo, telefono))
        self.conn.commit()

    def eliminar_cliente(self, clave):
        self.cursor.execute("DELETE FROM  clientes WHERE clave = %s", (clave,))
        self.conn.commit()

    def actualizar_cliente(self, clave, nombre=None, direccion=None, correo=None, telefono=None):
        if nombre:
            self.cursor.execute("UPDATE clientes SET nombre=%s WHERE clave=%s", (nombre, clave))
        if direccion:
            self.cursor.execute("UPDATE clientes SET direccion=%s WHERE clave=%s", (direccion, clave))
        if correo: 
            self.cursor.execute("UPDATE clientes SET correo=%s WHERE clave=%s", (correo, clave))
        if telefono: 
            self.cursor.execute("UPDATE clientes SET telefono=%s WHERE clave=%s", (telefono, clave))
        self.conn.commit()

    def cerrar_conexion(self):
        self.cursor.close()
        self.conn.close()
