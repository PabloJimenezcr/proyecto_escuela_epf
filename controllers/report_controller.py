import csv
from io import BytesIO, StringIO

from db import get_db_connection

TIPOS = {
    "asistencia": "Reporte de asistencia",
    "calificaciones": "Reporte de calificaciones",
    "comunicados": "Reporte de comunicados",
}


def obtener_periodos():
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


def _texto(valor):
    return "" if valor is None else str(valor)


def generar_reporte(tipo, id_grupo=None, id_periodo=None, desde=None, hasta=None):
    """Devuelve (titulo, columnas, filas)."""

    if tipo not in TIPOS:
        tipo = "asistencia"

    titulo = TIPOS[tipo]

    connection = get_db_connection()
    if not connection:
        return titulo, [], []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        params = []

        if tipo == "asistencia":
            columnas = ["Grupo", "Estudiante", "Fecha", "Estado", "Observación"]
            sql = """
                SELECT g.nombre AS c1,
                       CONCAT(u.apellido1, ' ', COALESCE(u.apellido2, ''), ', ', u.nombre) AS c2,
                       a.fecha AS c3, a.estado AS c4, a.observacion AS c5
                FROM asistencia a
                INNER JOIN estudiantes e ON e.id_estudiante = a.id_estudiante
                INNER JOIN usuarios u    ON u.id_usuario = e.id_usuario
                INNER JOIN grupos g      ON g.id_grupo = a.id_grupo
                WHERE 1 = 1
            """
            if id_grupo:
                sql += " AND a.id_grupo = %s"
                params.append(id_grupo)
            if desde:
                sql += " AND a.fecha >= %s"
                params.append(desde)
            if hasta:
                sql += " AND a.fecha <= %s"
                params.append(hasta)
            sql += " ORDER BY a.fecha DESC, g.nombre, c2"

        elif tipo == "calificaciones":
            columnas = ["Grupo", "Estudiante", "Materia", "Periodo", "Nota"]
            sql = """
                SELECT g.nombre AS c1,
                       CONCAT(u.apellido1, ' ', COALESCE(u.apellido2, ''), ', ', u.nombre) AS c2,
                       m.nombre AS c3, p.nombre AS c4, c.nota AS c5
                FROM calificaciones c
                INNER JOIN estudiantes e         ON e.id_estudiante = c.id_estudiante
                INNER JOIN usuarios u            ON u.id_usuario = e.id_usuario
                INNER JOIN grupos g              ON g.id_grupo = e.id_grupo
                INNER JOIN materias m            ON m.id_materia = c.id_materia
                INNER JOIN periodos_academicos p ON p.id_periodo = c.id_periodo
                WHERE 1 = 1
            """
            if id_grupo:
                sql += " AND e.id_grupo = %s"
                params.append(id_grupo)
            if id_periodo:
                sql += " AND c.id_periodo = %s"
                params.append(id_periodo)
            sql += " ORDER BY g.nombre, c2, m.nombre"

        else:  # comunicados
            columnas = ["Fecha", "Título", "Alcance", "Grupo", "Emisor"]
            sql = """
                SELECT DATE(co.fecha_envio) AS c1, co.titulo AS c2, co.alcance AS c3,
                       COALESCE(g.nombre, 'Toda la institución') AS c4,
                       CONCAT(u.nombre, ' ', u.apellido1) AS c5
                FROM comunicados co
                INNER JOIN usuarios u ON u.id_usuario = co.id_usuario_emisor
                LEFT JOIN grupos g    ON g.id_grupo = co.id_grupo
                WHERE 1 = 1
            """
            if id_grupo:
                sql += " AND (co.id_grupo = %s OR co.alcance = 'institucional')"
                params.append(id_grupo)
            if desde:
                sql += " AND DATE(co.fecha_envio) >= %s"
                params.append(desde)
            if hasta:
                sql += " AND DATE(co.fecha_envio) <= %s"
                params.append(hasta)
            sql += " ORDER BY co.fecha_envio DESC"

        cursor.execute(sql, tuple(params))

        filas = [
            [_texto(r[f"c{i}"]) for i in range(1, 6)]
            for r in cursor.fetchall()
        ]

        return titulo, columnas, filas

    except Exception as e:
        print(f"Error al generar reporte: {e}")
        return titulo, [], []

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ============================================================
# EPF-02-07 - EXPORTAR
# ============================================================

def exportar_csv(titulo, columnas, filas):
    """CSV compatible con Excel (tildes y ñ correctas)."""

    buffer = StringIO()
    escritor = csv.writer(buffer, delimiter=';')
    escritor.writerow(columnas)
    escritor.writerows(filas)

    datos = BytesIO(buffer.getvalue().encode('utf-8-sig'))
    datos.seek(0)
    return datos