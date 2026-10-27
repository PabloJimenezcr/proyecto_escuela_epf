from datetime import date, datetime
from werkzeug.security import generate_password_hash
from db import get_db_connection


def obtener_grupos_para_estudiantes():
    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id_grupo,
                nombre,
                nivel,
                seccion,
                anio_lectivo
            FROM grupos
            ORDER BY anio_lectivo DESC, nivel ASC, seccion ASC
            """
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"Error al consultar grupos para estudiantes: {e}")
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def obtener_estudiantes_registrados():
    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                e.id_estudiante,
                e.id_usuario,
                e.fecha_nacimiento,
                e.fecha_matricula,
                u.nombre,
                u.apellido1,
                u.apellido2,
                u.correo,
                u.telefono,
                u.estado,
                g.id_grupo,
                g.nombre AS nombre_grupo,
                g.nivel,
                g.seccion,
                g.anio_lectivo
            FROM estudiantes e
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            INNER JOIN grupos g
                ON g.id_grupo = e.id_grupo
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            WHERE r.nombre = 'Estudiante'
            ORDER BY e.id_estudiante DESC
            """
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"Error al consultar estudiantes registrados: {e}")
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def registrar_estudiante(
    nombre,
    apellido1,
    apellido2,
    correo,
    telefono,
    contrasena,
    fecha_nacimiento,
    id_grupo
):
    nombre = (nombre or "").strip()
    apellido1 = (apellido1 or "").strip()
    apellido2 = (apellido2 or "").strip()
    correo = (correo or "").strip().lower()
    telefono = (telefono or "").strip()
    contrasena = contrasena or ""
    fecha_nacimiento = (fecha_nacimiento or "").strip()
    id_grupo = (id_grupo or "").strip()

    if not nombre or not apellido1 or not correo or not contrasena:
        return False, "Completa los campos obligatorios."

    if not fecha_nacimiento or not id_grupo:
        return False, "Selecciona la fecha de nacimiento y el grupo."

    if len(nombre) > 60 or len(apellido1) > 60 or len(apellido2) > 60:
        return False, "Los nombres y apellidos no pueden superar los 60 caracteres."

    if len(correo) > 120:
        return False, "El correo no puede superar los 120 caracteres."

    if len(telefono) > 20:
        return False, "El teléfono no puede superar los 20 caracteres."

    if not correo.endswith("@escuela.com"):
        return False, "El correo debe pertenecer al dominio @escuela.com."

    if len(contrasena) < 8:
        return False, "La contraseña inicial debe tener al menos 8 caracteres."

    try:
        nacimiento = datetime.strptime(
            fecha_nacimiento,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return False, "La fecha de nacimiento no es válida."

    if nacimiento > date.today():
        return False, "La fecha de nacimiento no puede ser futura."

    try:
        id_grupo = int(id_grupo)

    except (TypeError, ValueError):
        return False, "Selecciona un grupo válido."

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE LOWER(correo) = LOWER(%s)
            LIMIT 1
            """,
            (correo,)
        )

        if cursor.fetchone():
            return False, "Ya existe una cuenta registrada con ese correo."

        cursor.execute(
            """
            SELECT id_rol
            FROM roles
            WHERE nombre = %s
            LIMIT 1
            """,
            ("Estudiante",)
        )

        rol_estudiante = cursor.fetchone()

        if not rol_estudiante:
            return False, "No existe el rol Estudiante en el sistema."

        cursor.execute(
            """
            SELECT id_grupo
            FROM grupos
            WHERE id_grupo = %s
            LIMIT 1
            """,
            (id_grupo,)
        )

        if not cursor.fetchone():
            return False, "El grupo seleccionado no existe."

        contrasena_hash = generate_password_hash(contrasena)

        cursor.execute(
            """
            INSERT INTO usuarios (
                nombre,
                apellido1,
                apellido2,
                correo,
                contrasena_hash,
                telefono,
                id_rol,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo')
            """,
            (
                nombre,
                apellido1,
                apellido2 or None,
                correo,
                contrasena_hash,
                telefono or None,
                rol_estudiante["id_rol"]
            )
        )

        id_usuario = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO estudiantes (
                id_usuario,
                fecha_nacimiento,
                id_grupo
            )
            VALUES (%s, %s, %s)
            """,
            (
                id_usuario,
                nacimiento,
                id_grupo
            )
        )

        connection.commit()

        return True, "Estudiante registrado correctamente."

    except Exception as e:
        connection.rollback()
        print(f"Error al registrar estudiante: {e}")
        return False, "No fue posible registrar al estudiante."

    finally:
        if cursor:
            cursor.close()

        connection.close()


def actualizar_estudiante(
    id_estudiante,
    nombre,
    apellido1,
    apellido2,
    correo,
    telefono,
    fecha_nacimiento
):
    nombre = (nombre or "").strip()
    apellido1 = (apellido1 or "").strip()
    apellido2 = (apellido2 or "").strip()
    correo = (correo or "").strip().lower()
    telefono = (telefono or "").strip()
    fecha_nacimiento = (fecha_nacimiento or "").strip()

    try:
        id_estudiante = int(id_estudiante)

    except (TypeError, ValueError):
        return False, "El estudiante seleccionado no es válido."

    if not nombre or not apellido1 or not correo or not fecha_nacimiento:
        return False, "Completa los campos obligatorios."

    if len(nombre) > 60 or len(apellido1) > 60 or len(apellido2) > 60:
        return False, "Los nombres y apellidos no pueden superar los 60 caracteres."

    if len(correo) > 120:
        return False, "El correo no puede superar los 120 caracteres."

    if len(telefono) > 20:
        return False, "El teléfono no puede superar los 20 caracteres."

    if not correo.endswith("@escuela.com"):
        return False, "El correo debe pertenecer al dominio @escuela.com."

    try:
        nacimiento = datetime.strptime(
            fecha_nacimiento,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return False, "La fecha de nacimiento no es válida."

    if nacimiento > date.today():
        return False, "La fecha de nacimiento no puede ser futura."

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT e.id_usuario
            FROM estudiantes e
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            WHERE e.id_estudiante = %s
              AND r.nombre = 'Estudiante'
            LIMIT 1
            """,
            (id_estudiante,)
        )

        estudiante = cursor.fetchone()

        if not estudiante:
            return False, "El estudiante no existe o no tiene el rol correspondiente."

        id_usuario = estudiante["id_usuario"]

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE LOWER(correo) = LOWER(%s)
              AND id_usuario <> %s
            LIMIT 1
            """,
            (
                correo,
                id_usuario
            )
        )

        if cursor.fetchone():
            return False, "Ya existe otra cuenta registrada con ese correo."

        cursor.execute(
            """
            UPDATE usuarios
            SET
                nombre = %s,
                apellido1 = %s,
                apellido2 = %s,
                correo = %s,
                telefono = %s
            WHERE id_usuario = %s
            """,
            (
                nombre,
                apellido1,
                apellido2 or None,
                correo,
                telefono or None,
                id_usuario
            )
        )

        cursor.execute(
            """
            UPDATE estudiantes
            SET fecha_nacimiento = %s
            WHERE id_estudiante = %s
            """,
            (
                nacimiento,
                id_estudiante
            )
        )

        connection.commit()

        return True, "La información del estudiante se actualizó correctamente."

    except Exception as e:
        connection.rollback()
        print(f"Error al actualizar estudiante: {e}")
        return False, "No fue posible actualizar la información del estudiante."

    finally:
        if cursor:
            cursor.close()

        connection.close()