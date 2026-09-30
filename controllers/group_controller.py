from db import get_db_connection


# ============================================================
# GRUPOS
# ============================================================

def obtener_grupos():
    """
    Obtiene todos los grupos registrados junto con:
    docente guía y cantidad de estudiantes.
    """

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                g.id_grupo,
                g.nombre,
                g.nivel,
                g.seccion,
                g.anio_lectivo,
                g.id_docente_guia,
                g.fecha_creacion,

                CASE
                    WHEN d.id_docente IS NOT NULL THEN
                        CONCAT(
                            u.nombre,
                            ' ',
                            COALESCE(u.apellido1, ''),
                            ' ',
                            COALESCE(u.apellido2, '')
                        )
                    ELSE
                        NULL
                END AS docente_guia,

                COUNT(DISTINCT e.id_estudiante) AS total_estudiantes

            FROM grupos g

            LEFT JOIN docentes d
                ON g.id_docente_guia = d.id_docente

            LEFT JOIN usuarios u
                ON d.id_usuario = u.id_usuario

            LEFT JOIN estudiantes e
                ON e.id_grupo = g.id_grupo

            GROUP BY
                g.id_grupo,
                g.nombre,
                g.nivel,
                g.seccion,
                g.anio_lectivo,
                g.id_docente_guia,
                g.fecha_creacion,
                d.id_docente,
                u.nombre,
                u.apellido1,
                u.apellido2

            ORDER BY
                g.anio_lectivo DESC,
                g.nivel ASC,
                g.seccion ASC,
                g.id_grupo ASC
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Exception as e:

        print(
            f"Error al obtener grupos: {e}"
        )

        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# OBTENER GRUPO POR ID
# ============================================================

def obtener_grupo_por_id(id_grupo):
    """
    Obtiene un grupo específico por su ID.
    """

    connection = get_db_connection()

    if not connection:
        return None

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id_grupo,
                nombre,
                nivel,
                seccion,
                anio_lectivo,
                id_docente_guia,
                fecha_creacion
            FROM grupos
            WHERE id_grupo = %s
            LIMIT 1
        """

        cursor.execute(
            query,
            (id_grupo,)
        )

        return cursor.fetchone()

    except Exception as e:

        print(
            f"Error al obtener grupo: {e}"
        )

        return None

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# DOCENTES
# ============================================================

def obtener_docentes():
    """
    Obtiene los docentes disponibles para asignarlos
    como docente guía de un grupo.
    """

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                d.id_docente,
                d.id_usuario,

                u.nombre,
                u.apellido1,
                u.apellido2,
                u.correo,

                CONCAT(
                    u.nombre,
                    ' ',
                    COALESCE(u.apellido1, ''),
                    ' ',
                    COALESCE(u.apellido2, '')
                ) AS nombre_completo

            FROM docentes d

            INNER JOIN usuarios u
                ON d.id_usuario = u.id_usuario

            ORDER BY
                u.nombre ASC,
                u.apellido1 ASC,
                u.apellido2 ASC
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Exception as e:

        print(
            f"Error al obtener docentes: {e}"
        )

        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# VALIDAR GRUPO
# ============================================================

def grupo_existe(
    nivel,
    seccion,
    anio_lectivo,
    excluir_id=None
):
    """
    Verifica si ya existe un grupo con la combinación:

    nivel + sección + año lectivo.

    excluir_id se utiliza al editar para no comparar
    el grupo consigo mismo.
    """

    connection = get_db_connection()

    if not connection:
        return False

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id_grupo
            FROM grupos
            WHERE nivel = %s
              AND seccion = %s
              AND anio_lectivo = %s
        """

        params = [
            nivel,
            seccion,
            anio_lectivo
        ]

        if excluir_id is not None:

            query += """
                AND id_grupo <> %s
            """

            params.append(excluir_id)

        query += """
            LIMIT 1
        """

        cursor.execute(
            query,
            tuple(params)
        )

        return cursor.fetchone() is not None

    except Exception as e:

        print(
            f"Error al validar grupo: {e}"
        )

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# CREAR GRUPO
# ============================================================

def crear_grupo(
    nivel,
    seccion,
    anio_lectivo,
    id_docente_guia=None
):
    """
    Crea un nuevo grupo académico.

    El nombre visual del grupo se genera automáticamente.
    """

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        # ----------------------------------------------------
        # LIMPIAR DATOS
        # ----------------------------------------------------

        nivel = (nivel or "").strip()
        seccion = (seccion or "").strip().upper()

        # ----------------------------------------------------
        # VALIDAR NIVEL
        # ----------------------------------------------------

        niveles_validos = {
            "Primero",
            "Segundo",
            "Tercero",
            "Cuarto",
            "Quinto",
            "Sexto"
        }

        if nivel not in niveles_validos:

            return (
                False,
                "El nivel académico seleccionado no es válido."
            )

        # ----------------------------------------------------
        # VALIDAR SECCIÓN
        # ----------------------------------------------------

        secciones_validas = {
            "A",
            "B",
            "C",
            "D",
            "E"
        }

        if seccion not in secciones_validas:

            return (
                False,
                "La sección seleccionada no es válida."
            )

        # ----------------------------------------------------
        # VALIDAR AÑO
        # ----------------------------------------------------

        try:

            anio_lectivo = int(anio_lectivo)

        except (TypeError, ValueError):

            return (
                False,
                "El año lectivo debe ser numérico."
            )

        if anio_lectivo < 2020 or anio_lectivo > 2100:

            return (
                False,
                "El año lectivo ingresado no es válido."
            )

        # ----------------------------------------------------
        # VALIDAR DOCENTE
        # ----------------------------------------------------

        if id_docente_guia in ("", None):

            id_docente_guia = None

        else:

            try:

                id_docente_guia = int(
                    id_docente_guia
                )

            except (TypeError, ValueError):

                return (
                    False,
                    "El docente guía seleccionado no es válido."
                )

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # VALIDAR DUPLICADO
        # ----------------------------------------------------

        query_duplicado = """
            SELECT
                id_grupo
            FROM grupos
            WHERE nivel = %s
              AND seccion = %s
              AND anio_lectivo = %s
            LIMIT 1
        """

        cursor.execute(
            query_duplicado,
            (
                nivel,
                seccion,
                anio_lectivo
            )
        )

        if cursor.fetchone():

            return (
                False,
                (
                    f"Ya existe el grupo de "
                    f"{nivel} sección {seccion} "
                    f"para el año {anio_lectivo}."
                )
            )

        # ----------------------------------------------------
        # VALIDAR DOCENTE
        # ----------------------------------------------------

        if id_docente_guia is not None:

            query_docente = """
                SELECT
                    id_docente
                FROM docentes
                WHERE id_docente = %s
                LIMIT 1
            """

            cursor.execute(
                query_docente,
                (id_docente_guia,)
            )

            if not cursor.fetchone():

                return (
                    False,
                    "El docente guía seleccionado no existe."
                )

        # ----------------------------------------------------
        # GENERAR NOMBRE
        # ----------------------------------------------------

        equivalencias_nivel = {
            "Primero": "1°",
            "Segundo": "2°",
            "Tercero": "3°",
            "Cuarto": "4°",
            "Quinto": "5°",
            "Sexto": "6°"
        }

        numero_nivel = equivalencias_nivel[nivel]

        nombre_grupo = (
            f"{numero_nivel} {seccion}"
        )

        # ----------------------------------------------------
        # INSERTAR
        # ----------------------------------------------------

        query = """
            INSERT INTO grupos (
                nombre,
                nivel,
                seccion,
                anio_lectivo,
                id_docente_guia
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            query,
            (
                nombre_grupo,
                nivel,
                seccion,
                anio_lectivo,
                id_docente_guia
            )
        )

        connection.commit()

        return (
            True,
            "Grupo creado correctamente."
        )

    except Exception as e:

        connection.rollback()

        print(
            f"Error al crear grupo: {e}"
        )

        return (
            False,
            "No fue posible crear el grupo."
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# EDITAR GRUPO
# ============================================================

def editar_grupo(
    id_grupo,
    nivel,
    seccion,
    anio_lectivo,
    id_docente_guia=None
):
    """
    Edita un grupo existente.
    """

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        # ----------------------------------------------------
        # LIMPIAR DATOS
        # ----------------------------------------------------

        try:

            id_grupo = int(id_grupo)

        except (TypeError, ValueError):

            return False, "El grupo seleccionado no es válido."

        nivel = (nivel or "").strip()
        seccion = (seccion or "").strip().upper()

        # ----------------------------------------------------
        # VALIDAR NIVEL
        # ----------------------------------------------------

        niveles_validos = {
            "Primero",
            "Segundo",
            "Tercero",
            "Cuarto",
            "Quinto",
            "Sexto"
        }

        if nivel not in niveles_validos:

            return (
                False,
                "El nivel académico seleccionado no es válido."
            )

        # ----------------------------------------------------
        # VALIDAR SECCIÓN
        # ----------------------------------------------------

        secciones_validas = {
            "A",
            "B",
            "C",
            "D",
            "E"
        }

        if seccion not in secciones_validas:

            return (
                False,
                "La sección seleccionada no es válida."
            )

        # ----------------------------------------------------
        # VALIDAR AÑO
        # ----------------------------------------------------

        try:

            anio_lectivo = int(anio_lectivo)

        except (TypeError, ValueError):

            return (
                False,
                "El año lectivo debe ser numérico."
            )

        if anio_lectivo < 2020 or anio_lectivo > 2100:

            return (
                False,
                "El año lectivo ingresado no es válido."
            )

        # ----------------------------------------------------
        # VALIDAR DOCENTE
        # ----------------------------------------------------

        if id_docente_guia in ("", None):

            id_docente_guia = None

        else:

            try:

                id_docente_guia = int(
                    id_docente_guia
                )

            except (TypeError, ValueError):

                return (
                    False,
                    "El docente guía seleccionado no es válido."
                )

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # VERIFICAR GRUPO
        # ----------------------------------------------------

        cursor.execute(
            """
                SELECT
                    id_grupo
                FROM grupos
                WHERE id_grupo = %s
                LIMIT 1
            """,
            (id_grupo,)
        )

        if not cursor.fetchone():

            return (
                False,
                "El grupo seleccionado no existe."
            )

        # ----------------------------------------------------
        # VALIDAR DUPLICADO
        # ----------------------------------------------------

        query_duplicado = """
            SELECT
                id_grupo
            FROM grupos
            WHERE nivel = %s
              AND seccion = %s
              AND anio_lectivo = %s
              AND id_grupo <> %s
            LIMIT 1
        """

        cursor.execute(
            query_duplicado,
            (
                nivel,
                seccion,
                anio_lectivo,
                id_grupo
            )
        )

        if cursor.fetchone():

            return (
                False,
                (
                    f"Ya existe otro grupo de "
                    f"{nivel} sección {seccion} "
                    f"para el año {anio_lectivo}."
                )
            )

        # ----------------------------------------------------
        # VALIDAR DOCENTE
        # ----------------------------------------------------

        if id_docente_guia is not None:

            cursor.execute(
                """
                    SELECT
                        id_docente
                    FROM docentes
                    WHERE id_docente = %s
                    LIMIT 1
                """,
                (id_docente_guia,)
            )

            if not cursor.fetchone():

                return (
                    False,
                    "El docente guía seleccionado no existe."
                )

        # ----------------------------------------------------
        # GENERAR NOMBRE
        # ----------------------------------------------------

        equivalencias_nivel = {
            "Primero": "1°",
            "Segundo": "2°",
            "Tercero": "3°",
            "Cuarto": "4°",
            "Quinto": "5°",
            "Sexto": "6°"
        }

        nombre_grupo = (
            f"{equivalencias_nivel[nivel]} {seccion}"
        )

        # ----------------------------------------------------
        # ACTUALIZAR
        # ----------------------------------------------------

        query = """
            UPDATE grupos
            SET
                nombre = %s,
                nivel = %s,
                seccion = %s,
                anio_lectivo = %s,
                id_docente_guia = %s
            WHERE id_grupo = %s
        """

        cursor.execute(
            query,
            (
                nombre_grupo,
                nivel,
                seccion,
                anio_lectivo,
                id_docente_guia,
                id_grupo
            )
        )

        connection.commit()

        return (
            True,
            "Grupo actualizado correctamente."
        )

    except Exception as e:

        connection.rollback()

        print(
            f"Error al editar grupo: {e}"
        )

        return (
            False,
            "No fue posible actualizar el grupo."
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# ELIMINAR GRUPO
# ============================================================

def eliminar_grupo(id_grupo):
    """
    Elimina un grupo únicamente si no tiene
    estudiantes asignados.
    """

    connection = get_db_connection()

    if not connection:
        return False, "No se pudo conectar a la base de datos."

    cursor = None

    try:

        try:

            id_grupo = int(id_grupo)

        except (TypeError, ValueError):

            return False, "El grupo seleccionado no es válido."

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # VERIFICAR GRUPO
        # ----------------------------------------------------

        cursor.execute(
            """
                SELECT
                    id_grupo,
                    nombre
                FROM grupos
                WHERE id_grupo = %s
                LIMIT 1
            """,
            (id_grupo,)
        )

        grupo = cursor.fetchone()

        if not grupo:

            return (
                False,
                "El grupo seleccionado no existe."
            )

        # ----------------------------------------------------
        # CONTAR ESTUDIANTES
        # ----------------------------------------------------

        cursor.execute(
            """
                SELECT
                    COUNT(*) AS total
                FROM estudiantes
                WHERE id_grupo = %s
            """,
            (id_grupo,)
        )

        resultado = cursor.fetchone()

        total_estudiantes = int(
            resultado["total"]
            if resultado
            else 0
        )

        # ----------------------------------------------------
        # BLOQUEAR SI TIENE ESTUDIANTES
        # ----------------------------------------------------

        if total_estudiantes > 0:

            return (
                False,
                (
                    f"No se puede eliminar el grupo porque "
                    f"tiene {total_estudiantes} "
                    f"estudiante(s) asignado(s)."
                )
            )

        # ----------------------------------------------------
        # ELIMINAR
        # ----------------------------------------------------

        cursor.execute(
            """
                DELETE FROM grupos
                WHERE id_grupo = %s
            """,
            (id_grupo,)
        )

        connection.commit()

        return (
            True,
            "Grupo eliminado correctamente."
        )

    except Exception as e:

        connection.rollback()

        print(
            f"Error al eliminar grupo: {e}"
        )

        return (
            False,
            "No fue posible eliminar el grupo."
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()