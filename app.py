from flask import Flask, render_template, request, redirect, url_for
from clientes import Cliente
from menu import Menu
from pedidos import Pedido
from conexion import get_connection
from datetime import datetime
import mysql.connector
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

#DESAYUNOS------------
@app.route("/desayunos", methods=["GET"])
def mostrar_desayunos():
    return render_template("desayunos.html")

@app.route("/pedido-desayuno", methods=["POST"])
def recibir_desayuno():
    seleccionados_raw = request.form.getlist("desayunos")
    cliente = request.form.get("cliente") or "Anónimo"

    seleccionados = []
    total = 0

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT IFNULL(MAX(id_pedido), 0) + 1 FROM pedidos_desayuno")
    id_pedido = cursor.fetchone()[0]

    for item in seleccionados_raw:
        platillo, precio = item.split("|")
        seleccionados.append((platillo, float(precio)))
        total += float(precio)

        cursor.execute("""
            INSERT INTO pedidos_desayuno (id_pedido, cliente_nombre, platillo, precio)
            VALUES (%s, %s, %s, %s)
        """, (id_pedido, cliente, platillo, precio))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template("resumen_desayuno.html",
                           seleccionados=seleccionados,
                           total=total,
                           cliente=cliente,
                           id_pedido=id_pedido)





@app.route("/pedido-desayuno-multiple", methods=["GET", "POST"])
def pedido_desayuno_multiple():
    if request.method == "GET":
        return render_template("formulario_desayunos.html")

    # Recibir el JSON oculto del formulario de confirmación
    datos_json = request.form.get("datos_json")
    if not datos_json:
        return "No se recibieron datos.", 400

    personas = json.loads(datos_json)

    conn = get_connection()
    cursor = conn.cursor()

    # Obtener nuevo ID de pedido general
    cursor.execute("SELECT IFNULL(MAX(id_pedido), 0) + 1 FROM pedidos_desayuno")
    id_pedido = cursor.fetchone()[0]

    for persona in personas:
        nombre = persona["nombre"]
        for platillo, precio in persona["platillos"]:
            cursor.execute("""
                INSERT INTO pedidos_desayuno (id_pedido, cliente_nombre, platillo, precio, fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_pedido, nombre, platillo, precio, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()

    # Calcular totales por persona para mostrar en resumen
    for p in personas:
        p["total"] = sum(p["precio"] for _, p["precio"] in p["platillos"])

    return render_template("resumen_multiple.html", id_pedido=id_pedido, personas=personas)



@app.route("/revisar-pedido", methods=["POST"])
def revisar_pedido():
    personas = []
    data = request.form.to_dict(flat=False)

    for key in data:
        if key.startswith("persona["):
            index = key.split("[")[1].split("]")[0]
            break
    total_general = 0

    i = 0
    while f"persona[{i}][cliente]" in data:
        nombre = data.get(f"persona[{i}][cliente]", [""])[0]
        desayunos_raw = data.get(f"persona[{i}][desayunos][]", [])
        platillos = []
        total = 0
        for item in desayunos_raw:
            platillo, precio = item.split("|")
            precio = float(precio)
            platillos.append((platillo, precio))
            total += precio
        personas.append({"nombre": nombre, "platillos": platillos, "total": total})
        total_general += total
        i += 1

    return render_template("resumen_pedido.html", personas=personas, total_general=total_general)





#--------------------
#historial desayunos------------------
@app.route("/historial-desayunos", methods=["GET", "POST"])
def historial_desayunos():
    cliente = request.form.get("cliente") if request.method == "POST" else ""
    fecha_inicio = request.form.get("fecha_inicio") if request.method == "POST" else ""
    fecha_fin = request.form.get("fecha_fin") if request.method == "POST" else ""

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id_pedido, cliente_nombre, platillo, precio, fecha
        FROM pedidos_desayuno
        WHERE 1 = 1
    """
    params = []

    if cliente:
        query += " AND cliente_nombre LIKE %s"
        params.append(f"%{cliente}%")
    if fecha_inicio:
        query += " AND fecha >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= %s"
        params.append(fecha_fin + " 23:59:59")

    query += " ORDER BY fecha DESC"

    cursor.execute(query, params)
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("historial_desayunos.html",
                           pedidos=pedidos,
                           cliente=cliente,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)

#--------------------------------


# CLIENTES
@app.route("/cliente", methods=["GET", "POST"])
def agregar_cliente():
    mensaje = None

    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]

        try:
            cliente = Cliente()
            cliente.cursor.execute("""
                INSERT INTO clientes (nombre, direccion, correo, telefono)
                VALUES (%s, %s, %s, %s)
            """, (nombre, direccion, correo, telefono))
            cliente.conn.commit()
            cliente.cerrar_conexion()
            return redirect("/")
        except mysql.connector.errors.IntegrityError as e:
            mensaje = "Ya existe un cliente con esos datos."
        except Exception as e:
            mensaje = f"Error al agregar cliente: {e}"

    return render_template("agregar_cliente.html", mensaje=mensaje)


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
def buscar_y_crear_pedido():
    pedido_info = None
    mensaje = None

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        # ------- Crear pedido -------
        if "cliente" in request.form and "producto" in request.form:
            cliente_id = request.form["cliente"]
            producto_id = request.form["producto"]

            nuevo_pedido = Pedido()
            nuevo_pedido.crear_pedido(cliente_id, producto_id)
            nuevo_pedido.cerrar_conexion()
            mensaje = "Pedido creado exitosamente."

        # ------- Buscar pedido por ID -------
        elif "pedido_id" in request.form:
            pedido_id = request.form.get("pedido_id")
            cursor.execute("""
                SELECT p.pedido, c.nombre AS cliente, m.nombre AS producto, p.precio
                FROM pedidos p
                JOIN clientes c ON p.cliente = c.clave
                JOIN menu m ON p.producto = m.clave
                WHERE p.pedido = %s
            """, (pedido_id,))
            pedido_info = cursor.fetchone()

    # ------- Consulta de todos los pedidos con paginación -------
    cursor.execute("""
        SELECT p.pedido, c.nombre AS cliente, m.nombre AS producto, p.precio
        FROM pedidos p
        JOIN clientes c ON p.cliente = c.clave
        JOIN menu m ON p.producto = m.clave
        ORDER BY p.pedido DESC
    """)
    pedidos = cursor.fetchall()

    # Paginación
    pagina_actual = int(request.args.get("pagina", 1))
    por_pagina = 5
    inicio = (pagina_actual - 1) * por_pagina
    fin = inicio + por_pagina
    pedidos_paginate = pedidos[inicio:fin]
    pedidos_total = len(pedidos)

    cursor.close()
    conn.close()

    return render_template("consultar_y_listar_pedidos.html",
                           pedido=pedido_info,
                           pedidos_paginate=pedidos_paginate,
                           pedidos_total=pedidos_total,
                           pagina_actual=pagina_actual,
                           mensaje=mensaje)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
