from db import get_db_connection


def obtener_materias_catalogo():
    connection = get_db_connection()
    if not connection:
        return []
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_materia, nombre FROM materias ORDER BY nombre")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener materias: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        connection.close()


def obtener_periodos_catalogo():
    connection = get_db_connection()
    if not connection:
        return []
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_periodo, nombre FROM periodos_academicos "
            "ORDER BY anio_lectivo DESC, fecha_inicio"
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener periodos: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        connection.close()


def obtener_notas_grupo(id_grupo, id_materia, id_periodo):
    """Estudiantes del grupo con su nota (None si aún no tiene)."""

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
                    c.nota
                FROM estudiantes e
                INNER JOIN usuarios u ON u.id_usuario = e.id_usuario
                LEFT JOIN calificaciones c
                       ON c.id_estudiante = e.id_estudiante
                      AND c.id_materia = %s
                      AND c.id_periodo = %s
                WHERE e.id_grupo = %s AND u.estado = 'activo'
                ORDER BY u.apellido1, u.apellido2, u.nombre
            """,
            (id_materia, id_periodo, id_grupo)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener notas del grupo: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        connection.close()


def guardar_notas(id_grupo, id_materia, id_periodo, notas):
    """
    notas: dict {id_estudiante: texto_de_la_nota}.
    Inserta o actualiza. Una nota vacía se ignora.
    Devuelve (exito, mensaje).
    """

    connection = get_db_connection()
    if not connection:
        return False, "No se pudo conectar a la base de datos."
    cursor = None
    try:
        try:
            id_grupo = int(id_grupo)
            id_materia = int(id_materia)
            id_periodo = int(id_periodo)
        except (TypeError, ValueError):
            return False, "Selecciona grupo, materia y período."

        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id_docente_guia FROM grupos WHERE id_grupo = %s", (id_grupo,))
        grupo = cursor.fetchone()
        if not grupo:
            return False, "El grupo seleccionado no existe."

        cursor.execute("SELECT id_materia FROM materias WHERE id_materia = %s", (id_materia,))
        if not cursor.fetchone():
            return False, "La materia seleccionada no existe."

        cursor.execute("SELECT id_periodo FROM periodos_academicos WHERE id_periodo = %s", (id_periodo,))
        if not cursor.fetchone():
            return False, "El período seleccionado no existe."

        # Docente que se registra: el asignado a la materia en el grupo, o el guía
        cursor.execute(
            "SELECT id_docente FROM docente_materia_grupo "
            "WHERE id_grupo = %s AND id_materia = %s LIMIT 1",
            (id_grupo, id_materia)
        )
        fila = cursor.fetchone()
        id_docente = fila["id_docente"] if fila else grupo["id_docente_guia"]

        if not id_docente:
            return False, ("El grupo no tiene docente asignado a esa materia ni docente guía. "
                           "Asigna uno antes de calificar.")

        # Estudiantes válidos del grupo
        cursor.execute("SELECT id_estudiante FROM estudiantes WHERE id_grupo = %s", (id_grupo,))
        validos = {f["id_estudiante"] for f in cursor.fetchall()}

        guardadas = 0

        for id_est, texto in notas.items():
            texto = (texto or "").strip().replace(",", ".")
            if texto == "":
                continue

            try:
                id_est = int(id_est)
                nota = round(float(texto), 2)
            except ValueError:
                return False, "Todas las notas deben ser numéricas."

            if id_est not in validos:
                return False, "Se envió un estudiante que no pertenece al grupo."

            if nota < 0 or nota > 100:
                return False, "Las notas deben estar entre 0 y 100."

            cursor.execute(
                """
                    INSERT INTO calificaciones
                        (id_estudiante, id_materia, id_docente, id_periodo, nota)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nota = VALUES(nota),
                        id_docente = VALUES(id_docente),
                        fecha_registro = CURRENT_TIMESTAMP
                """,
                (id_est, id_materia, id_docente, id_periodo, nota)
            )
            guardadas += 1

        if guardadas == 0:
            return False, "No ingresaste ninguna nota."

        connection.commit()
        return True, f"Se guardaron {guardadas} calificación(es) correctamente."

    except Exception as e:
        connection.rollback()
        print(f"Error al guardar notas: {e}")
        return False, "No fue posible guardar las calificaciones."
    finally:
        if cursor:
            cursor.close()
        connection.close()
# ============================================================
# EPF-08-03 - CALIFICACIONES POR PERIODO (TODOS LOS ESTUDIANTES)
# ============================================================

def obtener_calificaciones_periodo(id_grupo, id_periodo):
    """
    Devuelve (materias, filas):
      materias: lista de materias que tienen al menos una nota en el grupo/periodo.
      filas: una por estudiante, con 'notas' {id_materia: nota} y 'promedio'.
    """

    connection = get_db_connection()

    if not connection:
        return [], []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
                SELECT DISTINCT m.id_materia, m.nombre
                FROM calificaciones c
                INNER JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
                INNER JOIN materias m    ON m.id_materia = c.id_materia
                WHERE e.id_grupo = %s AND c.id_periodo = %s
                ORDER BY m.nombre
            """,
            (id_grupo, id_periodo)
        )

        materias = cursor.fetchall()

        cursor.execute(
            """
                SELECT
                    e.id_estudiante,
                    u.nombre, u.apellido1, u.apellido2
                FROM estudiantes e
                INNER JOIN usuarios u ON u.id_usuario = e.id_usuario
                WHERE e.id_grupo = %s AND u.estado = 'activo'
                ORDER BY u.apellido1, u.apellido2, u.nombre
            """,
            (id_grupo,)
        )

        estudiantes = cursor.fetchall()

        cursor.execute(
            """
                SELECT c.id_estudiante, c.id_materia, c.nota
                FROM calificaciones c
                INNER JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
                WHERE e.id_grupo = %s AND c.id_periodo = %s
            """,
            (id_grupo, id_periodo)
        )

        notas_por_est = {}

        for f in cursor.fetchall():
            notas_por_est.setdefault(f["id_estudiante"], {})[f["id_materia"]] = float(f["nota"])

        filas = []

        for e in estudiantes:
            notas = notas_por_est.get(e["id_estudiante"], {})
            promedio = round(sum(notas.values()) / len(notas), 2) if notas else None
            filas.append({
                "id_estudiante": e["id_estudiante"],
                "nombre": f"{e['apellido1']} {e['apellido2'] or ''}, {e['nombre']}".replace("  ", " "),
                "notas": notas,
                "promedio": promedio
            })

        return materias, filas

    except Exception as e:

        print(f"Error al obtener calificaciones por periodo: {e}")

        return [], []

  # ============================================================
# EPF-08-04 - HISTORIAL DE CALIFICACIONES DE UN ESTUDIANTE
# ============================================================

def obtener_estudiantes_con_grupo():
    """Estudiantes activos con su grupo, para el selector."""

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


def obtener_historial_calificaciones(id_estudiante):
    """
    Devuelve (estudiante, periodos, promedio_general).
    periodos: lista de {nombre, notas: [{materia, nota}], promedio}.
    Si el estudiante no existe devuelve (None, [], None).
    """

    connection = get_db_connection()

    if not connection:
        return None, [], None

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
                WHERE e.id_estudiante = %s
                LIMIT 1
            """,
            (id_estudiante,)
        )

        estudiante = cursor.fetchone()

        if not estudiante:
            return None, [], None

        cursor.execute(
            """
                SELECT
                    p.id_periodo, p.nombre AS periodo,
                    m.nombre AS materia, c.nota
                FROM calificaciones c
                INNER JOIN periodos_academicos p ON p.id_periodo = c.id_periodo
                INNER JOIN materias m            ON m.id_materia = c.id_materia
                WHERE c.id_estudiante = %s
                ORDER BY p.anio_lectivo, p.fecha_inicio, m.nombre
            """,
            (id_estudiante,)
        )

        agrupado = {}
        todas = []

        for f in cursor.fetchall():
            nota = float(f["nota"])
            todas.append(nota)
            p = agrupado.setdefault(
                f["id_periodo"], {"nombre": f["periodo"], "notas": []}
            )
            p["notas"].append({"materia": f["materia"], "nota": nota})

        periodos = []

        for p in agrupado.values():
            valores = [n["nota"] for n in p["notas"]]
            p["promedio"] = round(sum(valores) / len(valores), 2)
            periodos.append(p)

        general = round(sum(todas) / len(todas), 2) if todas else None

        return estudiante, periodos, general

    except Exception as e:

        print(f"Error al obtener historial de calificaciones: {e}")

        return None, [], None

    finally:

        if cursor:
            cursor.close()

        connection.close()
# ============================================================
# EPF-08-07 - REPORTES DE CALIFICACIONES
# ============================================================

import csv
from io import BytesIO, StringIO


def generar_reporte_calificaciones(id_grupo=None, id_materia=None,
                                   id_periodo=None, id_estudiante=None):
    """
    Devuelve (columnas, filas, promedio).
    filas: lista de listas de texto.
    """

    columnas = ["Grupo", "Estudiante", "Materia", "Período", "Nota"]

    connection = get_db_connection()

    if not connection:
        return columnas, [], None

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                g.nombre AS grupo,
                CONCAT(u.apellido1, ' ', COALESCE(u.apellido2, ''), ', ', u.nombre) AS estudiante,
                m.nombre AS materia,
                p.nombre AS periodo,
                c.nota
            FROM calificaciones c
            INNER JOIN estudiantes e         ON e.id_estudiante = c.id_estudiante
            INNER JOIN usuarios u            ON u.id_usuario = e.id_usuario
            INNER JOIN grupos g              ON g.id_grupo = e.id_grupo
            INNER JOIN materias m            ON m.id_materia = c.id_materia
            INNER JOIN periodos_academicos p ON p.id_periodo = c.id_periodo
            WHERE 1 = 1
        """

        params = []

        if id_grupo:
            sql += " AND e.id_grupo = %s"
            params.append(id_grupo)
        if id_materia:
            sql += " AND c.id_materia = %s"
            params.append(id_materia)
        if id_periodo:
            sql += " AND c.id_periodo = %s"
            params.append(id_periodo)
        if id_estudiante:
            sql += " AND c.id_estudiante = %s"
            params.append(id_estudiante)

        sql += " ORDER BY g.nombre, estudiante, p.anio_lectivo, p.fecha_inicio, m.nombre"

        cursor.execute(sql, tuple(params))

        datos = cursor.fetchall()

        filas = [
            [f["grupo"], f["estudiante"].replace("  ", " "), f["materia"],
             f["periodo"], f"{float(f['nota']):.2f}"]
            for f in datos
        ]

        promedio = (
            round(sum(float(f["nota"]) for f in datos) / len(datos), 2)
            if datos else None
        )

        return columnas, filas, promedio

    except Exception as e:

        print(f"Error al generar reporte de calificaciones: {e}")

        return columnas, [], None

    finally:

        if cursor:
            cursor.close()

        connection.close()


def exportar_calificaciones_csv(columnas, filas, promedio):
    """CSV compatible con Excel (tildes y ñ correctas)."""

    buffer = StringIO()
    escritor = csv.writer(buffer, delimiter=';')
    escritor.writerow(columnas)
    escritor.writerows(filas)

    if promedio is not None:
        escritor.writerow([])
        escritor.writerow(["", "", "", "Promedio", f"{promedio:.2f}"])

    datos = BytesIO(buffer.getvalue().encode('utf-8-sig'))
    datos.seek(0)
    return datos

