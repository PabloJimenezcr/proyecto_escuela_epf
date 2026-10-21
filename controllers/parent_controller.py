from db import get_db_connection

PARENTESCOS = ["Madre", "Padre", "Encargado", "Abuelo/a", "Tío/a", "Otro"]


def obtener_padres():
    """Padres activos. Crea el perfil en 'padres' si un usuario con rol Padre no lo tiene."""

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # Perfil faltante para usuarios con rol Padre de Familia
        cursor.execute(
            """
                INSERT INTO padres (id_usuario)
                SELECT u.id_usuario
                FROM usuarios u
                INNER JOIN roles r ON r.id_rol = u.id_rol
                WHERE r.nombre = 'Padre de Familia'
                  AND u.id_usuario NOT IN (SELECT id_usuario FROM padres)
            """
        )

        connection.commit()

        cursor.execute(
            """
                SELECT
                    p.id_padre,
                    u.nombre, u.apellido1, u.apellido2, u.correo
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
    """Estudiantes activos con su grupo."""

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
                    u.nombre, u.apellido1, u.apellido2,
                    g.nombre AS grupo
                FROM estudiantes e
                INNER JOIN usuarios u ON u.id_usuario = e.id_usuario
                INNER JOIN grupos g   ON g.id_grupo = e.id_grupo
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
    """Vínculos padre-estudiante existentes."""

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
                    CONCAT(up.nombre, ' ', up.apellido1, ' ', COALESCE(up.apellido2, '')) AS padre,
                    up.correo AS correo_padre,
                    CONCAT(ue.nombre, ' ', ue.apellido1, ' ', COALESCE(ue.apellido2, '')) AS estudiante,
                    g.nombre AS grupo
                FROM padre_estudiante pe
                INNER JOIN padres p       ON p.id_padre = pe.id_padre
                INNER JOIN usuarios up    ON up.id_usuario = p.id_usuario
                INNER JOIN estudiantes e  ON e.id_estudiante = pe.id_estudiante
                INNER JOIN usuarios ue    ON ue.id_usuario = e.id_usuario
                INNER JOIN grupos g       ON g.id_grupo = e.id_grupo
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
    """Vincula un padre con un estudiante. Devuelve (exito, mensaje)."""

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

        cursor.execute("SELECT id_padre FROM padres WHERE id_padre = %s", (id_padre,))

        if not cursor.fetchone():
            return False, "El padre seleccionado no existe."

        cursor.execute("SELECT id_estudiante FROM estudiantes WHERE id_estudiante = %s", (id_estudiante,))

        if not cursor.fetchone():
            return False, "El estudiante seleccionado no existe."

        cursor.execute(
            "SELECT id_vinculo FROM padre_estudiante WHERE id_padre = %s AND id_estudiante = %s",
            (id_padre, id_estudiante)
        )

        if cursor.fetchone():
            return False, "Ese padre ya está vinculado con ese estudiante."

        cursor.execute(
            "INSERT INTO padre_estudiante (id_padre, id_estudiante, parentesco) VALUES (%s, %s, %s)",
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
    """Quita un vínculo. Devuelve (exito, mensaje)."""

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

        cursor.execute("DELETE FROM padre_estudiante WHERE id_vinculo = %s", (id_vinculo,))

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