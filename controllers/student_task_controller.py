import os
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from db import get_db_connection

# Carpeta física donde se guardarán los documentos reales en computadora
UPLOAD_FOLDER = os.path.join('uploads', 'tareas')

def student_tasks_view():
    if 'id_usuario' not in session or session.get('rol_usuario') != 'Estudiante':
        flash('Acceso denegado: Sección exclusiva para estudiantes.', 'danger')
        return redirect(url_for('dashboard'))
        
    id_usuario_estudiante = session['id_usuario']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Buscar a q estudiante y grupo pertenece el usuario conectado
    cursor.execute("SELECT id_estudiante, id_grupo FROM estudiantes WHERE id_usuario = %s", (id_usuario_estudiante,))
    estudiante_reg = cursor.fetchone()
    
    if not estudiante_reg:
        flash('Error: No se encontró tu perfil de estudiante en el sistema.', 'danger')
        db.close()
        return redirect(url_for('dashboard'))
        
    id_estudiante = estudiante_reg['id_estudiante']
    id_grupo = estudiante_reg['id_grupo']

    # ==========================================
    # CARGAR LISTA DE TAREAS (GET)
    # ==========================================
    cursor.execute("""
        SELECT t.*, m.nombre AS nombre_materia, te.fecha_entrega AS entregado_fecha
        FROM tareas t
        INNER JOIN materias m ON t.id_materia = m.id_materia
        LEFT JOIN tarea_entregas te ON t.id_tarea = te.id_tarea AND te.id_estudiante = %s
        WHERE t.id_grupo = %s
        ORDER BY t.fecha_entrega ASC
    """, (id_estudiante, id_grupo))
    tareas = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('admin/estudiante_tareas.html', tareas=tareas)

#-

def student_view_task_logic(id_tarea):
    """Suma una vista a la tarea cuando el alumno presiona ver instrucciones."""
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    id_usuario_estudiante = session['id_usuario']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT id_estudiante FROM estudiantes WHERE id_usuario = %s", (id_usuario_estudiante,))
    estudiante = cursor.fetchone()
    
    if estudiante:
        id_estudiante = estudiante['id_estudiante']
        try:
            # INSERT IGNORE evita duplicar las vistas si el alumno la vuelve a abrir
            cursor.execute("""
                INSERT IGNORE INTO tarea_consulta (id_tarea, id_estudiante) 
                VALUES (%s, %s)
            """, (id_tarea, id_estudiante))
            db.commit()
        except Exception:
            pass
            
    cursor.close()
    db.close()
    return {"status": "ok"}


def student_submit_task_logic():
    """Procesa y guarda cualquier tipo de archivo subido por el alumno."""
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    id_usuario_estudiante = session['id_usuario']
    id_tarea = request.form.get('id_tarea')
    texto_entrega = request.form.get('texto_entrega', '')
    
    # Capturar el archivo del formulario
    file = request.files.get('archivo_tarea')
    
    if not file or file.filename == '':
        flash('Error: Debes seleccionar un archivo para realizar la entrega.', 'danger')
        return redirect(url_for('estudiante_tareas'))
        
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT id_estudiante FROM estudiantes WHERE id_usuario = %s", (id_usuario_estudiante,))
    estudiante = cursor.fetchone()
    
    if not estudiante:
        flash('Error en el perfil de estudiante.', 'danger')
        db.close()
        return redirect(url_for('dashboard'))
        
    id_estudiante = estudiante['id_estudiante']
    
    # Guardar archivo físico en el servidor de forma segura sin importar la extensión
    filename = secure_filename(f"tarea_{id_tarea}_{id_estudiante}_{file.filename}")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Crea la carpeta static/uploads/tareas/ si no existe
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    try:
        cursor.execute("""
            INSERT INTO tarea_entregas (id_tarea, id_estudiante, archivo_ruta, texto_entrega)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE archivo_ruta = %s, texto_entrega = %s, fecha_entrega = CURRENT_TIMESTAMP
        """, (id_tarea, id_estudiante, filename, texto_entrega, filename, texto_entrega))
        db.commit()
        flash('¡Tarea entregada con éxito!', 'success')
    except Exception:
        flash('Hubo un error al guardar tu entrega en la base de datos.', 'danger')
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('estudiante_tareas'))

def student_delete_submission_logic(id_tarea):
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    id_usuario_estudiante = session['id_usuario']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Obtener el id_estudiante real a partir de su cuenta conectada
    cursor.execute("SELECT id_estudiante FROM estudiantes WHERE id_usuario = %s", (id_usuario_estudiante,))
    estudiante = cursor.fetchone()
    
    if estudiante:
        id_estudiante = estudiante['id_estudiante']
        try:
            # Borrar el registro de la entrega del alumno de forma permanente en la BD
            cursor.execute("DELETE FROM tarea_entregas WHERE id_tarea = %s AND id_estudiante = %s", (id_tarea, id_estudiante))
            db.commit()
            flash('Entrega eliminada correctamente del aula virtual.', 'success')
        except Exception:
            flash('Ocurrió un error al intentar revocar la entrega.', 'danger')
            
    cursor.close()
    db.close()
    return redirect(url_for('estudiante_tareas'))