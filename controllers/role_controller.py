from db import get_db_connection



# ROLES


def obtener_roles():
    """consigue  todos los roles y la cantidad de permisos asignados"""

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                r.id_rol,
                r.nombre,
                r.descripcion,
                r.es_sistema,
                COUNT(rp.id_permiso) AS total_permisos
            FROM roles r
            LEFT JOIN rol_permiso rp
                ON r.id_rol = rp.id_rol
            GROUP BY
                r.id_rol,
                r.nombre,
                r.descripcion,
                r.es_sistema
            ORDER BY r.id_rol ASC
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Exception as e:

        print(f"Error al obtener roles: {e}")

        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


def obtener_rol_por_id(id_rol):
    """Obtiene un rol específico"""

    connection = get_db_connection()

    if not connection:
        return None

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id_rol,
                nombre,
                descripcion,
                es_sistema
            FROM roles
            WHERE id_rol = %s
        """

        cursor.execute(query, (id_rol,))

        return cursor.fetchone()

    except Exception as e:

        print(f"Error al obtener rol: {e}")

        return None

    finally:

        if cursor:
            cursor.close()

        connection.close()


def crear_rol(nombre, descripcion):
    """crea un rol personalizado"""

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        nombre = nombre.strip()
        descripcion = descripcion.strip()

        if not nombre:
            return False, "El nombre del rol es obligatorio."

        if len(nombre) > 40:
            return False, "El nombre del rol no puede superar los 40 caracteres."

        if len(descripcion) > 150:
            return False, "La descripción no puede superar los 150 caracteres."

        cursor = connection.cursor(dictionary=True)

        query_verificar = """
            SELECT id_rol
            FROM roles
            WHERE LOWER(nombre) = LOWER(%s)
            LIMIT 1
        """

        cursor.execute(query_verificar, (nombre,))

        if cursor.fetchone():
            return False, "Ya existe un rol con ese nombre."

        query = """
            INSERT INTO roles (
                nombre,
                descripcion,
                es_sistema
            )
            VALUES (%s, %s, 0)
        """

        cursor.execute(
            query,
            (nombre, descripcion)
        )

        connection.commit()

        return True, "Rol creado correctamente."

    except Exception as e:

        connection.rollback()

        print(f"Error al crear rol: {e}")

        return False, "No fue posible crear el rol."

    finally:

        if cursor:
            cursor.close()

        connection.close()


def editar_rol(id_rol, nombre, descripcion):
    """edita únicamente roles personalizados"""

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        nombre = nombre.strip()
        descripcion = descripcion.strip()

        if not nombre:
            return False, "El nombre del rol es obligatorio."

        if len(nombre) > 40:
            return False, "El nombre del rol no puede superar los 40 caracteres."

        if len(descripcion) > 150:
            return False, "La descripción no puede superar los 150 caracteres."

        cursor = connection.cursor(dictionary=True)

        query_rol = """
            SELECT
                id_rol,
                nombre,
                descripcion,
                es_sistema
            FROM roles
            WHERE id_rol = %s
        """

        cursor.execute(query_rol, (id_rol,))

        rol = cursor.fetchone()

        if not rol:
            return False, "El rol no existe."

        if rol["es_sistema"] == 1:
            return False, "Los roles del sistema no pueden modificarse."

        query_verificar = """
            SELECT id_rol
            FROM roles
            WHERE LOWER(nombre) = LOWER(%s)
            AND id_rol <> %s
            LIMIT 1
        """

        cursor.execute(
            query_verificar,
            (nombre, id_rol)
        )

        if cursor.fetchone():

            return False, "Ya existe otro rol con ese nombre."

        query = """
            UPDATE roles
            SET
                nombre = %s,
                descripcion = %s
            WHERE id_rol = %s
        """

        cursor.execute(
            query,
            (nombre, descripcion, id_rol)
        )

        connection.commit()

        return True, "Rol actualizado correctamente."

    except Exception as e:

        connection.rollback()

        print(f"Error al editar rol: {e}")

        return False, "No fue posible actualizar el rol."

    finally:

        if cursor:
            cursor.close()

        connection.close()


def eliminar_rol(id_rol):
    """
    Elimina únicamente roles personalizados
    que no estén siendo utilizados.
    """

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query_rol = """
            SELECT
                id_rol,
                nombre,
                es_sistema
            FROM roles
            WHERE id_rol = %s
        """

        cursor.execute(
            query_rol,
            (id_rol,)
        )

        rol = cursor.fetchone()

        if not rol:
            return False, "El rol no existe."

        if rol["es_sistema"] == 1:
            return False, "Los roles del sistema no pueden eliminarse."

        query_usuarios = """
            SELECT COUNT(*) AS total
            FROM usuarios
            WHERE id_rol = %s
        """

        cursor.execute(
            query_usuarios,
            (id_rol,)
        )

        resultado = cursor.fetchone()

        if resultado["total"] > 0:

            return (
                False,
                "No se puede eliminar este rol porque existen usuarios asociados."
            )

        query = """
            DELETE FROM roles
            WHERE id_rol = %s
        """

        cursor.execute(
            query,
            (id_rol,)
        )

        connection.commit()

        return True, "Rol eliminado correctamente."

    except Exception as e:

        connection.rollback()

        print(f"Error al eliminar rol: {e}")

        return False, "No fue posible eliminar el rol."

    finally:

        if cursor:
            cursor.close()

        connection.close()



# PERMISOS


def obtener_permisos():
    """
    Obtiene todos los permisos del sistema.
    """

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id_permiso,
                codigo,
                nombre,
                descripcion,
                modulo,
                orden
            FROM permisos
            ORDER BY modulo ASC, orden ASC
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Exception as e:

        print(f"Error al obtener permisos: {e}")

        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


def obtener_permisos_por_rol():
    """Devuelve un diccionario"""

    connection = get_db_connection()

    if not connection:
        return {}

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id_rol,
                id_permiso
            FROM rol_permiso
            ORDER BY id_rol, id_permiso
        """

        cursor.execute(query)

        filas = cursor.fetchall()

        permisos_por_rol = {}

        for fila in filas:

            id_rol = fila["id_rol"]

            if id_rol not in permisos_por_rol:
                permisos_por_rol[id_rol] = []

            permisos_por_rol[id_rol].append(
                fila["id_permiso"]
            )

        return permisos_por_rol

    except Exception as e:

        print(f"Error al obtener permisos por rol: {e}")

        return {}

    finally:

        if cursor:
            cursor.close()

        connection.close()


def guardar_permisos_rol(id_rol, permisos_ids):
    """reemplaza los permisos asignados a un rol, el rol Administrador conserva acceso total"""

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        
        # verifica rol
        

        query_rol = """
            SELECT
                id_rol,
                nombre
            FROM roles
            WHERE id_rol = %s
        """

        cursor.execute(
            query_rol,
            (id_rol,)
        )

        rol = cursor.fetchone()

        if not rol:
            return False, "El rol no existe."


        
        # protege administrador
        

        if rol["nombre"] == "Administrador":

            return (
                False,
                "El rol Administrador conserva acceso total al sistema."
            )


        
        # ids
        

        permisos_limpios = []

        for permiso_id in permisos_ids:

            try:

                permiso_id = int(permiso_id)

                if permiso_id > 0:
                    permisos_limpios.append(permiso_id)

            except (TypeError, ValueError):
                continue


        permisos_limpios = list(
            dict.fromkeys(permisos_limpios)
        )


        
        # valida permisos existentes
        

        if permisos_limpios:

            placeholders = ",".join(
                ["%s"] * len(permisos_limpios)
            )

            query_validar = f"""
                SELECT COUNT(*) AS total
                FROM permisos
                WHERE id_permiso IN ({placeholders})
            """

            cursor.execute(
                query_validar,
                tuple(permisos_limpios)
            )

            total_validos = cursor.fetchone()["total"]

            if total_validos != len(permisos_limpios):

                return (
                    False,
                    "Uno o más permisos seleccionados no son válidos."
                )


        
        # elimina permisos actuales
        

        query_delete = """
            DELETE FROM rol_permiso
            WHERE id_rol = %s
        """

        cursor.execute(
            query_delete,
            (id_rol,)
        )


        
        # mete nuevos permisos
        

        if permisos_limpios:

            query_insert = """
                INSERT INTO rol_permiso (
                    id_rol,
                    id_permiso
                )
                VALUES (%s, %s)
            """

            valores = [
                (id_rol, permiso_id)
                for permiso_id in permisos_limpios
            ]

            cursor.executemany(
                query_insert,
                valores
            )


        connection.commit()

        return True, "Permisos actualizados correctamente"

    except Exception as e:

        connection.rollback()

        print(f"Error al guardar permisos: {e}")

        return False, "No fue posible actualizar los permisos."

    finally:

        if cursor:
            cursor.close()

        connection.close()


def usuario_tiene_permiso(id_usuario, codigo_permiso):
    """ve  si un usuario posee un permiso y el Administrador tiene acceso total"""

    connection = get_db_connection()

    if not connection:
        return False

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                r.nombre AS rol,
                p.id_permiso
            FROM usuarios u
            INNER JOIN roles r
                ON u.id_rol = r.id_rol
            LEFT JOIN rol_permiso rp
                ON r.id_rol = rp.id_rol
            LEFT JOIN permisos p
                ON rp.id_permiso = p.id_permiso
            WHERE u.id_usuario = %s
              AND (
                    r.nombre = 'Administrador'
                    OR p.codigo = %s
                  )
              AND u.estado = 'activo'
            LIMIT 1
        """

        cursor.execute(
            query,
            (id_usuario, codigo_permiso)
        )

        return cursor.fetchone() is not None

    except Exception as e:

        print(f"Error al verificar permiso: {e}")

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()