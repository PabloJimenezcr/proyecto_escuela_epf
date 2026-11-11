from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection

def tasks_view():
    #Verificar que haya una sesión iniciada
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    id_usuario_conectado = session['id_usuario']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    #Obtener el id_docente real usando el id_usuario de la sesión
    cursor.execute("SELECT id_docente FROM docentes WHERE id_usuario = %s", (id_usuario_conectado,))
    docente_reg = cursor.fetchone()

    if not docente_reg:
        id_docente = 1  
    else:
        id_docente = docente_reg['id_docente']

    # ==========================================
    # PROCESAR FORMULARIO (POST: Publicar Tarea)
    # ==========================================
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha_entrega = request.form.get('fecha_entrega')
        
        # El select compuesto nos envía "id_materia-id_grupo" (como: "1-2")
        asignacion_raw = request.form.get('asignacion_dmg')
        if asignacion_raw and '-' in asignacion_raw:
            id_materia, id_grupo = asignacion_raw.split('-')
        else:
            id_materia = request.form.get('id_materia')
            id_grupo = request.form.get('id_grupo')
        
        try:
            cursor.execute("""
                INSERT INTO tareas (id_docente, id_grupo, id_materia, titulo, descripcion, fecha_entrega)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_docente, id_grupo, id_materia, titulo, descripcion, fecha_entrega))
            db.commit()
            flash('Tarea publicada exitosamente en el aula virtual.', 'success')
        except Exception as e:
            flash('Ocurrió un error al registrar la tarea en la base de datos.', 'danger')
            
        return redirect(url_for('admin_tareas'))

    # ==========================================
    # CARGAR DATOS VISTA (GET)
    # ==========================================
    # Traer las combinaciones de Materias y Grupos asignadas de tu tabla docente_materia_grupo
    cursor.execute("""
        SELECT dmg.id_grupo, dmg.id_materia, g.nombre AS nombre_grupo, m.nombre AS nombre_materia
        FROM docente_materia_grupo dmg
        INNER JOIN grupos g ON dmg.id_grupo = g.id_grupo
        INNER JOIN materias m ON dmg.id_materia = m.id_materia
    """)
    asignaciones = cursor.fetchall()
    
    # Leer todas las tareas guardadas y contar de forma agrupada cuántas vistas tieen para la hu 07-03
    cursor.execute("""
        SELECT t.*, g.nombre AS nombre_grupo, m.nombre AS nombre_materia,
               COUNT(tc.id_consulta) AS total_vistas
        FROM tareas t
        INNER JOIN grupos g ON t.id_grupo = g.id_grupo
        INNER JOIN materias m ON t.id_materia = m.id_materia
        LEFT JOIN tarea_consulta tc ON t.id_tarea = tc.id_tarea
        GROUP BY t.id_tarea
        ORDER BY t.fecha_entrega ASC
    """)
    tareas_publicadas = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('admin/tareas.html', asignaciones=asignaciones, tareas=tareas_publicadas)

def edit_task_logic():
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    id_tarea = request.form.get('id_tarea')
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    fecha_entrega = request.form.get('fecha_entrega')
    
    asignacion_raw = request.form.get('asignacion_dmg')
    if asignacion_raw and '-' in asignacion_raw:
        id_materia, id_grupo = asignacion_raw.split('-')
    else:
        id_materia = request.form.get('id_materia')
        id_grupo = request.form.get('id_grupo')
        
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE tareas 
            SET titulo = %s, descripcion = %s, fecha_entrega = %s, id_materia = %s, id_grupo = %s
            WHERE id_tarea = %s
        """, (titulo, descripcion, fecha_entrega, id_materia, id_grupo, id_tarea))
        db.commit()
        flash('Tarea modificada correctamente.', 'success')
    except Exception as e:
        flash('Ocurrió un error al intentar modificar la tarea.', 'danger')
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('admin_tareas'))


def delete_task_logic(id_tarea):
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM tareas WHERE id_tarea = %s", (id_tarea,))
        db.commit()
        flash('Tarea eliminada permanentemente del sistema.', 'success')
    except Exception as e:
        flash('Ocurrió un error al intentar eliminar la tarea.', 'danger')
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('admin_tareas'))

def view_submissions_view(id_tarea):
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Obtener detalles de la tarea seleccionada
    cursor.execute("""
        SELECT t.*, g.nombre AS nombre_grupo, m.nombre AS nombre_materia
        FROM tareas t
        INNER JOIN grupos g ON t.id_grupo = g.id_grupo
        INNER JOIN materias m ON t.id_materia = m.id_materia
        WHERE t.id_tarea = %s
    """, (id_tarea,))
    tarea = cursor.fetchone()
    
    if not tarea:
        flash('Tarea no encontrada.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('admin_tareas'))
        
    # raer a TODOS los estudiantes del grupo con sus nombres completos, vistas y archivos entregados
    cursor.execute("""
        SELECT e.id_estudiante, u.nombre, u.apellido1, u.apellido2,
               IF(tc.id_consulta IS NOT NULL, 'Sí', 'No') AS visto,
               te.archivo_ruta, te.texto_entrega, te.fecha_entrega
        FROM estudiantes e
        INNER JOIN usuarios u ON e.id_usuario = u.id_usuario
        LEFT JOIN tarea_consulta tc ON tc.id_tarea = %s AND tc.id_estudiante = e.id_estudiante
        LEFT JOIN tarea_entregas te ON te.id_tarea = %s AND te.id_estudiante = e.id_estudiante
        WHERE e.id_grupo = %s
        ORDER BY u.apellido1 ASC, u.apellido2 ASC
    """, (id_tarea, id_tarea, tarea['id_grupo']))
    alumnos = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('admin/tarea_revision.html', tarea=tarea, alumnos=alumnos)

def save_grade_logic():
    #Verificar que el usuario esté logueado
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    id_usuario_docente = session['id_usuario']
    id_tarea = request.form.get('id_tarea')
    id_materia = request.form.get('id_materia')
    id_estudiante = request.form.get('id_estudiante')
    nota = request.form.get('nota')
    comentario = request.form.get('comentario', '')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        #Buscar el id_docente real asignado a la cuenta conectada
        cursor.execute("SELECT id_docente FROM docentes WHERE id_usuario = %s", (id_usuario_docente,))
        docente = cursor.fetchone()
        id_docente = docente['id_docente'] if docente else 1
        
        # Obtener un id_periodo válido por defecto de tu tabla periodos_academicos
        cursor.execute("SELECT id_periodo FROM periodos_academicos LIMIT 1")
        periodo = cursor.fetchone()
        id_periodo = periodo['id_periodo'] if periodo else 1
        
        # Guardar la evaluación . 
        # Si ya existía una nota para esa materia y estudiante, se actualiza automáticamente.
        cursor.execute("""
            INSERT INTO calificaciones (id_estudiante, id_materia, id_docente, id_periodo, nota, comentario)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nota = %s, comentario = %s, fecha_registro = CURRENT_TIMESTAMP
        """, (id_estudiante, id_materia, id_docente, id_periodo, nota, comentario, nota, comentario))
        db.commit()
        
        flash('Calificación y retroalimentación registradas con éxito.', 'success')
    except Exception as e:
        flash('Ocurrió un error al intentar registrar la calificación.', 'danger')
    finally:
        cursor.close()
        db.close()
        
    # Regresa al docente a la misma pantalla 
    return redirect(url_for('admin_tareas_revision', id_tarea=id_tarea))