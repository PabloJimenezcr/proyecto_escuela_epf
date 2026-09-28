from db import get_db_connection
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets

def buscar_usuario_por_correo(correo):
    """Busca un usuario activo en la base de datos por su correo y retorna sus datos junto con su rol."""
    db = get_db_connection()
    if not db:
        return None
        
    try:
        cursor = db.cursor(dictionary=True)
        # Consulta SQL uniendo la tabla usuarios con roles
        sql = """
            SELECT u.*, r.nombre AS nombre_rol 
            FROM usuarios u 
            JOIN roles r ON u.id_rol = r.id_rol 
            WHERE u.correo = %s AND u.estado = 'activo'
        """
        cursor.execute(sql, (correo,))
        usuario = cursor.fetchone()
        return usuario
    except Exception as e:
        print(f"Error crítico al consultar el usuario en la BD: {e}")
        return None
    finally:
        cursor.close()
        db.close()

# register

def crear_nuevo_usuario(nombre, apellido1, apellido2, correo, contrasena_plana, telefono, id_rol):
    """Encripta la contraseña de forma nativa en la PC e inserta el usuario en MySQL."""
    db = get_db_connection()
    if not db:
        return False
        
    try:
        cursor = db.cursor()
        # Encriptamos la clave usando el motor nativo de la computadora actual
        contrasena_hash = generate_password_hash(contrasena_plana)
        
        sql = """
            INSERT INTO usuarios (nombre, apellido1, apellido2, correo, contrasena_hash, telefono, id_rol, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo')
        """
        valores = (nombre, apellido1, apellido2, correo, contrasena_hash, telefono, id_rol)
        cursor.execute(sql, valores)
        db.commit()
        return True
    except Exception as e:
        print(f"Error crítico al registrar usuario en la BD: {e}")
        return False
    finally:
        cursor.close()
        db.close()


#Recuperar contraseña

def registrar_token_real(correo):
    """Verifica si el correo existe, genera un token y lo guarda en la base de datos."""
    db = get_db_connection()
    if not db:
        return None
        
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s AND estado = 'activo'", (correo,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return None
            
        # Generamos el token y expira en 1 hora
        token = secrets.token_hex(16)
        fecha_expira = datetime.now() + timedelta(hours=1)
        
        sql = """
            INSERT INTO recuperacion_contrasena (id_usuario, token, fecha_expira, utilizado)
            VALUES (%s, %s, %s, 0)
        """
        cursor.execute(sql, (usuario['id_usuario'], token, fecha_expira))
        db.commit()
        return token
    except Exception as e:
        print(f"Error al registrar token en la BD: {e}")
        return None
    finally:
        cursor.close()
        db.close()

def actualizar_contrasena_real(token, nueva_clave_plana):
    """Valida el token y actualiza la clave del usuario con hash nativo."""
    db = get_db_connection()
    if not db:
        return False
        
    try:
        cursor = db.cursor(dictionary=True)
        # Validamos que el token exista en la tabla
        cursor.execute("SELECT * FROM recuperacion_contrasena WHERE token = %s AND utilizado = 0", (token,))
        registro = cursor.fetchone()
        
        if not registro:
            return False
            
        # Encriptamos la clave 
        nuevo_hash = generate_password_hash(nueva_clave_plana)
        
        #Modificamos la contraseña en la tabla "usuarios"
        cursor.execute("UPDATE usuarios SET contrasena_hash = %s WHERE id_usuario = %s", (nuevo_hash, registro['id_usuario']))
        #Se quema el tokem 
        cursor.execute("UPDATE recuperacion_contrasena SET utilizado = 1 WHERE id_recuperacion = %s", (registro['id_recuperacion'],))
        
        db.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar la contraseña en la BD: {e}")
        return False
    finally:
        cursor.close()
        db.close()