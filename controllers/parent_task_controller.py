from flask import render_template, redirect, url_for, session, flash
from db import get_db_connection

def parent_tasks_view():
    # Verificar que sea un Padre de Familia logueado
    if 'id_usuario' not in session or session.get('rol_usuario') != 'Padre de Familia':
        flash('Acceso denegado: Sección exclusiva para padres de familia.', 'danger')
        return redirect(url_for('dashboard'))
        
    id_usuario_padre = session['id_usuario']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Obtener el id_padre real a partir del id_usuario de la sesión
    cursor.execute("SELECT id_padre FROM padres WHERE id_usuario = %s", (id_usuario_padre,))
    padre_reg = cursor.fetchone()
    
    if not padre_reg:
        flash('Error: No se encontró tu perfil de tutor en el sistema.', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))
        
    id_padre = padre_reg['id_padre']

    # Jala los hijos vinculados (como Jeff) y las tareas de su grupo
    cursor.execute("""
        SELECT u.nombre AS nombre_hijo, u.apellido1 AS apellido_hijo, g.nombre AS nombre_grupo,
               t.titulo, t.fecha_entrega, m.nombre AS nombre_materia,
               IF(te.id_entrega IS NOT NULL, 'Entregado', 'Pendiente') AS estado_entrega
        FROM padre_estudiante pe
        INNER JOIN estudiantes e ON pe.id_estudiante = e.id_estudiante
        INNER JOIN usuarios u ON e.id_usuario = u.id_usuario
        INNER JOIN grupos g ON e.id_grupo = g.id_grupo
        INNER JOIN tareas t ON t.id_grupo = g.id_grupo
        INNER JOIN materias m ON t.id_materia = m.id_materia
        LEFT JOIN tarea_entregas te ON t.id_tarea = te.id_tarea AND te.id_estudiante = e.id_estudiante
        WHERE pe.id_padre = %s
        ORDER BY u.nombre ASC, t.fecha_entrega ASC
    """, (id_padre,))
    tareas_hijos = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('admin/padre_tareas.html', tareas_hijos=tareas_hijos)