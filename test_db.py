from db import get_db_connection

conn = get_db_connection()
if conn and conn.is_connected():
    print("Conexión exitosa")
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    print("Base de datos actual:", cursor.fetchone()[0])
    cursor.close()
    conn.close()
else:
    print("No se pudo conectar")