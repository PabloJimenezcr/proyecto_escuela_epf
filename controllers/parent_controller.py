from db import get_db_connection
from werkzeug.security import generate_password_hash

PARENTESCOS = [
    "Madre",
    "Padre",
    "Encargado",
    "Abuelo/a",
    "Tío/a",
    "Otro"
]


def registrar_padre_familia(
    nombre,
    apellido1,
    apellido2,
    correo,
    telefono,
    contrasena
):
    nombre = (nombre or "").strip()
    apellido1 = (apellido1 or "").strip()
    apellido2 = (apellido2 or "").strip()
    correo = (correo or "").strip().lower()
    telefono = (telefono or "").strip()
    contrasena = contrasena or ""

    if not nombre or not apellido1 or not correo or not contrasena:
        return False, "Completa los campos obligatorios."

    if not correo.endswith("@escuela.com"):
        return False, "El correo debe pertenecer al dominio @escuela.com."

    if len(nombre) > 100 or len(apellido1) > 100 or len(apellido2) > 100:
        return False, "Los nombres y apellidos no pueden superar los 100 caracteres."

    if len(correo) > 150:
        return False, "El correo no puede superar los 150 caracteres."

    if len(telefono) > 20:
        return False, "El teléfono no puede superar los 20 caracteres."

    if len(contrasena) < 8:
        return False, "La contraseña inicial debe tener al menos 8 caracteres."

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
            ("Padre de Familia",)
        )

        rol_padre = cursor.fetchone()

        if not rol_padre:
            return False, "No existe el rol Padre de Familia en el sistema."

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
                rol_padre["id_rol"]
            )
        )

        id_usuario = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO padres (id_usuario)
            VALUES (%s)
            """,
            (id_usuario,)
        )

        connection.commit()

        return True, "Padre de familia registrado correctamente."

    except Exception as e:
        connection.rollback()
        print(f"Error al registrar padre de familia: {e}")
        return False, "No fue posible registrar al padre de familia."

    finally:
        if cursor:
            cursor.close()
        connection.close()


def obtener_padres():
    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            INSERT INTO padres (id_usuario)
            SELECT u.id_usuario
            FROM usuarios u
            INNER JOIN roles r ON r.id_rol = u.id_rol
            WHERE r.nombre = 'Padre de Familia'
              AND NOT EXISTS (
                  SELECT 1
                  FROM padres p
                  WHERE p.id_usuario = u.id_usuario
              )
            """
        )

        connection.commit()

        cursor.execute(
            """
            SELECT
                p.id_padre,
                u.nombre,
                u.apellido1,
                u.apellido2,
                u.correo,
                u.telefono
            FROM padres p
            INNER JOIN usuarios u ON u.id_usuario = p.id_usuario
            WHERE u.estado = 'activo'
            ORDER BY u.apellido1, u.apellido2, u.nombre
            """
        )

        return cursor.fetchall()

    except Exception as e:
        connection.rollback()
        print(f"Error al obtener padres: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()


def obtener_estudiantes_activos():
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
                u.nombre,
                u.apellido1,
                u.apellido2,
                g.nombre AS grupo
            FROM estudiantes e
            INNER JOIN usuarios u ON u.id_usuario = e.id_usuario
            INNER JOIN grupos g ON g.id_grupo = e.id_grupo
            WHERE u.estado = 'activo'
            ORDER BY u.apellido1, u.apellido2, u.nombre
            """
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener estudiantes: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()


def obtener_vinculos():
    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                pe.id_vinculo,
                pe.parentesco,
                CONCAT(
                    up.nombre,
                    ' ',
                    up.apellido1,
                    ' ',
                    COALESCE(up.apellido2, '')
                ) AS padre,
                up.correo AS correo_padre,
                CONCAT(
                    ue.nombre,
                    ' ',
                    ue.apellido1,
                    ' ',
                    COALESCE(ue.apellido2, '')
                ) AS estudiante,
                g.nombre AS grupo
            FROM padre_estudiante pe
            INNER JOIN padres p ON p.id_padre = pe.id_padre
            INNER JOIN usuarios up ON up.id_usuario = p.id_usuario
            INNER JOIN estudiantes e ON e.id_estudiante = pe.id_estudiante
            INNER JOIN usuarios ue ON ue.id_usuario = e.id_usuario
            INNER JOIN grupos g ON g.id_grupo = e.id_grupo
            ORDER BY up.apellido1, up.nombre, ue.apellido1, ue.nombre
            """
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener vínculos: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()


def crear_vinculo(id_padre, id_estudiante, parentesco):
    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:
        try:
            id_padre = int(id_padre)
            id_estudiante = int(id_estudiante)
        except (TypeError, ValueError):
            return False, "Selecciona un padre y un estudiante."

        parentesco = (parentesco or "").strip()

        if parentesco not in PARENTESCOS:
            return False, "El parentesco seleccionado no es válido."

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_padre FROM padres WHERE id_padre = %s",
            (id_padre,)
        )

        if not cursor.fetchone():
            return False, "El padre seleccionado no existe."

        cursor.execute(
            "SELECT id_estudiante FROM estudiantes WHERE id_estudiante = %s",
            (id_estudiante,)
        )

        if not cursor.fetchone():
            return False, "El estudiante seleccionado no existe."

        cursor.execute(
            """
            SELECT id_vinculo
            FROM padre_estudiante
            WHERE id_padre = %s AND id_estudiante = %s
            """,
            (id_padre, id_estudiante)
        )

        if cursor.fetchone():
            return False, "Ese padre ya está vinculado con ese estudiante."

        cursor.execute(
            """
            INSERT INTO padre_estudiante (
                id_padre,
                id_estudiante,
                parentesco
            )
            VALUES (%s, %s, %s)
            """,
            (id_padre, id_estudiante, parentesco)
        )

        connection.commit()

        return True, "Vínculo creado correctamente."

    except Exception as e:
        connection.rollback()
        print(f"Error al crear vínculo: {e}")
        return False, "No fue posible crear el vínculo."

    finally:
        if cursor:
            cursor.close()
        connection.close()


def eliminar_vinculo(id_vinculo):
    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:
        try:
            id_vinculo = int(id_vinculo)
        except (TypeError, ValueError):
            return False, "El vínculo seleccionado no es válido."

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM padre_estudiante WHERE id_vinculo = %s",
            (id_vinculo,)
        )

        if cursor.rowcount == 0:
            return False, "El vínculo no existe."

        connection.commit()

        return True, "Vínculo eliminado correctamente."

    except Exception as e:
        connection.rollback()
        print(f"Error al eliminar vínculo: {e}")
        return False, "No fue posible eliminar el vínculo."

    finally:
        if cursor:
            cursor.close()
        connection.close()