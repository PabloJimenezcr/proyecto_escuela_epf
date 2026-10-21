from db import get_db_connection
from werkzeug.security import generate_password_hash


def obtener_lista_docentes():
    """Docentes con sus datos y cantidad de asignaciones."""

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
                SELECT
                    d.id_docente,
                    d.especialidad,
                    d.fecha_ingreso,
                    u.nombre,
                    u.apellido1,
                    u.apellido2,
                    u.correo,
                    u.telefono,
                    u.estado,
                    COUNT(dmg.id_asignacion) AS total_asignaciones
                FROM docentes d
                INNER JOIN usuarios u ON u.id_usuario = d.id_usuario
                LEFT JOIN docente_materia_grupo dmg ON dmg.id_docente = d.id_docente
                GROUP BY
                    d.id_docente, d.especialidad, d.fecha_ingreso,
                    u.nombre, u.apellido1, u.apellido2,
                    u.correo, u.telefono, u.estado
                ORDER BY u.apellido1, u.apellido2, u.nombre
            """
        )

        return cursor.fetchall()

    except Exception as e:

        print(f"Error al obtener docentes: {e}")

        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


def actualizar_docente(id_docente, nombre, apellido1, apellido2, telefono, especialidad):
    """Actualiza datos personales y especialidad. Devuelve (exito, mensaje)."""

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        try:
            id_docente = int(id_docente)
        except (TypeError, ValueError):
            return False, "El docente seleccionado no es válido."

        nombre = (nombre or "").strip()
        apellido1 = (apellido1 or "").strip()
        apellido2 = (apellido2 or "").strip() or None
        telefono = (telefono or "").strip() or None
        especialidad = (especialidad or "").strip() or None

        if not nombre or not apellido1:
            return False, "El nombre y el primer apellido son obligatorios."

        if len(nombre) > 60 or len(apellido1) > 60 or (apellido2 and len(apellido2) > 60):
            return False, "Nombre y apellidos no pueden superar 60 caracteres."

        if telefono and (len(telefono) > 20 or not telefono.replace("+", "").replace("-", "").replace(" ", "").isdigit()):
            return False, "El teléfono no es válido."

        if especialidad and len(especialidad) > 80:
            return False, "La especialidad no puede superar 80 caracteres."

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_usuario FROM docentes WHERE id_docente = %s LIMIT 1",
            (id_docente,)
        )

        docente = cursor.fetchone()

        if not docente:
            return False, "El docente seleccionado no existe."

        cursor.execute(
            """
                UPDATE usuarios
                SET nombre = %s, apellido1 = %s, apellido2 = %s, telefono = %s
                WHERE id_usuario = %s
            """,
            (nombre, apellido1, apellido2, telefono, docente["id_usuario"])
        )

        cursor.execute(
            "UPDATE docentes SET especialidad = %s WHERE id_docente = %s",
            (especialidad, id_docente)
        )

        connection.commit()

        return True, "Información del docente actualizada correctamente."

    except Exception as e:

        connection.rollback()

        print(f"Error al actualizar docente: {e}")

        return False, "No fue posible actualizar al docente."

    finally:

        if cursor:
            cursor.close()

        connection.close()

def registrar_docente(nombre, apellido1, apellido2, correo, telefono,
                      contrasena, especialidad, id_materia=None, id_grupo=None):
    """
    Crea usuario (rol Docente) + fila en docentes, y opcionalmente
    asigna materia y grupo. Todo en una transacción.
    Devuelve (exito, mensaje).
    """

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        nombre = (nombre or "").strip()
        apellido1 = (apellido1 or "").strip()
        apellido2 = (apellido2 or "").strip() or None
        correo = (correo or "").strip().lower()
        telefono = (telefono or "").strip() or None
        especialidad = (especialidad or "").strip() or None
        contrasena = contrasena or ""

        if not nombre or not apellido1 or not correo or not contrasena:
            return False, "Nombre, primer apellido, correo y contraseña son obligatorios."

        if len(nombre) > 60 or len(apellido1) > 60 or (apellido2 and len(apellido2) > 60):
            return False, "Nombre y apellidos no pueden superar 60 caracteres."

        if "@" not in correo or len(correo) > 120:
            return False, "El correo no es válido."

        if len(contrasena) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."

        if telefono and (len(telefono) > 20 or not telefono.replace("+", "").replace("-", "").replace(" ", "").isdigit()):
            return False, "El teléfono no es válido."

        if especialidad and len(especialidad) > 80:
            return False, "La especialidad no puede superar 80 caracteres."

        # Materia y grupo van juntos o ninguno
        id_materia = int(id_materia) if str(id_materia or "").isdigit() else None
        id_grupo = int(id_grupo) if str(id_grupo or "").isdigit() else None

        if (id_materia is None) != (id_grupo is None):
            return False, "Para asignar, selecciona materia y grupo (o deja ambos vacíos)."

        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s LIMIT 1", (correo,))

        if cursor.fetchone():
            return False, "Ya existe un usuario con ese correo."

        cursor.execute("SELECT id_rol FROM roles WHERE nombre = 'Docente' LIMIT 1")
        rol = cursor.fetchone()

        if not rol:
            return False, "No existe el rol Docente en la base de datos."

        if id_materia is not None:
            cursor.execute("SELECT id_materia FROM materias WHERE id_materia = %s", (id_materia,))
            if not cursor.fetchone():
                return False, "La materia seleccionada no existe."

            cursor.execute("SELECT id_grupo FROM grupos WHERE id_grupo = %s", (id_grupo,))
            if not cursor.fetchone():
                return False, "El grupo seleccionado no existe."

        cursor.execute(
            """
                INSERT INTO usuarios
                    (nombre, apellido1, apellido2, correo, contrasena_hash,
                     telefono, id_rol, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo')
            """,
            (nombre, apellido1, apellido2, correo,
             generate_password_hash(contrasena), telefono, rol["id_rol"])
        )

        id_usuario = cursor.lastrowid

        cursor.execute(
            "INSERT INTO docentes (id_usuario, especialidad) VALUES (%s, %s)",
            (id_usuario, especialidad)
        )

        id_docente = cursor.lastrowid

        if id_materia is not None:
            cursor.execute(
                "SELECT id_asignacion FROM docente_materia_grupo "
                "WHERE id_grupo = %s AND id_materia = %s LIMIT 1",
                (id_grupo, id_materia)
            )
            if cursor.fetchone():
                connection.rollback()
                return False, "Esa materia ya tiene un docente en el grupo elegido."

            cursor.execute(
                "INSERT INTO docente_materia_grupo (id_docente, id_materia, id_grupo) "
                "VALUES (%s, %s, %s)",
                (id_docente, id_materia, id_grupo)
            )

        connection.commit()

        return True, "Docente registrado correctamente."

    except Exception as e:

        connection.rollback()

        print(f"Error al registrar docente: {e}")

        return False, "No fue posible registrar al docente."

    finally:

        if cursor:
            cursor.close()

        connection.close()