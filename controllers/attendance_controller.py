from datetime import date, datetime

from db import get_db_connection


ESTADOS_ASISTENCIA = {
    "presente": "Presente",
    "ausente": "Ausente",
    "tardanza": "Tardanza",
    "justificado": "Justificado"
}


def convertir_fecha(valor):
    if not valor:
        return None

    try:
        return datetime.strptime(
            str(valor),
            "%Y-%m-%d"
        ).date()
    except (TypeError, ValueError):
        return None


def obtener_grupos_asistencia():
    conexion = get_db_connection()

    if not conexion:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                id_grupo,
                nombre,
                nivel,
                seccion,
                anio_lectivo
            FROM grupos
            ORDER BY
                anio_lectivo DESC,
                nivel,
                seccion,
                nombre
            """
        )

        return cursor.fetchall()

    except Exception as error:
        print(f"Error al consultar grupos: {error}")
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def obtener_estudiantes_grupo(id_grupo, fecha):
    fecha_validada = convertir_fecha(fecha)

    try:
        id_grupo = int(id_grupo)
    except (TypeError, ValueError):
        return []

    if id_grupo <= 0 or not fecha_validada:
        return []

    conexion = get_db_connection()

    if not conexion:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                e.id_estudiante,
                u.nombre,
                u.apellido1,
                u.apellido2,
                u.correo,
                a.id_asistencia,
                a.estado,
                a.observacion
            FROM estudiantes e
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            LEFT JOIN asistencias a
                ON a.id_estudiante = e.id_estudiante
                AND a.fecha = %s
            WHERE e.id_grupo = %s
                AND u.estado = 'activo'
            ORDER BY
                u.apellido1,
                u.apellido2,
                u.nombre
            """,
            (fecha_validada, id_grupo)
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            f"Error al consultar estudiantes del grupo: {error}"
        )
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def guardar_asistencia_diaria(
    id_grupo,
    fecha,
    id_usuario,
    datos_formulario
):
    try:
        id_grupo = int(id_grupo)
    except (TypeError, ValueError):
        return False, "Selecciona un grupo válido."

    fecha_validada = convertir_fecha(fecha)

    if id_grupo <= 0:
        return False, "Selecciona un grupo válido."

    if not fecha_validada:
        return False, "Selecciona una fecha válida."

    if fecha_validada > date.today():
        return False, (
            "No se puede registrar asistencia "
            "para una fecha futura."
        )

    try:
        id_usuario = int(id_usuario)
    except (TypeError, ValueError):
        return False, "La sesión del usuario no es válida."

    conexion = get_db_connection()

    if not conexion:
        return False, (
            "No se pudo conectar con la base de datos."
        )

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                e.id_estudiante
            FROM estudiantes e
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            WHERE e.id_grupo = %s
                AND u.estado = 'activo'
                AND r.nombre = 'Estudiante'
            ORDER BY e.id_estudiante
            """,
            (id_grupo,)
        )

        estudiantes = cursor.fetchall()

        if not estudiantes:
            return False, (
                "El grupo seleccionado no tiene "
                "estudiantes activos."
            )

        registros = []

        for estudiante in estudiantes:
            id_estudiante = estudiante["id_estudiante"]

            estado = (
                datos_formulario.get(
                    f"estado_{id_estudiante}"
                ) or ""
            ).strip().lower()

            observacion = (
                datos_formulario.get(
                    f"observacion_{id_estudiante}"
                ) or ""
            ).strip()

            if estado not in ESTADOS_ASISTENCIA:
                return False, (
                    "Selecciona un estado de asistencia "
                    "para cada estudiante."
                )

            if len(observacion) > 500:
                return False, (
                    "Las observaciones no pueden superar "
                    "los 500 caracteres."
                )

            registros.append(
                (
                    id_estudiante,
                    fecha_validada,
                    estado,
                    observacion or None,
                    id_usuario
                )
            )

        cursor.executemany(
            """
            INSERT INTO asistencias (
                id_estudiante,
                fecha,
                estado,
                observacion,
                registrado_por
            )
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                estado = VALUES(estado),
                observacion = VALUES(observacion),
                registrado_por = VALUES(registrado_por),
                fecha_actualizacion = CURRENT_TIMESTAMP
            """,
            registros
        )

        conexion.commit()

        return True, (
            f"La asistencia de {len(registros)} "
            "estudiantes se guardó correctamente."
        )

    except Exception as error:
        conexion.rollback()

        print(
            f"Error al guardar asistencia diaria: {error}"
        )

        return False, (
            "No fue posible guardar la asistencia. "
            "Verifica la conexión y la tabla de asistencia."
        )

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def obtener_estudiantes_para_historial():
    conexion = get_db_connection()

    if not conexion:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                e.id_estudiante,
                u.nombre,
                u.apellido1,
                u.apellido2,
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
            ORDER BY
                g.nombre,
                u.apellido1,
                u.apellido2,
                u.nombre
            """
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            f"Error al consultar estudiantes para historial: {error}"
        )
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def obtener_historial_asistencia_estudiante(id_estudiante):
    try:
        id_estudiante = int(id_estudiante)
    except (TypeError, ValueError):
        return []

    if id_estudiante <= 0:
        return []

    conexion = get_db_connection()

    if not conexion:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.id_asistencia,
                a.id_estudiante,
                a.fecha,
                a.estado,
                a.observacion,
                a.fecha_registro,
                a.fecha_actualizacion,
                CONCAT_WS(
                    ' ',
                    ur.nombre,
                    ur.apellido1
                ) AS registrado_por_nombre
            FROM asistencias a
            LEFT JOIN usuarios ur
                ON ur.id_usuario = a.registrado_por
            WHERE a.id_estudiante = %s
            ORDER BY
                a.fecha DESC,
                a.id_asistencia DESC
            """,
            (id_estudiante,)
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            f"Error al consultar historial individual: {error}"
        )
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def obtener_asistencia_por_id(id_asistencia):
    try:
        id_asistencia = int(id_asistencia)
    except (TypeError, ValueError):
        return None

    if id_asistencia <= 0:
        return None

    conexion = get_db_connection()

    if not conexion:
        return None

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.id_asistencia,
                a.id_estudiante,
                a.fecha,
                a.estado,
                a.observacion,
                a.fecha_registro,
                a.fecha_actualizacion,
                a.registrado_por,
                u.nombre,
                u.apellido1,
                u.apellido2,
                g.nombre AS nombre_grupo,
                g.nivel,
                g.seccion,
                g.anio_lectivo
            FROM asistencias a
            INNER JOIN estudiantes e
                ON e.id_estudiante = a.id_estudiante
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            INNER JOIN grupos g
                ON g.id_grupo = e.id_grupo
            WHERE a.id_asistencia = %s
            LIMIT 1
            """,
            (id_asistencia,)
        )

        return cursor.fetchone()

    except Exception as error:
        print(
            f"Error al consultar asistencia para editar: {error}"
        )
        return None

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def actualizar_registro_asistencia(
    id_asistencia,
    fecha,
    estado,
    observacion
):
    try:
        id_asistencia = int(id_asistencia)
    except (TypeError, ValueError):
        return False, (
            "El registro de asistencia no es válido."
        )

    if id_asistencia <= 0:
        return False, (
            "El registro de asistencia no es válido."
        )

    fecha_validada = convertir_fecha(fecha)

    if not fecha_validada:
        return False, "Selecciona una fecha válida."

    if fecha_validada > date.today():
        return False, (
            "No se puede registrar asistencia "
            "para una fecha futura."
        )

    estado = (estado or "").strip().lower()
    observacion = (observacion or "").strip()

    if estado not in ESTADOS_ASISTENCIA:
        return False, (
            "Selecciona un estado de asistencia válido."
        )

    if len(observacion) > 500:
        return False, (
            "La observación no puede superar "
            "los 500 caracteres."
        )

    conexion = get_db_connection()

    if not conexion:
        return False, (
            "No se pudo conectar con la base de datos."
        )

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id_asistencia,
                id_estudiante
            FROM asistencias
            WHERE id_asistencia = %s
            LIMIT 1
            """,
            (id_asistencia,)
        )

        registro = cursor.fetchone()

        if not registro:
            return False, (
                "El registro de asistencia no existe."
            )

        cursor.execute(
            """
            SELECT id_asistencia
            FROM asistencias
            WHERE id_estudiante = %s
                AND fecha = %s
                AND id_asistencia <> %s
            LIMIT 1
            """,
            (
                registro["id_estudiante"],
                fecha_validada,
                id_asistencia
            )
        )

        if cursor.fetchone():
            return False, (
                "Ya existe una asistencia para ese estudiante "
                "en la fecha seleccionada."
            )

        cursor.execute(
            """
            UPDATE asistencias
            SET fecha = %s,
                estado = %s,
                observacion = %s
            WHERE id_asistencia = %s
            """,
            (
                fecha_validada,
                estado,
                observacion or None,
                id_asistencia
            )
        )

        conexion.commit()

        return True, (
            "El registro de asistencia se actualizó correctamente."
        )

    except Exception as error:
        conexion.rollback()

        print(
            f"Error al actualizar registro de asistencia: {error}"
        )

        return False, (
            "No fue posible actualizar el registro de asistencia."
        )

def obtener_estudiante_por_usuario(id_usuario):
    try:
        id_usuario = int(id_usuario)
    except (TypeError, ValueError):
        return None

    if id_usuario <= 0:
        return None

    conexion = get_db_connection()

    if not conexion:
        return None

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                e.id_estudiante,
                e.fecha_nacimiento,
                e.fecha_matricula,
                u.id_usuario,
                u.nombre,
                u.apellido1,
                u.apellido2,
                u.correo,
                g.id_grupo,
                g.nombre AS nombre_grupo,
                g.nivel,
                g.seccion,
                g.anio_lectivo
            FROM estudiantes e
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            INNER JOIN grupos g
                ON g.id_grupo = e.id_grupo
            WHERE u.id_usuario = %s
                AND r.nombre = 'Estudiante'
                AND u.estado = 'activo'
            LIMIT 1
            """,
            (id_usuario,)
        )

        return cursor.fetchone()

    except Exception as error:
        print(
            f"Error al consultar el perfil del estudiante: {error}"
        )
        return None

def consultar_reporte_asistencia(
    tipo,
    id_grupo=None,
    id_estudiante=None,
    desde=None,
    hasta=None
):
    resumen_vacio = {
        "total": 0,
        "presente": 0,
        "ausente": 0,
        "tardanza": 0,
        "justificado": 0,
        "porcentaje": 0
    }

    tipo = (tipo or "").strip().lower()

    if tipo not in ("grupo", "estudiante"):
        return (
            False,
            "Selecciona un tipo de reporte válido.",
            [],
            resumen_vacio
        )

    if tipo == "grupo":
        try:
            id_grupo = int(id_grupo)

            if id_grupo <= 0:
                raise ValueError

        except (TypeError, ValueError):
            return (
                False,
                "Selecciona un grupo válido.",
                [],
                resumen_vacio
            )

    else:
        try:
            id_estudiante = int(id_estudiante)

            if id_estudiante <= 0:
                raise ValueError

        except (TypeError, ValueError):
            return (
                False,
                "Selecciona un estudiante válido.",
                [],
                resumen_vacio
            )

    fecha_desde = None
    fecha_hasta = None

    if desde:
        fecha_desde = convertir_fecha(desde)

        if not fecha_desde:
            return (
                False,
                "La fecha inicial no es válida.",
                [],
                resumen_vacio
            )

    if hasta:
        fecha_hasta = convertir_fecha(hasta)

        if not fecha_hasta:
            return (
                False,
                "La fecha final no es válida.",
                [],
                resumen_vacio
            )

    if fecha_desde and fecha_hasta:
        if fecha_desde > fecha_hasta:
            return (
                False,
                "La fecha inicial no puede ser posterior a la final.",
                [],
                resumen_vacio
            )

    conexion = get_db_connection()

    if not conexion:
        return (
            False,
            "No se pudo conectar con la base de datos.",
            [],
            resumen_vacio
        )

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT
                a.id_asistencia,
                a.id_estudiante,
                a.fecha,
                a.estado,
                a.observacion,
                a.fecha_registro,
                CONCAT_WS(
                    ' ',
                    u.nombre,
                    u.apellido1,
                    u.apellido2
                ) AS estudiante,
                g.id_grupo,
                g.nombre AS nombre_grupo,
                g.nivel,
                g.seccion,
                g.anio_lectivo
            FROM asistencias a
            INNER JOIN estudiantes e
                ON e.id_estudiante = a.id_estudiante
            INNER JOIN usuarios u
                ON u.id_usuario = e.id_usuario
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            INNER JOIN grupos g
                ON g.id_grupo = e.id_grupo
            WHERE r.nombre = 'Estudiante'
        """

        parametros = []

        if tipo == "grupo":
            query += " AND g.id_grupo = %s"
            parametros.append(id_grupo)
        else:
            query += " AND e.id_estudiante = %s"
            parametros.append(id_estudiante)

        if fecha_desde:
            query += " AND a.fecha >= %s"
            parametros.append(fecha_desde)

        if fecha_hasta:
            query += " AND a.fecha <= %s"
            parametros.append(fecha_hasta)

        query += """
            ORDER BY
                a.fecha DESC,
                u.apellido1,
                u.nombre
        """

        cursor.execute(query, tuple(parametros))
        filas = cursor.fetchall()

        resumen = {
            "total": len(filas),
            "presente": 0,
            "ausente": 0,
            "tardanza": 0,
            "justificado": 0,
            "porcentaje": 0
        }

        for fila in filas:
            estado = fila["estado"]

            if estado in (
                "presente",
                "ausente",
                "tardanza",
                "justificado"
            ):
                resumen[estado] += 1

        if resumen["total"] > 0:
            resumen["porcentaje"] = round(
                (
                    resumen["presente"]
                    + resumen["tardanza"]
                )
                / resumen["total"]
                * 100,
                1
            )

        return True, "", filas, resumen

    except Exception as error:
        conexion.rollback()

        print(
            f"Error al generar reporte de asistencia: {error}"
        )

        return (
            False,
            "No fue posible generar el reporte de asistencia.",
            [],
            resumen_vacio
        )

    finally:
        if cursor:
            cursor.close()

        conexion.close()