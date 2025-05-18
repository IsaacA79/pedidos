import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="MYSQL1002.site4now.net",
        user="ab9274_hburgue",
        password="Mysql.2025",
        database="db_ab9274_hburgue",
        )
        return conn
    except mysql.connector.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None