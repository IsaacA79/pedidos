from clientes import Cliente
from menu import Menu
from pedidos import Pedido

def mostrar_menu():
    print("\n--- Bienvenido a Happy Burger ---")
    print("Selecciona una opción:")
    print("1. Crear Pedido")
    print("2. Gestión de Clientes")
    print("3. Gestión del Menú")
    print("0. Salir")

def menu_clientes(cliente_obj):
    try:
        print("\n-- Gestión de Clientes --")
        print("1. Agregar cliente")
        print("2. Eliminar cliente")
        print("3. Actualizar cliente")
        opcion = input("Elige una opción: ")

        if opcion == '1':
            print(" Registro de cliente")
            clave = input("Clave del cliente: ")
            nombre = input("Nombre: ")
            direccion = input("Dirección: ")
            correo = input("Correo electrónico: ")
            telefono = input("Teléfono: ")
            cliente_obj.agregar_cliente(clave, nombre, direccion, correo, telefono)
            print("Cliente agregado correctamente.")

        elif opcion == '2':
            clave = input("Clave del cliente a eliminar: ")
            cliente_obj.eliminar_cliente(clave)
            print("Cliente eliminado.")

        elif opcion == '3':
            clave = input("Clave del cliente a actualizar: ")
            nombre = input("Nuevo nombre (Enter para omitir): ")
            direccion = input("Nueva dirección (Enter para omitir): ")
            correo = input("Nuevo correo (Enter para omitir): ")
            telefono = input("Nuevo teléfono (Enter para omitir): ")
            cliente_obj.actualizar_cliente(clave, nombre or None, direccion or None, correo or None, telefono or None)
            print("Cliente actualizado.")
        else:
            print("Opción no válida.")

    except Exception as e:
        print(f"Error en la gestión de clientes: {e}")

def menu_menu(menu_obj):
    try:
        print("\n-- Gestión del Menú --")
        print("1. Agregar producto")
        print("2. Eliminar producto")
        print("3. Actualizar producto")
        opcion = input("Elige una opción: ")

        if opcion == '1':
            clave = input("Clave del producto: ")
            nombre = input("Nombre del producto: ")
            precio = float(input("Precio: "))
            menu_obj.agregar_producto(clave, nombre, precio)
            print("Producto agregado.")

        elif opcion == '2':
            clave = input("Clave del producto a eliminar: ")
            menu_obj.eliminar_producto(clave)
            print("Producto eliminado.")

        elif opcion == '3':
            clave = input("Clave del producto a actualizar: ")
            nombre = input("Nuevo nombre (Enter para omitir): ")
            precio = input("Nuevo precio (Enter para omitir): ")
            precio = float(precio) if precio else None
            menu_obj.actualizar_producto(clave, nombre or None, precio)
            print("Producto actualizado.")
        else:
            print("Opción no válida.")

    except Exception as e:
        print(f"Error en la gestión del menú: {e}")

def crear_pedido(pedido_obj):
    try:
        print("\n-- Crear Pedido --")
        cliente = input("Clave del cliente: ")
        producto = input("Clave del producto: ")
        pedido_obj.crear_pedido(cliente, producto)
        print("Pedido creado correctamente.")
    except Exception as e:
        print(f"Error al crear el pedido: {e}")

def ejecutar_sistema():
    try:
        cliente_obj = Cliente()
        menu_obj = Menu()
        pedido_obj = Pedido()

        while True:
            mostrar_menu()
            opcion = input("Selecciona una opción (0-3): ")

            if opcion == '1':
                crear_pedido(pedido_obj)
            elif opcion == '2':
                menu_clientes(cliente_obj)
            elif opcion == '3':
                menu_menu(menu_obj)
            elif opcion == '0':
                print("Gracias por usar Happy Burger. ¡Hasta pronto!")
                break
            else:
                print("Opción no válida. Intenta de nuevo.")

    except Exception as e:
        print(f"Error general del sistema: {e}")
    finally:
        # Cierre de conexiones
        try:
            if cliente_obj: cliente_obj.cerrar_conexion()
            if menu_obj: menu_obj.cerrar_conexion()
            if pedido_obj: pedido_obj.cerrar_conexion()
        except:
            pass

if __name__ == "__main__":
    ejecutar_sistema()
