from datetime import datetime
from db import get_db_connection


def validar_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.strptime(str(valor), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def obtener_grupos_activos():
    conexion = get_db_connection()
    if not conexion:
        return []
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_grupo, nombre, nivel, seccion, anio_lectivo
            FROM grupos
            ORDER BY anio_lectivo DESC, nivel, seccion, nombre
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al consultar grupos para calendario: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def crear_evento_calendario(id_usuario_creador, titulo, descripcion, fecha, alcance, id_grupo=None):
    titulo = (titulo or "").strip()
    descripcion = (descripcion or "").strip()
    alcance = (alcance or "").strip().lower()
    fecha_validada = validar_fecha(fecha)

    if not titulo:
        return False, "El título del evento es obligatorio."
    if len(titulo) > 150:
        return False, "El título no puede superar los 150 caracteres."
    if len(descripcion) > 300:
        return False, "La descripción no puede superar los 300 caracteres."
    if not fecha_validada:
        return False, "Selecciona una fecha válida."
    if alcance not in ("institucional", "grupo"):
        return False, "Selecciona un alcance válido (Institucional o Por grupo)."

    if alcance == "grupo":
        try:
            id_grupo = int(id_grupo)
            if id_grupo <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return False, "Selecciona el grupo para este evento."
    else:
        id_grupo = None

    conexion = get_db_connection()
    if not conexion:
        return False, "No se pudo conectar con la base de datos."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO eventos_calendario
                (id_usuario_creador, titulo, descripcion, fecha, alcance, id_grupo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id_usuario_creador, titulo, descripcion or None, fecha_validada, alcance, id_grupo)
        )
        conexion.commit()
        return True, "Evento registrado en el calendario correctamente."
    except Exception as e:
        conexion.rollback()
        print(f"Error al crear evento de calendario: {e}")
        return False, "No fue posible guardar el evento."
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def actualizar_evento_calendario(id_evento, titulo, descripcion, fecha, alcance, id_grupo=None):
    try:
        id_evento = int(id_evento)
    except (TypeError, ValueError):
        return False, "Evento no válido."

    titulo = (titulo or "").strip()
    descripcion = (descripcion or "").strip()
    alcance = (alcance or "").strip().lower()
    fecha_validada = validar_fecha(fecha)

    if not titulo:
        return False, "El título del evento es obligatorio."
    if len(titulo) > 150:
        return False, "El título no puede superar los 150 caracteres."
    if len(descripcion) > 300:
        return False, "La descripción no puede superar los 300 caracteres."
    if not fecha_validada:
        return False, "Selecciona una fecha válida."
    if alcance not in ("institucional", "grupo"):
        return False, "Selecciona un alcance válido."

    if alcance == "grupo":
        try:
            id_grupo = int(id_grupo)
            if id_grupo <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return False, "Selecciona el grupo para este evento."
    else:
        id_grupo = None

    conexion = get_db_connection()
    if not conexion:
        return False, "No se pudo conectar con la base de datos."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE eventos_calendario
            SET titulo = %s,
                descripcion = %s,
                fecha = %s,
                alcance = %s,
                id_grupo = %s
            WHERE id_evento = %s
            """,
            (titulo, descripcion or None, fecha_validada, alcance, id_grupo, id_evento)
        )
        conexion.commit()
        return True, "Evento actualizado correctamente."
    except Exception as e:
        conexion.rollback()
        print(f"Error al actualizar evento: {e}")
        return False, "No fue posible actualizar el evento."
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def eliminar_evento_calendario(id_evento):
    try:
        id_evento = int(id_evento)
    except (TypeError, ValueError):
        return False, "Evento no válido."

    conexion = get_db_connection()
    if not conexion:
        return False, "No se pudo conectar con la base de datos."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM eventos_calendario WHERE id_evento = %s", (id_evento,))
        conexion.commit()
        return True, "Evento eliminado del calendario."
    except Exception as e:
        conexion.rollback()
        print(f"Error al eliminar evento: {e}")
        return False, "No fue posible eliminar el evento."
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def obtener_eventos_para_usuario(id_usuario, rol_usuario, mes=None, alcance_filtro=None):
    """
    Devuelve los eventos visibles según el rol:
    - Administrador / Personal Administrativo / Docente: todos los eventos (o filtrados).
    - Estudiante: eventos institucionales + eventos de su grupo.
    - Padre de Familia: eventos institucionales + eventos de los grupos de sus hijos.
    """
    conexion = get_db_connection()
    if not conexion:
        return []

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)

        grupos_permitidos = []
        restringir_por_grupo = False

        if rol_usuario == "Estudiante":
            restringir_por_grupo = True
            cursor.execute("SELECT id_grupo FROM estudiantes WHERE id_usuario = %s", (id_usuario,))
            grupos_permitidos = [row["id_grupo"] for row in cursor.fetchall()]

        elif rol_usuario == "Padre de Familia":
            restringir_por_grupo = True
            cursor.execute(
                """
                SELECT DISTINCT e.id_grupo
                FROM padres p
                INNER JOIN padre_estudiante pe ON pe.id_padre = p.id_padre
                INNER JOIN estudiantes e ON e.id_estudiante = pe.id_estudiante
                WHERE p.id_usuario = %s
                """,
                (id_usuario,)
            )
            grupos_permitidos = [row["id_grupo"] for row in cursor.fetchall()]

        sql = """
            SELECT
                ev.id_evento,
                ev.titulo,
                ev.descripcion,
                ev.fecha,
                ev.alcance,
                ev.id_grupo,
                ev.fecha_creacion,
                g.nombre AS nombre_grupo,
                g.nivel,
                g.seccion,
                CONCAT_WS(' ', u.nombre, u.apellido1) AS creador_nombre
            FROM eventos_calendario ev
            LEFT JOIN grupos g ON g.id_grupo = ev.id_grupo
            LEFT JOIN usuarios u ON u.id_usuario = ev.id_usuario_creador
            WHERE 1 = 1
        """
        params = []

        if restringir_por_grupo:
            if grupos_permitidos:
                placeholders = ",".join(["%s"] * len(grupos_permitidos))
                sql += f" AND (ev.alcance = 'institucional' OR ev.id_grupo IN ({placeholders}))"
                params.extend(grupos_permitidos)
            else:
                sql += " AND ev.alcance = 'institucional'"

        if mes:
            # mes en formato 'YYYY-MM'
            sql += " AND DATE_FORMAT(ev.fecha, '%Y-%m') = %s"
            params.append(mes)

        if alcance_filtro in ("institucional", "grupo"):
            sql += " AND ev.alcance = %s"
            params.append(alcance_filtro)

        sql += " ORDER BY ev.fecha ASC, ev.id_evento DESC"

        cursor.execute(sql, tuple(params))
        return cursor.fetchall()

    except Exception as e:
        print(f"Error al consultar eventos de calendario: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        conexion.close()