from conexion import get_connection
from datetime import datetime

class Pedido:

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

    def crear_pedido(self, cliente_clave, producto_clave):
        try:
            self.cursor.execute("SELECT nombre FROM clientes WHERE clave = %s", (cliente_clave,))
            cliente = self.cursor.fetchone()
            if not cliente:
                print(f"Cliente '{cliente_clave}' no encontrado.")
                return

            self.cursor.execute("SELECT nombre, precio FROM menu WHERE clave = %s AND eliminado = 0", (producto_clave,))
            producto = self.cursor.fetchone()
            if not producto:
                print(f"Producto '{producto_clave}' no encontrado o ha sido eliminado.")
                return

            nombre_cliente = cliente[0]
            nombre_producto, precio = producto

            self.cursor.execute(
                "INSERT INTO pedidos (cliente, producto, precio) VALUES (%s, %s, %s)",
                (cliente_clave, producto_clave, precio)
            )
            self.conn.commit()
            pedido_id = self.cursor.lastrowid

            self.generar_ticket(pedido_id, nombre_cliente, nombre_producto, precio)
            print(f"Pedido #{pedido_id} guardado correctamente.")

        except Exception as e:
            print(f"Error al crear el pedido: {e}")

    def generar_ticket(self, pedido_id, cliente, producto, precio):
        try:
            iva = precio * 0.16
            total = precio + iva
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            ticket = f"""
-------------------------------
Happy Burger - Ticket de Pedido
Pedido No.: {pedido_id}
Fecha: {fecha}
Cliente: {cliente}
Producto: {producto}
Precio: ${precio:.2f}
IVA: ${iva:.2f}
Total: ${total:.2f}
-------------------------------
"""
            with open(f"ticket_{pedido_id}.txt", "w", encoding="utf-8") as f:
                f.write(ticket)
            print(f"Ticket generado: ticket_{pedido_id}.txt")
        except Exception as e:
            print(f"Error al generar el ticket: {e}")

    def cancelar_pedido(self, pedido_id):
        try:
            self.cursor.execute("DELETE FROM pedidos WHERE pedido = %s", (pedido_id,))
            self.conn.commit()
            print(f"Pedido #{pedido_id} cancelado.")
        except Exception as e:
            print(f"Error al cancelar el pedido: {e}")

    def cerrar_conexion(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            pass
