from flask import Flask, render_template, request, redirect
from clientes import Cliente
from menu import Menu
from pedidos import Pedido
from conexion import get_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# CLIENTES
@app.route("/cliente", methods=["GET", "POST"])
def agregar_cliente():
    if request.method == "POST":
        clave = request.form["clave"]
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]

        cliente = Cliente()
        cliente.agregar_cliente(clave, nombre, direccion, correo, telefono)
        cliente.cerrar_conexion()
        return redirect("/")
    return render_template("agregar_cliente.html")

# PRODUCTOS
@app.route("/producto", methods=["GET", "POST"])
def agregar_producto():
    if request.method == "POST":
        clave = request.form["clave"]
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])

        menu = Menu()
        menu.agregar_producto(clave, nombre, precio)
        menu.cerrar_conexion()
        return redirect("/")
    return render_template("agregar_producto.html")

@app.route('/lista')
def lista_productos():
    menu = Menu()
    productos = menu.obtener_productos()
    menu.cerrar_conexion()
    return render_template('listar_producto.html', productos=productos)

@app.route('/editar/<clave>', methods=['GET', 'POST'])
def editar_producto(clave):
    menu = Menu()
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        menu.actualizar_producto(clave, nombre, precio)
        menu.cerrar_conexion()
        return redirect('/lista')
    
    menu.cursor.execute("SELECT * FROM menu WHERE clave = %s", (clave,))
    producto = menu.cursor.fetchone()
    menu.cerrar_conexion()
    return render_template('editar_producto.html', producto=producto)

@app.route('/eliminar/<clave>', methods=['POST'])
def eliminar_producto(clave):
    menu = Menu()
    menu.eliminar_producto(clave)
    menu.cerrar_conexion()
    return redirect('/')

# PEDIDOS
@app.route("/pedido", methods=["GET", "POST"])
def crear_pedido():
    if request.method == "POST":
        cliente_id = request.form["cliente"]
        producto_id = request.form["producto"]

        pedido = Pedido()
        pedido.crear_pedido(cliente_id, producto_id)
        pedido.cerrar_conexion()
        return redirect("/")
    return render_template("crear_pedido.html")

@app.route("/buscar-pedido", methods=["GET", "POST"])
def buscar_pedido():
    pedido_info = None
    if request.method == "POST":
        pedido_id = request.form.get("pedido_id")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.pedido, c.nombre AS cliente, m.nombre AS producto, p.precio
            FROM pedidos p
            JOIN clientes c ON p.cliente = c.clave
            JOIN menu m ON p.producto = m.clave
            WHERE p.pedido = %s
        """, (pedido_id,))
        pedido_info = cursor.fetchone()

        cursor.close()
        conn.close()

    return render_template("buscar_pedido.html", pedido=pedido_info)

if __name__ == "__main__":
    app.run(debug=True)
